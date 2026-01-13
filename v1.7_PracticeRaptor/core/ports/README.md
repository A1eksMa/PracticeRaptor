# Ports — Интерфейсы

## Что здесь

**Ports** — это интерфейсы (контракты), которые определяют, ЧТО нужно, но не КАК.

```
ports/
└── repositories.py   # IProblemRepository, ISolutionRepository, ...
```

## Зачем нужны интерфейсы?

### Проблема: жёсткая связь

```python
# Плохо — сервис знает о конкретной реализации
from adapters.storage.json import JsonProblemRepository

def get_problem_title(problem_id: int) -> str:
    repo = JsonProblemRepository(Path("data/json"))  # ← жёстко привязан
    problem = repo.get_by_id(problem_id)
    return problem.title.get("en")
```

Если захотим SQLite — придётся менять код сервиса.

### Решение: зависимость от интерфейса

```python
# Хорошо — сервис зависит от интерфейса
from core.ports import IProblemRepository

def get_problem_title(repo: IProblemRepository, problem_id: int) -> str:
    problem = repo.get_by_id(problem_id)  # ← работает с любой реализацией
    return problem.title.get("en")

# Можно передать любую реализацию
json_repo = JsonProblemRepository(...)
sqlite_repo = SqliteProblemRepository(...)

get_problem_title(json_repo, 1)    # работает
get_problem_title(sqlite_repo, 1)  # тоже работает
```

## Аналогия: Розетка

**Интерфейс** — это стандарт розетки (Type C, евророзетка).

```
┌─────────────────────┐
│   IProblemRepository │  ← Стандарт розетки
│   ─────────────────  │
│   get_by_id()       │
│   get_all_summaries()│
│   count()           │
└─────────────────────┘
        │
        │ реализуют
        ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ JsonProblem   │  │ SqliteProblem │  │ PostgresProblem│
│ Repository    │  │ Repository    │  │ Repository    │
└───────────────┘  └───────────────┘  └───────────────┘
   (JSON файлы)      (SQLite)          (PostgreSQL)
```

Приборы (сервисы) не знают, откуда берётся электричество (данные).
Они знают только стандарт подключения (интерфейс).

## Protocol vs ABC

В Python есть два способа определить интерфейс:

### ABC (Abstract Base Class) — явное наследование
```python
from abc import ABC, abstractmethod

class IProblemRepository(ABC):
    @abstractmethod
    def get_by_id(self, problem_id: int) -> Problem | None:
        pass

class JsonProblemRepository(IProblemRepository):  # ← явно наследует
    def get_by_id(self, problem_id: int) -> Problem | None:
        ...
```

### Protocol — структурная типизация (duck typing)
```python
from typing import Protocol

class IProblemRepository(Protocol):
    def get_by_id(self, problem_id: int) -> Problem | None: ...

class JsonProblemRepository:  # ← НЕ наследует, но соответствует
    def get_by_id(self, problem_id: int) -> Problem | None:
        ...
```

**Мы используем Protocol**, потому что:
- Не нужно явно наследовать
- Проверка совместимости — статическая (mypy)
- Более "питонический" подход (duck typing)

## Интерфейс IProblemRepository

```python
class IProblemRepository(Protocol):
    """Интерфейс репозитория задач."""

    def get_by_id(self, problem_id: int, locale: str = "en") -> Problem | None:
        """Получить полную задачу по ID."""
        ...

    def get_all_summaries(
        self,
        locale: str = "en",
        difficulty: Difficulty | None = None,
        category: Category | None = None,
        tag: str | None = None,
    ) -> list[ProblemSummary]:
        """Получить список задач для отображения."""
        ...

    def get_problem_ids(self) -> list[int]:
        """Получить все ID задач."""
        ...

    def count(self) -> int:
        """Количество задач."""
        ...
```

## Dependency Injection

Интерфейсы позволяют **внедрять зависимости**:

```python
# di/container.py
@dataclass
class Container:
    problem_repo: IProblemRepository
    solution_repo: ISolutionRepository
    ...

# di/providers.py
def create_container(config: Config) -> Container:
    if config.storage.type == "json":
        problem_repo = JsonProblemRepository(config.storage.json.path)
    elif config.storage.type == "sqlite":
        problem_repo = SqliteProblemRepository(config.storage.sqlite.path)
    else:
        raise ValueError(f"Unknown storage type: {config.storage.type}")

    return Container(problem_repo=problem_repo, ...)

# Использование
container = create_container(config)
problem = container.problem_repo.get_by_id(1)
```

Смена хранилища — это изменение **одной строки** в конфиге:

```yaml
storage:
  type: sqlite  # было: json
```

## Тестирование

Интерфейсы упрощают тестирование — можно создать **mock**:

```python
class MockProblemRepository:
    """Фейковый репозиторий для тестов."""

    def __init__(self, problems: list[Problem]):
        self.problems = {p.id: p for p in problems}

    def get_by_id(self, problem_id: int, locale: str = "en") -> Problem | None:
        return self.problems.get(problem_id)

    def count(self) -> int:
        return len(self.problems)

# В тесте
def test_some_service():
    mock_repo = MockProblemRepository([
        Problem(id=1, title=LocalizedText({"en": "Test"}), ...)
    ])

    result = some_service(mock_repo)

    assert result == expected
```

Не нужны файлы, база данных, или сложная настройка.
