# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The Either class represents a value of one of two possible types (a disjoint
union). An instance of Either is an instance of Left or Right. A common use of
Either is as an alternative to Option for dealing with possible missing values.
In this usage, None is replaced with a Left which can contain useful
information.

Example:

    >>> def divide(x: int, y: int) -> Either[Exception, int]:
    ...     try:
    ...         return right(int(x / y))
    ...     except Exception as e:
    ...         return left(e)
    >>> divide(1, 0)
    Left(ZeroDivisionError('division by zero'))
    >>> divide(1, 1)
    Right(1.0)
    >>> divide(1, 0).isLeft
    True
    >>> divide(1, 0).isRight
    False
"""

from typing import Generic, TypeVar, Callable

L = TypeVar('L')
R = TypeVar('R')
S = TypeVar('S')


class Either(Generic[L, R]):
    """
    """

    def __init__(self, value: L | R, is_left: bool):
        self.isLeft = is_left
        self.isRight = not is_left
        self.value = value

    def __repr__(self):
        return f"{'Left' if self.isLeft else 'Right'}({self.value})"

    def __eq__(self, other):
        """ Two Either are equal if they are both Left or Right and have the same value. """
        return self.isLeft == other.isLeft and self.value == other.value

    def __bool__(self):
        """ An Either is True if it is Right. """
        return self.isRight

    @staticmethod
    def left(value: L = None) -> 'Either[L, R]':
        """
        Creates an Either with a left value.
        """
        return Either(value, is_left=True)

    @staticmethod
    def right(value: R | Exception) -> 'Either[L, R]':
        """
        Creates an Either with a right value.
        """
        return Either(value, is_left=False)

    def amap(self: 'Either[L, Callable[[S], R]]', other: 'Either[L, S]'):
        """
        Applies a function in an Either to another Either.

        Example:

            >>> either = right(lambda x: x + 1)
            >>> either.amap(right(1))
            Right(2)

            >>> either = left(lambda x: x + 1)
            >>> either.amap(right(1))
            Left(<function <lambda> at 0x7f8d3b7d3b80>)
        """
        if self.isLeft:
            return self

        if other.isLeft:
            return other

        return Either.right(self.value(other.value))

    def map(self, f: Callable[[R], S]) -> 'Either[L, S]':
        """
        Maps a function over the right value.

        Example:

            >>> either = right(1)
            >>> either.map(lambda x: x + 1)
            Right(2)

            >>> either = left(1)
            >>> either.map(lambda x: x + 1)
            Left(1)
        """
        return self if self.isLeft else Either[R, S].right(f(self.value))

    def bind(self, f: Callable[[R], 'Either[L, S]']) -> 'Either[L, S]':
        """
        Binds a function over the right value.

        Example:

            >>> either = right(1)
            >>> either.bind(lambda x: right(x + 1))
            Right(2)

            >>> either = left(1)
            >>> either.bind(lambda x: right(x + 1))
            Left(1)
        """
        return self if self.isLeft else f(self.value)

    def plain(self):
        """
        Gets the right value. Raises an exception if the value is left.
        """
        return self.value


def left(value: L) -> Either[L, R]:
    """
    Creates an Either with a left value.
    """
    return Either.left(value)


def right(value: S) -> Either[L, S]:
    """
    Creates an Either with a right value.
    """
    return Either.right(value)


__all__ = ['Either', 'left', 'right']
