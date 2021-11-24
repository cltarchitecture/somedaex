from enum import auto, Enum


class Status(Enum):
    """A status describes the position of a task within its lifecycle."""

    INVALID = auto()
    """The task does not yet have a valid configuration and cannot process rows."""

    READY = auto()
    """The task is fully configured and ready to process rows, but none have been processed yet."""

    WORKING = auto()
    """The task is currently processing rows."""

    PAUSED = auto()
    """The task is not currently processing rows, but there are still input rows that have yet to be processed."""

    FINISHED = auto()
    """All input rows have been processed."""

    COMPLETE = auto()
    """All input rows have been processed and all results are available in the form of a memory-mapped table."""

    FAILED = auto()
    """The task was not able to process all of its input rows due to an unexpected error."""

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_string(cls, string):
        """Retrieve the status object that corresponds to the given string."""
        return getattr(cls, string.upper())
