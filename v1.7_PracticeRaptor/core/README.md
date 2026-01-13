# Core — Ядро приложения

## Что здесь

**Core** — это чистая бизнес-логика без внешних зависимостей.

```
core/
├── domain/        # ЧТО мы моделируем (Problem, Solution, User)
├── persistence/   # КАК храним (Records, Mappers)
└── ports/         # С ЧЕМ взаимодействуем (интерфейсы)
```

## Правило

**Core не знает о внешнем мире:**
- Не импортирует `json`, `sqlite3`, `requests`
- Не читает файлы
- Не делает HTTP-запросы
- Не знает, где хранятся данные

## Аналогия: Бухгалтерия

| Папка | Аналогия | Что делает |
|-------|----------|------------|
| `domain/` | Правила учёта | Что такое "счёт", "проводка", "баланс" |
| `persistence/` | Формы документов | Как заполнять журналы и ведомости |
| `ports/` | Должностные инструкции | Кто должен подавать документы |

Бухгалтерия не знает, откуда придут первичные документы — из почты, факса или курьером. Она знает только правила обработки.

## Зависимости

```
domain/          ← ничего не импортирует из core
    ↑
persistence/     ← импортирует domain
    ↑
ports/           ← импортирует domain (для типов в интерфейсах)
```

## Пример использования

```python
from core.domain import Problem, LocalizedText, Difficulty
from core.persistence.mappers import records_to_problem
from core.ports import IProblemRepository

# Domain — создаём объект напрямую (для тестов)
problem = Problem(
    id=1,
    title=LocalizedText({"en": "Two Sum", "ru": "Два числа"}),
    difficulty=Difficulty.EASY,
    ...
)

# Persistence — преобразуем records в domain
problem = records_to_problem(problem_rec, title_recs, ...)

# Ports — типизируем зависимости
def my_service(repo: IProblemRepository):
    problem = repo.get_by_id(1)
    ...
```

## Тестирование

Core тестируется **без I/O**:

```python
def test_problem_title():
    problem = Problem(
        id=1,
        title=LocalizedText({"en": "Test", "ru": "Тест"}),
        ...
    )
    assert problem.title.get("ru") == "Тест"
    assert problem.title.get("de") == "Test"  # fallback to en
```

Не нужны моки файловой системы или базы данных — это чистая логика.
