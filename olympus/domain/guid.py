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

    @staticmethod
    def new() -> 'Guid':
        """
        Creates a GUID.
        :return: Returns a Guid instance with a uuid4 string.
        """
        return Guid(str(uuid.uuid4()))

    def __init__(self, value: str = None):
        self.value = value or self.new()

    def __str__(self):
        return self.value

    def __repr__(self):
        """ Guid('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx') """
        return f"Guid('{self.value}')"
