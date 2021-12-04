import argparse
from somedaex.http import Server
from somedaex.pipeline import Pipeline
from somedaex.task_types import task_types


parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="Port number to listen on")
args = parser.parse_args()

pipeline = Pipeline(task_types)

server = Server(pipeline)
server.listen(args.port)
