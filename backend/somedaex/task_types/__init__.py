"""The task_types package contains concrete task implementations and provides an
index that maps those implementations to their string identifiers used elsewhere
in the app.
"""

from ..pipeline import TypeIndex
from .casefold import CaseFold
from .loadfile import LoadFile

task_types = TypeIndex()
task_types.add(CaseFold)
task_types.add(LoadFile)
