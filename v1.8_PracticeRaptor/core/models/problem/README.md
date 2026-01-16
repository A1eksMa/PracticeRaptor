# Problem — Домен задач

## Что здесь

**Problem-домен** — статический контент из банка задач.
Эти модели существуют независимо от пользователей.

```
problem/
├── localization.py   # LocalizedText — мультиязычный текст
├── example.py        # Example — пример с input/output
├── template.py       # ProblemTemplate, TestCase, CanonicalSolution
└── problem.py        # Problem, ProblemSummary
```

## Модели

### Problem

```python
@dataclass(frozen=True)
class Problem:
    """Полное описание задачи."""

    id: int
    title: LocalizedText           # {"en": "Two Sum", "ru": "Два числа"}
    description: LocalizedText     # Полное условие
    difficulty: Difficulty         # easy, medium, hard
    complexity: Complexity         # O(n), O(n²), ...
    categories: tuple[Category, ...]
    tags: tuple[str, ...]
    examples: tuple[Example, ...]  # Примеры с input/output
    hints: tuple[LocalizedText, ...]
    editorial: LocalizedText       # Разбор решения
```

### ProblemSummary

```python
@dataclass(frozen=True)
class ProblemSummary:
    """Лёгкая версия для списка задач."""

    id: int
    title: LocalizedText
    difficulty: Difficulty
    complexity: Complexity
    categories: tuple[Category, ...]
    tags: tuple[str, ...]
    status: ProblemStatus          # not_started, in_progress, solved
```

### ProblemTemplate

```python
@dataclass(frozen=True)
class ProblemTemplate:
    """Всё для решения задачи на конкретном языке."""

    problem_id: int
    language: ProgrammingLanguage  # python3, java, ...
    signature: str                 # "def two_sum(nums, target):"
    test_cases: tuple[TestCase, ...]
    canonical_solutions: tuple[CanonicalSolution, ...]
```

**Ключевое отличие от v1.7:**
- В v1.7 `Solution` содержала и шаблон, и код пользователя
- В v1.8 `ProblemTemplate` — чистый шаблон, без кода пользователя

## Аналогия: Библиотека задач

```
┌─────────────────────────────────────────────────────────────────┐
│                         БИБЛИОТЕКА                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │      Problem        │    │    ProblemTemplate   │            │
│  │  ─────────────────  │    │  ─────────────────   │            │
│  │  • Условие          │    │  • Сигнатура (Python)│            │
│  │  • Примеры          │    │  • Тесты (Python)    │            │
│  │  • Подсказки        │    │  • Эталонные решения │            │
│  │  • Разбор           │    │                      │            │
│  └─────────────────────┘    ├──────────────────────┤            │
│                             │  • Сигнатура (Java)  │            │
│                             │  • Тесты (Java)      │            │
│                             │  • Эталонные решения │            │
│                             └──────────────────────┘            │
│                                                                  │
│  Один Problem → несколько ProblemTemplate (по языкам)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## LocalizedText

```python
@dataclass(frozen=True)
class LocalizedText:
    """Мультиязычный текст с fallback."""

    translations: dict[str, str]   # {"en": "...", "ru": "..."}

    def get(self, locale: str = "en", fallback: str = "en") -> str:
        """Получить текст с fallback на английский."""
```

### Пример

```python
title = LocalizedText({"en": "Two Sum", "ru": "Два числа"})

title.get("ru")       # "Два числа"
title.get("de")       # "Two Sum" (fallback to en)
title.get("de", "ru") # "Два числа" (custom fallback)

str(title)            # "Two Sum" (default = en)
bool(title)           # True (есть переводы)
```

### Удобный конструктор

```python
from core.models.problem import text

title = text("Two Sum", "Два числа")  # en + ru
title = text("Two Sum")               # только en
```

## TestCase и CanonicalSolution

### TestCase (Value Object)

```python
@dataclass(frozen=True)
class TestCase:
    test: str              # "assert two_sum([2,7], 9) == [0,1]"
    is_example: bool       # True = показывать в условии
```

### CanonicalSolution (Value Object)

```python
@dataclass(frozen=True)
class CanonicalSolution:
    name: str              # "Hash Map (One Pass)"
    complexity: Complexity # O(n)
    code: str              # "def two_sum(nums, target): ..."
```

## Примеры использования

### Создание Problem

```python
from core.models import (
    Problem, ProblemTemplate, Example, TestCase, CanonicalSolution,
    LocalizedText, Difficulty, Complexity, Category, ProgrammingLanguage,
)
from core.models.problem import text

problem = Problem(
    id=1,
    title=text("Two Sum", "Два числа"),
    description=text(
        "Given an array of integers...",
        "Дан массив целых чисел...",
    ),
    difficulty=Difficulty.EASY,
    complexity=Complexity.O_N,
    categories=(Category.ARRAY, Category.HASH_TABLE),
    tags=("array", "hash-table"),
    examples=(
        Example(
            input="nums = [2, 7, 11, 15], target = 9",
            output="[0, 1]",
            explanation=text(
                "nums[0] + nums[1] = 2 + 7 = 9",
                "nums[0] + nums[1] = 2 + 7 = 9",
            ),
        ),
    ),
    hints=(
        text("Think about using a hash map", "Подумайте об использовании хэш-таблицы"),
    ),
)
```

### Создание ProblemTemplate

```python
template = ProblemTemplate(
    problem_id=1,
    language=ProgrammingLanguage.PYTHON,
    signature="def two_sum(nums: list[int], target: int) -> list[int]:",
    test_cases=(
        TestCase(test="assert two_sum([2,7,11,15], 9) == [0,1]", is_example=True),
        TestCase(test="assert two_sum([3,2,4], 6) == [1,2]", is_example=True),
        TestCase(test="assert two_sum([3,3], 6) == [0,1]", is_example=False),  # hidden
    ),
    canonical_solutions=(
        CanonicalSolution(
            name="Hash Map (One Pass)",
            complexity=Complexity.O_N,
            code="def two_sum(nums, target):\n    seen = {}\n    ...",
        ),
    ),
)
```

### Работа с ProblemTemplate

```python
# Получить только example тесты (для быстрой проверки)
examples = template.example_tests
# → (TestCase("assert two_sum([2,7,11,15], 9) == [0,1]", True), ...)

# Получить все тесты (для полной проверки)
all_tests = template.test_cases

# Получить тесты как строки (для executor)
test_strings = template.get_test_strings(examples_only=True)
# → ("assert two_sum([2,7,11,15], 9) == [0,1]", ...)
```

## Тестирование

```python
def test_problem_localization():
    problem = Problem(
        id=1,
        title=text("Test", "Тест"),
        description=text("Description", "Описание"),
        difficulty=Difficulty.EASY,
    )

    assert problem.get_title("ru") == "Тест"
    assert problem.get_title("de") == "Test"  # fallback
    assert problem.get_description("ru") == "Описание"

def test_template_example_tests():
    template = ProblemTemplate(
        problem_id=1,
        language=ProgrammingLanguage.PYTHON,
        signature="def f(): pass",
        test_cases=(
            TestCase("assert f() == 1", is_example=True),
            TestCase("assert f() == 2", is_example=False),
        ),
    )

    assert len(template.example_tests) == 1
    assert len(template.hidden_tests) == 1
    assert template.test_count == 2
```
