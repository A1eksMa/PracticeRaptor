# models.py — Доменные модели

**Путь:** `practiceraptor/core/domain/models.py`

Этот файл описывает **что такое данные** в системе. Никакой логики — только структуры.

---

## Ключевая конструкция: `@dataclass(frozen=True)`

```python
@dataclass(frozen=True)
class LocalizedText:
    translations: dict[str, str]
```

**Аналогия:** Представь, что ты делаешь формочку для печенья. `@dataclass` — это формочка. Она говорит: "Вот какой формы будут данные".

**`frozen=True`** — это как заморозить печенье после выпечки. Нельзя изменить форму, нельзя откусить кусочек. Объект создан — и всё, он навечно такой.

```python
text = LocalizedText({"en": "Hello", "ru": "Привет"})
text.translations["fr"] = "Bonjour"  # ОШИБКА! Нельзя изменять
```

**Зачем это нужно?**
- Безопасность: никто случайно не испортит данные
- Предсказуемость: если передал объект в функцию — он не изменится
- Отладка: легче искать баги, когда данные не мутируют

---

## Value Objects vs Entities

В файле есть два типа объектов:

### Value Objects (Объекты-значения)

```python
class LocalizedText    # Текст с переводами
class Example          # Пример входа/выхода
class TestCase         # Тестовый случай
class Solution         # Эталонное решение
class LanguageSpec     # Спецификация языка
```

**Аналогия:** Это как **деньги**. Тебе не важно, какая именно купюра 100 рублей — важна только сумма. Две купюры по 100 рублей равны.

```python
text1 = LocalizedText({"en": "Hi"})
text2 = LocalizedText({"en": "Hi"})
# text1 == text2  →  True (одинаковое содержимое = равны)
```

### Entities (Сущности)

```python
class Problem      # Задача
class User         # Пользователь
class Draft        # Черновик
class Submission   # Решение
class Progress     # Прогресс
```

**Аналогия:** Это как **люди**. У каждого человека есть уникальный ID (паспорт). Даже если два человека — полные тёзки, они разные люди.

```python
user1 = User(id="123", locale="en")
user2 = User(id="456", locale="en")
# user1 == user2  →  False (разные ID = разные сущности)
```

---

## Разбор каждого класса

### 1. `LocalizedText` — Мультиязычный текст

```python
@dataclass(frozen=True)
class LocalizedText:
    translations: dict[str, str] = field(default_factory=dict)

    def get(self, locale: str, fallback: str = "en") -> str:
        return self.translations.get(locale, self.translations.get(fallback, ""))
```

**Аналогия:** Это как **словарь-разговорник**. Спрашиваешь слово на русском — он даёт перевод. Нет русского? Даст английский.

```python
title = LocalizedText({"en": "Two Sum", "ru": "Сумма двух"})

title.get("ru")      # → "Сумма двух"
title.get("fr")      # → "Two Sum" (fallback на английский)
title.get("fr", "ru") # → "Сумма двух" (fallback на русский)
```

**`field(default_factory=dict)`** — это хитрость Python. Нельзя писать `translations: dict = {}`, потому что тогда ВСЕ объекты будут разделять один и тот же словарь (известный баг Python). `default_factory` создаёт новый словарь для каждого объекта.

---

### 2. `Example` — Пример задачи

```python
@dataclass(frozen=True)
class Example:
    input: dict[str, Any]              # {"nums": [2, 7], "target": 9}
    output: Any                         # [0, 1]
    explanation: LocalizedText | None   # Пояснение (опционально)
```

**Аналогия:** Это как **образец в инструкции IKEA**. "Вот входные детали, вот что должно получиться, вот пояснение".

```python
example = Example(
    input={"nums": [2, 7, 11, 15], "target": 9},
    output=[0, 1],
    explanation=LocalizedText({"en": "nums[0] + nums[1] = 9"})
)
```

**`dict[str, Any]`** — словарь, где ключи строки, а значения — что угодно (`Any`). Это гибкость: разные задачи имеют разные входные параметры.

---

### 3. `TestCase` — Тестовый случай

```python
@dataclass(frozen=True)
class TestCase:
    input: dict[str, Any]
    expected: Any
    description: str | None = None
    is_hidden: bool = False
```

**Отличие от Example:**
- `Example` — для показа пользователю (с объяснением)
- `TestCase` — для проверки кода (с флагом `is_hidden`)

**`is_hidden=True`** — скрытые тесты. Пользователь не видит их, но код должен их пройти. Защита от хардкода ответов.

**Аналогия:** На экзамене есть примеры задач (Example) и настоящие задания (TestCase). Некоторые задания секретные (`is_hidden`).

---

### 4. `Solution` — Эталонное решение

```python
@dataclass(frozen=True)
class Solution:
    name: str          # "Hash Map"
    complexity: str    # "O(n)"
    code: str          # Код решения
```

**Аналогия:** Это как **ответы в конце учебника**. Название подхода, его сложность, и сам код.

---

### 5. `LanguageSpec` — Спецификация языка

```python
@dataclass(frozen=True)
class LanguageSpec:
    language: Language                  # python3, go, java...
    function_signature: str             # "def two_sum(nums, target):"
    solutions: tuple[Solution, ...] = ()
```

**Зачем нужно?** Одна задача может решаться на разных языках. У каждого языка своя сигнатура функции и свои эталонные решения.

```python
python_spec = LanguageSpec(
    language=Language.PYTHON,
    function_signature="def two_sum(nums: list[int], target: int) -> list[int]:",
    solutions=(Solution(name="Hash Map", complexity="O(n)", code="..."),)
)
```

**`tuple[Solution, ...]`** — кортеж из любого количества `Solution`. Почему `tuple`, а не `list`? Потому что `frozen=True` требует неизменяемых коллекций.

---

### 6. `Problem` — Главная сущность: Задача

```python
@dataclass(frozen=True)
class Problem:
    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    tags: tuple[str, ...]              # ("array", "hash-table")
    examples: tuple[Example, ...]
    test_cases: tuple[TestCase, ...]
    languages: tuple[LanguageSpec, ...]
    hints: tuple[LocalizedText, ...]

    def get_language_spec(self, language: Language) -> LanguageSpec | None:
        for spec in self.languages:
            if spec.language == language:
                return spec
        return None
```

**Аналогия:** Это как **карточка задачи на LeetCode**:
- `id` — номер задачи
- `title` — название (на разных языках)
- `description` — условие
- `difficulty` — сложность (easy/medium/hard)
- `tags` — теги для поиска
- `examples` — примеры для понимания
- `test_cases` — тесты для проверки
- `languages` — поддерживаемые языки
- `hints` — подсказки

**Метод `get_language_spec`** — найти спецификацию для конкретного языка. Если задача не поддерживает Go — вернёт `None`.

---

### 7. `User` — Пользователь

```python
@dataclass(frozen=True)
class User:
    id: str
    locale: str = "en"
    preferred_language: Language = Language.PYTHON
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())
```

**`__post_init__`** — хук, который вызывается после создания объекта. Здесь он автоматически ставит время создания.

**Хитрость с `object.__setattr__`:** Объект `frozen`, поэтому нельзя просто написать `self.created_at = datetime.now()`. Приходится использовать низкоуровневый метод `object.__setattr__`.

---

### 8. `Draft` — Черновик

```python
@dataclass(frozen=True)
class Draft:
    user_id: str
    problem_id: int
    language: Language
    code: str
    updated_at: datetime
```

**Аналогия:** Это как **автосохранение в Google Docs**. Пользователь пишет код, система периодически сохраняет черновик. Если закрыл браузер — код не потеряется.

**Ключ черновика:** `(user_id, problem_id, language)` — уникальная комбинация. У одного пользователя может быть черновик на Python и отдельный на Go.

---

### 9. `Submission` — Успешное решение

```python
@dataclass(frozen=True)
class Submission:
    id: str
    user_id: str
    problem_id: int
    language: Language
    code: str
    execution_time_ms: int
    memory_used_kb: int
    created_at: datetime
```

**Аналогия:** Это как **сданная работа на экзамене**. Записывается код, время выполнения, использованная память, когда сдано.

---

### 10. `Progress` — Прогресс пользователя

```python
@dataclass(frozen=True)
class Progress:
    user_id: str
    problem_id: int
    status: ProgressStatus              # not_started, in_progress, solved
    attempts: int = 0
    solved_languages: tuple[Language, ...] = ()
    first_solved_at: datetime | None = None
```

**Аналогия:** Это как **журнал успеваемости**:
- `status` — статус (не начал, в процессе, решил)
- `attempts` — сколько попыток сделал
- `solved_languages` — на каких языках решил
- `first_solved_at` — когда впервые решил

---

### 11-12. `TestResult` и `ExecutionResult` — Результаты выполнения

```python
@dataclass(frozen=True)
class TestResult:
    test_case: TestCase
    passed: bool
    actual: Any = None           # Что вернула функция
    execution_time_ms: int = 0
    error_message: str | None = None

@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    test_results: tuple[TestResult, ...]
    total_time_ms: int = 0
    memory_used_kb: int = 0
    error: str | None = None

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.test_results if r.passed)
```

**Аналогия:**
- `TestResult` — результат одного вопроса теста (правильно/неправильно)
- `ExecutionResult` — итоговая оценка за весь тест

**`@property`** — делает метод похожим на атрибут. Вместо `result.passed_count()` пишем `result.passed_count`.

---

## Визуальная схема связей

```
Problem
├── title: LocalizedText
├── description: LocalizedText
├── difficulty: Difficulty (enum)
├── tags: tuple[str]
├── examples: tuple[Example]
│   └── explanation: LocalizedText
├── test_cases: tuple[TestCase]
├── languages: tuple[LanguageSpec]
│   ├── language: Language (enum)
│   └── solutions: tuple[Solution]
└── hints: tuple[LocalizedText]

User ──────┬──── Draft (черновик)
           ├──── Submission (решение)
           └──── Progress (прогресс)

ExecutionResult
└── test_results: tuple[TestResult]
    └── test_case: TestCase
```
