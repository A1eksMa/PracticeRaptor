"""User model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    """User entity.

    Represents a registered user account.
    Minimal for now - can be extended later.

    Example:
        user = User(
            user_id=1,
            user_name="john_doe",
            hash_password="...",
        )
    """

    user_id: int = 0
    user_name: str = ""
    hash_password: str = ""

    def __str__(self) -> str:
        return self.user_name or f"User#{self.user_id}"

    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous (guest)."""
        return self.user_id == 0


# Default anonymous user for CLI mode
DEFAULT_USER = User(
    user_id=0,
    user_name="guest",
    hash_password="",
)
