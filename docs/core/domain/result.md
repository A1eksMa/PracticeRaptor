# result.py — Тип Result для обработки ошибок

**Путь:** `practiceraptor/core/domain/result.py`

Этот файл реализует паттерн **Result Type** — функциональный способ обработки ошибок.

---

## Зачем нужен Result?

**Проблема:** Функция может либо вернуть результат, либо завершиться с ошибкой. Как это выразить?

### Вариант 1: Исключения (традиционный Python)

```python
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Использование
try:
    result = divide(10, 0)
except ValueError as e:
    print(e)
```

**Минусы:**
- Сигнатура `-> float` врёт — функция может не вернуть `float`
- Легко забыть `try/except`
- Исключения "прыгают" через стек вызовов непредсказуемо

### Вариант 2: Result (функциональный подход)

```python
def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Err("Cannot divide by zero")
    return Ok(a / b)

# Использование
result = divide(10, 0)
if result.is_ok():
    print(result.unwrap())
else:
    print(result.error)
```

**Плюсы:**
- Сигнатура `-> Result[float, str]` честная
- Невозможно "забыть" обработать ошибку — результат надо проверить
- Ошибки не "прыгают" — они явно передаются

---

## Аналогия: Коробка с подарком

Представь, что ты заказал посылку. Курьер приносит коробку. Внутри может быть:

1. **Ok** — Твой подарок (успех)
2. **Err** — Записка "Товар закончился" (ошибка)

Ты не можешь узнать, что внутри, пока не откроешь коробку и не проверишь.

```python
# Коробка пришла
result = order_gift("iPhone")

# Открываем и проверяем
if result.is_ok():
    gift = result.unwrap()  # Достаём подарок
    print(f"Ура! Получил {gift}")
else:
    error = result.error    # Читаем записку
    print(f"Облом: {error}")
```

---

## Разбор кода

### Класс `Ok` — Успешный результат

```python
@dataclass(frozen=True)
class Ok(Generic[T]):
    """Успешный результат."""
    value: T  # Значение внутри "коробки"

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        """Достать значение."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Достать значение (default игнорируется)."""
        return self.value

    def map(self, fn: Callable[[T], U]) -> 'Ok[U]':
        """Применить функцию к значению."""
        return Ok(fn(self.value))

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        """Применить функцию, возвращающую Result."""
        return fn(self.value)
```

**`Generic[T]`** — это параметр типа. `Ok[int]` содержит `int`, `Ok[str]` содержит `str`.

---

### Класс `Err` — Ошибка

```python
@dataclass(frozen=True)
class Err(Generic[E]):
    """Ошибка."""
    error: E  # Информация об ошибке

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> None:
        """Попытка достать значение — исключение!"""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Вернуть default, т.к. значения нет."""
        return default

    def map(self, fn: Callable[[T], U]) -> 'Err[E]':
        """Ничего не делаем — ошибка просто пробрасывается."""
        return self

    def flat_map(self, fn: Callable[[T], 'Result[U, E]']) -> 'Err[E]':
        """Ничего не делаем — ошибка просто пробрасывается."""
        return self
```

**Ключевое отличие:** Методы `map` и `flat_map` у `Err` ничего не делают — они просто возвращают ту же ошибку. Это позволяет писать цепочки преобразований.

---

### Type Alias

```python
Result = Union[Ok[T], Err[E]]
```

`Result[int, str]` — это либо `Ok[int]`, либо `Err[str]`.

---

## Методы и их назначение

### `is_ok()` / `is_err()` — Проверка типа

```python
result = divide(10, 2)

if result.is_ok():
    print("Успех!")
elif result.is_err():
    print("Ошибка!")
```

---

### `unwrap()` — Достать значение (опасно!)

```python
ok_result = Ok(42)
ok_result.unwrap()  # → 42

err_result = Err("oops")
err_result.unwrap()  # ValueError: Called unwrap on Err: oops
```

**Аналогия:** Как открыть коробку и схватить содержимое, не глядя. Если там записка об ошибке — больно ударишься.

**Когда использовать:** Только когда ты **уверен**, что это `Ok`:

```python
if result.is_ok():
    value = result.unwrap()  # Безопасно — мы проверили
```

---

### `unwrap_or(default)` — Достать или вернуть default

```python
Ok(42).unwrap_or(0)      # → 42
Err("oops").unwrap_or(0) # → 0
```

**Аналогия:** "Дай мне подарок, а если его нет — дай хотя бы конфету".

**Когда использовать:** Когда есть разумное значение по умолчанию:

```python
# Получить черновик или пустую строку
code = get_draft(user_id, problem_id).unwrap_or("")
```

---

### `map(fn)` — Преобразовать значение

```python
Ok(5).map(lambda x: x * 2)      # → Ok(10)
Err("oops").map(lambda x: x * 2) # → Err("oops") — ничего не происходит
```

**Аналогия:** "Если в коробке подарок — заверни его в красивую бумагу. Если записка об ошибке — просто передай дальше".

**Когда использовать:** Для преобразования успешного результата:

```python
# Получить задачу и преобразовать в текст для отображения
result = get_problem(1, repo).map(lambda p: p.title.get("ru"))
# Ok(Problem) → Ok("Сумма двух чисел")
# или
# Err(NotFoundError) → Err(NotFoundError)
```

---

### `flat_map(fn)` — Цепочка операций

```python
def get_user(id: str) -> Result[User, NotFoundError]:
    ...

def get_user_settings(user: User) -> Result[Settings, NotFoundError]:
    ...

# Цепочка: получить пользователя, затем его настройки
result = get_user("123").flat_map(get_user_settings)
```

**Аналогия:** "Если в первой коробке подарок — открой вторую коробку. Если в первой ошибка — не открывай вторую, просто передай ошибку".

**Разница между `map` и `flat_map`:**

```python
# map: функция возвращает обычное значение
Ok(5).map(lambda x: x * 2)  # Ok(10)

# flat_map: функция возвращает Result
Ok(5).flat_map(lambda x: Ok(x * 2) if x > 0 else Err("negative"))  # Ok(10)
```

Если бы мы использовали `map` с функцией, возвращающей `Result`:
```python
Ok(5).map(lambda x: Ok(x * 2))  # Ok(Ok(10)) — вложенный Result!
```

`flat_map` "разворачивает" вложенность.

---

## Паттерн: Match (Python 3.10+)

```python
result = get_problem(42, repo)

match result:
    case Ok(problem):
        print(f"Найдена задача: {problem.title}")
    case Err(NotFoundError() as e):
        print(f"Ошибка: {e.message}")
```

Это самый читаемый способ работы с `Result`.

---

## Реальные примеры из кодовой базы

### В сервисах

```python
# core/services/problems.py
def get_problem(
    problem_id: int,
    repo: IProblemRepository,
) -> Result[Problem, NotFoundError]:
    return repo.get_by_id(problem_id)
```

### В репозиториях

```python
# adapters/storage/json_problem_repository.py
def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
    for problem in self._problems:
        if problem.id == problem_id:
            return Ok(problem)
    return Err(NotFoundError(entity="Problem", id=problem_id))
```

### В CLI

```python
# clients/cli/app.py
result = get_problem(problem_id, self.container.problem_repo)
match result:
    case Ok(problem):
        self.presenter.show_problem(problem)
    case Err(error):
        self.presenter.show_error(str(error))
```

---

## Сравнение подходов

| Аспект | Exceptions | Result Type |
|--------|------------|-------------|
| Сигнатура | Скрывает ошибки | Показывает ошибки |
| Проверка | Опциональная | Обязательная |
| Цепочки | `try/except` вложенные | `map`/`flat_map` |
| Читаемость | Прерывает поток | Линейный поток |
| Типизация | Слабая | Сильная |

---

## Визуальная схема

```
         ┌─────────────────────────────────────┐
         │           Result[T, E]              │
         │  (либо Ok[T], либо Err[E])          │
         └─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ↓                       ↓
   ┌─────────┐             ┌─────────┐
   │  Ok[T]  │             │  Err[E] │
   │         │             │         │
   │ value:T │             │ error:E │
   └─────────┘             └─────────┘
        │                       │
        │ .unwrap() → T         │ .unwrap() → ValueError!
        │ .unwrap_or(d) → T     │ .unwrap_or(d) → d
        │ .map(f) → Ok[U]       │ .map(f) → Err[E]
        │ .flat_map(f) → f(T)   │ .flat_map(f) → Err[E]
        │                       │
        └───────────┬───────────┘
                    ↓
            match result:
                case Ok(value): ...
                case Err(error): ...
```
