import asyncio
from typing import Any

from aiohttp.web import Request
from aiohttp_sse import sse_response
import rx
import rx.operators
from rx.core.notification import OnNext, OnError
from rx.scheduler.eventloop import AsyncIOScheduler

from observableproxy import observe
from pipeline.task import Task, MonadicTask
from .encoder import to_json


def to_task_event(task, event_name):
    def mapper(value):
        return {"event": event_name, "task": task.id, "value": value}

    return rx.operators.map(mapper)


def map_reset(task):
    def mapper(reason):
        return {"event": "reset", "task": task.id, "reason": reason}

    return rx.operators.map(mapper)


# https://blog.oakbits.com/rxpy-and-asyncio.html
async def to_async_generator(
    observable: rx.Observable,
    loop: asyncio.AbstractEventLoop = None,
):
    """Create an async generator that yields the values emitted by an observable."""
    queue = asyncio.Queue()

    if loop is None:
        loop = asyncio.get_event_loop()

    def on_next(notification):
        queue.put_nowait(notification)

    disposable = observable.pipe(rx.operators.materialize()).subscribe(
        on_next=on_next, scheduler=AsyncIOScheduler(loop=loop)
    )

    while True:
        notification = await queue.get()
        if isinstance(notification, OnNext):
            yield notification.value
            queue.task_done()
        elif isinstance(notification, OnError):
            disposable.dispose()
            raise Exception(notification.value)
        else:
            disposable.dispose()
            break


class EventStream:
    """An EventStream listens for notifications from tasks and broadcasts them
    as server-sent events."""

    def __init__(self):
        self.subscribers = set()
        self.watchers = {}

    async def subscribe(self, request: Request):
        async with sse_response(request) as response:
            queue = asyncio.Queue()
            self.subscribers.add(queue)
            try:
                while not response.task.done():
                    payload = await queue.get()
                    payload = to_json(payload)
                    await response.send(payload)
                    queue.task_done()
            finally:
                self.subscribers.remove(queue)

    async def broadcast(self, payload: Any):
        """Enqueue a message for broadcast."""
        for queue in self.subscribers:
            await queue.put(payload)

    async def broadcast_from(self, observable: rx.Observable):
        async for message in to_async_generator(observable):
            try:
                await self.broadcast(message)
            except Exception as err:
                print(err)

    def watch(self, task: Task):
        """Collect notifications from a task."""
        streams = [
            observe(task.status).pipe(
                rx.operators.distinct_until_changed(),
                to_task_event(task, "status"),
            ),
            task.reset.pipe(map_reset(task)),
            observe(task.config).pipe(
                rx.operators.distinct_until_changed(),
                to_task_event(task, "config"),
            ),
            observe(task.schema).pipe(
                rx.operators.distinct_until_changed(),
                to_task_event(task, "schema"),
            ),
        ]

        if isinstance(task, MonadicTask):
            streams.append(
                observe(task.column).pipe(
                    rx.operators.distinct_until_changed(),
                    to_task_event(task, "column"),
                ),
            )

        watcher = rx.merge(*streams)
        self.watchers[task.id] = watcher.subscribe(async_on_next(self.broadcast))

    def unwatch(self, task: Task):
        """Stop collecting notifications from a task."""
        self.watchers[task.id].dispose()
        del self.watchers[task.id]


def async_on_next(coro):
    def on_next(*args, **kwargs):
        asyncio.create_task(coro(*args, **kwargs))

    return on_next
