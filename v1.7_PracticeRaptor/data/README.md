# Data — Хранилище данных

## Что здесь

**Data** — физическое хранилище данных.

```
data/
├── json/                    # JSON-файлы (11 штук)
│   ├── problems.json
│   ├── titles.json
│   ├── descriptions.json
│   └── ...
│
└── sqlite/
    ├── schema.sql           # CREATE TABLE ...
    └── seed.sql             # INSERT ... (те же данные)
```

## Ключевой принцип

```
1 Record = 1 JSON file = 1 SQL table
```

| Record Class | JSON File | SQL Table |
|--------------|-----------|-----------|
| `ProblemRecord` | problems.json | problems |
| `TitleRecord` | titles.json | titles |
| `ExampleRecord` | examples.json | examples |
| `ExplanationRecord` | explanations.json | explanations |
| `HintRecord` | hints.json | hints |
| `TagRecord` | tags.json | tags |
| `EditorialRecord` | editorials.json | editorials |
| `SignatureRecord` | signatures.json | signatures |
| `TestCaseRecord` | test_cases.json | test_cases |
| `CanonicalSolutionRecord` | canonical_solutions.json | canonical_solutions |

## Аналогия: Архив документов

**JSON** — папки с бумажными документами:
```
📁 Архив/
   📁 Задачи/
      📄 problems.json      (список задач)
      📄 titles.json        (названия на разных языках)
      📄 descriptions.json  (описания)
```

**SQLite** — картотека в одном шкафу:
```
🗄️ practiceraptor.db
   📋 TABLE problems
   📋 TABLE titles
   📋 TABLE descriptions
```

Содержимое одинаковое, формат разный.

## JSON: Структура файлов

Каждый файл — массив объектов:

```json
// titles.json
[
  {"problem_id": 1, "language": "en", "title": "Two Sum"},
  {"problem_id": 1, "language": "ru", "title": "Два числа"},
  {"problem_id": 2, "language": "en", "title": "Reverse String"}
]
```

Это соответствует `TitleRecord`:
```python
@dataclass
class TitleRecord:
    problem_id: int
    language: str
    title: str
```

## SQLite: Структура таблиц

Таблицы зеркалят JSON:

```sql
CREATE TABLE titles (
    problem_id INTEGER NOT NULL,
    language TEXT NOT NULL,
    title TEXT NOT NULL,
    PRIMARY KEY (problem_id, language)
);

INSERT INTO titles VALUES (1, 'en', 'Two Sum');
INSERT INTO titles VALUES (1, 'ru', 'Два числа');
```

## Почему нормализация?

### Нормализовано (как у нас):
```
problems.json:     [{problem_id: 1, difficulty: "easy"}]
titles.json:       [{problem_id: 1, language: "en", title: "Two Sum"}]
                   [{problem_id: 1, language: "ru", title: "Два числа"}]
```

**Плюсы:**
- Легко добавить новый язык
- Нет дублирования структуры
- Готово для SQL

### Денормализовано (как могло бы быть):
```
problems.json: [{
  problem_id: 1,
  difficulty: "easy",
  titles: {"en": "Two Sum", "ru": "Два числа"}  // вложено
}]
```

**Минусы:**
- Сложнее добавить язык
- Нужна миграция структуры для SQL
- Разный формат для JSON и SQL

## Использование

### JSON (для разработки)

```bash
# Данные уже в файлах — просто используй
python examples/usage_example.py
```

### SQLite (для production)

```bash
# 1. Создать базу
cd data/sqlite
sqlite3 practiceraptor.db < schema.sql
sqlite3 practiceraptor.db < seed.sql

# 2. Проверить
sqlite3 practiceraptor.db "SELECT * FROM problems;"
sqlite3 practiceraptor.db "SELECT * FROM titles WHERE language='ru';"
```

## Миграция JSON → SQLite

```python
import json
import sqlite3

def migrate():
    conn = sqlite3.connect("practiceraptor.db")

    # Для каждого JSON файла
    for filename, table in [("problems.json", "problems"), ...]:
        with open(f"json/{filename}") as f:
            records = json.load(f)

        for rec in records:
            columns = ", ".join(rec.keys())
            placeholders = ", ".join("?" * len(rec))
            conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                list(rec.values())
            )

    conn.commit()
```

## Резюме

| Аспект | JSON | SQLite |
|--------|------|--------|
| **Формат** | Текстовые файлы | Бинарный файл |
| **Запросы** | Загрузить всё → фильтровать в Python | SQL WHERE |
| **Транзакции** | Нет | Да |
| **Когда использовать** | Разработка, CLI | Production |
| **Одинаковая структура** | ✅ | ✅ |
