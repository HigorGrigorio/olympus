# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Type, Callable, TypeVar, Any, Generic

from olympus.domain import Guid, Entity
from olympus.monads.maybe import Maybe


class DomainEvent(ABC):
    """
    A domain event is an event that is relevant to the domain. The
    main purpose of a domain event is to record something that
    happened in the domain.
    """

    createdAt: datetime

    def __init__(self):
        """
        Creates a new instance of DomainEvent.
        """
        self.createAt = None

    @abstractmethod
    def get_aggregate_id(self) -> Guid:
        """
        Gets the aggregate ID.
        :return: Returns the aggregate ID.
        """
        ...


CallableEventHandler = Callable[[DomainEvent], None]

E = TypeVar('E')


class AggregateRoot(Generic[E], Entity[E]):
    """
    An Aggregate is a cluster of domain objects that can be treated as a single unit.
    It represents a part of the domain model that is treated as a cohesive whole.
    Aggregates can be thought of as transactional boundaries, which means that all
    changes to the objects within an aggregate are persisted or rolled back as a
    single transaction.

    Within an aggregate, one entity is designated as the Aggregate Root. The Aggregate
    Root is the entry point for any external access to the aggregate. It acts as a facade,
    providing methods for interaction with the objects inside the aggregate while
    controlling access and ensuring that all changes happen in a consistent manner.
    The Aggregate Root is responsible for enforcing invariants and consistency rules.

    This pattern is used to ensure consistency of data. It is also used to reduce the
    number of operations that have to be performed when dealing with complex domain
    models.

    Events are used to notify other parts of the system that something has happened.
    They are used to decouple the different parts of the system and to make it easier
    to extend the system with new functionality.
    """

    def __init__(self, props: E, id: Maybe[Guid]):
        super().__init__(props, id)
        self.__events__: List[DomainEvent] = []

    def get_events(self) -> List[DomainEvent]:
        """
        Gets the events that have occurred.

        :return: Returns the events that have occurred.
        """
        return self.__events__

    def clear_events(self):
        """
        Clears the events that have occurred.
        """
        self.__events__ = []

    def remind(self, event: DomainEvent):
        """
        Adds an event to the aggregate.

        :param event: The event.
        """

        # marks to dispatch. If not marked, no trigger events
        # when dispatched.
        EventBus.mark_aggregate_for_dispatch(self)

        # record to emit later.
        self.__events__.append(event)


T = TypeVar('T', bound=DomainEvent)


class EventBus:
    __handlers__: Dict[str, List[CallableEventHandler]] = {}
    __marked__: List[Guid] = []

    def __init__(self):
        raise Exception('Cannot instantiate EventBus class. It is a static class.')

    @staticmethod
    def bind(event: Type[T], handler: CallableEventHandler):
        """
        Binds a handler to an event.
        :param event: The event.
        :param handler: The handler.
        """
        key = event.__name__

        if key not in EventBus.__handlers__:
            EventBus.__handlers__[key] = []
        elif handler in EventBus.__handlers__[key]:
            return

        EventBus.__handlers__[key].append(handler)

    @staticmethod
    def unbind(event: Type[T], handler: CallableEventHandler):
        """
        Unbinds a handler from an event.
        :param event: The event.
        :param handler: The handler.
        """
        if event not in EventBus.__handlers__:
            return

        if handler not in EventBus.__handlers__[event]:
            return

        EventBus.__handlers__[event].remove(handler)

    @staticmethod
    def dispatch(e: DomainEvent):
        """
        Dispatches an event.
        :param e: The event.
        """

        key = type(e).__name__

        if key not in EventBus.__handlers__:
            return

        # fire all handlers
        for cb in EventBus.__handlers__[key]:
            cb(e)

    @staticmethod
    def clear_event_bus():
        """
        Clears all event handlers.
        """
        EventBus.__handlers__ = {}

    @staticmethod
    def mark_aggregate_for_dispatch(agg: 'AggregateRoot'):
        """
        Marks an aggregate for dispatch.
        :param agg: The aggregate.
        """

        if agg.get_id() in EventBus.__marked__:
            EventBus.__marked__.append(agg.get_id())

    @staticmethod
    def dispatch_event_bus_for_aggregate(agg: AggregateRoot[Any]):
        """
        Dispatches events for an aggregate.
        :param agg: The aggregate.
        """
        if agg.get_id() not in EventBus.__marked__:
            return

        for event in agg.get_events():
            EventBus.dispatch(event)

        agg.clear_events()
        EventBus.__marked__.remove(agg.get_id())

    @staticmethod
    def clear_marked_aggregates():
        """
        Clears all marked aggregates.
        """
        EventBus.__marked__ = []


def trigger(data: DomainEvent | List[DomainEvent] | 'AggregateRoot[Any]'):
    """
    Triggers an event.
    :param data: The event, list of events or aggregate root.
    """
    if isinstance(data, AggregateRoot):
        trigger(data.get_events())
        return

    if isinstance(data, list):
        [EventBus.dispatch(e) for e in data]
        return

    EventBus.dispatch(data)


def bind(event: Type[T], cb: CallableEventHandler):
    """
    Binds a handler to an event.

    :param event: The event.
    :param cb: The handler.

    """
    EventBus.bind(event, cb)


class EventHandler(ABC):
    """
    A handler for domain events.
    """

    @abstractmethod
    def setup(self):
        """
        Setups event handlers on the event bus.
        """
        raise NotImplementedError
