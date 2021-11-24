"""The encoder module provides a custom JSON encoder capable of handling types
commonly used in task pipelines."""

import base64
from functools import singledispatchmethod
import io
import json

import pandas
import pyarrow

from observableproxy import ObservableProxy
from pipeline.task import Task, Status


class JSONEncoder(json.JSONEncoder):
    """Converts instances of commonly used classes to a format that is palatable
    to the default JSON encoder."""

    @singledispatchmethod
    def default(self, o):
        return o

    @default.register
    @staticmethod
    def pyarrow_scalar(scalar: pyarrow.Scalar):
        """Convert a PyArrow scalar to a regular Python value."""
        converted = scalar.as_py()
        if isinstance(converted, pandas.Timestamp):
            converted = converted.isoformat()
        return converted

    @default.register
    @staticmethod
    def pyarrow_array(array: pyarrow.Array):
        """Convert a PyArrow array to a regular Python list."""
        return array.to_pylist()

    @default.register
    @staticmethod
    def pyarrow_schema(value: pyarrow.Schema):
        """Convert a PyArrow schema to a Base64-encoded string."""
        buffer = io.BytesIO()
        with pyarrow.ipc.new_stream(buffer, value) as writer:
            writer.write(value.empty_table())
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("ascii")

    @default.register
    @staticmethod
    def task(task: Task):
        """Return the ID of a task."""
        return task.id

    @default.register
    @staticmethod
    def status(status: Status):
        """Return the string representation of a task status."""
        return str(status)

    @default.register
    @staticmethod
    def observable_proxy(value: ObservableProxy):
        """Return the wrapped value of an ObservableProxy."""
        return value.__wrapped__


def to_json(value, **args):
    """Serialize the given value as a JSON-encoded string."""
    return json.dumps(value, cls=JSONEncoder, **args)
