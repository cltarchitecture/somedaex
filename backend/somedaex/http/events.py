import asyncio

from aiohttp.web import Request
from aiohttp_sse import sse_response
from somedaex.pipeline.pipeline import Pipeline

from ..pipeline import Pipeline
from ..pipeline.events import Event
from .encoder import to_json


def async_on_next(coro):
    """Wrap an async function so that it can be used to subscribe to an observable."""

    def on_next(*args, **kwargs):
        asyncio.create_task(coro(*args, **kwargs))

    return on_next


def _event_json(event: Event):
    return to_json(
        {
            "event": event.event,
            "task": event.task.id,
            "value": event.value,
        }
    )


class EventStream:
    """An EventStream listens for events from a pipeline and broadcasts them
    as server-sent events."""

    def __init__(self, pipeline: Pipeline):
        self.subscribers = set()
        pipeline.events.subscribe(async_on_next(self.broadcast))

    async def subscribe(self, request: Request):
        """Register an SSE request."""
        async with sse_response(request) as response:
            queue = asyncio.Queue()
            self.subscribers.add(queue)
            try:
                while not response.task.done():
                    event = await queue.get()
                    payload = _event_json(event)
                    await response.send(payload)
                    queue.task_done()
            finally:
                self.subscribers.remove(queue)

    async def broadcast(self, event: Event):
        """Enqueue a message for broadcast."""
        for queue in self.subscribers:
            await queue.put(event)
