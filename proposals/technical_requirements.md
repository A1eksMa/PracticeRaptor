# PracticeRaptor: Технические требования

## 1. Архитектурные принципы

### 1.1. Hexagonal Architecture (Ports & Adapters)

Система построена на принципе разделения ядра от внешних зависимостей:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS LAYER                                   │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│      CLI        │  Telegram Bot   │    Web App      │       Widget          │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬───────────┘
         │                 │                 │                    │
         └─────────────────┴────────┬────────┴────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                           FastAPI Gateway                                    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CORE LAYER                                      │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  DOMAIN: Models (frozen), Enums, Errors, Result[T, E]                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  PORTS: Protocols (IProblemRepository, ICodeExecutor, IAuthProvider)  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  SERVICES: Pure functions (validate, filter, calculate, transform)   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  USE CASES: Orchestration (side effects at boundaries)               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────────┐
│ STORAGE ADAPTERS│    │ EXECUTOR ADAPTERS   │    │    AUTH ADAPTERS        │
│ JSON │ SQLite   │    │ Local │ Docker      │    │ Anonymous │ Token       │
│ PostgreSQL      │    │ Remote API          │    │ OAuth                   │
└─────────────────┘    └─────────────────────┘    └─────────────────────────┘
```

### 1.2. Функциональный стиль

| Принцип | Реализация |
|---------|------------|
| Immutable data | `@dataclass(frozen=True)` для всех моделей |
| Pure functions | Services без side effects |
| Composition | Функции как строительные блоки |
| Result type | `Ok[T] \| Err[E]` вместо exceptions |
| Side effects | Только на границах (adapters) |

### 1.3. Dependency Injection

- Ручная реализация (без библиотек)
- Container как frozen dataclass
- Factory functions для создания зависимостей
- Конфигурация через YAML

### 1.4. Интерфейсы через Protocol

```python
from typing import Protocol

class IProblemRepository(Protocol):
    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]: ...
    def get_all(self, filters: ProblemFilters) -> tuple[Problem, ...]: ...
```

- Структурная типизация (duck typing)
- Не требует явного наследования
- Совместимость проверяется статически (mypy)

---

## 2. Структура проекта

```
practiceraptor/
│
├── core/                           # Ядро (без внешних зависимостей)
│   ├── domain/
│   │   ├── models.py               # Problem, User, Submission, Draft, Progress
│   │   ├── enums.py                # Difficulty, Language, Status
│   │   ├── errors.py               # Типизированные ошибки
│   │   └── result.py               # Result[T, E] = Ok[T] | Err[E]
│   │
│   ├── ports/                      # Интерфейсы (Protocols)
│   │   ├── repositories.py         # IProblemRepository, IUserRepository, ...
│   │   ├── executors.py            # ICodeExecutor
│   │   └── auth.py                 # IAuthProvider
│   │
│   ├── services/                   # Чистые функции
│   │   ├── problems.py             # get_problem, filter_problems
│   │   ├── execution.py            # validate_code, run_tests
│   │   ├── progress.py             # calculate_stats, update_progress
│   │   └── drafts.py               # save_draft, load_draft
│   │
│   └── use_cases/                  # Композиция (orchestration)
│       ├── solve_problem.py
│       ├── submit_solution.py
│       └── get_user_stats.py
│
├── adapters/                       # Реализации портов
│   ├── storage/
│   │   ├── json_repository.py      # JSON файлы
│   │   ├── sqlite_repository.py    # SQLite
│   │   └── postgres_repository.py  # PostgreSQL
│   │
│   ├── executors/
│   │   ├── local_executor.py       # multiprocessing sandbox
│   │   ├── docker_executor.py      # Docker контейнеры
│   │   └── remote_executor.py      # HTTP API
│   │
│   └── auth/
│       ├── anonymous_auth.py       # CLI (без авторизации)
│       ├── telegram_auth.py        # Telegram ID
│       └── token_auth.py           # JWT (Web/Widget)
│
├── di/                             # Dependency Injection
│   ├── container.py                # Container dataclass
│   ├── providers.py                # Factory functions
│   └── config.py                   # Загрузка конфигурации
│
├── clients/                        # Интерфейсы пользователя
│   ├── cli/
│   │   ├── main.py
│   │   ├── commands/
│   │   ├── presenter.py
│   │   └── editor.py
│   │
│   ├── api/                        # REST API (FastAPI)
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── dependencies.py
│   │
│   ├── telegram/
│   │   ├── main.py
│   │   ├── handlers/
│   │   ├── keyboards/
│   │   └── states/
│   │
│   └── web/
│       ├── main.py
│       ├── templates/
│       └── static/
│
├── tests/                          # Тесты (см. раздел 6)
│
├── data/                           # Данные (для JSON storage)
│   ├── problems/
│   ├── users/
│   ├── submissions/
│   └── drafts/
│
├── docker/                         # Docker конфигурации
│   ├── Dockerfile.test
│   ├── Dockerfile.cli
│   ├── Dockerfile.api
│   └── docker-compose.yml
│
├── config/                         # Конфигурационные файлы
│   ├── config.example.yaml
│   └── config.test.yaml
│
└── scripts/                        # Утилиты
    ├── migrate.py
    └── seed.py
```

---

## 3. Ключевые паттерны

### 3.1. Result Type

```python
# core/domain/result.py
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, fn: Callable[[T], U]) -> 'Ok[U]':
        return Ok(fn(self.value))

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        return fn(self.value)

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, fn: Callable) -> 'Err[E]':
        return self

    def flat_map(self, fn: Callable) -> 'Err[E]':
        return self

    def unwrap(self) -> None:
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        return default

Result = Ok[T] | Err[E]
```

### 3.2. Immutable Models

```python
# core/domain/models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Problem:
    id: int
    title: dict[str, str]           # i18n: {"en": "...", "ru": "..."}
    description: dict[str, str]     # i18n
    difficulty: Difficulty
    tags: tuple[str, ...]           # Immutable collection
    examples: tuple[Example, ...]
    test_cases: tuple[TestCase, ...]
    languages: tuple[LanguageSpec, ...]

@dataclass(frozen=True)
class Submission:
    id: str
    user_id: str
    problem_id: int
    code: str
    language: Language
    execution_time_ms: int
    memory_used_kb: int
    created_at: datetime

@dataclass(frozen=True)
class Draft:
    user_id: str
    problem_id: int
    language: Language
    code: str
    updated_at: datetime
```

### 3.3. Dependency Injection Container

```python
# di/container.py
from dataclasses import dataclass
from core.ports.repositories import IProblemRepository, IUserRepository
from core.ports.executors import ICodeExecutor
from core.ports.auth import IAuthProvider

@dataclass(frozen=True)
class Container:
    problem_repo: IProblemRepository
    user_repo: IUserRepository
    submission_repo: ISubmissionRepository
    draft_repo: IDraftRepository
    executor: ICodeExecutor
    auth: IAuthProvider

# di/providers.py
def create_container(config: Config) -> Container:
    """Factory для создания контейнера на основе конфигурации"""

    # Storage
    problem_repo = _create_problem_repo(config.storage)
    user_repo = _create_user_repo(config.storage)
    submission_repo = _create_submission_repo(config.storage)
    draft_repo = _create_draft_repo(config.storage)

    # Executor
    executor = _create_executor(config.executor)

    # Auth
    auth = _create_auth(config.auth)

    return Container(
        problem_repo=problem_repo,
        user_repo=user_repo,
        submission_repo=submission_repo,
        draft_repo=draft_repo,
        executor=executor,
        auth=auth,
    )

def _create_problem_repo(storage_config: StorageConfig) -> IProblemRepository:
    match storage_config.type:
        case "json":
            from adapters.storage.json_repository import JsonProblemRepository
            return JsonProblemRepository(storage_config.json.path)
        case "sqlite":
            from adapters.storage.sqlite_repository import SqliteProblemRepository
            return SqliteProblemRepository(storage_config.sqlite.path)
        case "postgresql":
            from adapters.storage.postgres_repository import PostgresProblemRepository
            return PostgresProblemRepository(storage_config.postgresql)
```

---

## 4. Конфигурация

### 4.1. Формат конфигурации

```yaml
# config.yaml
app:
  name: PracticeRaptor
  environment: development  # development | staging | production
  default_language: en      # i18n default

storage:
  type: json  # json | sqlite | postgresql

  json:
    base_path: ./data

  sqlite:
    path: ./data/practiceraptor.db

  postgresql:
    host: localhost
    port: 5432
    database: practiceraptor
    user: ${DB_USER}
    password: ${DB_PASSWORD}

executor:
  type: local  # local | docker | remote
  timeout_sec: 5
  memory_limit_mb: 256

  docker:
    image: practiceraptor/executor:latest
    network: none

  remote:
    url: http://executor-service:8080
    api_key: ${EXECUTOR_API_KEY}

auth:
  type: anonymous  # anonymous | telegram | token

  token:
    secret: ${JWT_SECRET}
    expiration_hours: 24
```

### 4.2. Переменные окружения

```bash
# .env.example

# Database (for PostgreSQL)
DB_USER=practiceraptor
DB_PASSWORD=secure_password

# Executor (for remote)
EXECUTOR_API_KEY=your_api_key

# Auth (for token-based)
JWT_SECRET=your_jwt_secret

# Telegram (for bot)
TELEGRAM_BOT_TOKEN=your_bot_token
```

---

## 5. Переключаемые адаптеры

### 5.1. Storage Adapters

| Adapter | Когда использовать | Особенности |
|---------|-------------------|-------------|
| JSON | CLI, разработка | Файлы, нет зависимостей |
| SQLite | CLI с историей, тесты | Один файл, SQL |
| PostgreSQL | Production (TG, Web) | Масштабируемость, ACID |

### 5.2. Executor Adapters

| Adapter | Когда использовать | Особенности |
|---------|-------------------|-------------|
| Local | CLI, разработка | multiprocessing, быстрый |
| Docker | Production | Полная изоляция |
| Remote | Распределённая система | HTTP API, масштабируемость |

### 5.3. Auth Adapters

| Adapter | Когда использовать | Особенности |
|---------|-------------------|-------------|
| Anonymous | CLI | Локальный пользователь |
| Telegram | Telegram Bot | Telegram ID |
| Token | Web, Widget | JWT, OAuth |

---

## 6. Тестирование

### 6.1. Принципы

- **TDD** — тесты пишутся ДО кода
- **Изоляция** — все тесты запускаются в Docker
- **Покрытие** — минимум 80%, цель 90%
- **CI Gate** — merge блокируется при падении покрытия

### 6.2. Структура тестов

```
tests/
├── unit/                          # Быстрые, изолированные
│   ├── core/
│   │   ├── domain/
│   │   │   ├── test_models.py
│   │   │   └── test_result.py
│   │   ├── services/
│   │   │   ├── test_problems.py
│   │   │   ├── test_execution.py
│   │   │   └── test_progress.py
│   │   └── use_cases/
│   │       └── test_submit_solution.py
│   │
│   └── adapters/
│       ├── storage/
│       │   ├── test_json_repository.py
│       │   └── test_sqlite_repository.py
│       └── executors/
│           └── test_local_executor.py
│
├── integration/                   # Взаимодействие компонентов
│   ├── test_solve_problem_flow.py
│   ├── test_user_progress_flow.py
│   └── test_storage_migration.py
│
├── e2e/                           # End-to-end
│   ├── test_cli_workflow.py
│   └── test_api_workflow.py
│
├── fixtures/                      # Тестовые данные
│   ├── problems.py
│   ├── users.py
│   └── factories.py
│
├── conftest.py                    # Общие fixtures
└── pytest.ini
```

### 6.3. Docker-окружение для тестов

```dockerfile
# docker/Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .

CMD ["pytest", "--cov=practiceraptor", "--cov-report=term-missing", "--cov-fail-under=80"]
```

```yaml
# docker/docker-compose.test.yml
version: '3.8'

services:
  test:
    build:
      context: ..
      dockerfile: docker/Dockerfile.test
    environment:
      - PYTHONPATH=/app
      - CONFIG_PATH=/app/config/config.test.yaml
    volumes:
      - ../tests:/app/tests:ro
      - test-results:/app/results

  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: test_practiceraptor
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test

volumes:
  test-results:
```

### 6.4. CI Pipeline

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run tests in Docker
        run: |
          docker-compose -f docker/docker-compose.test.yml up \
            --build \
            --abort-on-container-exit \
            --exit-code-from test

      - name: Check coverage
        run: |
          # Fail if coverage dropped compared to main branch
          # (реализация зависит от инструмента)
```

### 6.5. Пример теста

```python
# tests/unit/core/services/test_execution.py
import pytest
from core.domain.result import Ok, Err
from core.domain.models import TestCase
from core.services.execution import validate_code, run_single_test

class TestValidateCode:
    def test_empty_code_returns_error(self):
        result = validate_code("")

        assert result.is_err()
        assert "empty" in result.error.message.lower()

    def test_valid_code_returns_ok(self):
        code = "def solution(x): return x * 2"
        result = validate_code(code)

        assert result.is_ok()
        assert result.value == code

    def test_syntax_error_returns_error(self):
        code = "def solution(x) return x"  # Missing colon
        result = validate_code(code)

        assert result.is_err()
        assert "syntax" in result.error.message.lower()

class TestRunSingleTest:
    def test_correct_solution_passes(self):
        code = "def solution(x): return x * 2"
        test_case = TestCase(
            input={"x": 5},
            expected=10,
        )

        result = run_single_test(code, test_case, timeout=5)

        assert result.is_ok()
        assert result.value.passed is True

    def test_wrong_answer_fails(self):
        code = "def solution(x): return x + 2"
        test_case = TestCase(
            input={"x": 5},
            expected=10,
        )

        result = run_single_test(code, test_case, timeout=5)

        assert result.is_ok()
        assert result.value.passed is False
        assert result.value.actual == 7
```

---

## 7. Технологический стек

### 7.1. Core

| Компонент | Технология | Версия |
|-----------|------------|--------|
| Язык | Python | 3.11+ |
| Типизация | mypy | latest |
| Линтер | ruff | latest |
| Форматтер | ruff format | latest |

### 7.2. Clients

| Клиент | Технология |
|--------|------------|
| CLI | typer или click |
| API | FastAPI |
| Telegram | aiogram 3.x |
| Web | FastAPI + Jinja2 / HTMX |

### 7.3. Storage

| Хранилище | Технология |
|-----------|------------|
| JSON | stdlib (json, pathlib) |
| SQLite | aiosqlite + SQLAlchemy |
| PostgreSQL | asyncpg + SQLAlchemy |

### 7.4. Testing

| Компонент | Технология |
|-----------|------------|
| Framework | pytest |
| Coverage | pytest-cov |
| Fixtures | pytest + factory_boy |
| Async | pytest-asyncio |

### 7.5. Infrastructure

| Компонент | Технология |
|-----------|------------|
| Контейнеризация | Docker |
| Оркестрация | Docker Compose |
| CI/CD | GitHub Actions |

---

## 8. Требования к окружению

### 8.1. Development

| Параметр | Значение |
|----------|----------|
| Python | 3.11+ |
| Docker | 24+ |
| Docker Compose | v2 |
| OS | Linux / macOS / WSL2 |

### 8.2. Production (см. roadmap для конкретных этапов)

Минимальные требования зависят от этапа:
- Stage 1.x: 1 vCPU, 1 GB RAM
- Stage 2+: 2+ vCPU, 2+ GB RAM

---

## 9. Безопасность

### 9.1. Выполнение кода

- Изоляция: Docker контейнеры или multiprocessing sandbox
- Лимиты: CPU, память, время выполнения
- Сеть: отключена в sandbox
- Файловая система: read-only (кроме /tmp)
- Whitelist: только разрешённые модули

### 9.2. Данные

- Минимальный сбор данных
- Секреты в переменных окружения
- Шифрование чувствительных данных
- HTTPS для всех внешних соединений

### 9.3. API

- Rate limiting
- Валидация входных данных (Pydantic)
- CORS политика
- Authentication/Authorization

---

## 10. Мониторинг и логирование

### 10.1. Логирование

- Структурированные логи (JSON)
- Уровни: DEBUG, INFO, WARNING, ERROR
- Контекст: request_id, user_id, problem_id

### 10.2. Метрики (для Production)

- Количество submissions
- Время выполнения
- Процент успешных решений
- API latency
- Ошибки и exceptions

### 10.3. Health Checks

```
GET /health          # Общий статус
GET /health/storage  # Статус хранилища
GET /health/executor # Статус executor
```
