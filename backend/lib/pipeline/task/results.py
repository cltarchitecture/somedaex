import pyarrow


class ResultsBuffer:
    """Stores results from a task until they can be written to a file."""

    def __init__(self, schema: pyarrow.Schema):
        self._schema = schema
        self._columns = [[] for _ in schema]

    def append(self, *values):
        for column, value in zip(self._columns, values):
            column.append(value)

    def to_batch(self) -> pyarrow.RecordBatch:
        return pyarrow.record_batch(self._columns, schema=self._schema)

    def clear(self):
        self._columns = [[] for _ in self._schema]

    def flush(self) -> pyarrow.RecordBatch:
        batch = self.to_batch()
        self.clear()
        return batch

    def __len__(self):
        return len(self._columns[0])

    def __getitem__(self, index):
        return tuple(column[index] for column in self._columns)


class Results:
    pass
