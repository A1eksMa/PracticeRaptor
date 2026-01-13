# PracticeRaptor v1.7 — Архитектура с разделением Domain и Persistence

## Ключевая идея

**Модели для кода и модели для хранения — это разные вещи.**

```
┌─────────────────────────────────────────────────────────────┐
│  DOMAIN MODELS                                              │
│  Богатые объекты для бизнес-логики                          │
│  • Вложенность (Problem содержит Examples)                  │
│  • Удобные типы (datetime, Enum, LocalizedText)             │
│  • Методы бизнес-логики                                     │
└─────────────────────────────────────────────────────────────┘
                            ↑↓  mappers
┌─────────────────────────────────────────────────────────────┐
│  PERSISTENCE RECORDS                                        │
│  Плоские структуры для хранения                             │
│  • Только ID-ссылки (problem_id, example_id)                │
│  • Только примитивы (str, int, bool)                        │
│  • 1 Record = 1 JSON файл = 1 SQL таблица                   │
└─────────────────────────────────────────────────────────────┘
                            ↑↓  repositories
┌─────────────────────────────────────────────────────────────┐
│  STORAGE                                                    │
│  Физическое хранилище                                       │
│  • JSON файлы (для CLI, разработки)                         │
│  • SQLite (для production)                                  │
│  • PostgreSQL (будущее)                                     │
└─────────────────────────────────────────────────────────────┘
```

## Проблема, которую решаем

### До (v1.6): Смешение слоёв

```python
# Domain model выглядит как SQL таблица
class Title:
    problem_id: int      # ← ID-ссылка
    language: Language
    title: str

# Неудобно в коде:
problem = get_problem(1)
title = get_title(problem.problem_id, "ru")  # Отдельный запрос!
description = get_description(problem.problem_id, "ru")  # Ещё запрос!
```

### После (v1.7): Разделение слоёв

```python
# Domain model — богатый объект
class Problem:
    title: LocalizedText           # ← вложенность
    description: LocalizedText
    examples: tuple[Example, ...]  # ← вложенность

# Удобно в коде:
problem = repo.get_by_id(1)
print(problem.title.get("ru"))        # Всё под рукой
print(problem.examples[0].input)      # Без дополнительных запросов
```

## Структура проекта

```
v1.7_PracticeRaptor/
│
├── core/                    # Чистая бизнес-логика (без I/O)
│   ├── domain/             # Богатые объекты для работы в коде
│   ├── persistence/        # Плоские структуры + mappers
│   ├── ports/              # Интерфейсы (контракты)
│   └── services/           # Use Cases (оркестрация)
│
├── adapters/               # Реализации интерфейсов (I/O)
│   └── storage/
│       ├── json/          # JSON-хранилище
│       └── sqlite/        # SQLite-хранилище
│
├── data/                   # Данные
│   ├── json/              # JSON файлы
│   └── sqlite/            # SQL схема и seed
│
└── examples/              # Примеры использования
```

## Аналогия: Документооборот

| Концепция | Аналогия |
|-----------|----------|
| **Domain Model** | Удобная форма для работы (Word документ) |
| **Persistence Record** | Форма для архива (карточка с полями) |
| **Mapper** | Секретарь, который переносит данные между формами |
| **Repository** | Архивариус, который знает где хранятся карточки |
| **JSON/SQLite** | Физический архив (папки или картотека) |

## Поток данных

### Чтение (Storage → Domain)

```
JSON файл          →  dict           →  Record        →  Domain Model
problems.json         {"problem_id": 1}   ProblemRecord    Problem(id=1, ...)
titles.json           [{"title": "..."}]  [TitleRecord]    ↓ (LocalizedText)
examples.json         [{"input": "..."}]  [ExampleRecord]  ↓ (tuple[Example])
                                              ↓
                                         records_to_problem()
                                              ↓
                                         Problem (богатый объект)
```

### Запись (Domain → Storage)

```
Problem              →  Records          →  dicts         →  JSON файлы
Problem(id=1, ...)      ProblemRecord       {"problem_id": 1}  problems.json
  .title                [TitleRecord]       [{"title": "..."}] titles.json
  .examples             [ExampleRecord]     [{"input": "..."}] examples.json
        ↓
   problem_to_records()
        ↓
   ProblemRecords (контейнер)
```

## Главное преимущество

**Один mapper для всех хранилищ:**

```python
# JSON Repository
records = load_from_json()
return records_to_problem(records)  # ← тот же mapper

# SQLite Repository
records = load_from_sqlite()
return records_to_problem(records)  # ← тот же mapper

# PostgreSQL Repository (будущее)
records = load_from_postgres()
return records_to_problem(records)  # ← тот же mapper
```

Логика преобразования пишется **один раз** в mapper, а не дублируется в каждом репозитории.

## Быстрый старт

```python
from pathlib import Path
from adapters.storage.json import JsonProblemRepository

# Создаём репозиторий
repo = JsonProblemRepository(Path("data/json"))

# Получаем проблему — богатый объект
problem = repo.get_by_id(1, locale="ru")

# Работаем удобно
print(problem.title.get("ru"))           # "Два числа"
print(problem.examples[0].input)         # "nums = [2, 7, 11, 15]"
print(problem.hints[0].get("ru"))        # "Попробуйте использовать хеш-таблицу"
```

## Навигация по документации

- [core/README.md](core/README.md) — Обзор ядра
- [core/domain/README.md](core/domain/README.md) — Domain Models
- [core/persistence/README.md](core/persistence/README.md) — Records и Mappers
- [core/ports/README.md](core/ports/README.md) — Интерфейсы
- [core/services/README.md](core/services/README.md) — Use Cases (оркестрация)
- [adapters/README.md](adapters/README.md) — Реализации репозиториев
- [data/README.md](data/README.md) — Структура данных
