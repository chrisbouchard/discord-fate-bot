from itertools import zip_longest

def join_as_columns(values):
    columns = tuple(str(value).splitlines() for value in values)
    column_widths = tuple(max(len(line) for line in column) for column in columns)

    return '\n'.join(
        ''.join(line.ljust(column_widths[i]) for (i, line) in enumerate(row))
        for row in zip_longest(*columns, fillvalue='')
    )

