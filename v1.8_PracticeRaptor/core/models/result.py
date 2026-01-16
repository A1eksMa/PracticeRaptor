"""Result type for functional error handling.

Provides Ok[T] and Err[E] types for explicit error handling
without exceptions. Inspired by Rust's Result type.

Example:
    def divide(a: int, b: int) -> Result[float, str]:
        if b == 0:
            return Err("Division by zero")
        return Ok(a / b)

    result = divide(10, 2)
    if result.is_ok():
        print(result.unwrap())  # 5.0
"""

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, Union

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Success case of Result."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, fn: Callable[[T], U]) -> 'Ok[U]':
        """Apply function to value."""
        return Ok(fn(self.value))

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Apply function that returns Result (monadic bind)."""
        return fn(self.value)

    def map_err(self, fn: Callable[[E], U]) -> 'Ok[T]':
        """No-op for Ok (error mapping doesn't apply)."""
        return self

    def unwrap(self) -> T:
        """Get value. Safe to call on Ok."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get value (ignores default for Ok)."""
        return self.value

    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """Get value (ignores fn for Ok)."""
        return self.value

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error case of Result."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, fn: Callable[[T], U]) -> 'Err[E]':
        """No-op for Err (value mapping doesn't apply)."""
        return self

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Err[E]':
        """No-op for Err."""
        return self

    def map_err(self, fn: Callable[[E], U]) -> 'Err[U]':
        """Apply function to error."""
        return Err(fn(self.error))

    def unwrap(self) -> T:
        """Raises ValueError. Use unwrap_or or check is_ok first."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return default value."""
        return default

    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """Compute value from error."""
        return fn(self.error)

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type alias for Result
Result = Union[Ok[T], Err[E]]
