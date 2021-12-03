# Data Processing Backend

The Somedaex backend exposes an HTTP interface that allows the Electron app to create and manipulate data processing pipelines in Python.


## Getting Started

The backend is built on [Python 3.9](https://docs.python.org/3/whatsnew/3.9.html) and uses [Poetry](https://python-poetry.org/) to manage its dependencies. To install those dependencies in an isolated virtual environment, run:

```
$ poetry install
```

You can then start a backend process that listens on port 8080 by running:

```
$ poetry run python scripts/run_server.py -p 8080
```


## Rebuilding the Task Index

The `__init__.py` file for the `task_types` package contains an automatically generated index of task types. You can refresh this index by running:

```
$ poetry run python scripts/build_index.py
```


## Code Quality

The backend is configured for linting with [Pylint](https://pylint.org/) and formatting with [Black](https://pypi.org/project/black/). If you are developing in Visual Studio Code, Pylint will detect errors as you type and Black will automatically be run each time a Python file is saved. However, you can also run these tools manually using the following commands:

```
$ poetry run pylint lib/*
$ poetry run black .
```


## Python Path

Because the backend does not follow the standard folder structure for Python projects, the `PYTHONPATH` environment variable must be set in order for `run_server.py`, `build_index.py`, and other scripts to locate the packages stored under `lib`. If you use [direnv](https://direnv.net/), this environment variable will be automatically set when you navigate into the backend folder. If not, you will need to manually set it by running:

```
$ source .envrc
```


## Security

The Somedaex backend is **NOT** intended to be exposed to an open network, much less the Internet. Each backend process is only intended to be used by the Electron instance that spawned it.
