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

from inspect import signature
from typing import overload, Generic, Callable, Any, List, TypeVar, Union

from .guards import GuardResult

T = TypeVar('T')
U = TypeVar('U')
S = TypeVar('S')


class Result(Generic[T]):
    def __init__(self, is_ok: bool, value: T = None, error: str | Exception | T = None):
        self.value = value
        self.error = error
        self.is_ok = is_ok
        self.is_err = not is_ok

    def __bool__(self):
        """ Allows the Result to be used in a boolean expression. """
        return self.is_ok

    def __iter__(self):
        """ Allows the Result to be used in a for loop. """
        if self.is_ok:
            value = self.value

            # if value is iterable, return each item
            if hasattr(value, '__iter__'):
                for item in value:
                    yield item

            yield value

        raise StopIteration

    def __next__(self):
        """ Allows the Result to be used in a for loop. """
        if self.is_ok:
            value = self.value

            # if value is iterable, return each item
            if hasattr(value, '__iter__'):
                for item in value:
                    yield item

            yield value

        raise StopIteration

    def __repr__(self):
        if self.is_ok:
            return f'Result.ok({self.value})'
        return f'Result.fail({self.error})'

    def unwrap(self) -> T:
        """
        Returns the value of the Result. If the Result is a failure, the error will be
        raised.

        :return: The value.
        """

        if self.is_ok:
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

        if self.is_ok:
            return self.value
        return default(self.error)

    def err(self) -> str | Exception:
        """
        Returns the error of the Result. If the Result is a success, the error will be
        raised.

        :return: The error.
        """

        if self.is_err:
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

        if self.is_err:
            raise ValueError(self.error)

        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows the Result to be used in a with statement.
        """
        pass

    @overload
    def bind(self, f: Callable[[], 'Result[U] | U']) -> 'Result[U]':
        ...

    @overload
    def bind(self, f: Callable[[T], 'Result[U] | U']) -> 'Result[U]':
        ...

    @overload
    def bind(self, f: Callable[[T, str | Exception], 'Result[U] | U']) -> 'Result[U]':
        ...

    def bind(self, f: Callable[..., 'Result[U] | U']) -> 'Result[U]':
        """
        Binds the Result to a function when the Result is a success. If the Result is a
        failure, the Result will be returned.

        -------
        Example
        -------

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

        Arguments
        ---------
        f : Callable[..., 'Result[U] | U']
            The function to be called if the Result is a success.

        Returns
        -------
        Result[U]
            The Result of the function call.


        """

        parameters = len(signature(f).parameters)

        other: Result[U] | U = None

        if parameters == 2:
            other = f(self.value, self.error)
        elif not self.is_err:
            if parameters == 0:
                other = f()
            elif parameters == 1:
                other = f(self.value)
        else:
            return self

        if not isinstance(other, Result):
            other = Result.ok(other)

        return other

    def if_err(self, f: Callable[..., 'Result[U] | U']) -> 'Result[U]':
        """
        Binds the Result to a function if the Result is a failure. Util for chaining
        Result-returning functions.

        -------
        Example
        -------

            >>> def divide(x: int, y: int) -> Result[int]:
            ...     if y == 0:
            ...         return Result.fail("Cannot divide by zero.")
            ...     else:
            ...         return Result.ok(int(x / y))

            >>> divide(1, 0).if_err(lambda: -1)
            ok(-1)

        Arguments
        ---------
        f : Callable[..., 'Result[U] | U']
            The function to be called if the Result is a failure.

        Returns
        -------
        Result[U]
            The Result of the function call.
        """
        if self.is_ok:
            return self

        parameters = len(signature(f).parameters)

        if parameters > 1:
            raise ValueError('The function f() must have 0 or 1 parameters.')

        other = f(self.error) if parameters == 1 else f()

        if not isinstance(other, Result):
            other = Result.ok(other)

        return other

    def bind_if(self, condition: Union[Callable[..., bool], bool], f: Callable[..., 'Result[U] | U']) -> 'Result[U]':
        """
        Binds the Result if a condition is met. Util for chaining Result-returning functions.

        -------
        Example
        -------

            >>> def divide(x: int, y: int) -> Result[int]:
            ...     if y == 0:
            ...         return Result.fail("Cannot divide by zero.")
            ...     else:
            ...         return Result.ok(int(x / y))
            >>> def multiply(x: int, y: int) -> Result[int]:
            ...     return Result.ok(int(x * y))

            >>> divide(1, 0).bind_if(lambda x: x > 0, lambda x: multiply(x, 2))
            fail('Cannot divide by zero.')

            >>> divide(1, 1).bind_if(lambda x: x > 0, lambda x: multiply(x, 2))
            ok(2)

            >>> y = random.randint(0, 1)
            >>> divide(1, y).bind_if(y != 0, lambda x: multiply(x, 2))
            ok(2)

        Arguments
        -------
        condition : Union[Callable[..., bool], bool]
            The condition to be met.
        f : Callable[..., 'Result[U] | U']
            The function to be called if the Result is a failure.

        Returns
        -------
        Result[U]
            The Result of the function call.
        """
        if self.is_err:
            return self

        if condition(self.value) if callable(condition) else condition:
            return self.bind(f)

        return self

    @classmethod
    def ok(cls, value: T = None) -> 'Result[T]':
        """
        Creates a successful Result.

        Example:

            >>> Result.ok(1)
            Result.ok(1)

        :param value: The value.

        :return: A Result instance.
        """
        return cls(True, value, None)

    @classmethod
    def fail(cls, error: str | Exception) -> 'Result[T]':
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

    @classmethod
    def with_bool(cls, condition: bool, value: T) -> 'Result[T]':
        """
        Creates a Result from a boolean condition.

        :param condition: The condition.
        :param value: The value.

        :return: A Result instance.
        """
        if condition:
            return cls.ok(value)
        return cls.fail(value)

    @classmethod
    def combine(cls, results: List['Result[Any]']) -> 'Result[tuple[Any, ...]]':
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
            if result.is_err:
                return cls.fail(result.err())
            values.append(result.unwrap())
        return cls.ok(tuple(values))

    @classmethod
    def from_guard(cls, result: GuardResult):
        """
        A helper for chain guard results.

        :param result: The guard result.

        :return: A Result instance.
        """
        if result:
            return cls.ok()
        return cls.fail(result.get_message())

    @classmethod
    def from_exception(cls, exception: Exception):
        """
        Converts an Exception to a Result.

        :param exception: The error.

        :return: A Result instance.
        """
        return cls.fail(exception.args[0])


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
