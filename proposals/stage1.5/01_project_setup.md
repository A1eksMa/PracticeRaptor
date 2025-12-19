# Step 1: Project Setup & Foundation

## Цель

Создать структуру проекта и базовые модули, которые будут использоваться всеми остальными компонентами.

## Задачи

### 1.1. Создать структуру директорий

```bash
practiceraptor/
├── core/
│   ├── __init__.py
│   ├── domain/
│   │   └── __init__.py
│   ├── ports/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── adapters/
│   ├── __init__.py
│   ├── storage/
│   │   └── __init__.py
│   ├── executors/
│   │   └── __init__.py
│   └── auth/
│       └── __init__.py
├── di/
│   └── __init__.py
├── clients/
│   └── cli/
│       └── __init__.py
├── data/
│   └── problems/
├── config/
├── docker/
└── tests/
    ├── unit/
    ├── integration/
    └── fixtures/
```

### 1.2. Создать core/domain/result.py

```python
"""Result type for functional error handling."""
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

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
        """Apply function to value if Ok."""
        return Ok(fn(self.value))

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Apply function that returns Result."""
        return fn(self.value)

    def unwrap(self) -> T:
        """Get value or raise if Err."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get value or default."""
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

    def map(self, fn: Callable) -> 'Err[E]':
        """Return self (error propagates)."""
        return self

    def flat_map(self, fn: Callable) -> 'Err[E]':
        """Return self (error propagates)."""
        return self

    def unwrap(self) -> None:
        """Raise ValueError with error details."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return default value."""
        return default

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


# Type alias
Result = Ok[T] | Err[E]
```

### 1.3. Создать core/domain/errors.py

```python
"""Domain error types."""
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainError:
    """Base class for domain errors."""
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class NotFoundError(DomainError):
    """Entity not found."""
    entity: str
    id: str | int

    def __post_init__(self):
        object.__setattr__(
            self,
            'message',
            f"{self.entity} with id '{self.id}' not found"
        )


@dataclass(frozen=True)
class ValidationError(DomainError):
    """Validation failed."""
    field: str | None = None


@dataclass(frozen=True)
class ExecutionError(DomainError):
    """Code execution failed."""
    error_type: str  # syntax, runtime, timeout, memory


@dataclass(frozen=True)
class StorageError(DomainError):
    """Storage operation failed."""
    operation: str  # read, write, delete
```

### 1.4. Создать core/domain/enums.py

```python
"""Domain enumerations."""
from enum import Enum, auto


class Difficulty(str, Enum):
    """Problem difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python3"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"


class SubmissionStatus(str, Enum):
    """Status of a submission."""
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"


class ProgressStatus(str, Enum):
    """User progress on a problem."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
```

### 1.5. Создать файлы конфигурации

**pyproject.toml:**
```toml
[project]
name = "practiceraptor"
version = "0.2.0"
description = "Practice coding problems with rapid feedback"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
    "mypy>=1.0",
    "ruff>=0.1",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = "-v --tb=short"
```

**config/config.example.yaml:**
```yaml
app:
  name: PracticeRaptor
  environment: development
  default_locale: en

storage:
  type: json
  json:
    base_path: ./data

executor:
  type: local
  timeout_sec: 5
  memory_limit_mb: 256

auth:
  type: anonymous
```

### 1.6. Создать .gitignore дополнения

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
dist/
build/

# Virtual environment
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Local config
config/config.yaml
.env

# Data (keep structure, ignore content)
data/users/
data/submissions/
data/drafts/
!data/problems/
```

## Критерии готовности

- [ ] Структура директорий создана
- [ ] `core/domain/result.py` работает (тесты проходят)
- [ ] `core/domain/errors.py` определены
- [ ] `core/domain/enums.py` определены
- [ ] `pyproject.toml` настроен
- [ ] `mypy --strict` проходит на созданных файлах
- [ ] `ruff check` проходит без ошибок

## Тесты для Step 1

```python
# tests/unit/core/domain/test_result.py
import pytest
from core.domain.result import Ok, Err

class TestOk:
    def test_is_ok_returns_true(self):
        result = Ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False

    def test_unwrap_returns_value(self):
        result = Ok("hello")
        assert result.unwrap() == "hello"

    def test_map_applies_function(self):
        result = Ok(5).map(lambda x: x * 2)
        assert result.unwrap() == 10

    def test_flat_map_chains_results(self):
        result = Ok(5).flat_map(lambda x: Ok(x * 2))
        assert result.unwrap() == 10


class TestErr:
    def test_is_err_returns_true(self):
        result = Err("error")
        assert result.is_err() is True
        assert result.is_ok() is False

    def test_unwrap_raises(self):
        result = Err("error")
        with pytest.raises(ValueError):
            result.unwrap()

    def test_unwrap_or_returns_default(self):
        result = Err("error")
        assert result.unwrap_or(42) == 42

    def test_map_propagates_error(self):
        result = Err("error").map(lambda x: x * 2)
        assert result.is_err()
        assert result.error == "error"
```

## Следующий шаг

После завершения Step 1 переходите к [Step 2: Domain Models](./02_domain_models.md).
