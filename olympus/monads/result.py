# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The monad Result represents a value that may be a success or a failure. A value
is a success, in which case the Result is a success value. Otherwise, the Result
is a failure value.

When the Result is a success value, it contains a value of type T. If it is a
failure value, it can be a str or an Exception.

Example:

    >>> def divide(x: int, y: int) -> Result[int]:
    ...     if y == 0:
    ...         return Result.fail("Cannot divide by zero.")
    ...     else:
    ...         return Result.ok(int(x / y))
    >>> divide(1, 0)
    fail('Cannot divide by zero.')

    >>> divide(1, 1)
    ok(1)
"""

from typing import overload, Generic, Callable, Any, List, TypeVar

from .guards import GuardResult

T = TypeVar('T')
U = TypeVar('U')
S = TypeVar('S')


class Result(Generic[T]):
    def __init__(self, isSuccess: bool, value: T = None, error: str | Exception | T = None):
        self.value = value
        self.error = error
        self.isSuccess = isSuccess
        self.isFailure = not isSuccess

    def __bool__(self):
        """ Allows the Result to be used in a boolean expression. """
        return self.isSuccess

    def __repr__(self):
        if self.isSuccess:
            return f'Result.ok({self.value})'
        return f'Result.fail({self.error})'

    def unwrap(self) -> T:
        """
        Returns the value of the Result. If the Result is a failure, the error will be
        raised.

        :return: The value.
        """

        if self.isSuccess:
            return self.value
        print(self.error)
        raise RuntimeError('Cannot get value of a failed result')

    def unwrap_or_else(self, default: Callable[[Any], S]) -> S:
        """
        Returns the value of the Result. If the Result is a failure, the default value
        will be returned.

        :param default: The default value.

        :return: The value.
        """

        if self.isSuccess:
            return self.value
        return default(self.error)

    def err(self) -> str | Exception:
        """
        Returns the error of the Result. If the Result is a success, the error will be
        raised.

        :return: The error.
        """

        if self.isFailure:
            return self.error

        raise RuntimeError('Cannot get error of a successful result')

    def __enter__(self) -> T:
        """
        Allows the Result to be used in a with statement. If the Result is a failure,
        the error will be raised. Otherwise, the value will be returned.

        Example:

            >>> def divide(x: int, y: int) -> Result[int]:
            ...     if y == 0:
            ...         return Result.fail("Cannot divide by zero.")
            ...     else:
            ...         return Result.ok(int(x / y))

            >>> with divide(1, 0) as result:
            ...     print(result)
            Cannot divide by zero.

        :return: The value.
        """

        if self.isFailure:
            raise ValueError(self.error)

        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows the Result to be used in a with statement.
        """
        pass

    def bind(self, f: Callable[[T | None], 'Result[U]|U']) -> 'Result[U]':
        """
        Binds the Result to a function that returns a Result. Util for chaining
        Result-returning functions.

        Example:

            >>> def divide(x: int, y: int) -> Result[int]:
            ...     if y == 0:
            ...         return Result.fail("Cannot divide by zero.")
            ...     else:
            ...         return Result.ok(int(x / y))
            >>> def multiply(x: int, y: int) -> Result[int]:
            ...     return Result.ok(int(x * y))

            >>> divide(1, 0).bind(lambda x: multiply(x, 2))
            fail('Cannot divide by zero.')

            >>> divide(1, 1).bind(lambda x: multiply())
        :param f:
        :return:
        """
        if self.isFailure:
            return self

        other = f(self.value)

        if not isinstance(other, Result):
            other = Result.ok(other)

        return other

    @staticmethod
    def ok(value: T = None) -> 'Result[T]':
        """
        Creates a successful Result.

        Example:

            >>> Result.ok(1)
            Result.ok(1)

        :param value: The value.

        :return: A Result instance.
        """
        return Result(True, value, None)

    @staticmethod
    def fail(error: str | Exception) -> 'Result[T]':
        """
        Creates a failed Result.

            >>> Result.fail('Fatal error!')
            Result.fail('Fatal error!')

            >>> Result.fail(Exception('Fatal Error!'))
            Result.fail('Fatal error!')

        :param error: The error.

        :return: A Result instance with error value.
        """
        return Result(False, None, error)

    @staticmethod
    def combine(results: List['Result[Any]']) -> 'Result[tuple[Any, ...]]':
        """
        Combines a list of Results into a single Result containing a tuple of values. If any
        of the Results are failures, the first failure will be returned.

        Exemple:

            >>> Result.combine([W(1), W(2)])
            Result.ok()

            >>> Result.combine([W(1), W(Exception('Fatal error!')), W(2)])
            Result.fail('Fatal error!')

        :param results: The result list.

        :return: Return an empty ok() or a fail() instance.
        """

        values = []

        for result in results:
            if result.isFailure:
                return Result.fail(result.err())
            values.append(result.unwrap())
        return Result.ok(tuple(values))

    @staticmethod
    def from_guard(result: GuardResult):
        """
        A helper for chain guard results.

        :param result: The guard result.

        :return: A Result instance.
        """
        if result:
            return Result.ok()
        return Result.fail(result.get_message())

    @staticmethod
    def from_exception(exception: Exception):
        """
        Converts an Exception to a Result.

        :param exception: The error.

        :return: A Result instance.
        """
        return Result.fail(exception.args[0])


@overload
def W(value: T, /) -> 'Result[T]':
    """
    This is a type hint for the W function. It is used to indicate that the function
    can be used as a constructor for a Result.

    :param value: The value to construct a result.

    :return: A Result instance.
    """
    ...


@overload
def W(error: Exception | GuardResult, /) -> 'Result[T]':
    """
    This is a type hint for the W function. It is used to indicate that the function.

    :param error: The error value.

    :return: A Result error.
    """
    ...


def W(value: T | Exception | GuardResult = None, /) -> 'Result[T]':
    """
    A helper function for creating a Result. If the value is an Exception or GuardResult,
    it will be converted to a failure Result. Otherwise, a successful Result will be created.

    :param value: The value or error.

    :return: The Result value.
    """
    if isinstance(value, Exception):
        return Result.fail(value.args[0])
    if isinstance(value, GuardResult):
        return Result.from_guard(value)
    if isinstance(value, Result):
        return value
    return Result.ok(value)


def fail(error: str | Exception) -> 'Result[T]':
    """
    Creates a failed Result.

        >>> fail('Fatal error!')
        Result.fail('Fatal error!')

        >>> fail(Exception('Fatal Error!'))
        Result.fail('Fatal error!')

    :param error: The error.

    :return: A Result instance with error value.
    """
    return Result.fail(error)


def ok(value: T = None) -> 'Result[T]':
    """
    Creates a successful Result.

    Example:

        >>> ok(1)
        Result.ok(1)

    :param value: The value.

    :return: A Result instance.
    """
    return Result.ok(value)
