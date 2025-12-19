# Step 3: Ports (Interfaces)

## Цель

Определить все интерфейсы (Ports) как typing.Protocol для репозиториев, executor и auth.

## Задачи

### 3.1. Создать core/ports/repositories.py

```python
"""Repository interfaces (Ports)."""
from typing import Protocol

from core.domain.models import (
    Problem,
    User,
    Draft,
    Submission,
    Progress,
)
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.result import Result
from core.domain.errors import NotFoundError, StorageError


class IProblemRepository(Protocol):
    """Interface for problem storage."""

    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        """Get problem by ID."""
        ...

    def get_all(self) -> tuple[Problem, ...]:
        """Get all problems."""
        ...

    def filter(
        self,
        difficulty: Difficulty | None = None,
        tags: tuple[str, ...] | None = None,
        language: Language | None = None,
    ) -> tuple[Problem, ...]:
        """Filter problems by criteria."""
        ...

    def count(self) -> int:
        """Get total number of problems."""
        ...


class IUserRepository(Protocol):
    """Interface for user storage."""

    def get_by_id(self, user_id: str) -> Result[User, NotFoundError]:
        """Get user by ID."""
        ...

    def save(self, user: User) -> Result[User, StorageError]:
        """Save user (create or update)."""
        ...

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """Delete user."""
        ...


class IDraftRepository(Protocol):
    """Interface for draft storage."""

    def get(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[Draft, NotFoundError]:
        """Get draft for user/problem/language combination."""
        ...

    def save(self, draft: Draft) -> Result[Draft, StorageError]:
        """Save draft (overwrites existing)."""
        ...

    def delete(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[None, NotFoundError]:
        """Delete draft."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Draft, ...]:
        """Get all drafts for a user."""
        ...


class ISubmissionRepository(Protocol):
    """Interface for submission storage."""

    def get_by_id(self, submission_id: str) -> Result[Submission, NotFoundError]:
        """Get submission by ID."""
        ...

    def save(self, submission: Submission) -> Result[Submission, StorageError]:
        """Save new submission."""
        ...

    def get_for_problem(
        self,
        user_id: str,
        problem_id: int,
    ) -> tuple[Submission, ...]:
        """Get all submissions for user/problem."""
        ...

    def get_for_user(self, user_id: str) -> tuple[Submission, ...]:
        """Get all submissions for user."""
        ...


class IProgressRepository(Protocol):
    """Interface for progress storage."""

    def get(
        self,
        user_id: str,
        problem_id: int,
    ) -> Result[Progress, NotFoundError]:
        """Get progress for user/problem."""
        ...

    def save(self, progress: Progress) -> Result[Progress, StorageError]:
        """Save progress."""
        ...

    def get_all_for_user(self, user_id: str) -> tuple[Progress, ...]:
        """Get all progress entries for user."""
        ...

    def get_solved_count(self, user_id: str) -> int:
        """Get number of solved problems for user."""
        ...

    def get_solved_by_difficulty(
        self,
        user_id: str,
    ) -> dict[Difficulty, int]:
        """Get solved count grouped by difficulty."""
        ...
```

### 3.2. Создать core/ports/executors.py

```python
"""Code executor interfaces (Ports)."""
from typing import Protocol

from core.domain.models import TestCase, ExecutionResult
from core.domain.result import Result
from core.domain.errors import ExecutionError


class ICodeExecutor(Protocol):
    """Interface for code execution."""

    def execute(
        self,
        code: str,
        test_cases: tuple[TestCase, ...],
        function_name: str,
        timeout_sec: int = 5,
    ) -> Result[ExecutionResult, ExecutionError]:
        """
        Execute code against test cases.

        Args:
            code: User's code to execute
            test_cases: Test cases to run
            function_name: Name of the function to call
            timeout_sec: Maximum execution time per test

        Returns:
            Result with ExecutionResult on success or ExecutionError on failure
        """
        ...

    def validate_syntax(self, code: str) -> Result[None, ExecutionError]:
        """
        Check if code has valid syntax.

        Args:
            code: Code to validate

        Returns:
            Ok(None) if valid, Err(ExecutionError) if invalid
        """
        ...
```

### 3.3. Создать core/ports/auth.py

```python
"""Authentication interfaces (Ports)."""
from typing import Protocol

from core.domain.models import User
from core.domain.result import Result
from core.domain.errors import DomainError


class AuthError(DomainError):
    """Authentication/authorization error."""
    pass


class IAuthProvider(Protocol):
    """Interface for authentication."""

    def get_current_user(self) -> Result[User, AuthError]:
        """
        Get currently authenticated user.

        Returns:
            Result with User on success or AuthError if not authenticated
        """
        ...

    def authenticate(self, credentials: dict) -> Result[User, AuthError]:
        """
        Authenticate with credentials.

        Args:
            credentials: Authentication credentials (format depends on provider)

        Returns:
            Result with User on success or AuthError on failure
        """
        ...
```

### 3.4. Обновить core/ports/__init__.py

```python
"""Ports layer - interfaces for external dependencies."""
from .repositories import (
    IProblemRepository,
    IUserRepository,
    IDraftRepository,
    ISubmissionRepository,
    IProgressRepository,
)
from .executors import ICodeExecutor
from .auth import IAuthProvider, AuthError

__all__ = [
    "IProblemRepository",
    "IUserRepository",
    "IDraftRepository",
    "ISubmissionRepository",
    "IProgressRepository",
    "ICodeExecutor",
    "IAuthProvider",
    "AuthError",
]
```

## Диаграмма зависимостей

```
                    ┌─────────────────────┐
                    │    core/ports/      │
                    │                     │
                    │  IProblemRepository │
                    │  IUserRepository    │
                    │  IDraftRepository   │
                    │  ISubmissionRepo    │
                    │  IProgressRepository│
                    │  ICodeExecutor      │
                    │  IAuthProvider      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
      ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
      │   adapters/   │ │   adapters/   │ │   adapters/   │
      │   storage/    │ │   executors/  │ │   auth/       │
      │               │ │               │ │               │
      │ JsonProblem   │ │ LocalExecutor │ │ AnonymousAuth │
      │ SqliteProblem │ │ DockerExecutor│ │ TelegramAuth  │
      │ PostgresProblem│ │ RemoteExecutor│ │ TokenAuth     │
      └───────────────┘ └───────────────┘ └───────────────┘
```

## Критерии готовности

- [ ] Все Protocol интерфейсы определены
- [ ] Методы имеют type hints
- [ ] Docstrings написаны для всех методов
- [ ] `__init__.py` экспортирует все интерфейсы
- [ ] mypy проходит без ошибок

## Тесты для Step 3

```python
# tests/unit/core/ports/test_protocols.py
"""Test that protocols are properly defined."""
from typing import get_type_hints
from core.ports import (
    IProblemRepository,
    IUserRepository,
    ICodeExecutor,
    IAuthProvider,
)


class TestProtocolsHaveTypeHints:
    """Verify all protocol methods have type hints."""

    def test_problem_repository_has_hints(self):
        hints = get_type_hints(IProblemRepository.get_by_id)
        assert 'problem_id' in hints
        assert 'return' in hints

    def test_code_executor_has_hints(self):
        hints = get_type_hints(ICodeExecutor.execute)
        assert 'code' in hints
        assert 'test_cases' in hints
        assert 'return' in hints
```

## Следующий шаг

После завершения Step 3 можно параллельно работать над:
- [Step 4: Storage Adapters](./04_storage_adapters.md)
- [Step 5: Executor Adapter](./05_executor_adapter.md)
- [Step 6: Core Services](./06_core_services.md)
