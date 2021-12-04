"""The loadfile module provides a task implementation that loads data from a
file into a pipeline.
"""

from collections.abc import Mapping
from pathlib import Path

import pyarrow.csv
import pyarrow.json
import pyarrow.parquet

from ..arrow_util import ArrowFileWriter
from ..observableproxy import observe
from ..pipeline.task import NiladicTask, Status


VALID_FORMATS = ("arrow", "csv", "json", "parquet")


def _has_required_keys(config, keys):
    if isinstance(config, Mapping):
        return any(key in config for key in keys)
    return False


class LoadFile(NiladicTask):
    """A LoadFile task reads data from a file."""

    @property
    def path(self):
        """The path to the file."""
        return Path(self.config["path"])

    @property
    def format(self):
        """The format of the file."""
        return self.config["format"]

    def validate(self) -> bool:
        return (
            _has_required_keys(self.config, ("path", "format"))
            and self.path.is_file()
            and self.format in VALID_FORMATS
        )

    async def get_table(self):
        return self._get_table()

    def _get_full_table(self) -> pyarrow.Table:
        return self._table_reader.read_table()

    def file_path(self) -> Path:
        if self.format == "arrow":
            return self.path
        return super().file_path()

    async def run(self):
        await observe(self.status).equals(Status.READY)

        if self.format == "arrow":
            print("format is arrow")
            table = await self.get_table()
            print("table", table, table.schema)
            self.schema = table.schema
            print("schema", self.schema)

        else:
            try:
                method_name = "_read_" + self.format
                read_table = getattr(self, method_name)
            except NameError as err:
                raise Exception(f"Unsupported format {self.format}") from err

            self.status = Status.WORKING
            temp_table = read_table()
            self.schema = temp_table.schema
            ArrowFileWriter.write_table(temp_table, self.file_path())

        self.status = Status.COMPLETE

    def _read_csv(self):
        return pyarrow.csv.read_csv(self.path)

    def _read_json(self):
        return pyarrow.json.read_json(self.path)

    def _read_parquet(self):
        return pyarrow.parquet.read_table(self.path)
