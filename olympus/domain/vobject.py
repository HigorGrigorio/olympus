# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The Value Object (VO) is an immutable object that represents a domain concept.
The Value Object is used to encapsulate a set of values that belong together.
So its state cannot be changed once it is created.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')


@dataclass(frozen=True)
class ValueObject(Generic[T]):
    """
    The ValueObject class represents an object that contains attributes but has
    no conceptual identity. They should be treated as immutable.
    """

    def __init__(self, value: T):
        """
        Creates a ValueObject instance.

        :param value: The value of the ValueObject.
        """
        object.__setattr__(self, "value", value)

    def to_value(self) -> T:
        """
        A helper method to get the value of the ValueObject.

        :return: The value of the ValueObject.
        """
        return object.__getattribute__(self, "value")

    def __eq__(self, other):
        if other is None:
            return False

        return self.to_value() == other.toValue()
