"""The task module defines Task, the abstract base class for all tasks."""

# Standard library imports
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Mapping, Union

# Third-party library imports
from datasets.table import Table
import rx.operators
from rx.subject import Subject

# Local imports
from ...arrow_util import MemoryMappedTableReader, get_row
from ...observableproxy import ObservableProperty, observe
from .status import Status


class Task(ABC):
    """An abstract base class for tasks."""

    config = ObservableProperty("The task's configuration")
    status = ObservableProperty[Status]("The data processing status of the task.")
    schema = ObservableProperty("The schema of the task's result data.")

    def __init__(self, id: Union[int, str], workdir: Path, **config):
        self.id = id
        self._workdir = workdir
        self.status = Status.INVALID
        self.config = config
        self.schema = None

        self.reset = Subject()

        self._table: Table = None
        """A table containing the full set of results output by the task."""

        self._table_reader: MemoryMappedTableReader = None
        """An object that contains or manages the handle for the file the task's
        results are stored in."""

        observe(self.config).pipe(
            rx.operators.distinct_until_changed(),
        ).subscribe(self.reset)
        self.reset.subscribe(self.on_reset)

    def __del__(self):
        try:
            if self._table_reader:
                self._table_reader.close()
        except:
            pass

    @classmethod
    @property
    def type(cls) -> str:
        """The name of the task's type."""
        name = cls.__name__
        return name[0].lower() + name[1:]

    def args(self) -> Mapping[str, Any]:
        """Create a representation of the task's state that consists solely of
        primitives in a dictionary. The output of this method is used for
        serializing tasks.
        """
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            **self.config,
        }

    def update(self, updates: dict[str, Any]):
        self.config.update(updates)  # lambda config: config | updates)

    async def get_table(self) -> Table:
        await observe(self.status).equals(Status.COMPLETE)
        return self._get_table()

    def _get_table(self) -> Table:
        if self._table is None:
            self._table_reader = MemoryMappedTableReader(self.file_path())
            self._table = self._get_full_table()

        return self._table

    def on_reset(self, _):
        """Reset the task's state due to a change in its input or configuration."""
        self._table = None
        self.schema = None

        if self._table_reader is not None:
            self._table_reader.close()
            self._table_reader = None

        if self.validate():
            self.status = Status.READY
        else:
            self.status = Status.INVALID

    def file_path(self) -> Path:
        """Get the path to the Arrow file containing the task's results."""
        return self._workdir / f"{self.id}.arrow"

    @abstractmethod
    def _get_full_table(self) -> Table:
        """Get the full result table that combines this task's output with the
        results from its parent tasks."""

    @abstractmethod
    def validate(self) -> bool:
        """Check whether the task is properly configured and ready to process data."""

    # @abstractmethod
    # def get_schema(self) -> pyarrow.Schema:
    #     """Get the schema of the data produced by this task."""

    @abstractmethod
    async def run(self):
        """Run the task."""

    def rows(self, column_names: List[str] = None):
        """Get an iterator over the task's result rows, optionally limited to a
        list of specified columns."""
        return RowIterator(self, column_names)


class DatasetTask(Task):
    """A dataset task processes all rows from its source task(s) at the same time."""

    # Examples: Topic modeling, table joins


class RowIterator:
    """Iterates over the rows produced by a task."""

    def __init__(self, task: Task, column_names=None):
        self._task = task
        self._column_names = column_names
        self._index = 0
        self._task_reset_subscription = self._task.reset.subscribe(self.on_reset)

    def __del__(self):
        self._task_reset_subscription.dispose()

    def on_reset(self, _):
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._task.status == Status.INVALID:
            await observe(self._task.status).equals(Status.READY)
        if self._task.status in (Status.READY, Status.PAUSED):
            await self._task.run()
        await observe(self._task.status).equals(Status.COMPLETE)
        return await self._next_row_from_table()

    async def _next_row_from_table(self):
        table = await self._task.get_table()

        if self._index >= len(table):
            raise StopAsyncIteration

        row = get_row(table, self._index, self._column_names)
        self._index += 1
        return row

    def skip(self, num: int):
        self._index += num
