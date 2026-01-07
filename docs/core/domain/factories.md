# factories.py — Фабричные функции

**Путь:** `practiceraptor/core/domain/factories.py`

Этот файл содержит **фабричные функции** — специальные функции для создания доменных объектов.

---

## Зачем нужны фабрики?

### Проблема: Сложное создание объектов

Наши модели — это `frozen` dataclass'ы. Они требуют передать все поля при создании:

```python
# Без фабрики — нужно указать всё
user = User(
    id="???",                        # Откуда взять ID?
    locale="en",
    preferred_language=Language.PYTHON,
    created_at=datetime.now(),       # Не забыть про время!
)
```

**Проблемы:**
1. **Генерация ID** — каждый раз писать `str(uuid4())`
2. **Текущее время** — каждый раз писать `datetime.now()`
3. **Дефолты** — легко забыть или ошибиться
4. **Дублирование** — один и тот же код в разных местах

### Решение: Фабричная функция

```python
# С фабрикой — просто и безопасно
user = create_user()  # ID и время сгенерируются автоматически

# Или с кастомными параметрами
user = create_user(locale="ru", preferred_language=Language.GO)
```

---

## Аналогия: Кондитерская фабрика

Представь, что ты владелец кондитерской. Каждый торт требует:
- Основу (бисквит)
- Крем
- Украшения
- Дату изготовления
- Уникальный номер партии

**Без фабрики** — каждый кондитер сам решает:
```
Кондитер 1: "Я положу 3 слоя крема"
Кондитер 2: "А я положу 5 слоёв"
Кондитер 3: "Я забыл написать дату..."
```

**С фабрикой** — есть стандартный рецепт:
```
create_cake(flavor="chocolate")
→ Автоматически: 4 слоя крема, стандартные украшения,
  сегодняшняя дата, уникальный номер
```

Фабрика гарантирует **единообразие** и **корректность**.

---

## Разбор каждой фабрики

### 1. `create_user()` — Создание пользователя

```python
def create_user(
    user_id: str | None = None,
    locale: str = "en",
    preferred_language: Language = Language.PYTHON,
) -> User:
    """Создать нового пользователя с дефолтами."""
    return User(
        id=user_id or str(uuid4()),      # Если ID не передан — генерируем
        locale=locale,
        preferred_language=preferred_language,
        created_at=datetime.now(),       # Всегда текущее время
    )
```

**Что делает:**
- Генерирует уникальный `id`, если не передан
- Устанавливает `locale="en"` по умолчанию
- Устанавливает `preferred_language=PYTHON` по умолчанию
- Автоматически ставит `created_at` на текущее время

**Использование:**

```python
# Анонимный пользователь (ID генерируется)
user = create_user()
# User(id="a1b2c3d4-...", locale="en", ...)

# Пользователь с Telegram ID
user = create_user(user_id="telegram_123456")
# User(id="telegram_123456", locale="en", ...)

# Русскоязычный пользователь, предпочитающий Go
user = create_user(locale="ru", preferred_language=Language.GO)
# User(id="...", locale="ru", preferred_language=Language.GO, ...)
```

**`str(uuid4())`** — генерирует уникальный идентификатор вида `"550e8400-e29b-41d4-a716-446655440000"`. UUID практически невозможно угадать или подделать.

---

### 2. `create_draft()` — Создание черновика

```python
def create_draft(
    user_id: str,
    problem_id: int,
    code: str,
    language: Language = Language.PYTHON,
) -> Draft:
    """Создать новый черновик."""
    return Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),  # Время последнего изменения
    )
```

**Что делает:**
- Принимает обязательные поля: `user_id`, `problem_id`, `code`
- Устанавливает `language=PYTHON` по умолчанию
- Автоматически ставит `updated_at` на текущее время

**Использование:**

```python
# Сохранить черновик решения
draft = create_draft(
    user_id="user_123",
    problem_id=1,
    code="def two_sum(nums, target):\n    pass"
)

# Черновик на Go
draft = create_draft(
    user_id="user_123",
    problem_id=1,
    code="func twoSum(nums []int, target int) []int {\n    return nil\n}",
    language=Language.GO
)
```

**Почему `user_id` и `problem_id` обязательные?**

Черновик без привязки к пользователю и задаче бессмысленен. Это не "пустой шаблон", а конкретная работа конкретного человека над конкретной задачей.

---

### 3. `create_submission()` — Создание решения

```python
def create_submission(
    user_id: str,
    problem_id: int,
    code: str,
    execution_time_ms: int = 0,
    memory_used_kb: int = 0,
    language: Language = Language.PYTHON,
    submission_id: str | None = None,
) -> Submission:
    """Создать новое решение."""
    return Submission(
        id=submission_id or str(uuid4()),  # Уникальный ID решения
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        execution_time_ms=execution_time_ms,
        memory_used_kb=memory_used_kb,
        created_at=datetime.now(),
    )
```

**Что делает:**
- Генерирует уникальный `id` для решения (или использует переданный)
- Принимает метрики выполнения: время и память
- Автоматически ставит `created_at`

**Использование:**

```python
# После успешного прохождения всех тестов
submission = create_submission(
    user_id="user_123",
    problem_id=1,
    code="def two_sum(nums, target):\n    ...",
    execution_time_ms=42,
    memory_used_kb=1024,
)
```

**Почему `execution_time_ms=0` по умолчанию?**

Это позволяет создать submission даже если метрики не были измерены. В реальности значения всегда передаются после выполнения тестов.

---

### 4. `create_progress()` — Создание записи прогресса

```python
def create_progress(
    user_id: str,
    problem_id: int,
    status: ProgressStatus = ProgressStatus.NOT_STARTED,
    attempts: int = 0,
    solved_languages: tuple[Language, ...] = (),
) -> Progress:
    """Создать запись прогресса."""
    return Progress(
        user_id=user_id,
        problem_id=problem_id,
        status=status,
        attempts=attempts,
        solved_languages=solved_languages,
        first_solved_at=None,  # Пока не решено
    )
```

**Что делает:**
- Создаёт запись прогресса для пары (пользователь, задача)
- По умолчанию: статус `NOT_STARTED`, 0 попыток
- `first_solved_at=None` — задача ещё не решена

**Использование:**

```python
# Начальный прогресс
progress = create_progress(user_id="user_123", problem_id=1)
# Progress(status=NOT_STARTED, attempts=0, solved_languages=(), ...)

# Прогресс после нескольких попыток
progress = create_progress(
    user_id="user_123",
    problem_id=1,
    status=ProgressStatus.IN_PROGRESS,
    attempts=3,
)
```

---

### 5. `create_initial_progress()` — Удобная обёртка

```python
def create_initial_progress(user_id: str, problem_id: int) -> Progress:
    """Создать начальный прогресс для задачи."""
    return create_progress(user_id=user_id, problem_id=problem_id)
```

**Зачем отдельная функция?**

Это **семантический сахар** — функция с говорящим именем. Когда читаешь код:

```python
# Менее понятно — что за progress создаём?
progress = create_progress(user_id=uid, problem_id=pid)

# Более понятно — ага, это начальный прогресс
progress = create_initial_progress(user_id=uid, problem_id=pid)
```

Название функции — это документация в коде.

---

## Паттерн: Фабрика vs Конструктор

### Конструктор (dataclass `__init__`)

```python
@dataclass(frozen=True)
class User:
    id: str
    locale: str
    preferred_language: Language
    created_at: datetime
```

- **Требует все поля**
- **Не генерирует значения**
- **Не имеет бизнес-логики**

### Фабрика

```python
def create_user(user_id: str | None = None, ...) -> User:
    return User(
        id=user_id or str(uuid4()),  # Генерация
        created_at=datetime.now(),    # Вычисление
        ...
    )
```

- **Имеет дефолты**
- **Генерирует значения**
- **Может содержать логику**

---

## Почему не методы класса?

В некоторых языках (Java, C#) фабрики часто реализуют как статические методы:

```python
# Альтернативный подход (НЕ используется в проекте)
class User:
    @staticmethod
    def create(user_id: str | None = None, ...) -> "User":
        return User(...)
```

**Почему в PracticeRaptor используются функции:**

1. **Простота** — функции проще классов
2. **Тестируемость** — легко мокать
3. **Функциональный стиль** — соответствует архитектуре проекта
4. **Frozen dataclass** — статический метод не может создать frozen объект "изнутри"

---

## Где используются фабрики

### В адаптерах (auth)

```python
# adapters/auth/anonymous_auth.py
def get_current_user(self) -> Result[User, AuthError]:
    return Ok(create_user(user_id="anonymous"))
```

### В сервисах (progress)

```python
# core/services/progress.py
def get_user_progress(user_id: str, problem_id: int, ...) -> Progress:
    result = progress_repo.get(user_id, problem_id)
    match result:
        case Ok(progress):
            return progress
        case Err(_):
            return create_initial_progress(user_id, problem_id)  # Фабрика!
```

### В тестах

```python
# tests/fixtures/...
def sample_user():
    return create_user(user_id="test_user", locale="en")

def sample_draft():
    return create_draft(
        user_id="test_user",
        problem_id=1,
        code="def solution(): pass"
    )
```

---

## Визуальная схема

```
┌─────────────────────────────────────────────────────────────┐
│                     ФАБРИЧНЫЕ ФУНКЦИИ                        │
│                                                             │
│  create_user()  ──────────────────────→  User               │
│      │                                    │                 │
│      ├─ user_id: генерирует uuid4()       ├─ id             │
│      ├─ locale: "en"                      ├─ locale         │
│      ├─ preferred_language: PYTHON        ├─ preferred_lang │
│      └─ created_at: datetime.now()        └─ created_at     │
│                                                             │
│  create_draft()  ─────────────────────→  Draft              │
│      │                                    │                 │
│      ├─ user_id: ОБЯЗАТЕЛЬНО              ├─ user_id        │
│      ├─ problem_id: ОБЯЗАТЕЛЬНО           ├─ problem_id     │
│      ├─ code: ОБЯЗАТЕЛЬНО                 ├─ code           │
│      ├─ language: PYTHON                  ├─ language       │
│      └─ updated_at: datetime.now()        └─ updated_at     │
│                                                             │
│  create_submission()  ────────────────→  Submission         │
│      │                                    │                 │
│      ├─ id: генерирует uuid4()            ├─ id             │
│      ├─ execution_time_ms: 0              ├─ execution_time │
│      ├─ memory_used_kb: 0                 ├─ memory_used    │
│      └─ created_at: datetime.now()        └─ created_at     │
│                                                             │
│  create_progress()  ──────────────────→  Progress           │
│      │                                    │                 │
│      ├─ status: NOT_STARTED               ├─ status         │
│      ├─ attempts: 0                       ├─ attempts       │
│      ├─ solved_languages: ()              ├─ solved_langs   │
│      └─ first_solved_at: None             └─ first_solved   │
│                                                             │
│  create_initial_progress()  ──→  create_progress()          │
│      (семантическая обёртка)                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
