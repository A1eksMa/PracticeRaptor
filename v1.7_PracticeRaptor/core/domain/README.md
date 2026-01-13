# Domain — Доменные модели

## Что здесь

**Domain Models** — это богатые объекты для работы в коде.

```
domain/
├── enums.py         # Перечисления (Difficulty, Language, Category)
├── localization.py  # LocalizedText — мультиязычный текст
├── problem.py       # Problem, ProblemSummary, Example
└── solution.py      # Solution, Signature, TestCase, CanonicalSolution
```

## Ключевой принцип

**Вложенность вместо ID-ссылок.**

### Плохо (как в SQL):
```python
class Title:
    problem_id: int       # ← ссылка
    language: str
    title: str

# Использование — неудобно:
title = get_title(problem.id, "ru")
```

### Хорошо (Domain Model):
```python
class Problem:
    title: LocalizedText  # ← вложенность

# Использование — удобно:
problem.title.get("ru")
```

## Аналогия: Заказ в ресторане

**SQL-стиль (нормализовано):**
```
Заказ #42 → ссылка на клиента #7
         → ссылка на блюдо #15
         → ссылка на блюдо #23
```
Чтобы узнать, что заказал клиент, нужно 4 запроса.

**Domain-стиль (вложенность):**
```
Заказ {
    клиент: { имя: "Иван", телефон: "..." }
    блюда: [
        { название: "Борщ", цена: 350 },
        { название: "Котлета", цена: 450 }
    ]
}
```
Всё в одном объекте — удобно работать.

## Модели

### LocalizedText
```python
@dataclass(frozen=True)
class LocalizedText:
    translations: dict[str, str]  # {"en": "Hello", "ru": "Привет"}

    def get(self, locale: str, fallback: str = "en") -> str:
        return self.translations.get(locale, self.translations.get(fallback, ""))
```

**Зачем:** Хранить переводы внутри объекта, а не в отдельных записях.

### Problem
```python
@dataclass(frozen=True)
class Problem:
    id: int
    title: LocalizedText           # ← вложенный LocalizedText
    description: LocalizedText
    difficulty: Difficulty         # ← Enum, не строка
    examples: tuple[Example, ...]  # ← вложенные объекты
    hints: tuple[LocalizedText, ...]
    ...
```

**Зачем:** Один объект содержит всё необходимое для отображения задачи.

### ProblemSummary
```python
@dataclass(frozen=True)
class ProblemSummary:
    id: int
    title: str              # ← уже на нужном языке!
    difficulty: Difficulty
    tags: tuple[str, ...]
    status: ProblemStatus
```

**Зачем:** Лёгкая версия для списка задач. Не грузим descriptions, examples, hints.

### Solution
```python
@dataclass(frozen=True)
class Solution:
    problem_id: int
    language: ProgrammingLanguage
    signature: Signature              # ← вложенный
    test_cases: tuple[TestCase, ...]  # ← вложенные
    canonical_solutions: tuple[CanonicalSolution, ...]
    code: str                         # ← код пользователя
```

**Зачем:** Рабочий контекст для решения задачи — всё под рукой.

## Характеристики

| Свойство | Значение | Зачем |
|----------|----------|-------|
| `frozen=True` | Иммутабельность | Безопасность, предсказуемость |
| Вложенность | Объекты внутри объектов | Удобство работы |
| `tuple` вместо `list` | Неизменяемые коллекции | Согласованность с frozen |
| `Enum` | Типизированные значения | Автодополнение, проверка типов |

## Примеры использования

```python
# Создание
problem = Problem(
    id=1,
    title=LocalizedText({"en": "Two Sum", "ru": "Два числа"}),
    description=LocalizedText({"en": "Given an array..."}),
    difficulty=Difficulty.EASY,
    examples=(
        Example(
            input="nums = [2, 7], target = 9",
            output="[0, 1]",
            explanation=LocalizedText({"en": "Because 2 + 7 = 9"})
        ),
    ),
    ...
)

# Использование
print(problem.title.get("ru"))              # "Два числа"
print(problem.difficulty.value)              # "easy"
print(problem.examples[0].explanation.get("en"))  # "Because 2 + 7 = 9"

# Проверка
if problem.difficulty == Difficulty.EASY:
    print("Лёгкая задача")
```

## Связь с Persistence

Domain Models **не знают** о хранении. Они не содержат `problem_id` для связей — вместо этого используют вложенность.

Преобразование Domain ↔ Records происходит в `persistence/mappers/`.
