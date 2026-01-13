# Adapters — Реализации интерфейсов

## Что здесь

**Adapters** — это конкретные реализации интерфейсов из `ports/`.

```
adapters/
└── storage/
    ├── json/
    │   └── json_problem_repository.py    # JSON-реализация
    │
    └── sqlite/
        └── sqlite_problem_repository.py  # SQLite-реализация
```

## Роль адаптера

**Адаптер** знает:
- **Где** хранятся данные (путь к файлам, строка подключения к БД)
- **Как** читать/писать в конкретное хранилище (json.load, SQL-запросы)
- **Как** конвертировать формат хранилища в Records

**Адаптер НЕ знает:**
- Бизнес-логику (это domain)
- Как преобразовать Records в Domain (это mappers)
- О других адаптерах

## Аналогия: Переводчик

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Японец    │ ←→  │  Переводчик │ ←→  │   Русский   │
│  (Storage)  │     │  (Adapter)  │     │  (Domain)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

- **Японец** говорит на своём языке (JSON, SQL)
- **Переводчик** знает оба языка (адаптер)
- **Русский** получает понятный текст (Domain Model)

Если нужен другой источник (китаец = PostgreSQL), нанимаем другого переводчика (адаптер), но русский язык (Domain) остаётся тем же.

## Структура адаптера

```python
class JsonProblemRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir  # ← знает ГДЕ

    def get_by_id(self, problem_id: int) -> Problem | None:
        # 1. Загрузить данные из хранилища
        problem_data = self._load_json("problems.json")  # ← знает КАК
        title_data = self._load_json("titles.json")
        ...

        # 2. Конвертировать в Records
        problem_rec = ProblemRecord(**problem_data)
        title_recs = [TitleRecord(**d) for d in title_data]

        # 3. Использовать общий mapper
        return records_to_problem(problem_rec, title_recs, ...)  # ← НЕ знает КАК
```

## JSON vs SQLite — разница только в загрузке

### JSON
```python
def _load_titles(self, problem_id: int) -> list[TitleRecord]:
    data = json.load(open("titles.json"))
    return [
        TitleRecord(**item)
        for item in data
        if item["problem_id"] == problem_id
    ]
```

### SQLite
```python
def _load_titles(self, problem_id: int) -> list[TitleRecord]:
    cursor = self.conn.execute(
        "SELECT * FROM titles WHERE problem_id = ?",
        (problem_id,)
    )
    return [
        TitleRecord(
            problem_id=row["problem_id"],
            language=row["language"],
            title=row["title"],
        )
        for row in cursor.fetchall()
    ]
```

### Общее — mapper

```python
# И JSON, и SQLite используют ОДИН mapper:
return records_to_problem(problem_rec, title_recs, example_recs, ...)
```

## Почему это хорошо?

### 1. Легко добавить новое хранилище

```python
# adapters/storage/postgres/postgres_problem_repository.py
class PostgresProblemRepository:
    def _load_titles(self, problem_id: int) -> list[TitleRecord]:
        # Своя логика загрузки из PostgreSQL
        ...

    def get_by_id(self, problem_id: int) -> Problem | None:
        # Но тот же mapper!
        return records_to_problem(...)
```

### 2. Легко тестировать

```python
def test_json_repository_loads_problem():
    # Создаём временные JSON-файлы
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "problems.json").write_text('[{"problem_id": 1, ...}]')
        Path(tmp, "titles.json").write_text('[{"problem_id": 1, ...}]')

        repo = JsonProblemRepository(Path(tmp))
        problem = repo.get_by_id(1)

        assert problem.id == 1
```

### 3. Легко переключаться

```yaml
# config.yaml
storage:
  type: json   # разработка
  # type: sqlite  # production
```

```python
if config.storage.type == "json":
    repo = JsonProblemRepository(config.storage.json.path)
elif config.storage.type == "sqlite":
    repo = SqliteProblemRepository(config.storage.sqlite.path)
```

## Кэширование

JSON-репозиторий использует простой кэш:

```python
def _load_json(self, filename: str) -> list[dict]:
    if filename not in self._cache:
        with open(self.data_dir / filename) as f:
            self._cache[filename] = json.load(f)
    return self._cache[filename]
```

SQLite-репозиторий использует соединение с БД:

```python
@property
def conn(self) -> sqlite3.Connection:
    if self._conn is None:
        self._conn = sqlite3.connect(self.db_path)
    return self._conn
```

## Резюме

| Аспект | JSON Adapter | SQLite Adapter |
|--------|--------------|----------------|
| **Хранилище** | Файлы `.json` | База `.db` |
| **Загрузка** | `json.load()` | `SELECT * FROM` |
| **Фильтрация** | В памяти (Python) | В БД (SQL WHERE) |
| **Mapper** | `records_to_problem()` | `records_to_problem()` |
| **Domain Model** | `Problem` | `Problem` |

Разные адаптеры, одинаковый результат.
