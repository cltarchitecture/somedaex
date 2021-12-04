"""The index module defines the TypeIndex class and associated exceptions."""

from collections.abc import Mapping
from typing import Iterator, Type
from .task import Task


class NameConflict(Exception):
    """A NameConflict error is raised when the name of a task type that is being
    added to a TypeIndex normalizes to the same value as the name of a task type
    that is already defined in the index."""

    def __init__(self, new_type, existing_type):
        new_name = new_type.__qualname__
        existing_name = existing_type.__qualname__
        super().__init__(f"Name of task {new_name} conflicts with {existing_name}")


class NoSuchType(LookupError):
    """A NoSuchType error is raised when an undefined task type is requested
    from a TypeIndex."""

    def __init__(self, name, index):
        super().__init__(f"Task type '{name}' is not defined")
        self.requested_type = name
        self.valid_types = [t.type for t in index]


class TypeIndex(Mapping[str, Type[Task]]):
    """A TypeIndex maps the names of task types to their implementations."""

    def __init__(self):
        self._index = {}

    def __len__(self):
        return len(self._index)

    def __iter__(self) -> Iterator[Type[Task]]:
        return iter(self._index.values())

    def __getitem__(self, name: str) -> Type[Task]:
        try:
            return self._index[name.lower()]
        except KeyError as err:
            raise NoSuchType(type, self) from err

    def add(self, task_class: Type[Task]):
        """Add a task type to the index."""
        key = task_class.type.lower()
        if key in self._index:
            raise NameConflict(task_class, self._index[key])
        self._index[key] = task_class
