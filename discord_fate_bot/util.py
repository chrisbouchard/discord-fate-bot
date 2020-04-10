from abc import ABCMeta, abstractmethod
from itertools import zip_longest
from typing import List, Mapping

def join_as_columns(values):
    columns = tuple(str(value).splitlines() for value in values)
    column_widths = tuple(max(len(line) for line in column) for column in columns)

    return '\n'.join(
        ''.join(line.ljust(column_widths[i]) for (i, line) in enumerate(row))
        for row in zip_longest(*columns, fillvalue='')
    )

def pluralize(n: int, singular: str, plural: str) -> str:
    """Choose between the singular and plural forms of a word depending on the
    given count.
    """
    if n == 1:
        return singular
    else:
        return plural


class ValidationError(Exception):
    """Exception indicating that an object's state is invalid."""

    complaints: List[str]

    def __init__(self, message, complaints):
        super().__init__(message)
        self.complaints = complaints

