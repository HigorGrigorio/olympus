# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The class Guid represents a unique identifier (GUID) that is a 128-bit integer
(16 bytes) that can be used across all computers and networks wherever a unique
identifier is required. Such an identifier has a very low probability of being
duplicated.

The main purpose of this class is to provide a unique identifier for each entity
in the domain layer. This is useful for comparing entities and for storing them
in a dictionary.
"""

import uuid


class Guid:
    """
    This class represents a GUID. It is used to identify an entity.
    """

    @classmethod
    def new(cls) -> 'Guid':
        """
        Creates a GUID.

        :return: Returns a Guid instance with an uuid4 string.
        """
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_string(cls, value: str) -> 'Guid':
        """
        Creates a GUID from a string.

        :param value: The string value.
        :return: Returns a Guid instance with the given string.
        """
        return cls(value)

    def __init__(self, value: str = None):
        self.value = value or self.new()

    def __str__(self):
        return self.value

    def __repr__(self):
        """ Guid('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx') """
        return f"Guid('{self.value}')"
