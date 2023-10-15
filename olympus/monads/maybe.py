# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The monad Maybe represents a value that may or may not be present. A value
maybe present, in which case the Maybe is a just value. Otherwise, the Maybe
is a nothing value.

Just: Represents a value that is present.
Nothing: Represents a value that is not present.

This monad is useful for representing optional values. It allows you to chain
operations that might fail, stopping the calculation as soon as an operation
fails (returns Nothing).

Example:

    >>> def divide(x: int, y: int) -> Maybe[int]:
    ...     if y == 0:
    ...         return Maybe()
    ...     else:
    ...         return Maybe.just(int(x / y))
    >>> divide(1, 0)
    none()

    >>> divide(1, 1)
    just(1)
"""

from typing import overload, Generic, TypeVar, Callable, Any, cast

T = TypeVar('T')
U = TypeVar('U')
S = TypeVar('S')


class MissingValueError(ValueError):
    """
    Raised to indicate a potentially missing value was missing.
    """

    def __init__(self):
        super().__init__("Cannot get value from a Maybe with no value.")


class Maybe(Generic[T]):
    """
    Represents a value that may or may not be present. This is useful for
    representing optional values.
    """

    sentinel = None

    @overload
    def __init__(self, /) -> None:
        ...

    @overload
    def __init__(self, value: T, /) -> None:
        ...

    def __init__(self, /, *args: T) -> None:
        if len(args) == 0:
            self.value = Maybe.sentinel
        else:
            self.value = args[0]

    def __repr__(self, /) -> str:
        """
        Returns a string representation of the Maybe.
        """

        cls = type(self)

        if self.value is cls.sentinel:
            return f"Maybe()"
        else:
            return f"Maybe.just({self.value!r})"

    def __eq__(self, other):
        """ Two Maybe are equal if they are both just or nothing and have the same value. """
        return self.is_just() == other.is_just() and self.value == other.value

    @staticmethod
    def just(value: T, /) -> 'Maybe[T]':
        """
        Creates a Maybe with a value.
        """
        return Maybe(value)

    @staticmethod
    def nothing() -> 'Maybe[Any]':
        """
        Creates a Maybe with no value. This is useful for representing
        optional values.
        """
        return Maybe()

    def is_just(self) -> bool:
        """
        Returns True if the Maybe is a just value. Otherwise, returns False.
        """
        cls = type(self)
        return self.value is not cls.sentinel

    def is_nothing(self) -> bool:
        """
        Returns True if the Maybe is a nothing value. Otherwise, returns False.
        """
        cls = type(self)
        return self.value is cls.sentinel

    def get(self) -> T:
        """
        Gets the value if is a just value. Otherwise, raises a exception.

        Example:

            >>> Maybe.just(1).get()
            1

            >>> Maybe().get()
            Traceback (most recent call last):
            ...
        """

        cls = type(self)

        if self.value is cls.sentinel:
            raise MissingValueError()

        return cast(T, self.value)

    def map(self: 'Maybe[T]', f: Callable[[T], U], /) -> 'Maybe[U]':
        """
        Helper function for mapping a function over a Maybe.f:

        Example:

            >>> Maybe.just(1).map(lambda x: x + 1)
            Maybe.just(2)

            >>> Maybe().map(lambda x: x + 1)
            Maybe()
        """
        cls = type(self)
        if self.value is cls.sentinel:
            return cls()
        else:
            return cls(f(cast(T, self.value)))

    def amap(self: 'Maybe[Callable[[T], S]]', other: 'Maybe[T]', /) -> 'Maybe[S]':
        """
        Applies a Maybe function to another Maybe. If either Maybe has no
        value, then the result is a Maybe with no value.

        Example:

            >>> Maybe.just(lambda x: x + 1).amap(Maybe[int].just(1))
            Maybe.just(2)

            >>> Maybe.just(lambda x: x + 1).amap(Maybe())
            Maybe()

            >>> Maybe().amap(Maybe.just(1))
            Maybe()

            >>> Maybe().amap(Maybe())
            Maybe()
        """
        if self.value is type(self).sentinel:
            return type(self)()
        elif other.value is type(other).sentinel:
            return type(other)()
        else:
            return type(self)(self.value(cast(T, other.value)))

    def flatmap(self: 'Maybe[T]', f: Callable[[T], 'Maybe[U]'], /) -> 'Maybe[U]':
        """
        Helper function for mapping a function over a Maybe. The function
        should return a Maybe.

        Example:

            >>> Maybe.just(1).flatmap(lambda x: Maybe.just(x + 1))
            Maybe.just(2)

            >>> Maybe().flatmap(lambda x: Maybe.just(x + 1))
            Maybe()

        :param f: The function to map.

        :return: Returns a Maybe.
        """
        cls = type(self)

        if self.value is cls.sentinel:
            return cls()
        else:
            maybe2 = f(cast(T, self.value))
            if maybe2.value is cls.sentinel:
                return cls()
            else:
                return cls(cast(U, maybe2.value))

    def join(self: "Maybe['Maybe[T]']", /) -> 'Maybe[T]':
        """
        Flattens a nested Maybe.

        Example:

            >>> Maybe.just(Maybe.just(1)).join()
            Maybe.just(1)

            >>> Maybe.just(Maybe()).join()
            Maybe()
        :return:
        """

        cls = cast(type['Maybe[T]'], type(self))

        if self.value is cls.sentinel:
            return self
        elif cast('Maybe[T]', self.value).value is cls().sentinel:
            return self
        else:
            return cls(cast(T, cast('Maybe[T]', self.value).value))

    def bind(self: 'Maybe[T]', f: Callable[[T], 'Maybe[U]'], /) -> 'Maybe[U]':
        """
        Binds a function over the just value.

        Example:

            >>> Maybe.just(1).bind(lambda x: Maybe.just(x + 1))
            Maybe.just(2)

            >>> Maybe().bind(lambda x: Maybe.just(x + 1))
            Maybe()

        :param f: The function to bind.

        :return: Returns a Maybe.
        """

        cls = type(self)

        if self.value is cls.sentinel:
            return self
        else:
            return f(cast(T, self.value))

    def get_or_else(self, value: T, /) -> T:
        """
        Gets the value if is a just value. Otherwise, returns the provided
        value.

        :param value: The provided value.

        :return: Returns the value or the provided value.
        """
        cls = type(self)
        if self.value is cls.sentinel:
            return value
        else:
            return cast(T, self.value)

    @staticmethod
    def with_bool(present: bool, value: T) -> 'Maybe[T]':
        """
        Creates a Maybe with a value if the present is True. Otherwise,
        """
        if present:
            return Maybe(value)
        else:
            return Maybe()

    def __bool__(self, /) -> bool:
        """
        Returns True if the Maybe is a just value. Otherwise, returns False.
        """
        cls = type(self)
        return self.value is not cls.sentinel


Nothing: Maybe[Any] = Maybe.nothing()


def none():
    """
    Creates a Maybe with no value. This is useful for representing
    optional values. You can also use the Nothing constant, which is
    equivalent to this function.

    Example:

        >>> none()
        Maybe()

        >>> Nothing
        Maybe()

        >>> none() == Nothing
        True

    :return: Returns a Maybe with no value.
    """
    return Nothing


def just(value):
    """
    Creates a Maybe with a value.

    Example:

        >>> just(1)
        Maybe.just(1)

    :param value: The value.

    :return: Returns a Maybe with a value.
    """
    return Maybe.just(value)
