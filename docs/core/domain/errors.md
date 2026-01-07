# errors.py — Доменные ошибки

**Путь:** `practiceraptor/core/domain/errors.py`

Этот файл определяет **типы ошибок**, которые могут возникнуть в системе.

---

## Почему ошибки — это dataclass, а не Exception?

В традиционном Python ошибки бросаются как исключения:

```python
# Традиционный подход
def get_user(id: str) -> User:
    user = db.find(id)
    if not user:
        raise UserNotFoundError(f"User {id} not found")  # Бросаем исключение
    return user

# Использование
try:
    user = get_user("123")
except UserNotFoundError as e:
    print(e)
```

**Проблемы этого подхода:**
1. **Неявность:** Глядя на сигнатуру `get_user(id) -> User`, непонятно, что функция может "упасть"
2. **Забывчивость:** Легко забыть обернуть в `try/except`
3. **Производительность:** Исключения в Python медленные

**В PracticeRaptor используется функциональный подход:**

```python
# Функциональный подход
def get_user(id: str) -> Result[User, NotFoundError]:
    user = db.find(id)
    if not user:
        return Err(NotFoundError(entity="User", id=id))  # Возвращаем ошибку
    return Ok(user)

# Использование
result = get_user("123")
if result.is_ok():
    user = result.unwrap()
else:
    print(result.error)
```

**Преимущества:**
1. **Явность:** Сигнатура `Result[User, NotFoundError]` явно показывает возможную ошибку
2. **Принудительность:** Нельзя получить `User`, не проверив результат
3. **Типизация:** mypy проверяет, что все ошибки обработаны

---

## Базовый класс: `DomainError`

```python
@dataclass(frozen=True)
class DomainError:
    """Базовый класс для всех доменных ошибок."""
    message: str

    def __str__(self) -> str:
        return self.message
```

**Аналогия:** Это как **базовый бланк жалобы**. На нём есть поле "сообщение", и его можно распечатать (`__str__`).

Все остальные ошибки наследуются от него, добавляя свои специфичные поля.

---

## Разбор каждой ошибки

### 1. `NotFoundError` — Сущность не найдена

```python
@dataclass(frozen=True)
class NotFoundError(DomainError):
    """Сущность не найдена."""
    entity: str = ""              # Что искали: "User", "Problem"
    id: Union[str, int] = ""      # Какой ID искали
    message: str = field(init=False)  # Генерируется автоматически

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            'message',
            f"{self.entity} with id '{self.id}' not found"
        )
```

**Аналогия:** Как ответ библиотекаря: "Книга 'Война и мир' с номером 12345 не найдена".

**Особенности:**
- `message` не передаётся при создании (`init=False`)
- `message` автоматически генерируется в `__post_init__`
- Используется `object.__setattr__` из-за `frozen=True`

**Использование:**
```python
error = NotFoundError(entity="Problem", id=42)
print(error)  # "Problem with id '42' not found"

# Или с Union типом id:
error = NotFoundError(entity="User", id="abc-123")
print(error)  # "User with id 'abc-123' not found"
```

**Когда возникает:**
- Запрос задачи с несуществующим ID
- Запрос пользователя, которого нет в базе
- Запрос черновика, который не был сохранён

---

### 2. `ValidationError` — Ошибка валидации

```python
@dataclass(frozen=True)
class ValidationError(DomainError):
    """Валидация не пройдена."""
    field: Union[str, None] = None  # Какое поле не прошло валидацию
```

**Аналогия:** Как красная пометка на анкете: "Поле 'email' заполнено неверно".

**Использование:**
```python
# Ошибка в конкретном поле
error = ValidationError(
    message="Email must contain @",
    field="email"
)

# Общая ошибка валидации
error = ValidationError(
    message="Code cannot be empty",
    field="code"
)
```

**Когда возникает:**
- Пустой код при отправке решения
- Синтаксическая ошибка в коде
- Некорректный формат данных

---

### 3. `ExecutionError` — Ошибка выполнения кода

```python
@dataclass(frozen=True)
class ExecutionError(DomainError):
    """Выполнение кода не удалось."""
    error_type: str = ""  # Тип ошибки: syntax, runtime, timeout, memory
```

**Аналогия:** Как отчёт о крушении программы: "Тип: timeout, Сообщение: Превышено время выполнения (5 сек)".

**Типы ошибок:**

| `error_type` | Описание | Пример |
|--------------|----------|--------|
| `syntax` | Синтаксическая ошибка | `def foo( ← забыли закрыть скобку` |
| `runtime` | Ошибка во время выполнения | `1 / 0` — деление на ноль |
| `timeout` | Превышено время | Бесконечный цикл |
| `memory` | Превышена память | Создание огромного списка |
| `validation` | Язык не поддерживается | Задача без Python-версии |

**Использование:**
```python
# Таймаут
error = ExecutionError(
    message="Execution timed out after 5 seconds",
    error_type="timeout"
)

# Ошибка выполнения
error = ExecutionError(
    message="ZeroDivisionError: division by zero",
    error_type="runtime"
)
```

---

### 4. `StorageError` — Ошибка хранилища

```python
@dataclass(frozen=True)
class StorageError(DomainError):
    """Операция с хранилищем не удалась."""
    operation: str = ""  # Операция: read, write, delete
```

**Аналогия:** Как сообщение от жёсткого диска: "Операция 'write' не удалась: диск переполнен".

**Использование:**
```python
# Ошибка записи
error = StorageError(
    message="Failed to save draft: disk full",
    operation="write"
)

# Ошибка чтения
error = StorageError(
    message="Cannot read problems.json: file corrupted",
    operation="read"
)
```

**Когда возникает:**
- Файл заблокирован другим процессом
- Нет прав на запись
- Диск переполнен
- Файл повреждён

---

## Иерархия ошибок

```
DomainError (базовый)
├── NotFoundError      (сущность не найдена)
├── ValidationError    (данные некорректны)
├── ExecutionError     (код не выполнился)
└── StorageError       (хранилище недоступно)
```

---

## Как ошибки используются в коде

### В репозиториях (ports)

```python
class IProblemRepository(Protocol):
    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        ...
```

Метод явно говорит: "Я верну либо `Problem`, либо `NotFoundError`".

### В сервисах

```python
def validate_code_syntax(code: str) -> Result[str, ValidationError]:
    if not code.strip():
        return Err(ValidationError(
            message="Code cannot be empty",
            field="code"
        ))
    try:
        ast.parse(code)
        return Ok(code)
    except SyntaxError as e:
        return Err(ValidationError(
            message=f"Syntax error: {e.msg}",
            field="code"
        ))
```

### В клиентском коде (CLI)

```python
result = get_problem(problem_id, repo)

match result:
    case Ok(problem):
        display_problem(problem)
    case Err(NotFoundError() as e):
        print(f"Error: {e.message}")
```

---

## Сравнение с исключениями

| Аспект | Exceptions | Domain Errors |
|--------|------------|---------------|
| Сигнатура | Скрыта | Явная (`Result[T, E]`) |
| Проверка типов | Слабая | Строгая (mypy) |
| Пропуск обработки | Легко забыть | Компилятор напомнит |
| Стек вызовов | Автоматический | Нет (не нужен) |
| Производительность | Медленнее | Быстрее |
| Стиль | Императивный | Функциональный |
