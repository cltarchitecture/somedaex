# Standard library imports
from abc import abstractmethod
from pathlib import Path
from typing import Iterable, Iterator

# Third-party library imports
from datasets.table import ConcatenationTable
import pyarrow

# Local imports
from ...arrow_util import (
    ArrowStreamReader,
    ArrowStreamWriter,
    copy_stream_to_file,
    iter_rows,
)

from .monadic import MonadicTask
from .results import ResultsBuffer
from .status import Status
from .task import RowIterator


MAX_BUFFERED_RESULT_ROWS = 1000
MIN_INITIAL_SAMPLES = 10


class RowwiseTask(MonadicTask):
    """A row-wise task processes the results of one exactly one source task one
    row at a time."""

    def __init__(self, **args):
        super().__init__(**args)
        self._output_buffer: ResultsBuffer = None
        self._output_writer: ArrowStreamWriter = None

        self._schema: pyarrow.Schema = None
        self._num_input_rows_processed = 0  # No. of input rows processed by run()
        self._num_output_rows_buffered = 0  # No. of output rows appended to the buffer
        self._num_output_rows_written = 0  # No. of output rows written to disk

        self._input_rows = None

    @property
    def output_path(self) -> Path:
        """Get the path to the task's streaming output file."""
        return self._workdir / f"{self.id}.arrows"

    def stream_path(self) -> Path:
        """Get the path to the task's streaming output file."""
        return self._workdir / f"{self.id}.arrows"

    def output_row(self, *values):
        """Write a single row to the task's output buffer."""
        if self._output_buffer is None:
            self._output_buffer = ResultsBuffer(self.schema)

        self._output_buffer.append(*values)
        self._num_output_rows_buffered += 1

        if len(self._output_buffer) >= MAX_BUFFERED_RESULT_ROWS:
            self.flush_output_buffer()

    def flush_output_buffer(self):
        """Write the contents of the output buffer to the streaming output file."""
        batch = self._output_buffer.flush()
        self.output_batch(batch)

    def output_batch(self, batch):
        """Write a record batch to the streaming output file."""
        if self._schema is None:
            raise Exception("Unable to write because there is no schema")

        if self._output_writer is None:
            self._output_writer = ArrowStreamWriter(self.output_path, self._schema)

        self._output_writer.write(batch)
        self._num_output_rows_written += batch.num_rows

    def on_reset(self, reason):
        """Reset the task's state due to a change in its input or configuration."""
        super().on_reset(reason)
        self._output_buffer = None
        self._output_writer = None
        self._num_input_rows_processed = 0
        self._num_output_rows_buffered = 0
        self._num_output_rows_written = 0
        # Delete the file so no one else can read it?

    def rows(self, column_names: Iterable[str] = None):
        return RowwiseResultsIterator(self, column_names)

    async def run(self):
        if self._input_rows is None:
            column_names = self.column
            if not isinstance(column_names, list):
                column_names = [column_names]
            self._input_rows = self.source.rows(column_names)

        try:
            self.status = Status.WORKING

            row = await self._input_rows.__anext__()
            raw_result = self.execute(*row)
            self._num_input_rows_processed += 1

            if isinstance(raw_result, Iterator):
                for result in raw_result:
                    self.output_row(*result)
            elif raw_result is not None:
                self.output_row(*raw_result)

            self.status = Status.PAUSED

        except StopIteration:
            self.flush_output_buffer()
            self.status = Status.FINISHED

            stream_path = self.stream_path()
            file_path = self.file_path()
            copy_stream_to_file(stream_path, file_path)
            self.status = Status.COMPLETE

    @abstractmethod
    def execute(self, *inputs):
        """Execute the task on a single row of data."""


class OneToOneRowwiseTask(RowwiseTask):
    """A one-to-one row-wise task produces exactly one output row for each input row."""

    def _get_full_table(self):
        return ConcatenationTable.from_tables(
            [
                self.source.table,
                self._table_reader.read_table(),
            ],
            1,
        )


class OneToManyRowwiseTask(RowwiseTask):
    """A one-to-many task can produce one output row, several output rows, or no
    output rows for each input row."""


async def emptyTupler():
    """A generator that yields empty tuples forever."""
    while True:
        yield ()


class RowwiseResultsIterator(RowIterator):
    """Iterates over the results from a row-wise task."""

    def __init__(self, task: RowwiseTask, column_names: Iterable[str] = None):
        super().__init__(task, column_names)
        self._task = task  # Only necessary for type hints
        self._stream_reader = None
        self._current_batch = None
        self._source_rows = None
        self._source_column_names = None
        self._own_column_names = None

    def on_reset(self, reason):
        super().on_reset(reason)
        self._current_batch = None
        self._source_rows = None
        self._source_column_names = None
        self._own_column_names = None

        if self._stream_reader is not None:
            self._stream_reader.close()
            self._stream_reader = None

    def _split_column_names(self):
        own_columns = set(self._task.schema.names)
        requested_columns = set(self._column_names)
        self._own_column_names = list(requested_columns & own_columns)
        self._source_column_names = list(requested_columns - own_columns)

    def __aiter__(self):
        return self

    async def __anext__(self):
        """Get the next row of output.

        First, exhaust the rows already written to the parent task's output stream
        Then pull rows sitting in the parent task's output buffer
        Then subscribe to parent_task.output and yield rows as they come in

        A significant amount of time may elapse between __next__() calls,
        so we'll need to check the status of the parent task to see what stage
        we're at.
        """

        # If the task is complete, we can read values directly from its result table.
        if self._task.status == Status.COMPLETE:
            return self._next_row_from_table()

        # Ensure that the source rows iterator is set up
        if self._source_rows is None:
            await self._setup_source_row_iterator()

        # Run the task until there is a row to return
        while self._index >= self._task._num_output_rows_buffered:
            await self._task.run()

        # If we already have a RecordBatch iterator, attempt to read a row from it
        if self._current_batch:
            row = self._from_current_batch()
            if row is not None:
                return await self._add_source_columns(row)

        # If we haven't yet read all the rows that have been written to disk
        if self._index < self._task._num_output_rows_written:

            # Create a reader if we don't already have one
            if self._stream_reader is None:
                self._stream_reader = ArrowStreamReader(self._task.output_path)

            try:
                batch = next(self._stream_reader)
                self._current_batch = iter_rows(batch)
            except StopIteration as stop:
                # There are no more batches in the output stream
                # We shouldn't ever get here
                raise Exception("Unexpected end of output stream") from stop

            row = self._from_current_batch()
            return await self._add_source_columns(row)

        row = self._from_buffer()
        return await self._add_source_columns(row)

    async def _setup_source_row_iterator(self):
        if self._column_names is None:
            self._source_column_names = None
            self._own_column_names = None
        else:
            self._split_column_names()
            if len(self._source_column_names) == 0:
                self._source_rows = emptyTupler()
                return

        self._source_rows = self._task.source.rows(self._source_column_names)

        # Get the _source_rows iterator "caught up"
        delta = self._index - self._source_rows._index
        if hasattr(self._source_rows, "skip"):
            self._source_rows.skip(delta)
        else:
            for _ in range(delta):
                await self._source_rows.__anext__()

    def _from_current_batch(self):
        try:
            row = next(self._current_batch)
        except StopAsyncIteration:
            # The current batch has been exhausted
            self._current_batch = None
            return

        # try:
        #     parent_row = next(self._source_rows)
        # except StopAsyncIteration as stop:
        #     raise Exception("Unexpected end of source row iterable") from stop

        self._index += 1
        return row  # self._unify_tuples(own_row, parent_row)

    def _from_buffer(self):
        buffer_index = self._index - self._task._num_output_rows_written
        row = self._task._output_buffer[buffer_index]
        self._index += 1
        return row

    async def _add_source_columns(self, own_row):
        try:
            parent_row = await self._source_rows.__anext__()
        except StopAsyncIteration as stop:
            raise Exception("Unexpected end of source row iterable") from stop

        return self._unify_tuples(own_row, parent_row)

    def _unify_tuples(self, own_row, parent_row):
        if self._column_names is None:
            return parent_row + own_row

        unified = []

        for column_name in self._column_names:
            try:
                index = self._own_column_names.index(column_name)
                unified.append(own_row[index])
            except ValueError:
                index = self._parent_column_names.index(column_name)
                unified.append(parent_row[index])

        return tuple(unified)
