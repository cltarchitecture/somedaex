"""The pipeline module defines the Pipeline class."""

# Standard library imports
import asyncio
from pathlib import Path
from typing import Mapping

import rx.operators

# Local imports
from .events import EventStream
from .index import TypeIndex
from .task import Task, Status


class Pipeline(Mapping):
    """A pipeline is a directed acyclic graph of tasks."""

    def __init__(self, index: TypeIndex, workdir: Path):
        self._tasks = {}
        self._types = index
        self._counter = 0
        self._workdir = workdir
        self._workdir.mkdir(parents=True, exist_ok=True)

        self.events = EventStream()
        self._min_sample_rows = 5

        self.events.pipe(
            rx.operators.filter(
                lambda e: e.event == "status" and e.value == Status.READY
            ),
            rx.operators.map(lambda e: e.task),
        ).subscribe(self._on_task_ready)

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

        self.events.broadcast("created", task)
        self.events.watch(task)

        return task

    def get_task(self, task_id: int) -> Task:
        """Retrieve a task in the pipeline."""
        return self._tasks[task_id]

    def remove_task(self, task_id: int) -> Task:
        """Remove a task from the pipeline."""
        task = self._tasks.pop(task_id)
        # disconnect task from sources

        self.events.unwatch(task)
        self.events.broadcast("deleted", task)

        return task

    def __getitem__(self, task_id: int) -> Task:
        return self.get_task(task_id)

    def __delitem__(self, task_id: int):
        self.remove_task(task_id)

    def __iter__(self):
        return iter(self._tasks.values())

    def __len__(self):
        return len(self._tasks)

    def _on_task_ready(self, task: Task):
        asyncio.create_task(self._get_sample_rows(task))

    async def _get_sample_rows(self, task: Task):
        count = 0
        async for row in task.rows():
            self.events.broadcast("result", task, row)
            count += 1
            if count >= self._min_sample_rows:
                return
