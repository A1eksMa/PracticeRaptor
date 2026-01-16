# DTO — Data Transfer Objects

## Что здесь

**DTO** — объекты для передачи данных между сервисами.

```
dto/
└── execution.py   # ExecutionRequest, ExecutionResult, TestResultDTO
```

## Зачем нужен этот слой?

### Проблема: Domain Models слишком богатые для API

```python
# Domain Model — богатый объект
@dataclass(frozen=True)
class Draft:
    user: User                    # вложенный объект
    problem: Problem              # вложенный объект
    template: ProblemTemplate     # вложенный объект
    code: str
```

Передавать такой объект через HTTP API:
- Избыточно (executor'у не нужен Problem целиком)
- Сложно сериализовать (datetime, Enum, вложенные объекты)
- Раскрывает внутреннюю структуру

### Решение: DTO — плоские объекты для API

```python
# DTO — только нужные данные
@dataclass(frozen=True)
class ExecutionRequest:
    user_id: int           # примитив
    problem_id: int        # примитив
    language: str          # строка, не Enum
    code: str
    test_cases: tuple[str, ...]  # строки, не TestCase объекты
    timeout_sec: int
    memory_limit_mb: int
```

## Аналогия: Курьерская доставка

```
┌─────────────────┐                    ┌─────────────────┐
│   ОТПРАВИТЕЛЬ   │                    │   ПОЛУЧАТЕЛЬ    │
│   (Core)        │                    │   (Executor)    │
│                 │                    │                 │
│  WorkContext    │                    │  Нужно только:  │
│  ├── user       │                    │  - код          │
│  ├── problem    │                    │  - тесты        │
│  ├── template   │    ┌─────────┐    │  - лимиты       │
│  └── draft      │───►│   DTO   │───►│                 │
│                 │    │ (посылка)│    │                 │
│  (всё богатство)│    └─────────┘    │                 │
│                 │                    │                 │
└─────────────────┘                    └─────────────────┘

DTO = только то, что нужно получателю, в удобном формате
```

## ExecutionRequest

```python
@dataclass(frozen=True)
class ExecutionRequest:
    """Запрос к executor-сервису."""

    user_id: int              # для авторизации и rate-limiting
    problem_id: int           # для логирования
    language: str             # "python3", "java"
    code: str                 # код пользователя
    test_cases: tuple[str, ...]  # ["assert f(1) == 2", ...]
    timeout_sec: int = 5
    memory_limit_mb: int = 256

    def to_dict(self) -> dict:
        """Для JSON сериализации."""
        return {...}
```

## ExecutionResult

```python
@dataclass(frozen=True)
class ExecutionResult:
    """Ответ от executor-сервиса."""

    status: str               # "accepted", "wrong_answer", ...
    test_results: tuple[TestResultDTO, ...]
    total_time_ms: int
    memory_used_kb: int
    error_message: str | None = None

    @property
    def is_accepted(self) -> bool:
        return self.status == "accepted"

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionResult":
        """Из JSON ответа."""
        ...
```

## TestResultDTO

```python
@dataclass(frozen=True)
class TestResultDTO:
    """Результат одного теста."""

    test_index: int
    status: str               # строка, не Enum
    time_ms: int = 0
    memory_kb: int = 0
    error: str | None = None
```

## Поток данных

```
┌─────────────────────────────────────────────────────────────────┐
│                           CORE                                   │
│                                                                  │
│  WorkContext ──► build_execution_request() ──► ExecutionRequest │
│       │                                              │          │
│       │                                              ▼          │
│       │                                    request.to_dict()    │
│       │                                              │          │
└───────┼──────────────────────────────────────────────┼──────────┘
        │                                              │
        │                                              ▼
        │                                    ┌─────────────────┐
        │                                    │   HTTP POST     │
        │                                    │   /execute      │
        │                                    │   {json body}   │
        │                                    └────────┬────────┘
        │                                             │
        │                                             ▼
        │                                    ┌─────────────────┐
        │                                    │    EXECUTOR     │
        │                                    │    SERVICE      │
        │                                    └────────┬────────┘
        │                                             │
        │                                             ▼
        │                                    ┌─────────────────┐
        │                                    │   HTTP 200 OK   │
        │                                    │   {json result} │
        │                                    └────────┬────────┘
        │                                             │
        │                                             ▼
┌───────┼─────────────────────────────────────────────┼───────────┐
│       │                                             │           │
│       │                           ExecutionResult.from_dict()   │
│       │                                             │           │
│       ▼                                             ▼           │
│  create_submission(context, result) ──────────► Submission      │
│                                                                  │
│                           CORE                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Примеры использования

### Создание запроса

```python
from core.dto import ExecutionRequest, build_execution_request

# Из WorkContext (рекомендуемый способ)
request = build_execution_request(
    context=context,
    code=user_code,
    examples_only=False,  # все тесты
    timeout_sec=5,
)

# Или напрямую
request = ExecutionRequest(
    user_id=1,
    problem_id=42,
    language="python3",
    code="def two_sum(nums, target): ...",
    test_cases=(
        "assert two_sum([2,7], 9) == [0,1]",
        "assert two_sum([3,2,4], 6) == [1,2]",
    ),
    timeout_sec=5,
    memory_limit_mb=256,
)
```

### Отправка запроса

```python
import httpx

# Сериализация в JSON
response = httpx.post(
    "http://executor-service/execute",
    json=request.to_dict(),
)

# Десериализация ответа
result = ExecutionResult.from_dict(response.json())
```

### Обработка результата

```python
if result.is_accepted:
    print(f"Solved in {result.total_time_ms}ms")
else:
    print(f"Failed: {result.status}")
    for tr in result.test_results:
        if not tr.passed:
            print(f"  Test {tr.test_index}: {tr.error}")
```

### Создание Submission из результата

```python
from core.models.user.submission import create_submission

# Конвертация DTO → Domain Model
submission = create_submission(
    submission_id=next_id,
    user=context.user,
    problem=context.problem,
    template=context.template,
    code=user_code,
    result=ExecutionStatus(result.status),
    total_time_ms=result.total_time_ms,
    memory_used_kb=result.memory_used_kb,
    test_results=tuple(
        TestResult(
            test_index=tr.test_index,
            status=ExecutionStatus(tr.status),
            time_ms=tr.time_ms,
            memory_kb=tr.memory_kb,
            error_message=tr.error,
        )
        for tr in result.test_results
    ),
    error_message=result.error_message,
)

# Теперь submission — богатая Domain Model
repo.save(submission)
```

## Отличия от Domain Models

| Аспект | Domain Model | DTO |
|--------|--------------|-----|
| Цель | Бизнес-логика | Передача данных |
| Типы | `Enum`, `datetime`, вложенные | `str`, `int`, примитивы |
| Связи | Вложенные объекты | ID или строки |
| Поведение | Методы, свойства | Только данные |
| Сериализация | Требует маппинг | `to_dict()` / `from_dict()` |

## Тестирование

```python
def test_build_execution_request():
    context = WorkContext(
        user=User(user_id=1),
        settings=Settings(user_id=1),
        problem=problem,
        template=template,
    )

    request = build_execution_request(context, "def f(): pass")

    assert request.user_id == 1
    assert request.problem_id == problem.id
    assert request.language == "python3"
    assert len(request.test_cases) == len(template.test_cases)

def test_execution_result_from_dict():
    data = {
        "status": "accepted",
        "test_results": [
            {"test_index": 0, "status": "accepted", "time_ms": 10},
        ],
        "total_time_ms": 45,
        "memory_used_kb": 2048,
    }

    result = ExecutionResult.from_dict(data)

    assert result.is_accepted
    assert result.total_time_ms == 45
    assert len(result.test_results) == 1
```
