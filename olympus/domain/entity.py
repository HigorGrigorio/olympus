# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
THe Entity class represents an entity in the domain layer. It is the base class
for all entities, and it provides a unique identifier for each entity. This class
use the props pattern to store the entity's properties. The props pattern is a
dictionary that stores the entity's properties. This pattern is useful for
comparing entities and for storing them in a dictionary.

Entities are compared by their GUIDs. If two entities have the same GUID, they
are considered equal. Otherwise, they are considered different.

Example:

    >>> class PersonProps(TypedDict):
    ...     name: str
    ...     age: int

    >>> class Person(Entity[PersonProps]):
    ...     def __init__(self, props: PersonProps, guid: Guid = None):
    ...         super().__init__(props, Maybe(guid))

    >>> person1 = Person(PersonProps(name='John', age=30))
    >>> person2 = Person(PersonProps(name='John', age=30))
    >>> person1 == person2
    False

    >>> person1 = Person(PersonProps(name='John', age=30), Guid('1'))
    >>> person2 = Person(PersonProps(name='John', age=31), Guid('1'))

    >>> person1 == person2
    True
"""

from typing import Generic, TypeVar, TypedDict

from olympus.monads.maybe import Maybe
from .guid import Guid

E = TypeVar('E')


class Entity(Generic[E]):
    """
    The Entity class represents an entity, which is an object that is not defined by its attributes, but rather by
    a thread of continuity and its identity.
    """

    def __init__(self, props: E, id: Maybe[Guid]):
        self.id = id.get_or_else(Guid.new)
        self.props = props

    def get_props(self) -> E:
        """
        Gets the properties of the entity.

        :return:
        """
        return self.props

    def get_id(self) -> Guid:
        """
        Gets the ID of the entity.
        :return:
        """
        return self.id
