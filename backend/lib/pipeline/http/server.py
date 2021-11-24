import asyncio

from aiohttp import web
import aiohttp_cors
import rx.operators
from wrapt import decorator

from observableproxy import observe
from pipeline import Pipeline
from pipeline.index import NoSuchType
from pipeline.task import Task, Status
from .encoder import to_json
from .events import EventStream


def task_handler(method):
    async def wrapper(self, request):
        task_id = int(request.match_info["id"])
        try:
            task = self.pipeline[task_id]
        except KeyError:
            return web.Response(status=404)

        return await method(self, request, task)

    return wrapper


class Provocateur:
    def __init__(self, event_stream: EventStream, n: int):
        self.n = n
        self.watchers = {}
        self.event_stream = event_stream

    def watch(self, task: Task):
        watcher = (
            observe(task.status)
            .pipe(
                rx.operators.filter(lambda status: status == Status.READY),
                rx.operators.map(lambda _: task),
            )
            .subscribe(self.on_task_ready)
        )
        self.watchers[task.id] = watcher

    def unwatch(self, task):
        self.watchers[task.id].dispose()
        del self.watchers[task.id]

    def on_task_ready(self, task):
        print("on_task_ready", task)
        asyncio.create_task(self.get_rows(task))

    async def get_rows(self, task):
        print("get_rows", task)
        count = 0
        async for row in task.rows():
            print("get_rows", count, row)
            await self.event_stream.broadcast(
                {"event": "result", "task": task.id, "value": row}
            )
            count += 1
            if count >= self.n:
                return


class Server:
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.events = EventStream()
        self.provocateur = Provocateur(self.events, 5)

        self.app = web.Application()
        self.cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )

        self.define_endpoint(
            "/",
            {
                "GET": self.get_pipeline,
                "POST": self.add_task,
            },
        )

        self.define_endpoint(
            r"/{id:\d+}",
            {
                "GET": self.get_task,
                "POST": self.update_task,
                "DELETE": self.delete_task,
            },
        )

    def define_endpoint(self, path, handlers):
        endpoint = self.cors.add(self.app.router.add_resource(path))
        for method in handlers:
            self.cors.add(endpoint.add_route(method, handlers[method]))

    def listen(self, port):
        web.run_app(self.app, port=port)

    async def get_pipeline(self, request):
        if request.headers.get("accept") == "text/event-stream":
            await self.events.subscribe(request)

        else:
            tasks = [t.args() for t in self.pipeline]
            return web.json_response({"tasks": tasks}, dumps=to_json)

    async def add_task(self, request):
        body = await request.json()
        type = body.pop("type")

        print(f"Creating {type} task with {body}")

        try:
            task = self.pipeline.create_task(type, **body)
            await self.events.broadcast({"event": "created", "task": task.id})
            self.events.watch(task)
            self.provocateur.watch(task)

            headers = {"Location": f"/{task.id}"}
            return web.json_response(
                task.args(), status=201, headers=headers, dumps=to_json
            )

        except NoSuchType as err:
            return web.Response(status=400, text=str(err))

    @task_handler
    async def get_task(self, _, task):
        return web.json_response(task.args(), dumps=to_json)

    @task_handler
    async def update_task(self, request, task):
        body = await request.json()
        print(f"Updating task {task.id} with {body}")

        if "source" in body and body["source"] is not None:
            try:
                body["source"] = self.pipeline[body["source"]]
            except KeyError:
                msg = f"Task {body['source']} is not defined"
                return web.json_response(status=400, text=msg)

        # try:
        # task.config.update(lambda config: config | body)
        task.update(body)
        return web.json_response(task.args(), dumps=to_json)

        # except Exception as err:
        #     print(err)
        #     return web.Response(status=400, text=str(err))

    @task_handler
    async def delete_task(self, _, task):
        self.pipeline.remove_task(task.id)
        await self.events.broadcast({"event": "deleted", "task": task.id})
        self.events.unwatch(task)
        self.provocateur.unwatch(task)
        return web.Response(status=204)
