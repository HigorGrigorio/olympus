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
    >>> divide(1, 0).is_left
    True
    >>> divide(1, 0).is_right
    False
"""

from typing import Generic, TypeVar, Callable, Any

L = TypeVar('L')
R = TypeVar('R')
S = TypeVar('S')


class Either(Generic[L, R]):
    """
    """

    def __init__(self, value: L | R, is_left: bool):
        self.is_left = is_left
        self.is_right = not is_left
        self.value = value

    def __repr__(self):
        return f"{'Left' if self.is_left else 'Right'}({self.value})"

    def __eq__(self, other):
        """ Two Either are equal if they are both Left or Right and have the same value. """
        return self.is_left == other.is_left and self.value == other.value

    def __bool__(self):
        """ An Either is True if it is Right. """
        return self.is_right

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
        if self.is_left:
            return self

        if other.is_left:
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
        return self if self.is_left else Either[R, S].right(f(self.value))

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
        return self if self.is_left else f(self.value)

    def plain(self):
        """
        Gets the right value. Raises an exception if the value is left.
        """
        return self.value


def left(value: L) -> Either[L, Any]:
    """
    Creates an Either with a left value.
    """
    return Either.left(value)


def right(value: R) -> Either[Any, R]:
    """
    Creates an Either with a right value.
    """
    return Either.right(value)


__all__ = ['Either', 'left', 'right']
