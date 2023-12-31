# Olympus - An Standard library for Domain Driven Design in python

This library is a collection of tools and patterns to help you build Domain Driven Design applications in python.

## Installation

git install

```bash
pip install git+https://github.com/HigorGrigorio/olympus.git
```

## Usage

In this library you will find some tools to help you build your DDD application.

### Monads

Monads are a way to handle errors and side effects in a functional way. In this library you will find some monads
implementations. The monads are:

- Maybe
- Either
- Result
- Guard

The Guard monad is a special monad that is used to validate data. It is used in the Value Objects. The other monads are
used to handle errors and side effects.

You can create custom monads guards and use them in your application.

```python
from olympus.monads.guards import guarder, AbstractGuard, GuardResult


@guarder('user_email')
class UserEmailGuarder(AbstractGuard):
    """
    Guard for the manager email
    """

    message = 'The manager email{not}is invalid'

    def isSatisfiedBy(self, value: str) -> GuardResult:
        return value is not None and value != ''

    def __repr__(self):
        return f'UserEmail({self.negate, self.args}'

    def __str__(self):
        return f'UserEmail({self.negate, self.args}'
```

The guard is registered in the `guard` decorator. The decorator will register the guard in the `Guards` class,
an static class. `user_email` is instantiated with the `args` parameters. The `args` is a list of arguments
passed in the test string. The `message` is the message that will be returned if the guard fails.

You can use the guard in your value objects.

### Value Objects

Value objects are immutable objects that represent a concept in your domain. They are used to validate and encapsulate
data.

```python
from olympus.domain import ValueObject
from olympus.monads import W, Result, guard


class UserEmail(ValueObject[str]):
    def __init__(self, value: str):
        super().__init__(value)

    @staticmethod
    def create(value: str) -> Result['UserEmail']:
        # validates the entry with custom guard
        guardResult = guard({
            'value': value,
            'name': 'Name'
        }, 'user_email')

        # If guard is not None, it means that the validation failed

        # if not guard:
        #    return W(guard)
        #
        # return W(Name(value))
        # 
        # Same as:
        return W(guard).bind(lambda _: W(UserEmail(value)))
```

And Usage example:

```python
from my_project.domain import UserEmail

try:
    # throws ValueError if the validation fails
    name = UserEmail.create('joe@gmail.com').unwrap()

    # do something with name
except ValueError as e:
    print(e)
```

or you can use the `Result` helpers:

```python
from my_project.domain import UserEmail

name = UserEmail.create('joe@gmail.com').unwrap_or_else(lambda e: print(e))

...
```

```python
from my_project.domain import User, UserEmail

from olympus.monads import maybe

user = UserEmail.create('joe@gmail.com').bind(
    lambda email: User.create(
        {
            'email': email,  # unwrapped email
            'name': 'Joe Doe',
            'age': 18
        },
        maybe.none()  # no id provided
    )
).unwrap_or_else(lambda e: print(e))

...
```

### Entities

Entities are objects that have an identity. They are mutable and can be compared by their identity.

To create an entity, you must inherit from the `Entity` class. The entity class uses property encapsulation to manage
entity properties.

See the Example:

```python

from typing import TypedDict

from my_project.domain import UserEmail

from olympus.domain import Entity, Guid
from olympus.monads import W, Result, guard_all, maybe


class UserProps(TypedDict):
    """
    The UserProps class is a TypedDict that represents the properties of
    the User class.

    Note: The user id is represented by GUID (Globally Unique Identifier)
    in Entity base class.
    """

    """
    The user name. The user name is cannot empty and cannot have special
    characters.
    """
    name: str

    """
    The user age. The user age is cannot be negative.
    """
    age: int

    """
    User email. Instance of UserEmail class.
    """
    email: UserEmail


class User(Entity[UserProps]):
    """
    The User class represents a user.
    """

    def __init__(self, props: UserProps, id: maybe.Maybe[Guid]):
        """
        Creates a User instance.
        :param props: The properties of the User.
        """
        super().__init__(props, id)

    @staticmethod
    def create(props: UserProps, id: maybe.Maybe[Guid]) -> Result['User']:
        """
        Creates a User instance.

        Rules:

            - The age must be greater than 18.
            - name cannot be empty and cannot have special characters.

        :param id: The user id.
        :param props: The properties of the User.
        :return: The User.
        """
        return W(guard_all(props, {
            'name': 'required|regex[r"^[a-zA-Z0-9 ]+$"]',
            'age': 'lt[18]',
        })).bind(lambda _: W(User(props, id)))
```

and usage example:

```python
from my_project.domain import User, UserEmail
from olympus.monads import maybe

user = UserEmail.create('joe@email.com')
.bind(lambda email: User.create({
    'name': 'Joe Doe',
    'age': 18,
    'email': email
}, maybe.none())).unwrap_or_else(lambda e: print(e))
```

### Aggregate Root and Domain events

The aggregates are objects that deal with the business rules of your application. They are responsible for managing
events and publishing them.

To create an aggregate, you must inherit from the `AggregateRoot` class. The aggregate class extend the `Entity` class.

See the Example:

the main imports:

```python
from olympus.domain.events import AggregateRoot, DomainEvent, EventHandler, bind, trigger

...
```

the domain event:

```python
class UserEmailChanged(DomainEvent):
    """
    The main proposal of the DomainEvent is to represent a change in the
    aggregate state.
    """

    user: User
    old_email: UserEmail

    def __init__(self, user: User, old_email: UserEmail):
        super().__init__()
        self.user = user
        self.old_email = old_email

    def get_aggregate_id(self) -> Guid:
        return self.user.id
```

the aggregate implementation:

```python
# in the user classes
class User(AggregateRoot[UserProps]):
    ...
    # rest of implementation

    def changeEmail(self, email: UserEmail):
        self.remind(UserEmailChanged(self, self.props.email))
        self.props.email = email
```

the handler:

```python
class UserEmailChangedHandler(EventHandler):
    """
    The EventHandler is a class that handles the DomainEvent.
    """

    def setup(self):
        bind(UserEmailChanged, self.on_email_change)

    def on_email_change(self, event: UserEmailChanged):
        print(f'User email changed from {event.old_email} to {event.user.email}')
```

the trigger:

```python

class UserRepo:
    """
    The UserRepo is a class that represents the repository of the User
    aggregate.
    """

    def save(self, user: User):
        """
        Saves the user.
        :param user: The user.
        :return: None
        """
        # save the user
        ...

        # trigger the events
        trigger(user)
```
