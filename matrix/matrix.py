"""Definitions of the various classes."""

from itertools import starmap

from .utils import *


class Matrix:
    """
    The main matrix definition.

    The properties here are used to:
    - ensure the "public" attribute is unwritable.
    - make sure potential subclasses have a means of access to the "private" attribute."

    A matrix can be constructed in two ways:
    - Given two positive integers, it's initialized as a zero matrix of that dimension.
      e.g

      >>> print(Matrix(2, 2))
      —————————
      | 0 | 0 |
      —————————
      | 0 | 0 |
      —————————

    - Given a 2-D iterable of integers:
      - If all rows have the same length, initialized as if the array is row-major.
      - If row lengths don't match but `zfill is True`, zero-fill to the right to match.
    """

    __slots__ = ("__array", "__nrow", "__ncol", "__rows", "__columns")

    def __init__(self, rows_array=None, cols_zfill=None):
        """
        Two signatures:

        class Matrix(rows: int, cols: int)

        OR

        class Matrix(array: iterable, zfill: bool = False)
        """

        if isinstance(rows_array, int) and isinstance(cols_zfill, int):
            rows, cols = rows_array, cols_zfill

            if rows > 0 and cols > 0:
                self.__array = [[0] * cols for _ in range(rows)]
                self.__nrow, self.__ncol = rows, cols
            else:
                raise ValueError("Both dimensions must be positive integers.")
        elif hasattr(rows_array, "__iter__") and isinstance(cols_zfill, (type(None), bool)):
            minlen, maxlen, self.__nrow, array = check_iterable(rows_array)

            if maxlen == 0:
                raise ValueError("The inner iterables are empty.\n"
                                "\tBoth dimensions must be greater than zero.")

            if minlen == maxlen:
                self.__array = array
                self.__ncol = maxlen
            elif cols_zfill:
                self.__array = array
                self.resize(self.__nrow, maxlen)
            else:
                raise ValueError("'zfill' should be `True`"
                                " when the array has variable row lengths.")
        else:
            raise TypeError("Constructor arguments must either be two positive integers"
                            " OR a 2D iterable of integers and an optional boolean.")

        self.__rows = Rows(self)
        self.__columns = Columns(self)


    _array = property(lambda self: self.__array, doc="Gets underlying array of the matrix.")

    rows = property(lambda self: self.__rows, doc="Gets Rows() object of the matrix.")

    columns = property(lambda self: self.__columns, doc="Gets Colums() object of the matrix.")

    nrow = property(lambda self: self.__nrow, doc="Gets number of rows of the matrix.")

    ncol = property(lambda self: self.__ncol, doc="Gets number of columns of the matrix.")

    size = property(lambda self: (self.__nrow, self.__ncol),
                    doc="Gets dimension of the matrix.")


    def __repr__(self):
        return "{}({}, {})".format(type(self).__name__, self.__nrow, self.__ncol)

    def __str__(self):
        column_widths = [len(str(max(column))) for column in self.__columns]
        width_fmt = [f"^{width}" for width in column_widths]

        bar = '\u2015' * (sum(column_widths) + self.__ncol * 3  + 1)

        return (bar
            + ('\n' + bar).join('\n| ' + ' | '.join(starmap(format, zip(row, width_fmt))) + ' |'
                            for row in self.__array)
            + '\n' + bar)


    def __getitem__(self, sub):
        """
        Returns:
        - element at given position, if `sub` is a tuple of integers `(row, col)`.
          e.g `matrix[1, 2]`
          - Indices must be in range
          - Negative indices are not allowed.
        - a new Matrix instance, if `sub` is a tuple of slices.
          e.g `matrix[1:3, 3:4]`
          - the first slice selects rows.
          - the second slice selects columns.
          - slices out of range are "forgiven".
          - Negative indices or steps are not allowed.

        NOTE:
          - Both Row and Column are **indexed starting from `1`**.
          - A **slice includes `stop`**.
        """

        if isinstance(sub, tuple) and len(sub) == 2:

            if all(isinstance(x, int) for x in sub):
                row, col = sub
                if 0 < row <= self.__nrow and 0 < col <= self.__ncol:
                    return self.__array[row - 1][col - 1]
                else:
                    raise IndexError("Row and/or Column index is/are"
                                    " either out of range or negative.")

            elif all(isinstance(x, slice) for x in sub):
                if not all(map(valid_slice, sub)):
                    raise ValueError("start, stop or step of slice cannot be negative.")

                rows, cols = starmap(adjust_slice, zip(sub, self.size))
                return type(self)(row[cols] for row in self.__array[rows])

            else:
                raise TypeError(
                        "Matrixes only support subscription of elements or submatrices.")
        else:
            raise TypeError(
                "Subscript element must be a tuple of integers or slices\n"
                "\t(with or without parenthesis).") from None


class Rows:
    """
    A (pseudo-container) view over the rows of a matrix.
    Implements direct row read/write operations.
    """

    def __init__(self, matrix):
        self.__matrix = matrix

    def __iter__(self):
        return (row.copy() for row in self.__matrix._array)


class Columns:
    """A (pseudo-container) view over the colums of a matrix.
    Implements direct column read/write operations.
    """

    def __init__(self, matrix):
        self.__matrix = matrix

    def __iter__(self):
        return ([row[col] for row in self.__matrix._array] for col in range(self.__matrix.ncol))

