# User — Домен пользователя

## Что здесь

**User-домен** — динамический контент, создаваемый пользователями.
Эти модели зависят от Problem-домена.

```
user/
├── user.py           # User — сущность пользователя
├── settings.py       # Settings, FilterState — настройки
├── draft.py          # Draft — черновик решения
└── submission.py     # Submission, TestResult — результат
```

## Модели

### User

```python
@dataclass(frozen=True)
class User:
    """Пользователь системы."""

    user_id: int
    user_name: str
    hash_password: str

    @property
    def is_anonymous(self) -> bool:
        return self.user_id == 0

# Гость для CLI
DEFAULT_USER = User(user_id=0, user_name="guest")
```

### Settings

```python
@dataclass(frozen=True)
class Settings:
    """Настройки пользователя."""

    user_id: int

    # Постоянные настройки
    language: Language                    # UI язык (en, ru)
    programming_language: ProgrammingLanguage  # python3, java
    text_editor: TextEditor               # vim, nano, code

    # Сессионное состояние
    filters: FilterState                  # текущие фильтры
```

### Draft (Богатая модель)

```python
@dataclass(frozen=True)
class Draft:
    """Черновик решения — богатая модель с вложенными объектами."""

    draft_id: int
    user: User                    # ← полный объект
    problem: Problem              # ← полный объект
    template: ProblemTemplate     # ← полный объект
    code: str                     # код пользователя
    created_at: datetime
    updated_at: datetime
```

### Submission (Богатая модель)

```python
@dataclass(frozen=True)
class Submission:
    """Результат выполнения — богатая модель."""

    submission_id: int
    user: User                    # ← полный объект
    problem: Problem              # ← полный объект
    template: ProblemTemplate     # ← полный объект
    code: str
    result: ExecutionStatus       # accepted, wrong_answer, ...
    total_time_ms: int
    memory_used_kb: int
    test_results: tuple[TestResult, ...]
    error_message: str | None
    created_at: datetime
```

## Зачем богатые модели?

### Проблема: плоские модели требуют дополнительных запросов

```python
# Плоская модель (как в Records)
@dataclass
class DraftRecord:
    user_id: int       # только ID
    problem_id: int    # только ID
    code: str

# Чтобы показать информацию, нужны дополнительные запросы
draft = repo.get_draft(draft_id)
user = user_repo.get(draft.user_id)           # ещё запрос
problem = problem_repo.get(draft.problem_id)  # ещё запрос
template = template_repo.get(...)             # ещё запрос

print(f"{user.user_name} solving {problem.title.get('en')}")
```

### Решение: богатые модели с вложенными объектами

```python
# Богатая модель (Domain)
draft = repo.get_draft(draft_id)  # один вызов, всё внутри

# Прямой доступ без дополнительных запросов
print(f"{draft.user.user_name} solving {draft.problem.title.get('en')}")
print(f"Language: {draft.template.language.value}")
print(f"Signature: {draft.template.signature}")
```

## Аналогия: Заказ в ресторане

```
┌─────────────────────────────────────────────────────────────────┐
│                          ЗАКАЗ (Draft)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Гость:     Иван Петров (User)                                  │
│  Блюдо:     Борщ с пампушками (Problem)                         │
│  Рецепт:    Классический рецепт (ProblemTemplate)               │
│  Процесс:   Нарезаны овощи, варится бульон (code)               │
│                                                                  │
│  Всё в одном месте — не нужно искать по отдельности            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## TestResult

```python
@dataclass(frozen=True)
class TestResult:
    """Результат одного теста (Value Object)."""

    test_index: int
    status: ExecutionStatus    # accepted, wrong_answer, ...
    time_ms: int
    memory_kb: int
    error_message: str | None

    @property
    def passed(self) -> bool:
        return self.status == ExecutionStatus.ACCEPTED
```

## Примеры использования

### Создание Draft

```python
from core.models import User, Problem, ProblemTemplate, Draft
from core.models.user.draft import create_draft

# Через фабричную функцию
draft = create_draft(
    draft_id=1,
    user=user,
    problem=problem,
    template=template,
    code="def two_sum(nums, target): pass",
)

# Или напрямую
draft = Draft(
    draft_id=1,
    user=user,
    problem=problem,
    template=template,
    code="def two_sum(nums, target): pass",
    created_at=datetime.now(),
    updated_at=datetime.now(),
)
```

### Работа с Draft

```python
# Удобный доступ к вложенным данным
print(draft.user.user_name)           # "john"
print(draft.problem.get_title("ru"))  # "Два числа"
print(draft.template.signature)       # "def two_sum(...):"
print(draft.language)                 # ProgrammingLanguage.PYTHON (shortcut)

# Иммутабельное обновление кода
new_draft = draft.with_code("def two_sum(nums, target): return []")

assert draft.code != new_draft.code   # старый не изменился
assert new_draft.updated_at > draft.updated_at
```

### Работа с Submission

```python
from core.models import Submission, TestResult, ExecutionStatus

submission = Submission(
    submission_id=1,
    user=user,
    problem=problem,
    template=template,
    code="def two_sum(nums, target): ...",
    result=ExecutionStatus.ACCEPTED,
    total_time_ms=45,
    memory_used_kb=2048,
    test_results=(
        TestResult(test_index=0, status=ExecutionStatus.ACCEPTED, time_ms=10, memory_kb=512),
        TestResult(test_index=1, status=ExecutionStatus.ACCEPTED, time_ms=15, memory_kb=512),
    ),
    error_message=None,
    created_at=datetime.now(),
)

# Анализ результатов
if submission.is_accepted:
    print(f"Solved in {submission.total_time_ms}ms")
else:
    print(f"Failed: {submission.passed_count}/{submission.total_count} tests")
    failed = submission.first_failed
    if failed:
        print(f"First failure at test {failed.test_index}: {failed.error_message}")
```

## Связь с Records

Богатые модели **собираются из плоских Records** через Mappers:

```
┌─────────────────┐     ┌─────────────────┐
│   DraftRecord   │     │      Draft      │
│  ─────────────  │     │  ─────────────  │
│  user_id: 1     │     │  user: User     │
│  problem_id: 42 │ ──► │  problem: Prob  │
│  code: "..."    │     │  template: Tmpl │
└─────────────────┘     │  code: "..."    │
                        └─────────────────┘
        ↑                       ↑
    Storage                  Domain
  (для хранения)         (для логики)
```

## Тестирование

```python
def test_draft_with_code():
    draft = create_draft(1, user, problem, template, "code1")
    new_draft = draft.with_code("code2")

    assert draft.code == "code1"
    assert new_draft.code == "code2"
    assert new_draft.updated_at > draft.updated_at

def test_submission_analysis():
    submission = Submission(
        ...,
        result=ExecutionStatus.WRONG_ANSWER,
        test_results=(
            TestResult(0, ExecutionStatus.ACCEPTED, 10, 512),
            TestResult(1, ExecutionStatus.WRONG_ANSWER, 15, 512, "Expected 5, got 3"),
        ),
    )

    assert not submission.is_accepted
    assert submission.passed_count == 1
    assert submission.failed_count == 1
    assert submission.first_failed.test_index == 1
```
