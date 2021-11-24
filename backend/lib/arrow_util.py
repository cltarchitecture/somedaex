"""The arrow_util module provides convenience wrappers and utility functions
for working with PyArrow tables."""

from pathlib import Path
from typing import Iterable, Iterator, List, Tuple, Union

import pyarrow


# Type aliases
Pathlike = Union[Path, str]
TableOrBatch = Union[pyarrow.Table, pyarrow.RecordBatch]
OptionalStrings = Union[Iterable[str], None]
Column = Union[pyarrow.Array, pyarrow.ChunkedArray]


class ArrowStreamReader:
    """An ArrowStreamReader enables simple iteration over the batches in an
    Arrow stream format file."""

    def __init__(self, path: Pathlike):
        self._file = pyarrow.input_stream(str(path))
        self._reader = pyarrow.ipc.open_stream(self._file)

    def __del__(self):
        self.close()

    def __iter__(self) -> Iterator[pyarrow.RecordBatch]:
        return self

    def __next__(self) -> pyarrow.RecordBatch:
        return self._reader.read_next_batch()

    def reset(self):
        """Reset the reader to the beginning of the file."""
        self._file.seek(0)
        self._reader = pyarrow.ipc.open_stream(self._file)

    def close(self):
        """Close the underlying file handle."""
        self._file.close()


class ArrowStreamWriter:
    """An ArrowStreamWriter writes data to a file in the Arrow stream format."""

    def __init__(self, path: Pathlike, schema: pyarrow.Schema):
        self._stream = pyarrow.output_stream(str(path))
        self._writer = pyarrow.ipc.new_stream(self._stream, schema)

    def __del__(self):
        self.close()

    def write(self, table_or_batch: TableOrBatch):
        """Write a PyArrow table or record batch to the file."""
        self._writer.write(table_or_batch)

    def close(self):
        """Finish writing the file and close the underlying file handle."""
        self._writer.close()
        self._stream.close()


class ArrowFileWriter:
    """An ArrowFileWriter writes data to a file in the Arrow IPC format."""

    def __init__(self, path: Pathlike, schema: pyarrow.Schema):
        self._file = pyarrow.output_stream(str(path))
        self._writer = pyarrow.ipc.new_file(self._file, schema)

    def __del__(self):
        self._file.close()

    def write(self, table_or_batch: TableOrBatch):
        """Write a PyArrow table or record batch to the file."""
        self._writer.write(table_or_batch)

    def close(self):
        """Finish writing the file and close the underlying file handle."""
        self._writer.close()
        self._file.close()

    @classmethod
    def write_table(cls, table: pyarrow.Table, path: Pathlike):
        """Write a PyArrow table to a file at the given path."""
        writer = cls(path, table.schema)
        for batch in table.to_batches():
            writer.write(batch)
        writer.close()


class MemoryMappedTableReader:
    """An MemoryMappedTableReader ."""

    def __init__(self, path: Pathlike):
        self._file = pyarrow.memory_map(str(path))

    def __del__(self):
        self._file.close()

    def read_table(self) -> pyarrow.Table:
        """Read the file"""
        reader = pyarrow.ipc.open_file(self._file)
        return reader.read_all()

    def close(self):
        """Close the underlying file handle."""
        self._file.close()


def copy_stream_to_file(stream_path: Path, file_path: Path, delete_original=False):
    """Copy the contents of an Arrow stream format file to an IPC format file."""
    stream_reader = ArrowStreamReader(stream_path)
    batch = next(stream_reader)
    file_writer = ArrowFileWriter(file_path, batch.schema)

    while batch:
        file_writer.write(batch)
        batch = next(stream_reader, None)

    file_writer.close()
    stream_reader.close()

    if delete_original:
        stream_path.unlink()


def get_columns(
    table_or_batch: TableOrBatch,
    column_names: OptionalStrings = None,
) -> List[Column]:
    """Return the PyArrow arrays in which the values for the named columns are stored.

    If no column names are provided, arrays corresponding to all the columns in
    the given table or record batch are returned.
    """
    if column_names is None:
        return table_or_batch.columns
    return [table_or_batch.column(name) for name in column_names]


def iter_rows(
    table_or_batch: TableOrBatch,
    column_names: OptionalStrings = None,
) -> Iterable[Tuple]:
    """Create an iterable over the rows in a PyArrow table or record batch.

    If a list of column names is provided, only values from those columns will
    be included in the output.
    """
    return zip(get_columns(table_or_batch, column_names))


def get_row(
    table_or_batch: TableOrBatch,
    index: int,
    column_names: OptionalStrings = None,
) -> Tuple:
    """Retrieve a single row from a PyArrow table or record batch.

    If a list of column names is provided, only values from those columns will
    be included in the output.
    """
    return tuple(column[index] for column in get_columns(table_or_batch, column_names))
