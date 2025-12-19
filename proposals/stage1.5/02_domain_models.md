# Step 2: Domain Models

## Цель

Определить все доменные модели как immutable dataclasses с поддержкой i18n.

## Задачи

### 2.1. Создать core/domain/models.py

```python
"""Domain models - immutable data structures."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .enums import Difficulty, Language, SubmissionStatus, ProgressStatus


# ============================================================
# Value Objects
# ============================================================

@dataclass(frozen=True)
class LocalizedText:
    """Text with translations."""
    translations: dict[str, str]  # {"en": "...", "ru": "..."}

    def get(self, locale: str, fallback: str = "en") -> str:
        """Get text for locale with fallback."""
        return self.translations.get(locale, self.translations.get(fallback, ""))

    def __str__(self) -> str:
        return self.get("en")


@dataclass(frozen=True)
class Example:
    """Problem example with input/output."""
    input: dict[str, Any]
    output: Any
    explanation: LocalizedText | None = None


@dataclass(frozen=True)
class TestCase:
    """Test case for validation."""
    input: dict[str, Any]
    expected: Any
    description: str | None = None
    is_hidden: bool = False


@dataclass(frozen=True)
class Solution:
    """Canonical/reference solution."""
    name: str
    complexity: str  # e.g., "O(n)"
    code: str


@dataclass(frozen=True)
class LanguageSpec:
    """Language-specific problem data."""
    language: Language
    function_signature: str
    solutions: tuple[Solution, ...]


# ============================================================
# Entities
# ============================================================

@dataclass(frozen=True)
class Problem:
    """Coding problem entity."""
    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    tags: tuple[str, ...]
    examples: tuple[Example, ...]
    test_cases: tuple[TestCase, ...]
    languages: tuple[LanguageSpec, ...]
    hints: tuple[LocalizedText, ...] = ()

    def get_language_spec(self, language: Language) -> LanguageSpec | None:
        """Get spec for specific language."""
        for spec in self.languages:
            if spec.language == language:
                return spec
        return None


@dataclass(frozen=True)
class User:
    """User entity."""
    id: str
    locale: str = "en"
    preferred_language: Language = Language.PYTHON
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())


@dataclass(frozen=True)
class Draft:
    """Unsaved user code."""
    user_id: str
    problem_id: int
    language: Language
    code: str
    updated_at: datetime


@dataclass(frozen=True)
class Submission:
    """Successful submission."""
    id: str
    user_id: str
    problem_id: int
    language: Language
    code: str
    execution_time_ms: int
    memory_used_kb: int
    created_at: datetime


@dataclass(frozen=True)
class Progress:
    """User progress on a problem."""
    user_id: str
    problem_id: int
    status: ProgressStatus
    attempts: int = 0
    solved_languages: tuple[Language, ...] = ()
    first_solved_at: datetime | None = None


# ============================================================
# Result Objects (for execution)
# ============================================================

@dataclass(frozen=True)
class TestResult:
    """Result of running a single test."""
    test_case: TestCase
    passed: bool
    actual: Any = None
    execution_time_ms: int = 0
    error_message: str | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Result of running all tests."""
    success: bool
    test_results: tuple[TestResult, ...]
    total_time_ms: int
    memory_used_kb: int = 0
    error: str | None = None

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.test_results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.test_results)
```

### 2.2. Создать фабричные функции (опционально)

```python
# core/domain/factories.py
"""Factory functions for creating domain objects."""
from datetime import datetime
from uuid import uuid4

from .models import User, Draft, Submission, Progress
from .enums import Language, ProgressStatus


def create_user(
    user_id: str | None = None,
    locale: str = "en",
    preferred_language: Language = Language.PYTHON,
) -> User:
    """Create a new user with defaults."""
    return User(
        id=user_id or str(uuid4()),
        locale=locale,
        preferred_language=preferred_language,
        created_at=datetime.now(),
    )


def create_draft(
    user_id: str,
    problem_id: int,
    code: str,
    language: Language = Language.PYTHON,
) -> Draft:
    """Create a new draft."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )


def create_submission(
    user_id: str,
    problem_id: int,
    code: str,
    execution_time_ms: int,
    memory_used_kb: int = 0,
    language: Language = Language.PYTHON,
) -> Submission:
    """Create a new submission."""
    return Submission(
        id=str(uuid4()),
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        execution_time_ms=execution_time_ms,
        memory_used_kb=memory_used_kb,
        created_at=datetime.now(),
    )


def create_initial_progress(user_id: str, problem_id: int) -> Progress:
    """Create initial progress for a problem."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=ProgressStatus.NOT_STARTED,
        attempts=0,
        solved_languages=(),
        first_solved_at=None,
    )
```

### 2.3. Обновить __init__.py

```python
# core/domain/__init__.py
"""Domain layer - models, enums, errors, result type."""
from .enums import Difficulty, Language, SubmissionStatus, ProgressStatus
from .errors import (
    DomainError,
    NotFoundError,
    ValidationError,
    ExecutionError,
    StorageError,
)
from .result import Ok, Err, Result
from .models import (
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
    Problem,
    User,
    Draft,
    Submission,
    Progress,
    TestResult,
    ExecutionResult,
)

__all__ = [
    # Enums
    "Difficulty",
    "Language",
    "SubmissionStatus",
    "ProgressStatus",
    # Errors
    "DomainError",
    "NotFoundError",
    "ValidationError",
    "ExecutionError",
    "StorageError",
    # Result
    "Ok",
    "Err",
    "Result",
    # Models
    "LocalizedText",
    "Example",
    "TestCase",
    "Solution",
    "LanguageSpec",
    "Problem",
    "User",
    "Draft",
    "Submission",
    "Progress",
    "TestResult",
    "ExecutionResult",
]
```

## Миграция данных

### Текущий формат JSON (prototype)

```json
{
  "id": 1,
  "title": "Two Sum",
  "description": "Given an array...",
  "python3": {
    "function_signature": "def two_sum(...):",
    "solutions": [...]
  }
}
```

### Новый формат JSON (i18n)

```json
{
  "id": 1,
  "title": {
    "en": "Two Sum",
    "ru": "Сумма двух чисел"
  },
  "description": {
    "en": "Given an array...",
    "ru": "Дан массив..."
  },
  "difficulty": "easy",
  "tags": ["array", "hash-table"],
  "examples": [...],
  "test_cases": [...],
  "languages": {
    "python3": {
      "function_signature": "def two_sum(...):",
      "solutions": [...]
    }
  }
}
```

## Критерии готовности

- [ ] Все модели определены как `@dataclass(frozen=True)`
- [ ] `LocalizedText` поддерживает fallback
- [ ] Фабричные функции созданы
- [ ] `__init__.py` экспортирует все публичные типы
- [ ] mypy проходит без ошибок
- [ ] Тесты для моделей написаны

## Тесты для Step 2

```python
# tests/unit/core/domain/test_models.py
import pytest
from core.domain.models import (
    LocalizedText,
    Problem,
    TestCase,
    Example,
    LanguageSpec,
    Solution,
)
from core.domain.enums import Difficulty, Language


class TestLocalizedText:
    def test_get_returns_translation(self):
        text = LocalizedText({"en": "Hello", "ru": "Привет"})
        assert text.get("en") == "Hello"
        assert text.get("ru") == "Привет"

    def test_get_falls_back_to_english(self):
        text = LocalizedText({"en": "Hello"})
        assert text.get("fr") == "Hello"

    def test_str_returns_english(self):
        text = LocalizedText({"en": "Hello", "ru": "Привет"})
        assert str(text) == "Hello"


class TestProblem:
    def test_get_language_spec_returns_spec(self):
        spec = LanguageSpec(
            language=Language.PYTHON,
            function_signature="def solve():",
            solutions=(),
        )
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Test"}),
            description=LocalizedText({"en": "Desc"}),
            difficulty=Difficulty.EASY,
            tags=("test",),
            examples=(),
            test_cases=(),
            languages=(spec,),
        )

        result = problem.get_language_spec(Language.PYTHON)
        assert result == spec

    def test_get_language_spec_returns_none_if_not_found(self):
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Test"}),
            description=LocalizedText({"en": "Desc"}),
            difficulty=Difficulty.EASY,
            tags=(),
            examples=(),
            test_cases=(),
            languages=(),
        )

        result = problem.get_language_spec(Language.GO)
        assert result is None


class TestImmutability:
    def test_problem_is_frozen(self):
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Test"}),
            description=LocalizedText({"en": "Desc"}),
            difficulty=Difficulty.EASY,
            tags=(),
            examples=(),
            test_cases=(),
            languages=(),
        )

        with pytest.raises(AttributeError):
            problem.id = 2
```

## Следующий шаг

После завершения Step 2 переходите к [Step 3: Ports](./03_ports.md).
