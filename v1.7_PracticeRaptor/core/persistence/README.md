# Persistence — Слой хранения

## Что здесь

**Persistence** — промежуточный слой между Domain и Storage.

```
persistence/
├── records/           # Плоские структуры для хранения
│   ├── problem_records.py
│   └── solution_records.py
│
└── mappers/           # Преобразование Domain ↔ Records
    ├── problem_mapper.py
    └── solution_mapper.py
```

## Зачем нужен этот слой?

### Проблема: разные нужды

| Domain Models | Storage (JSON/SQL) |
|---------------|-------------------|
| Вложенность (`problem.title.get("ru")`) | Плоские таблицы |
| `datetime`, `Enum` | Строки, числа |
| Удобство в коде | Удобство хранения |

### Решение: промежуточный формат

```
Domain Model  ←→  Record  ←→  Storage
   Problem         ProblemRecord    JSON/SQLite
                   TitleRecord
                   ExampleRecord
```

**Record** — это "общий знаменатель", который:
- Легко сериализовать в JSON (`dataclasses.asdict`)
- Легко записать в SQL (`INSERT INTO ... VALUES`)
- Типизирован (не `dict[str, Any]`)

## Records

### Характеристики

```python
@dataclass
class TitleRecord:
    problem_id: int    # Только примитивы
    language: str      # str, не Enum
    title: str         # str, не LocalizedText
```

| Свойство | Domain Model | Record |
|----------|--------------|--------|
| Типы | `datetime`, `Enum`, вложенные объекты | `str`, `int`, `bool`, `None` |
| Связи | Вложенность | ID-ссылки |
| frozen | Да | Нет (не обязательно) |
| Цель | Работа в коде | Хранение |

### Соответствие Record ↔ Storage

```
1 Record class = 1 JSON file = 1 SQL table
```

| Record | JSON | SQL |
|--------|------|-----|
| `ProblemRecord` | problems.json | TABLE problems |
| `TitleRecord` | titles.json | TABLE titles |
| `ExampleRecord` | examples.json | TABLE examples |

## Mappers

### Что делают

**Mapper** — функции преобразования между Domain и Records.

```python
# Records → Domain (при чтении)
def records_to_problem(
    problem_rec: ProblemRecord,
    title_recs: list[TitleRecord],
    example_recs: list[ExampleRecord],
    ...
) -> Problem:
    """Собирает богатый объект из плоских записей."""

# Domain → Records (при записи)
def problem_to_records(problem: Problem) -> ProblemRecords:
    """Разбирает богатый объект на плоские записи."""
```

### Аналогия: Сборка мебели

**Records** — это детали в коробке:
```
Коробка: [Доска, Доска, Доска, Ножка, Ножка, Ножка, Ножка, Шурупы]
```

**Mapper** — это инструкция по сборке:
```
records_to_problem() = собрать стол из деталей
problem_to_records() = разобрать стол обратно в коробку
```

**Domain Model** — это готовый стол:
```
Стол(столешница=..., ножки=[...])
```

### Пример: LocalizedText

```python
# Records (плоские)
title_recs = [
    TitleRecord(problem_id=1, language="en", title="Two Sum"),
    TitleRecord(problem_id=1, language="ru", title="Два числа"),
]

# Mapper собирает в LocalizedText
def _group_by_language(records, field):
    return LocalizedText({r.language: getattr(r, field) for r in records})

title = _group_by_language(title_recs, "title")
# → LocalizedText({"en": "Two Sum", "ru": "Два числа"})

# Domain Model использует удобно
print(title.get("ru"))  # "Два числа"
```

### Пример: Вложенные объекты

```python
# Records (плоские)
example_recs = [
    ExampleRecord(example_id=1, problem_id=1, input="...", output="..."),
    ExampleRecord(example_id=2, problem_id=1, input="...", output="..."),
]
explanation_recs = [
    ExplanationRecord(example_id=1, language="en", explanation="..."),
    ExplanationRecord(example_id=1, language="ru", explanation="..."),
]

# Mapper собирает Example с вложенным LocalizedText
examples = tuple(
    Example(
        input=rec.input,
        output=rec.output,
        explanation=_get_explanations(rec.example_id, explanation_recs)
    )
    for rec in example_recs
)

# Domain Model — всё вложено
problem.examples[0].explanation.get("ru")
```

## Главное преимущество

**Один mapper для всех хранилищ:**

```python
# В JsonProblemRepository:
records = load_records_from_json()
return records_to_problem(records)  # ← один и тот же

# В SqliteProblemRepository:
records = load_records_from_sqlite()
return records_to_problem(records)  # ← один и тот же

# В PostgresProblemRepository (будущее):
records = load_records_from_postgres()
return records_to_problem(records)  # ← один и тот же
```

Логика преобразования написана **один раз** — в mapper.
Репозитории только загружают Records из своего хранилища.

## Тестирование

Mappers тестируются отдельно от I/O:

```python
def test_records_to_problem():
    # Arrange — создаём records вручную
    problem_rec = ProblemRecord(problem_id=1, difficulty="easy", ...)
    title_recs = [TitleRecord(problem_id=1, language="en", title="Test")]

    # Act — вызываем mapper
    problem = records_to_problem(problem_rec, title_recs, ...)

    # Assert — проверяем domain model
    assert problem.id == 1
    assert problem.title.get("en") == "Test"
    assert problem.difficulty == Difficulty.EASY
```

Не нужны файлы или база данных — это чистая трансформация данных.
