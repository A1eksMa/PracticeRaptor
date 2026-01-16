# Core — Ядро приложения

## Что здесь

**Core** — это чистая бизнес-логика без внешних зависимостей.

```
core/
├── models/        # ЧТО мы моделируем (Problem, User, WorkContext)
│   ├── problem/   # Problem-домен (статический контент)
│   ├── user/      # User-домен (динамический контент)
│   └── context/   # Рабочий контекст (агрегат)
├── dto/           # КАК общаемся с микросервисами
├── persistence/   # КАК храним (Records, Mappers)
├── ports/         # С ЧЕМ взаимодействуем (интерфейсы)
└── services/      # ЧТО делаем (Use Cases, оркестрация)
```

## Ключевые изменения в v1.8

### Разделение доменов

```
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN MODELS                            │
├────────────────────────────┬────────────────────────────────────┤
│     PROBLEM-ДОМЕН          │          USER-ДОМЕН                │
│     (статический)          │         (динамический)             │
│                            │                                    │
│  • Problem                 │  • User                            │
│  • ProblemSummary          │  • Settings                        │
│  • ProblemTemplate         │  • Draft                           │
│  • Example                 │  • Submission                      │
│  • TestCase (VO)           │  • TestResult (VO)                 │
│  • CanonicalSolution (VO)  │                                    │
│  • LocalizedText (VO)      │                                    │
└────────────────────────────┴────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   WORK CONTEXT   │
                    │   (агрегат)      │
                    └──────────────────┘
```

### Слой DTO

```
WorkContext + code                ExecutionResult
       │                                │
       ▼                                ▼
ExecutionRequest ──► [Executor] ──► Submission
       │                                │
       └── JSON API ────────────────────┘
```

## Правило

**Core не знает о внешнем мире:**
- Не импортирует `json`, `sqlite3`, `requests`
- Не читает файлы
- Не делает HTTP-запросы
- Не знает, где хранятся данные

## Аналогия: Ресторан

| Папка | Роль | Что делает |
|-------|------|------------|
| `models/problem/` | Меню | Описание блюд, ингредиенты, рецепты |
| `models/user/` | Заказы гостей | Кто заказал, что готовится, что подано |
| `models/context/` | Стол с заказом | Гость + его заказ + текущее блюдо |
| `dto/` | Накладные для кухни | Что передать повару, что получить обратно |
| `persistence/` | Журналы учёта | Как записывать заказы в книги |
| `ports/` | Должностные инструкции | Кто должен что делать |
| `services/` | Повар | Готовит по правилам |

## Зависимости

```
models/
├── problem/         ← ничего не импортирует из core
├── user/            ← импортирует problem (для Draft, Submission)
└── context/         ← импортирует problem и user
    ↑
dto/                 ← импортирует models (для конвертации)
    ↑
persistence/         ← импортирует models (для маппинга)
    ↑
ports/               ← импортирует models (для типов)
    ↑
services/            ← импортирует models и ports
```

## Пример использования

```python
from core.models import Problem, User, WorkContext, ProblemTemplate
from core.models import Difficulty, ExecutionStatus
from core.dto import ExecutionRequest, build_execution_request
from core.persistence import ProblemRecord, SubmissionRecord

# Domain — создаём объект напрямую (для тестов)
problem = Problem(
    id=1,
    title=LocalizedText({"en": "Two Sum", "ru": "Два числа"}),
    difficulty=Difficulty.EASY,
    ...
)

# Context — собираем рабочий контекст
context = WorkContext(
    user=user,
    settings=settings,
    problem=problem,
    template=template,
)

# DTO — создаём запрос к executor
request = build_execution_request(context, user_code)

# Persistence — работаем с записями
record = SubmissionRecord(
    submission_id=1,
    user_id=context.user_id,
    problem_id=context.problem_id,
    ...
)
```

## Тестирование

Core тестируется **без I/O**:

```python
def test_work_context():
    context = WorkContext(
        user=User(user_id=1, user_name="test"),
        settings=Settings(user_id=1),
        problem=problem,
        template=template,
    )

    assert context.problem_title == "Two Sum"
    assert context.can_submit() == False  # no code yet

def test_execution_request():
    request = build_execution_request(context, "def solution(): pass")

    assert request.user_id == 1
    assert request.language == "python3"
    assert len(request.test_cases) > 0
```

Не нужны моки файловой системы или базы данных — это чистая логика.
