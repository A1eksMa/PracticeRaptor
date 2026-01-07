# enums.py — Перечисления

**Путь:** `practiceraptor/core/domain/enums.py`

Этот файл содержит **перечисления (enums)** — фиксированные наборы допустимых значений.

---

## Зачем нужны Enum?

**Аналогия:** Представь светофор. У него только три состояния: красный, жёлтый, зелёный. Не бывает "синего" или "фиолетового" сигнала. Enum — это способ сказать: "Вот все возможные варианты, других не существует".

**Без Enum:**
```python
difficulty = "esay"  # Опечатка! Программа не заметит
```

**С Enum:**
```python
difficulty = Difficulty.ESAY  # Ошибка компиляции! Такого значения нет
difficulty = Difficulty.EASY  # Правильно
```

---

## Особенность: `str, Enum`

```python
class Difficulty(str, Enum):
    EASY = "easy"
```

**Почему наследуем от `str`?**

Это делает enum совместимым со строками:

```python
# Без str:
Difficulty.EASY == "easy"  # False

# С str:
Difficulty.EASY == "easy"  # True
```

**Зачем это нужно?**
- Легко сериализовать в JSON: `json.dumps(Difficulty.EASY)` → `"easy"`
- Легко читать из JSON/YAML конфигов
- Совместимость с базами данных (хранится как строка)

---

## Разбор каждого Enum

### 1. `Difficulty` — Сложность задачи

```python
class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
```

**Аналогия:** Как уровни сложности в игре — лёгкий, средний, сложный.

**Использование:**
```python
problem.difficulty = Difficulty.EASY

# Фильтрация задач по сложности
easy_problems = [p for p in problems if p.difficulty == Difficulty.EASY]

# В JSON файле задачи:
# "difficulty": "easy"
```

---

### 2. `Language` — Язык программирования

```python
class Language(str, Enum):
    PYTHON = "python3"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"
```

**Почему `PYTHON = "python3"`, а не `"python"`?**

Чтобы явно указать версию Python 3. Это важно для исполнителя кода — он должен знать, какой интерпретатор запускать.

**Использование:**
```python
user.preferred_language = Language.PYTHON

# Получить спецификацию задачи для Python:
spec = problem.get_language_spec(Language.PYTHON)

# В JSON:
# "language": "python3"
```

**Расширяемость:** Добавить новый язык просто:
```python
class Language(str, Enum):
    ...
    RUST = "rust"
    CPP = "cpp"
```

---

### 3. `SubmissionStatus` — Статус решения

```python
class SubmissionStatus(str, Enum):
    ACCEPTED = "accepted"           # Принято (все тесты пройдены)
    WRONG_ANSWER = "wrong_answer"   # Неверный ответ
    RUNTIME_ERROR = "runtime_error" # Ошибка выполнения
    TIMEOUT = "timeout"             # Превышено время
    MEMORY_LIMIT = "memory_limit"   # Превышена память
```

**Аналогия:** Как вердикт судьи на соревновании по программированию.

**Жизненный цикл решения:**
```
Пользователь отправляет код
           ↓
    Код компилируется
           ↓
   ┌───────┴───────┐
   ↓               ↓
Ошибка        Запуск тестов
синтаксиса          ↓
                ┌───┴───┐
                ↓       ↓
           Все тесты   Провал
           прошли        ↓
                ↓    ┌───┴───┬─────────┐
           ACCEPTED  ↓       ↓         ↓
                  WRONG   TIMEOUT   RUNTIME
                  ANSWER            ERROR
```

---

### 4. `ProgressStatus` — Прогресс пользователя

```python
class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"  # Не начинал
    IN_PROGRESS = "in_progress"  # В процессе (есть попытки, но не решил)
    SOLVED = "solved"            # Решил
```

**Аналогия:** Как статус задачи в Trello — "To Do", "In Progress", "Done".

**Переходы состояний:**
```
NOT_STARTED ──(первая попытка)──→ IN_PROGRESS ──(успех)──→ SOLVED
                                       ↑                      │
                                       └──(новая попытка)─────┘
                                         (статус не меняется)
```

**Важно:** Если задача уже `SOLVED`, неудачная попытка на другом языке не меняет статус обратно на `IN_PROGRESS`.

---

## Как работать с Enum

### Получить значение
```python
Difficulty.EASY.value  # → "easy"
Language.PYTHON.value  # → "python3"
```

### Создать из строки
```python
Difficulty("easy")     # → Difficulty.EASY
Language("python3")    # → Language.PYTHON

Difficulty("invalid")  # ValueError: 'invalid' is not a valid Difficulty
```

### Итерация по всем значениям
```python
for diff in Difficulty:
    print(diff.value)
# easy
# medium
# hard
```

### Проверка принадлежности
```python
"easy" in [d.value for d in Difficulty]  # True
Difficulty.EASY in Difficulty            # True
```

---

## Визуальная схема

```
Difficulty              Language              SubmissionStatus        ProgressStatus
┌──────────┐           ┌─────────────┐       ┌────────────────┐      ┌──────────────┐
│ EASY     │           │ PYTHON      │       │ ACCEPTED       │      │ NOT_STARTED  │
│ MEDIUM   │           │ GO          │       │ WRONG_ANSWER   │      │ IN_PROGRESS  │
│ HARD     │           │ JAVA        │       │ RUNTIME_ERROR  │      │ SOLVED       │
└──────────┘           │ JAVASCRIPT  │       │ TIMEOUT        │      └──────────────┘
                       └─────────────┘       │ MEMORY_LIMIT   │
                                             └────────────────┘
```

---

## Почему Enum лучше строковых констант

| Аспект | Строки | Enum |
|--------|--------|------|
| Опечатки | Не отловит | Ошибка компиляции |
| Автодополнение | Нет | Да (IDE подскажет) |
| Документация | Надо искать | Все значения в одном месте |
| Рефакторинг | Опасно | Безопасно |
| Type hints | `str` (слабо) | `Difficulty` (строго) |
