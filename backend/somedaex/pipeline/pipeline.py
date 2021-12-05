"""The pipeline module defines the Pipeline class."""

# Standard library imports
from pathlib import Path
from typing import Mapping

# Local imports
from .index import TypeIndex
from .task import Task


class Pipeline(Mapping):
    """A pipeline is a directed acyclic graph of tasks."""

    def __init__(self, index: TypeIndex, workdir: Path):
        self._tasks = {}
        self._types = index
        self._counter = 0
        self._workdir = workdir

    def _get_id(self):
        next_id = self._counter
        self._counter += 1
        return next_id

    # pylint: disable=redefined-builtin
    def create_task(self, type, id=None, **kwargs) -> Task:
        """Create a new task and add it to the pipeline."""
        cls = self._types[type]

        if id is None:
            id = self._get_id()
        elif id in self._tasks:
            raise Exception(f"A task with ID {id} is already defined")
        elif id >= self._counter:
            self._counter = id + 1

        if "source" in kwargs and kwargs["source"] is not None:
            kwargs["source"] = self.get_task(kwargs["source"])

        task = cls(id=id, workdir=self._workdir, **kwargs)
        self._tasks[id] = task
        return task

    def get_task(self, id: int) -> Task:
        """Retrieve a task in the pipeline."""
        return self._tasks[id]

    def remove_task(self, id: int) -> Task:
        """Remove a task from the pipeline."""
        task = self._tasks.pop(id)
        # disconnect task from sources
        return task

    def __getitem__(self, id) -> Task:
        return self.get_task(id)

    def __delitem__(self, id):
        self.remove_task(id)

    def __iter__(self):
        return iter(self._tasks.values())

    def __len__(self):
        return len(self._tasks)
