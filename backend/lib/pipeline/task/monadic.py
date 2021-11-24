from abc import abstractmethod
from typing import Union

import pyarrow
import rx.operators

from observableproxy import observe, ObservableProperty
from .status import Status
from .task import Task


class MonadicTask(Task):
    """A monadic task processes the results of exactly one source task."""

    source = ObservableProperty("The source of the task's input data.")
    column = ObservableProperty("The name of the column that the task operates on.")

    def __init__(self, source: Union[Task, None], column: str, **other):
        super().__init__(**other)
        self.source = source
        self.column = column

        if source is not None:
            self._source_reset_subscription = source.reset.subscribe(self.reset)
        else:
            self._source_reset_subscription = None

        self._source_reset_subscription = None
        observe(self.source).subscribe(self.on_source_change)
        observe(self.column).subscribe(self.reset)
        observe(self.status).pipe(
            rx.operators.filter(lambda status: status == Status.READY),
        ).subscribe(self.on_ready)

    def __del__(self):
        if self._source_reset_subscription is not None:
            self._source_reset_subscription.dispose()
            self._source_reset_subscription = None

    def args(self):
        return {
            **super().args(),
            "source": self.source,
            "column": self.column,
        }

    def update(self, updates: dict):
        if "source" in updates:
            self.source = updates.pop("source")
        if "column" in updates:
            self.column = updates.pop("column")
        super().update(updates)

    def validate(self) -> bool:
        if not isinstance(self.source, Task):
            return False

        if isinstance(self.column, list):
            return all(self.validate_column_name(name) for name in self.column)

        return self.validate_column_name(self.column)

    def validate_column_name(self, name) -> bool:
        if not isinstance(name, str):
            return False

        source_schema = self.source.schema
        print(source_schema)
        if not isinstance(source_schema, pyarrow.Schema):
            return False

        return name in source_schema.names

    def on_source_change(self, new_source):
        if self._source_reset_subscription is not None:
            self._source_reset_subscription.dispose()
            self._source_reset_subscription = None

        if new_source is not None:
            self._source_reset_subscription = new_source.reset.subscribe(self.reset)

        self.reset.emit()

    def on_ready(self, _):
        self.schema = self.get_schema()

    @abstractmethod
    def get_schema(self) -> pyarrow.Schema:
        """Get the schema of the data produced by this task."""
