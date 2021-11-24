from .task import Task


class NiladicTask(Task):
    """A niladic task reads data from an external source (such as a file) and
    makes that data available to other tasks. Because it does not rely on
    another task for input, its internal mechanisms are significantly different
    from most other classes of task.
    """
