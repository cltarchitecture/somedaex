"""The casefold module provides a task implementation that converts text to lowercase.
"""

import pyarrow
from pipeline.task import OneToOneRowwiseTask


class CaseFold(OneToOneRowwiseTask):
    """A CaseFold task reads normalizes text to lowercase.

    It uses the `casefold` method, which implements the algorithm described in
    section 3.13 of the Unicode standard. This algorithm is more thorough than
    a traditional lowercasing function, handling situations when there is not
    a one-to-one mapping between characters in folded versus unfolded text.

    - https://docs.python.org/3/library/stdtypes.html#str.casefold
    - https://www.w3.org/TR/charmod-norm/#definitionCaseFolding
    """

    def execute(self, *text):
        return tuple(t.as_py().casefold() for t in text)

    def get_schema(self):
        column_names = self.column.value
        if not isinstance(self.column.value, list):
            column_names = [column_names]

        return pyarrow.schema(
            {name + "_lower": pyarrow.string() for name in column_names}
        )
