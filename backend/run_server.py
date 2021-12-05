import argparse
from pathlib import Path
from somedaex.http import Server
from somedaex.pipeline import Pipeline
from somedaex.task_types import task_types

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Port number to listen on")
parser.add_argument(
    "-d",
    "--workdir",
    help="Path to the working directory for the pipeline",
    type=Path,
    default=Path.cwd() / ".somedaex_workdir",
)
args = parser.parse_args()

pipeline = Pipeline(task_types, args.workdir)

server = Server(pipeline)
server.listen(args.port)
