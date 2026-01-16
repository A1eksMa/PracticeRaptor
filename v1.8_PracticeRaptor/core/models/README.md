# Models — Доменные модели

## Что здесь

**Models** — богатые объекты для бизнес-логики.

```
models/
├── enums.py           # Перечисления (Difficulty, Category, ...)
├── result.py          # Result[T, E] = Ok[T] | Err[E]
├── errors.py          # Типизированные ошибки
│
├── problem/           # Problem-домен (статический контент)
│   ├── localization.py
│   ├── example.py
│   ├── template.py
│   └── problem.py
│
├── user/              # User-домен (динамический контент)
│   ├── user.py
│   ├── settings.py
│   ├── draft.py
│   └── submission.py
│
└── context/           # Рабочий контекст
    └── work_context.py
```

## Два домена

### Проблема: Solution смешивала два контекста

```python
# Было в v1.7 — Solution это и шаблон, и работа пользователя
class Solution:
    problem_id: int
    signature: Signature           # ← часть Problem (шаблон)
    test_cases: tuple[TestCase]    # ← часть Problem (шаблон)
    code: str                      # ← часть User (работа пользователя)
```

### Решение: разделение на домены

```
PROBLEM-ДОМЕН                    USER-ДОМЕН
(существует без пользователя)   (создаётся пользователем)
─────────────────────────────   ─────────────────────────────
Problem                          User
ProblemTemplate                  Settings
├── signature                    Draft
├── test_cases                   ├── user
└── canonical_solutions          ├── problem      ← ссылка
                                 ├── template     ← ссылка
                                 └── code         ← работа пользователя
```

## Характеристики моделей

### Immutable (frozen)

```python
@dataclass(frozen=True)
class Problem:
    id: int
    title: LocalizedText
    ...
```

- Все модели `frozen=True`
- Изменение через `replace()`:
  ```python
  new_draft = draft.with_code("new code")
  ```

### Богатые (nested objects)

```python
# Draft содержит полные вложенные объекты
@dataclass(frozen=True)
class Draft:
    user: User                    # полный объект
    problem: Problem              # полный объект
    template: ProblemTemplate     # полный объект
    code: str
```

Это удобно для бизнес-логики:
```python
draft.problem.title.get("ru")    # прямой доступ
draft.template.test_cases        # без дополнительных запросов
```

### Value Objects vs Entities

| Тип | Характеристика | Примеры |
|-----|----------------|---------|
| **Value Object** | Нет ID, встраивается | `LocalizedText`, `Example`, `TestCase` |
| **Entity** | Есть ID, хранится отдельно | `Problem`, `User`, `Submission` |

## Иерархия импортов

```
enums.py, result.py, errors.py   ← базовые, ничего не импортируют
         ↓
problem/                          ← импортирует только enums
         ↓
user/                             ← импортирует enums и problem
         ↓
context/                          ← импортирует всё выше
```

## Аналогия: Строительство дома

| Модуль | Аналогия | Что содержит |
|--------|----------|--------------|
| `enums.py` | Справочники | Типы материалов, категории работ |
| `problem/` | Проект дома | Чертежи, спецификации, примеры |
| `user/` | Строительство | Кто строит, что построено, черновики |
| `context/` | Стройплощадка | Всё вместе: проект + бригада + материалы |

## Примеры использования

### Создание объектов

```python
from core.models import (
    Problem, ProblemTemplate, LocalizedText,
    User, Settings, Draft,
    Difficulty, ProgrammingLanguage,
)

# Problem-домен
problem = Problem(
    id=1,
    title=LocalizedText({"en": "Two Sum", "ru": "Два числа"}),
    description=LocalizedText({"en": "Given an array..."}),
    difficulty=Difficulty.EASY,
)

template = ProblemTemplate(
    problem_id=1,
    language=ProgrammingLanguage.PYTHON,
    signature="def two_sum(nums: list[int], target: int) -> list[int]:",
    test_cases=(...),
)

# User-домен
user = User(user_id=1, user_name="john")
settings = Settings(user_id=1, programming_language=ProgrammingLanguage.PYTHON)

draft = Draft(
    draft_id=1,
    user=user,
    problem=problem,
    template=template,
    code="def two_sum(nums, target): pass",
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
```

### Работа с объектами

```python
# Локализация
title_ru = problem.title.get("ru")        # "Два числа"
title_de = problem.title.get("de")        # "Two Sum" (fallback)

# Навигация по вложенным объектам
user_name = draft.user.user_name          # "john"
difficulty = draft.problem.difficulty     # Difficulty.EASY
signature = draft.template.signature      # "def two_sum(...)"

# Иммутабельные обновления
new_draft = draft.with_code("def two_sum(nums, target): return []")
assert draft.code != new_draft.code       # старый объект не изменился
```

## Публичный API

Всё экспортируется через `core.models`:

```python
from core.models import (
    # Result
    Ok, Err, Result,
    # Errors
    DomainError, NotFoundError, ValidationError,
    # Enums
    Difficulty, Category, ExecutionStatus, ProgrammingLanguage,
    # Problem-домен
    Problem, ProblemSummary, ProblemTemplate, LocalizedText, Example,
    # User-домен
    User, Settings, Draft, Submission, TestResult,
    # Context
    WorkContext,
)
```

## Тестирование

Модели тестируются без I/O:

```python
def test_problem_localization():
    problem = Problem(
        id=1,
        title=LocalizedText({"en": "Test", "ru": "Тест"}),
        ...
    )

    assert problem.get_title("ru") == "Тест"
    assert problem.get_title("de") == "Test"  # fallback

def test_draft_immutability():
    draft = create_draft(1, user, problem, template, "code1")
    new_draft = draft.with_code("code2")

    assert draft.code == "code1"      # старый не изменился
    assert new_draft.code == "code2"  # новый с изменением
```
