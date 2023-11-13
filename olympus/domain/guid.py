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

        -------
        Returns
        -------
        Guid
            A Guid instance.
        """
        return cls(str(uuid.uuid4()))

    @classmethod
    def from_string(cls, value: str) -> 'Guid':
        """
        Creates a GUID from a string.

        ----------
        Parameters
        ----------
        value : str
            The string value of the GUID.

        -------
        Returns
        -------
        Guid
            A Guid instance.
        """
        return cls(value)

    def __init__(self, value: str = None):
        """
        Creates a GUID. If no value is provided, a new value is created
        automatically, based on the UUID4 algorithm.

        ----------
        Parameters
        ----------
        value : str
            The string value of the GUID.
        """
        self.value = value or str(uuid.uuid4())

    def __str__(self):
        """ xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx """
        return self.value

    def __repr__(self):
        """ Guid('xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx') """
        return f"{self.__class__.__name__}('{self.value}')"
