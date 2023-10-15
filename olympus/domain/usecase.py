# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------
"""
The main proposal of IUseCase is to provide a common interface for all use cases
in the application. This interface is used by the application layer to execute
use cases.

Example:

    >>> class DoSomethingUseCase(IUseCase[int, str]):
    ...     def execute(self, request: Request) -> Response:
    ...         return 'Something'

    >>> use_case = DoSomethingUseCase()
    >>> use_case.execute(1)
    'Something'
"""

from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True)
class UseCaseError:
    """
    A wrapper for use case errors.
    """

    def __init__(self, message: str, err: Exception = None):
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "err", err)

        print(f'[AppError]: An unexpected error occurred.')
        print(err)

    def get_message(self) -> str:
        """
        Gets the message of the error.
        """
        return object.__getattribute__(self, "message")

    def get_err(self) -> Exception:
        """
        Gets the error.
        """
        return object.__getattribute__(self, "err")

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.get_message()})'


T = TypeVar('T')
U = TypeVar('U')


class IUseCase(Generic[T, U]):
    """
    The IUseCase interface represents a use case in the application. It is used by
    the application layer to execute use cases.
    """

    def execute(self, request: T) -> U:
        """
        Executes the use case.

        :param request: The request.
        :return: The response.
        """
        raise NotImplementedError()

    def __call__(self, request: T) -> U:
        """
        Executes the use case.
        """
        return self.execute(request)