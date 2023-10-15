# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

"""
The domain errors are used to represent errors that occur in the domain layer.
"""


class DomainError(Exception):
    """Base class for domain errors."""

    def __init__(self, message: str):
        """Create a new instance of DomainError."""
        super().__init__(message)
