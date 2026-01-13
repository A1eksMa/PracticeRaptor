# Предложение: Persistence Layer

## Проблема

В v1.5 логика преобразования данных (`_parse_*`, `_serialize_*`) дублируется в каждом репозитории.
При добавлении SQLite/PostgreSQL придётся копировать эту логику.

## Решение

Ввести промежуточный слой **Persistence Records** + **Mappers**:

```
Domain Model  ←→  Record  ←→  Storage
   (User)      mapper   (UserRecord)   repository   (JSON/SQLite/PG)
```

## Предлагаемая структура

```
core/
├── domain/                    # Доменные модели (бизнес-логика)
│   ├── __init__.py
│   ├── user.py               # User
│   ├── problem.py            # Problem, ProblemSelector, etc.
│   ├── solution.py           # Solution, Draft, etc.
│   ├── execution.py          # Execution, Submission, etc.
│   └── ...
│
└── persistence/               # Слой персистентности
    ├── __init__.py
    │
    ├── records/              # Структуры для хранения (плоские, примитивы)
    │   ├── __init__.py
    │   ├── user_record.py    # UserRecord
    │   ├── problem_record.py # ProblemRecord, ProblemSelectorRecord, etc.
    │   ├── solution_record.py
    │   └── ...
    │
    └── mappers/              # Преобразование Domain ↔ Record
        ├── __init__.py
        ├── user_mapper.py    # user_to_record(), record_to_user()
        ├── problem_mapper.py
        ├── solution_mapper.py
        └── ...

adapters/
└── storage/                   # Реализации репозиториев
    ├── __init__.py
    │
    ├── json/                 # JSON-хранилище
    │   ├── __init__.py
    │   ├── json_base.py      # Базовые операции JSON I/O
    │   ├── json_user_repository.py
    │   ├── json_problem_repository.py
    │   └── ...
    │
    └── sqlite/               # SQLite-хранилище (будущее)
        ├── __init__.py
        ├── sqlite_base.py
        ├── sqlite_user_repository.py
        └── ...
```

## Пример: User

### 1. Domain Model (core/domain/user.py)

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    """Пользователь — доменная модель."""
    user_id: int
    user_name: str
    hash_password: str
    email: str
    created_at: datetime
```

### 2. Persistence Record (core/persistence/records/user_record.py)

```python
from dataclasses import dataclass

@dataclass
class UserRecord:
    """Запись пользователя для хранения.

    Только примитивные типы: str, int, float, bool, None.
    Нет datetime, Enum, вложенных объектов.
    """
    user_id: int
    user_name: str
    hash_password: str
    email: str
    created_at: str  # ISO format string
```

### 3. Mapper (core/persistence/mappers/user_mapper.py)

```python
from datetime import datetime
from core.domain.user import User
from core.persistence.records.user_record import UserRecord

def user_to_record(user: User) -> UserRecord:
    """Domain Model → Persistence Record"""
    return UserRecord(
        user_id=user.user_id,
        user_name=user.user_name,
        hash_password=user.hash_password,
        email=user.email,
        created_at=user.created_at.isoformat(),
    )

def record_to_user(record: UserRecord) -> User:
    """Persistence Record → Domain Model"""
    return User(
        user_id=record.user_id,
        user_name=record.user_name,
        hash_password=record.hash_password,
        email=record.email,
        created_at=datetime.fromisoformat(record.created_at),
    )
```

### 4. JSON Repository (adapters/storage/json/json_user_repository.py)

```python
import json
from dataclasses import asdict
from pathlib import Path

from core.domain.user import User
from core.persistence.records.user_record import UserRecord
from core.persistence.mappers.user_mapper import user_to_record, record_to_user

class JsonUserRepository:
    def __init__(self, path: Path):
        self.path = path

    def get_by_id(self, user_id: int) -> User | None:
        data = self._read_all()
        for item in data:
            if item["user_id"] == user_id:
                record = UserRecord(**item)
                return record_to_user(record)
        return None

    def save(self, user: User) -> None:
        record = user_to_record(user)
        data = asdict(record)
        self._append_or_update(data)

    # ... internal methods ...
```

### 5. SQLite Repository (adapters/storage/sqlite/sqlite_user_repository.py)

```python
from core.domain.user import User
from core.persistence.records.user_record import UserRecord
from core.persistence.mappers.user_mapper import user_to_record, record_to_user

class SqliteUserRepository:
    def __init__(self, connection):
        self.conn = connection

    def get_by_id(self, user_id: int) -> User | None:
        cursor = self.conn.execute(
            "SELECT user_id, user_name, hash_password, email, created_at "
            "FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            record = UserRecord(*row)
            return record_to_user(record)  # ← тот же mapper!
        return None

    def save(self, user: User) -> None:
        record = user_to_record(user)  # ← тот же mapper!
        self.conn.execute(
            "INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?)",
            (record.user_id, record.user_name, record.hash_password,
             record.email, record.created_at)
        )
```

## Поток данных

```
ЧТЕНИЕ:
  JSON file → dict → UserRecord → User
  SQLite    → tuple → UserRecord → User
                         ↑
                    общий mapper

ЗАПИСЬ:
  User → UserRecord → dict  → JSON file
  User → UserRecord → tuple → SQLite
           ↑
      общий mapper
```

## Преимущества

1. **Один mapper для всех хранилищ** — нет дублирования логики преобразования
2. **Типизация** — UserRecord типизирован, в отличие от dict[str, Any]
3. **Тестируемость** — mappers тестируются отдельно от I/O
4. **Расширяемость** — добавление PostgreSQL требует только нового репозитория

## Открытые вопросы

- [ ] Нужен ли базовый класс/протокол для Record?
- [ ] Где хранить валидацию данных — в mapper или в Record?
- [ ] Как обрабатывать миграции схемы (версионирование Record)?

---

*Создано: 2025-01*
