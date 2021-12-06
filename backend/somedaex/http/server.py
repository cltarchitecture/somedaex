import inspect

from aiohttp import web
import aiohttp_cors
import wrapt

from somedaex.pipeline import Pipeline
from somedaex.pipeline.index import NoSuchType
from somedaex.pipeline.task import Task
from .encoder import to_json
from .events import EventStream


ROUTE_PARAMS_ATTR = "_route_params"


def route_params(http_method: str, path: str):
    """Add routing information to a method."""

    def decorator(class_method):
        setattr(class_method, ROUTE_PARAMS_ATTR, (http_method, path))
        return class_method

    return decorator


@wrapt.decorator
async def task_handler(wrapped, instance, args, kwargs):
    """Provide the task object referenced by the request's id parameter as the last
    argument to the decorated method."""
    request = args[0]
    task_id = int(request.match_info["id"])
    try:
        kwargs["task"] = instance.pipeline[task_id]
    except KeyError:
        return web.Response(status=404)

    return await wrapped(*args, **kwargs)


class Server:
    """A server provides an HTTP interface to a pipeline."""

    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.events = EventStream(pipeline)
        # self.provocateur = Provocateur(self.events, 5)

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

        # Look for methods with route information and add them to the routing table
        http_resources = {}
        for name in dir(self):
            attr = getattr(self, name)
            if inspect.ismethod(attr) and hasattr(attr, ROUTE_PARAMS_ATTR):
                method, path = getattr(attr, ROUTE_PARAMS_ATTR)
                if path not in http_resources:
                    http_resources[path] = self.app.router.add_resource(path)
                self.cors.add(http_resources[path].add_route(method, attr))

    def listen(self, port):
        """Run the server."""
        web.run_app(self.app, port=port)

    @route_params("GET", "/")
    async def get_pipeline(self, request):
        """Handle GET requests for the pipeline."""
        if request.headers.get("accept") == "text/event-stream":
            await self.events.subscribe(request)

        else:
            tasks = [t.args() for t in self.pipeline]
            return web.json_response({"tasks": tasks}, dumps=to_json)

    @route_params("POST", "/")
    async def add_task(self, request):
        """Handle POST requests for the pipeline."""
        body = await request.json()
        task_type = body.pop("type")

        print(f"Creating {task_type} task with {body}")

        try:
            task = self.pipeline.create_task(task_type, **body)
            headers = {"Location": f"/{task.id}"}
            return web.json_response(
                task.args(), status=201, headers=headers, dumps=to_json
            )

        except NoSuchType as err:
            return web.Response(status=400, text=str(err))

    @task_handler
    @route_params("GET", r"/{id:\d+}")
    async def get_task(self, _, task):
        """Handle GET requests for a specific task by returning a JSON representation
        of that task.
        """
        return web.json_response(task.args(), dumps=to_json)

    @task_handler
    @route_params("POST", r"/{id:\d+}")
    async def update_task(self, request: web.Request, task: Task):
        """Handle POST requests for a specific task by applying the values in the
        request body to the task and returning a JSON representation of the task's new
        state.
        """
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
    @route_params("DELETE", r"/{id:\d+}")
    async def delete_task(self, _, task):
        """Handle DELETE requests for a specific task by deleting the task."""
        self.pipeline.remove_task(task.id)
        return web.Response(status=204)
