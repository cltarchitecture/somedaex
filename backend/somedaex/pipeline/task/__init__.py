"""The task package provides base classes for defining tasks."""

from .monadic import MonadicTask
from .niladic import NiladicTask
from .rowwise import OneToOneRowwiseTask, RowwiseTask
from .status import Status
from .task import Task
