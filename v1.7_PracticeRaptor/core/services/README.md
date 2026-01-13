# Services — Use Cases

## Что здесь

**Services** — это чистые функции, которые оркестрируют бизнес-логику.

```
services/
└── problems.py    # get_problem, get_problem_summaries, get_random_problem
```

## Зачем нужен этот слой?

### Проблема: логика размазана по клиентам

```python
# Плохо — одна и та же логика в CLI и в Telegram
# cli/commands/problems.py
def cmd_random():
    problems = repo.get_all_summaries(difficulty="easy")
    available = [p for p in problems if p.id not in solved_ids]
    chosen = random.choice(available)
    problem = repo.get_by_id(chosen.id)
    ...

# telegram/handlers/problems.py
def handle_random():
    problems = repo.get_all_summaries(difficulty="easy")  # ← копипаста
    available = [p for p in problems if p.id not in solved_ids]
    chosen = random.choice(available)
    problem = repo.get_by_id(chosen.id)
    ...
```

### Решение: вынести в services

```python
# Хорошо — логика в одном месте
# core/services/problems.py
def get_random_problem(repo, difficulty, exclude_ids):
    summaries = repo.get_all_summaries(difficulty=difficulty)
    available = [s for s in summaries if s.id not in exclude_ids]
    if not available:
        return None
    chosen = random.choice(available)
    return repo.get_by_id(chosen.id)

# cli/commands/problems.py
def cmd_random():
    problem = get_random_problem(repo, Difficulty.EASY, solved_ids)
    ...

# telegram/handlers/problems.py
def handle_random():
    problem = get_random_problem(repo, Difficulty.EASY, solved_ids)  # ← тот же вызов
    ...
```

## Место в архитектуре

```
┌─────────────────────────────────────────────────────────────┐
│  CLI / Telegram / Web                                       │
│  "Интерфейс пользователя"                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓ вызывают
┌─────────────────────────────────────────────────────────────┐
│  SERVICES                           ← этот слой             │
│  "Что делать" (use cases)                                   │
│  get_problem(), get_random_problem(), format_for_display()  │
└─────────────────────────────────────────────────────────────┘
                            ↓ используют
┌─────────────────────────────────────────────────────────────┐
│  PORTS (interfaces)                                         │
│  IProblemRepository                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓ реализуют
┌─────────────────────────────────────────────────────────────┐
│  ADAPTERS                                                   │
│  JsonProblemRepository, SqliteProblemRepository             │
└─────────────────────────────────────────────────────────────┘
```

## Аналогия: Ресторан

| Слой | Роль | Что делает |
|------|------|------------|
| **CLI/Web** | Официант | Принимает заказ, отдаёт блюдо |
| **Services** | Повар | Готовит блюдо по рецепту |
| **Ports** | Требования к продуктам | "Нужно мясо, овощи" |
| **Adapters** | Поставщики | "Мясо от фермера А, овощи с рынка Б" |
| **Domain** | Ингредиенты и рецепты | Что такое "мясо", как готовить |

**Повар (services):**
- Не знает, откуда продукты (JSON или SQL)
- Знает рецепт (бизнес-логику)
- Получает продукты через интерфейс (ports)

## Характеристики функций

### 1. Чистые функции (Pure Functions)

```python
def get_problem(problem_id: int, repo: IProblemRepository, locale: str) -> Problem | None:
    return repo.get_by_id(problem_id, locale)
```

- **Нет глобального состояния** — всё через параметры
- **Нет side effects** — side effects в repo, не в функции
- **Детерминированность** — одни входы → один выход

### 2. Dependency Injection

```python
def get_random_problem(
    repo: IProblemRepository,  # ← зависимость передаётся
    locale: str = "en",
    difficulty: Difficulty | None = None,
) -> Problem | None:
    ...
```

- Репозиторий **передаётся**, не создаётся внутри
- Можно подставить любую реализацию
- Легко тестировать с mock

### 3. Композиция

```python
def get_random_problem(repo, locale, difficulty, exclude_ids):
    # Использует другой service
    summaries = get_problem_summaries(repo, locale, difficulty)

    # Своя логика
    available = [s for s in summaries if s.id not in exclude_ids]
    if not available:
        return None

    # Использует repo напрямую
    chosen = random.choice(available)
    return repo.get_by_id(chosen.id, locale)
```

## Примеры использования

### В CLI

```python
from core.services import get_problem, get_problem_summaries, format_problem_for_display
from adapters.storage.json import JsonProblemRepository

repo = JsonProblemRepository(Path("data/json"))

# Список задач
summaries = get_problem_summaries(repo, locale="ru", difficulty=Difficulty.EASY)
for s in summaries:
    print(f"[{s.difficulty.value}] {s.title}")

# Выбор задачи
problem = get_problem(1, repo, locale="ru")
if problem:
    display = format_problem_for_display(problem, locale="ru")
    print(display.title)
    print(display.description)
```

### В тестах

```python
class MockProblemRepository:
    def __init__(self, problems: list[Problem]):
        self._problems = {p.id: p for p in problems}

    def get_by_id(self, problem_id: int, locale: str) -> Problem | None:
        return self._problems.get(problem_id)

    def get_all_summaries(self, **kwargs) -> list[ProblemSummary]:
        return [p.to_summary() for p in self._problems.values()]

def test_get_random_excludes_ids():
    mock_repo = MockProblemRepository([
        Problem(id=1, ...),
        Problem(id=2, ...),
        Problem(id=3, ...),
    ])

    # Исключаем 1 и 2 — должен вернуть 3
    result = get_random_problem(mock_repo, exclude_ids=[1, 2])

    assert result is not None
    assert result.id == 3
```

## Что НЕ должно быть в services

| Не должно | Почему | Где должно быть |
|-----------|--------|-----------------|
| `json.load()` | I/O операция | Adapters |
| `sqlite3.connect()` | I/O операция | Adapters |
| `print()` | Side effect | CLI/Web |
| Глобальные переменные | Нарушает чистоту | DI Container |
| HTTP-запросы | I/O операция | Adapters |

## Резюме

| Аспект | Описание |
|--------|----------|
| **Что** | Чистые функции для бизнес-логики |
| **Зачем** | Единая точка входа, нет дублирования |
| **Как** | Dependency Injection, композиция |
| **Где** | `core/services/` |
| **Тестирование** | Mock-репозитории, без I/O |
