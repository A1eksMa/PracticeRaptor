# Persistence — Слой хранения

## Что здесь

**Persistence** — промежуточный слой между Domain Models и Storage.

```
persistence/
├── records/           # Плоские структуры для хранения
│   ├── problem_records.py
│   └── user_records.py
│
└── mappers/           # Преобразование Domain ↔ Records
    └── (TODO)
```

## Зачем нужен этот слой?

### Проблема: разные нужды

| Domain Models | Storage (JSON/SQL) |
|---------------|-------------------|
| Вложенность (`draft.problem.title`) | Плоские таблицы |
| `datetime`, `Enum` | Строки, числа |
| Удобство в коде | Удобство хранения |
| Один объект = много связей | Одна строка = одна таблица |

### Решение: промежуточный формат

```
Domain Model  ←→  Records  ←→  Storage
   Draft          DraftRecord     JSON/SQLite
                  UserRecord
                  ProblemRecord
```

**Record** — это "общий знаменатель", который:
- Легко сериализовать в JSON (`dataclasses.asdict`)
- Легко записать в SQL (`INSERT INTO ... VALUES`)
- Типизирован (не `dict[str, Any]`)

## Records

### Характеристики

```python
@dataclass
class DraftRecord:
    draft_id: int          # Только примитивы
    user_id: int           # ID-ссылки вместо объектов
    problem_id: int
    language: str          # str, не Enum
    code: str
    created_at: str        # ISO-строка, не datetime
    updated_at: str
```

| Свойство | Domain Model | Record |
|----------|--------------|--------|
| Типы | `datetime`, `Enum`, вложенные объекты | `str`, `int`, `bool`, `None` |
| Связи | Вложенность | ID-ссылки |
| Коллекции | `tuple` | `list` |
| frozen | Да | Нет |
| Цель | Работа в коде | Хранение |

### Соответствие Record ↔ Storage

```
1 Record class = 1 JSON file = 1 SQL table
```

## Problem Records

```python
# Основная запись
ProblemRecord           → problems.json / TABLE problems
├── id, difficulty, complexity, categories, tags

# Локализованные тексты
TitleRecord             → titles.json / TABLE problem_titles
DescriptionRecord       → descriptions.json / TABLE problem_descriptions
HintRecord              → hints.json / TABLE problem_hints
EditorialRecord         → editorials.json / TABLE problem_editorials

# Примеры
ExampleRecord           → examples.json / TABLE problem_examples
ExplanationRecord       → explanations.json / TABLE example_explanations

# Шаблоны для языков программирования
TemplateRecord          → templates.json / TABLE problem_templates
TestCaseRecord          → test_cases.json / TABLE test_cases
CanonicalSolutionRecord → canonical_solutions.json / TABLE canonical_solutions
```

## User Records

```python
UserRecord              → users.json / TABLE users
SettingsRecord          → settings.json / TABLE user_settings
DraftRecord             → drafts.json / TABLE drafts
SubmissionRecord        → submissions.json / TABLE submissions
```

### SubmissionRecord — особый случай

```python
@dataclass
class SubmissionRecord:
    submission_id: int
    user_id: int
    problem_id: int
    language: str
    code: str
    result: str
    total_time_ms: int
    memory_used_kb: int
    error_message: str | None
    test_results_json: str   # ← JSON-массив TestResultRecord
    created_at: str
```

`test_results_json` — это денормализация. Вместо отдельной таблицы храним JSON-массив:
```json
[
  {"test_index": 0, "status": "accepted", "time_ms": 10},
  {"test_index": 1, "status": "wrong_answer", "time_ms": 15, "error_message": "..."}
]
```

Это допустимо, потому что:
- Тест-результаты не запрашиваются отдельно
- Всегда загружаются вместе с submission
- Упрощает структуру

## Mappers (TODO)

**Mapper** — функции преобразования между Domain и Records.

### Сборка богатой модели

```python
def records_to_draft(
    draft_rec: DraftRecord,
    user: User,
    problem: Problem,
    template: ProblemTemplate,
) -> Draft:
    """Собирает богатый объект из записи и связанных объектов."""
    return Draft(
        draft_id=draft_rec.draft_id,
        user=user,
        problem=problem,
        template=template,
        code=draft_rec.code,
        created_at=datetime.fromisoformat(draft_rec.created_at),
        updated_at=datetime.fromisoformat(draft_rec.updated_at),
    )
```

### Разборка в плоскую запись

```python
def draft_to_record(draft: Draft) -> DraftRecord:
    """Разбирает богатый объект в плоскую запись."""
    return DraftRecord(
        draft_id=draft.draft_id,
        user_id=draft.user.user_id,
        problem_id=draft.problem.id,
        language=draft.template.language.value,
        code=draft.code,
        created_at=draft.created_at.isoformat(),
        updated_at=draft.updated_at.isoformat(),
    )
```

## Аналогия: Сборка мебели

**Records** — это детали в коробке:
```
Коробка: [Доска, Доска, Ножка, Ножка, Шурупы]
```

**Mapper** — это инструкция по сборке:
```
records_to_draft() = собрать стол из деталей
draft_to_record() = разобрать стол обратно
```

**Domain Model** — это готовый стол:
```
Draft(user=..., problem=..., code=...)
```

## Главное преимущество

**Один mapper для всех хранилищ:**

```python
# В JsonDraftRepository:
record = load_record_from_json(draft_id)
user = user_repo.get(record.user_id)
problem = problem_repo.get(record.problem_id)
template = template_repo.get(record.problem_id, record.language)
return records_to_draft(record, user, problem, template)  # ← один и тот же

# В SqliteDraftRepository:
record = load_record_from_sqlite(draft_id)
user = user_repo.get(record.user_id)
problem = problem_repo.get(record.problem_id)
template = template_repo.get(record.problem_id, record.language)
return records_to_draft(record, user, problem, template)  # ← один и тот же
```

Логика преобразования написана **один раз** — в mapper.
Репозитории только загружают Records из своего хранилища.

## Тестирование

Records и Mappers тестируются отдельно от I/O:

```python
def test_draft_to_record():
    draft = Draft(
        draft_id=1,
        user=User(user_id=1, user_name="test"),
        problem=problem,
        template=template,
        code="def f(): pass",
        created_at=datetime(2024, 1, 1, 12, 0),
        updated_at=datetime(2024, 1, 1, 12, 30),
    )

    record = draft_to_record(draft)

    assert record.draft_id == 1
    assert record.user_id == 1
    assert record.problem_id == problem.id
    assert record.language == "python3"
    assert record.created_at == "2024-01-01T12:00:00"

def test_records_to_draft():
    record = DraftRecord(
        draft_id=1,
        user_id=1,
        problem_id=42,
        language="python3",
        code="def f(): pass",
        created_at="2024-01-01T12:00:00",
        updated_at="2024-01-01T12:30:00",
    )

    draft = records_to_draft(record, user, problem, template)

    assert draft.draft_id == 1
    assert draft.user.user_id == 1
    assert draft.problem.id == 42
    assert draft.code == "def f(): pass"
```

Не нужны файлы или база данных — это чистая трансформация данных.
