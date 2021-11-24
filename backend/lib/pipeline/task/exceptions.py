class TaskNotComplete(Exception):
    def __init__(self, task):
        super().__init__(
            "The requested operation cannot be carried out because {}({}) is not yet complete.".format(
                task.type, task.id
            )
        )
