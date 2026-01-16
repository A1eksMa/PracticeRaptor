# Context — Рабочий контекст

## Что здесь

**Context** — агрегат, объединяющий Problem-домен и User-домен.

```
context/
└── work_context.py   # WorkContext — рабочий контекст сессии
```

## WorkContext

```python
@dataclass(frozen=True)
class WorkContext:
    """Полный контекст текущей работы."""

    # User-домен (всегда есть)
    user: User
    settings: Settings

    # Problem-домен (опционально)
    problem: Problem | None
    template: ProblemTemplate | None

    # Работа пользователя (опционально)
    draft: Draft | None
```

## Зачем нужен WorkContext?

### Проблема: много отдельных объектов

```python
# Без контекста — передаём много параметров
def submit_solution(
    user: User,
    settings: Settings,
    problem: Problem,
    template: ProblemTemplate,
    draft: Draft,
    code: str,
) -> Submission:
    ...

# Вызов громоздкий
result = submit_solution(user, settings, problem, template, draft, code)
```

### Решение: единый контекст

```python
# С контекстом — один параметр
def submit_solution(context: WorkContext, code: str) -> Submission:
    # Всё доступно через context
    user_id = context.user_id
    problem_title = context.problem.get_title(context.locale)
    test_cases = context.template.test_cases
    ...

# Вызов простой
result = submit_solution(context, code)
```

## Аналогия: Рабочий стол

```
┌─────────────────────────────────────────────────────────────────┐
│                    РАБОЧИЙ СТОЛ (WorkContext)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐ │
│  │  Кто работает   │  │  Над чем работает                    │ │
│  │  (User)         │  │  (Problem + Template)                │ │
│  │                 │  │                                      │ │
│  │  Иван           │  │  Задача: Two Sum                     │ │
│  │  Язык: Python   │  │  Сигнатура: def two_sum(...)         │ │
│  │                 │  │  Тесты: 5 штук                       │ │
│  └─────────────────┘  └──────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Текущая работа (Draft)                                     ││
│  │                                                              ││
│  │  def two_sum(nums, target):                                 ││
│  │      seen = {}                                              ││
│  │      for i, n in enumerate(nums):                           ││
│  │          ...                                                ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Свойства для удобного доступа

```python
context = WorkContext(user=user, settings=settings, problem=problem, template=template)

# User properties
context.user_id                    # 1
context.user_name                  # "john"
context.is_anonymous               # False

# Settings properties
context.locale                     # "en"
context.language                   # Language.EN
context.programming_language       # ProgrammingLanguage.PYTHON

# Problem properties
context.has_problem                # True
context.problem_id                 # 42
context.problem_title              # "Two Sum"

# Template properties
context.has_template               # True
context.signature                  # "def two_sum(...):"
context.test_cases                 # tuple[TestCase, ...]
context.example_tests              # только примеры

# Draft/Code properties
context.has_draft                  # True/False
context.code                       # код из draft или signature
```

## Иммутабельные обновления

```python
# Выбор задачи
context = context.with_problem(problem, template)

# Обновление кода в draft
context = context.with_code("new code")

# Смена настроек
context = context.with_settings(new_settings)

# Сброс задачи
context = context.clear_problem()
```

## Валидация

```python
# Проверка готовности к submit
if context.can_submit():
    request = build_execution_request(context, context.code)
else:
    print("Not ready: no problem or no code")

# Детальная валидация
errors = context.validate()
if errors:
    for error in errors:
        print(f"Validation error: {error}")
```

## Сборка контекста

WorkContext **не хранится** — он собирается при необходимости:

```python
def build_work_context(
    user_id: int,
    problem_id: int | None,
    repos: RepositoryContainer,
) -> WorkContext:
    """Собрать контекст из репозиториев."""

    # User-домен (всегда)
    user = repos.users.get_by_id(user_id)
    settings = repos.settings.get_by_user_id(user_id)

    # Problem-домен (если выбрана задача)
    problem = None
    template = None
    draft = None

    if problem_id:
        problem = repos.problems.get_by_id(problem_id)
        template = repos.templates.get(problem_id, settings.programming_language)
        draft = repos.drafts.get(user_id, problem_id, settings.programming_language)

    return WorkContext(
        user=user,
        settings=settings,
        problem=problem,
        template=template,
        draft=draft,
    )
```

## Примеры использования

### В CLI

```python
# При старте — минимальный контекст
context = WorkContext(user=DEFAULT_USER, settings=DEFAULT_SETTINGS)

# При выборе задачи — добавляем problem
context = context.with_problem(problem, template)

# При вводе кода — обновляем draft
context = context.with_code(user_input)

# При submit — создаём запрос
if context.can_submit():
    request = build_execution_request(context, context.code)
    result = executor.execute(request)
```

### В сервисах

```python
def get_problem_display(context: WorkContext) -> dict:
    """Подготовить данные для отображения задачи."""

    if not context.has_problem:
        raise ValueError("No problem selected")

    return {
        "title": context.problem.get_title(context.locale),
        "description": context.problem.get_description(context.locale),
        "signature": context.signature,
        "examples": [
            {
                "input": ex.input,
                "output": ex.output,
                "explanation": ex.get_explanation(context.locale),
            }
            for ex in context.problem.examples
        ],
        "current_code": context.code,
    }
```

## Тестирование

```python
def test_work_context_properties():
    context = WorkContext(
        user=User(user_id=1, user_name="test"),
        settings=Settings(user_id=1, language=Language.RU),
        problem=problem,
        template=template,
    )

    assert context.user_id == 1
    assert context.locale == "ru"
    assert context.problem_title == problem.get_title("ru")
    assert context.can_submit() == False  # no draft/code

def test_work_context_with_draft():
    context = WorkContext(
        user=user,
        settings=settings,
        problem=problem,
        template=template,
        draft=draft,
    )

    assert context.has_draft
    assert context.code == draft.code
    assert context.can_submit() == True
```
