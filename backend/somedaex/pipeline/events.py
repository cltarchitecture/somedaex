"""The events module defines the classes for observing the state of a pipeline."""

from typing import Any, NamedTuple
import rx
import rx.operators
from rx.subject import Subject
from ..observableproxy import observe
from ..pipeline.task import Task, MonadicTask


class Event(NamedTuple):
    """An Event represents a change in the state of a task."""

    event: str
    task: Task
    value: Any


class EventStream(Subject):
    """An EventStream listens for changes to tasks and rebroadcasts them as Event objects."""

    def __init__(self):
        super().__init__()
        self.tasks = {}

    def broadcast(self, event_name: str, task: Task, value: Any = None):
        """Broadcast an event."""
        event = Event(event_name, task, value)
        self.on_next(event)

    def watch(self, task: Task):
        """Watch for changes to the state of a task."""
        streams = [
            observe(task.status).pipe(
                rx.operators.distinct_until_changed(),
                rx.operators.map(lambda value: Event("status", task, value)),
            ),
            task.reset.pipe(
                rx.operators.map(lambda reason: Event("reset", task, reason))
            ),
            observe(task.config).pipe(
                rx.operators.distinct_until_changed(),
                rx.operators.map(lambda value: Event("config", task, value)),
            ),
            observe(task.schema).pipe(
                rx.operators.distinct_until_changed(),
                rx.operators.map(lambda value: Event("schema", task, value)),
            ),
        ]

        if isinstance(task, MonadicTask):
            streams.append(
                observe(task.column).pipe(
                    rx.operators.distinct_until_changed(),
                    rx.operators.map(lambda value: Event("column", task, value)),
                ),
            )

        self.tasks[task.id] = rx.merge(*streams).subscribe(self)

    def unwatch(self, task: Task):
        """Stop watching a task."""
        self.tasks[task.id].dispose()
        del self.tasks[task.id]
