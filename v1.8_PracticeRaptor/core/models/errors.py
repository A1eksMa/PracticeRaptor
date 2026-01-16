"""Domain error types.

All errors are frozen dataclasses (immutable value objects).
Used with Result type for functional error handling.
"""

from dataclasses import dataclass, field
from typing import Union


@dataclass(frozen=True)
class DomainError:
    """Base error type for all domain errors."""

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class NotFoundError(DomainError):
    """Entity not found in storage."""

    entity: str = ""
    entity_id: Union[str, int] = ""
    message: str = field(init=False)

    def __post_init__(self) -> None:
        msg = f"{self.entity} with id '{self.entity_id}' not found"
        object.__setattr__(self, 'message', msg)


@dataclass(frozen=True)
class ValidationError(DomainError):
    """Input validation failed."""

    field_name: str | None = None

    def __str__(self) -> str:
        if self.field_name:
            return f"{self.field_name}: {self.message}"
        return self.message


@dataclass(frozen=True)
class ExecutionError(DomainError):
    """Code execution failed."""

    error_type: str = ""  # syntax, runtime, timeout, memory

    def __str__(self) -> str:
        if self.error_type:
            return f"[{self.error_type}] {self.message}"
        return self.message


@dataclass(frozen=True)
class StorageError(DomainError):
    """Storage operation failed."""

    operation: str = ""  # read, write, delete

    def __str__(self) -> str:
        if self.operation:
            return f"Storage {self.operation} failed: {self.message}"
        return self.message


@dataclass(frozen=True)
class AuthError(DomainError):
    """Authentication or authorization failed."""

    def __str__(self) -> str:
        return f"Auth error: {self.message}"
