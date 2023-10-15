# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The WatchedList class is used to keep track of the items that were added and
removed from a list. This is useful for storing the changes in a database.

Example:

    >>> class Person(TypedDict):
    ...     name: str
    ...     age: int

    >>> class PersonList(WatchedList[Person]):
    ...     def compare(self, a: Person, b: Person) -> bool:
    ...         return a['name'] == b['name']

    >>> l = PersonList()
    >>> l.add(Person(name='John', age=30))
    >>> l.add(Person(name='Mary', age=25))
    >>> l.getItems()
    [{'name': 'John', 'age': 30}, {'name': 'Mary', 'age': 25}]

    >>> l.get_added_items()
    [{'name': 'John', 'age': 30}, {'name': 'Mary', 'age': 25}]

    >>> l.get_removed_items()
    []

    >>> l.remove(Person(name='John', age=30))
    >>> l.getItems()
    [{'name': 'Mary', 'age': 25}]

    >>> l.get_added_items()
    [{'name': 'Mary', 'age': 25}]

The WatchedList class is an abstract class. You must implement the compare method
to compare two items in the list.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, NoReturn, TypedDict

T = TypeVar('T')


class WatchedList(Generic[T], ABC):
    """
    The WatchedList class is used to keep track of the items that were added and
    removed from a list. This is useful for storing the changes in a database.
    """

    def __init__(self, items: Optional[List[T]] = None):
        object.__setattr__(self, "items", list(items or []))
        object.__setattr__(self, "original", list(items or []))
        object.__setattr__(self, "added", [])
        object.__setattr__(self, "removed", [])

    @abstractmethod
    def compare(self, a: T, b: T) -> bool:
        """
        Compares two items to determine if they are the same.

        :param a: Left item.
        :param b: Right item.

        :return: True if the items are the same, otherwise False.
        """
        pass

    def getItems(self) -> List[T]:
        """
        Gets the items in the list.

        :return: The items in the list.
        """
        return object.__getattribute__(self, "items")

    def get_original_items(self) -> List[T]:
        """
        Gets the original items in the list.

        :return: The original items in the list.
        """
        return object.__getattribute__(self, "original")

    def get_added_items(self) -> List[T]:
        """
        Gets the items that were added to the list.

        :return: The items that were added to the list.
        """
        return object.__getattribute__(self, "added")

    def get_removed_items(self) -> List[T]:
        """
        Gets the items that were removed from the list.

        :return: The items that were removed from the list.
        """
        return object.__getattribute__(self, "removed")

    def __is_current_item(self, item: T) -> bool:
        """
        Determines if the item is in the list.
        """
        for i in self.getItems():
            if self.compare(item, i):
                return True
        return False

    def __is_new_item(self, item: T) -> bool:
        """
        Determines if the item was added to the list.
        """
        for i in self.get_added_items():
            if self.compare(item, i):
                return True
        return False

    def __is_removed_item(self, item: T) -> bool:
        """
        Determines if the item was removed from the list.
        """
        for i in self.get_removed_items():
            if self.compare(item, i):
                return True
        return False

    def __remove_from_added(self, item: T) -> None:
        """
        Removes the item from the added list.
        """
        added = self.get_added_items()
        added.remove(item)
        object.__setattr__(self, "added", added)

    def __remove_from_removed(self, item: T) -> None:
        """
        Removes the item from the removed list.
        """
        removed = self.get_removed_items()
        removed.remove(item)
        object.__setattr__(self, "removed", removed)

    def __remove_from_items(self, item: T) -> None:
        """
        Removes the item from the list.
        """
        items = self.getItems()
        items.remove(item)
        object.__setattr__(self, "items", items)

    def __was_added_initially(self, item: T) -> bool:
        """
        Determines if the item was added initially.
        """
        for i in self.get_original_items():
            if self.compare(item, i):
                return True
        return False

    def exists(self, item: T) -> bool:
        """
        Determines if the item exists in the list.

        :param item: The item.

        :return: True if the item exists in the list, otherwise False.
        """
        return self.__is_current_item(item) or self.__is_new_item(item)

    def add(self, item: T) -> None:
        """
        Adds the item to the list.
        If the item was removed, it will be removed from the removed list.
        If the item was not added initially, it will be added to the added list.
        If the item is not in the list, it will be added to the list.

        :param item:
        :return:
        """
        if self.__is_removed_item(item):
            self.__remove_from_removed(item)
        if not self.__is_new_item(item) and not self.__was_added_initially(item):
            self.get_added_items().append(item)
        if not self.__is_current_item(item):
            self.getItems().append(item)

    def remove(self, item: T) -> NoReturn:
        """
        Removes the item from the list.

        If the item was added, it will be removed from the added list.
        If the item was not added initially, it will be added to the removed list.

        :param item: The item.
        """
        if self.__is_current_item(item):
            self.__remove_from_items(item)

        if self.__is_new_item(item):
            self.__remove_from_added(item)
            return

        if self.__was_added_initially(item):
            self.get_removed_items().append(item)
