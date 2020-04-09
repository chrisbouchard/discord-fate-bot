from abc import ABCMeta, abstractmethod
from itertools import zip_longest
from typing import List

def join_as_columns(values):
    columns = tuple(str(value).splitlines() for value in values)
    column_widths = tuple(max(len(line) for line in column) for column in columns)

    return '\n'.join(
        ''.join(line.ljust(column_widths[i]) for (i, line) in enumerate(row))
        for row in zip_longest(*columns, fillvalue='')
    )


class ValidationError(Exception):
    """Exception indicating that an object's state is invalid."""

    complaints: List[str]

    def __init__(self, message, complaints):
        super().__init__(message)
        self.complaints = complaints

