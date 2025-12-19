# PracticeRaptor: Roadmap

## Видение проекта

**PracticeRaptor** — платформа для отработки практических навыков программирования через короткие алгоритмические задания. Быстрые, хваткие, точные упражнения для развития coding skills.

### Стратегия развития

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            КЛИЕНТЫ                                       │
├──────────────┬──────────────┬──────────────┬───────────────────────────┤
│     CLI      │   Telegram   │  Web-сайт    │   Embeddable Widget       │
│  (standalone │     Bot      │              │  (для учебных платформ)   │
│  open-source)│              │              │                           │
└──────────────┴───────┬──────┴───────┬──────┴─────────────┬─────────────┘
                       │              │                    │
                       └──────────────┴────────────────────┘
                                      │
                       ┌──────────────▼──────────────┐
                       │      ЕДИНОЕ ЯДРО (Core)     │
                       │                             │
                       │  • Domain Models            │
                       │  • Business Logic           │
                       │  • Repository Interfaces    │
                       │  • Executor Interfaces      │
                       └──────────────┬──────────────┘
                                      │
                       ┌──────────────▼──────────────┐
                       │         АДАПТЕРЫ            │
                       ├─────────────────────────────┤
                       │ Storage:    JSON│SQLite│PG  │
                       │ Executor:   Local│Docker│API│
                       │ Auth:       Anon│Token│OAuth│
                       └─────────────────────────────┘
```

### Модели распространения

| Интерфейс | Модель | Описание |
|-----------|--------|----------|
| CLI | Open-source | Бесплатно, standalone, для гиков |
| Telegram Bot | Freemium | Бесплатные базовые задачи + подписка |
| Web | Freemium | Бесплатные базовые задачи + подписка |
| Widget | B2B | Интеграция в учебные платформы |

---

## Архитектурные принципы

1. **Ядро независимо от интерфейса** — вся бизнес-логика в core, клиенты — тонкие обёртки
2. **Переключаемые хранилища** — JSON → SQLite → PostgreSQL через конфигурацию
3. **Изолированное выполнение** — executor как отдельный сервис (local/docker/remote)
4. **Функциональный паритет** — все интерфейсы равноправны, CLI не урезан
5. **Интерфейс-специфичные адаптации** — отступы для TG, vim для CLI — в адаптерах

---

## Этапы развития

```
Stage 1     [DONE]     CLI Prototype — прототип, проверка концепции
    │
Stage 1.5  [NEXT]     Core Extraction — выделение ядра, архитектура Ports & Adapters
    │
Stage 1.6             CLI Enhancement — доработка CLI до полноценного продукта
    │
Stage 1.7             Storage Abstraction — JSON ↔ SQLite ↔ PostgreSQL
    │
Stage 1.8             Execution Service — executor как микросервис
    │
Stage 2               Telegram Bot — первый внешний клиент
    │
Stage 3               Web Interface — сайт + embeddable widget
    │
Stage 4               Production & Scale — мониторинг, billing, масштабирование
```

---

## Stage 1: CLI Prototype [DONE]

**Статус:** Завершён

**Цель:** Проверить концепцию, отладить ядро логики выполнения и проверки кода.

**Результат:**
- Загрузка задач из JSON
- Интерактивный выбор задач
- Многострочный ввод кода с командами (!hint, !reset, !cancel)
- Безопасное выполнение в sandbox (multiprocessing)
- Валидация синтаксиса и тестирование
- Отображение результатов

**Документация:** [proposals/stage1/](./stage1/)

---

## Stage 1.5: Core Extraction [NEXT]

**Цель:** Рефакторинг в архитектуру Ports & Adapters. Отделение ядра от CLI.

### Структура после рефакторинга

```
practiceraptor/
├── core/
│   ├── domain/
│   │   ├── models.py           # Task, User, Solution, Progress, TestResult
│   │   └── services.py         # TaskService, ExecutionService, ProgressService
│   │
│   ├── ports/                  # Интерфейсы (абстракции)
│   │   ├── repositories.py     # ITaskRepository, IUserRepository, IProgressRepository
│   │   ├── executors.py        # ICodeExecutor
│   │   └── auth.py             # IAuthProvider
│   │
│   └── adapters/               # Реализации
│       ├── storage/
│       │   └── json_repository.py
│       ├── executors/
│       │   └── local_executor.py
│       └── auth/
│           └── anonymous_auth.py
│
├── clients/
│   └── cli/                    # Текущий CLI, рефакторинг
│       ├── main.py
│       ├── presenter.py
│       ├── input_handler.py
│       └── ...
│
├── data/
│   └── tasks/                  # JSON-файлы задач
│
└── tests/
```

### Модель данных (Domain Models)

```python
@dataclass
class User:
    id: str
    name: str | None
    settings: UserSettings
    created_at: datetime

@dataclass
class Progress:
    user_id: str
    task_id: int
    status: ProgressStatus  # not_started, in_progress, solved
    attempts: int
    best_time_ms: int | None
    solved_at: datetime | None

@dataclass
class Solution:
    id: str
    user_id: str
    task_id: int
    code: str
    language: str
    status: SolutionStatus  # accepted, wrong_answer, error, timeout
    execution_time_ms: int | None
    created_at: datetime

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    condition: str  # e.g., "solved_count >= 10"
```

### Критерии готовности

- [ ] CLI работает идентично текущему, но через абстракции
- [ ] Все зависимости инвертированы (DI)
- [ ] Domain models определены полностью
- [ ] Тесты для core проходят
- [ ] Документация обновлена

**Документация:** [proposals/stage1.5/](./stage1.5/)

---

## Stage 1.6: CLI Enhancement

**Цель:** Доработка CLI до полноценного продукта.

### Планируемые фичи

**Работа с задачами:**
- Фильтрация по тегам и сложности
- Поиск задач по названию
- Открытие в редакторе (vim/nano/code)
- Загрузка решения из файла (улучшенная)

**Пользовательский опыт:**
- Локальная история решений
- Прогресс и статистика (решено X из Y)
- Конфигурационный файл (~/.practriceraptor.yaml)
- Цветовые темы

**Расширенные возможности:**
- Режим соревнования (таймер)
- Сравнение с эталонным решением
- Экспорт статистики

### Критерии готовности

- [ ] Все запланированные фичи реализованы
- [ ] Документация пользователя обновлена
- [ ] Конфигурация через YAML

---

## Stage 1.7: Storage Abstraction

**Цель:** Поддержка нескольких бэкендов хранения с переключением через конфигурацию.

### Конфигурация

```yaml
# ~/.practriceraptor.yaml
storage:
  type: sqlite  # json | sqlite | postgresql

  # Для json
  json:
    tasks_dir: ./data/tasks
    users_dir: ./data/users

  # Для sqlite
  sqlite:
    path: ./data/practriceraptor.db

  # Для postgresql
  postgresql:
    host: localhost
    port: 5432
    database: practriceraptor
    user: ${DB_USER}
    password: ${DB_PASSWORD}
```

### Репозитории

| Interface | JSON | SQLite | PostgreSQL |
|-----------|------|--------|------------|
| ITaskRepository | ✓ | ✓ | ✓ |
| IUserRepository | ✓ | ✓ | ✓ |
| IProgressRepository | ✓ | ✓ | ✓ |
| ISolutionRepository | ✓ | ✓ | ✓ |

### Миграции

- JSON → SQLite: скрипт импорта
- SQLite → PostgreSQL: Alembic миграции

### Критерии готовности

- [ ] Все три бэкенда работают
- [ ] Переключение через конфигурацию
- [ ] Миграции данных работают
- [ ] Тесты для каждого бэкенда

---

## Stage 1.8: Execution Service

**Цель:** Выделение executor в отдельный микросервис.

### Архитектура

```
┌─────────────┐         ┌──────────────────┐
│    Core     │  HTTP   │ Execution Service│
│  (клиент)   │ ──────► │   (FastAPI)      │
└─────────────┘         └────────┬─────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │  Python  │ │   Go     │ │  Java    │
              │ Executor │ │ Executor │ │ Executor │
              └──────────┘ └──────────┘ └──────────┘
```

### Режимы работы

```yaml
executor:
  type: local    # local | service

  # Для local (текущий multiprocessing)
  local:
    timeout_sec: 5

  # Для service (HTTP API)
  service:
    url: http://localhost:8080
    api_key: ${EXECUTOR_API_KEY}
```

### API Execution Service

```
POST /execute
{
  "code": "def solution(...)...",
  "language": "python",
  "test_cases": [...],
  "timeout_sec": 5,
  "memory_limit_mb": 256
}

Response:
{
  "status": "accepted",
  "results": [...],
  "execution_time_ms": 45,
  "memory_used_kb": 14200
}
```

### Изоляция

- **Развёртывание на одном сервере:** Docker контейнеры
- **Развёртывание на разных серверах:** отдельный инстанс для executor

### Критерии готовности

- [ ] Execution Service работает как отдельное приложение
- [ ] API документирован (OpenAPI)
- [ ] Docker-образ для execution service
- [ ] Переключение local/service через конфигурацию

---

## Stage 2: Telegram Bot

**Цель:** Первый внешний клиент, подключённый к ядру через API.

### Архитектура

```
┌─────────────────┐     ┌─────────────────┐
│   Telegram      │     │   Bot Service   │
│   Users         │◄───►│   (aiogram 3.x) │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   Core API      │
                        │   (FastAPI)     │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
      │   Storage     │  │   Executor    │  │     Auth      │
      │   (PostgreSQL)│  │   Service     │  │   Service     │
      └───────────────┘  └───────────────┘  └───────────────┘
```

### Функциональность

- Регистрация пользователей (Telegram ID)
- Выбор задач с фильтрацией
- Решение задач через чат
- Статистика и прогресс
- Подсказки и эталонные решения
- Freemium модель (базовые задачи бесплатно)

### Адаптации для мобильных устройств

- Код без начальных отступов (добавляются автоматически)
- Inline-клавиатуры для навигации
- Компактное отображение результатов

### Технологии

- aiogram 3.x (async)
- FastAPI для Core API
- PostgreSQL (через Stage 1.7)
- Redis для сессий

### Критерии готовности

- [ ] Бот работает в Telegram
- [ ] Пользователи могут решать задачи
- [ ] Статистика сохраняется
- [ ] Docker Compose для развёртывания

---

## Stage 3: Web Interface

**Цель:** Web-сайт и embeddable widget для учебных платформ.

### Компоненты

1. **Web-сайт** — полнофункциональный интерфейс в браузере
2. **Widget** — встраиваемый iframe для учебных платформ

### Widget Integration

```html
<!-- На учебной платформе -->
<iframe
  src="https://practice.raptor/embed/task/42"
  data-user-token="..."
></iframe>
```

### SSO между платформами

- Единая система авторизации
- Пользователь учебной платформы = пользователь PracticeRaptor
- Общий прогресс и статистика

### Технологии

- Frontend: React/Vue или HTMX (TBD)
- API: тот же Core API
- Auth: OAuth2 / JWT

---

## Stage 4: Production & Scale

**Цель:** Готовность к production-нагрузкам и монетизации.

### Инфраструктура

- Load Balancer (Nginx)
- Горизонтальное масштабирование
- PostgreSQL репликация
- Redis кластер

### Мониторинг

- Prometheus + Grafana
- Структурированные логи
- Алерты

### Billing

- Stripe/ЮKassa интеграция
- Подписки и разовые платежи
- Управление доступом к premium-контенту

### Безопасность

- Rate limiting
- DDoS protection
- Secrets management
- Regular backups

---

## Сводная таблица

| Stage | Интерфейс | Хранилище | Executor | Пользователи |
|-------|-----------|-----------|----------|--------------|
| 1 | CLI | JSON | Local | — |
| 1.5 | CLI | JSON | Local (abstracted) | Модель |
| 1.6 | CLI+ | JSON | Local | Локальные |
| 1.7 | CLI+ | JSON/SQLite/PG | Local | Локальные |
| 1.8 | CLI+ | JSON/SQLite/PG | Local/Service | Локальные |
| 2 | CLI+, TG | PostgreSQL | Service | Registered |
| 3 | CLI+, TG, Web | PostgreSQL | Service | Registered |
| 4 | All | PostgreSQL (scaled) | Service (scaled) | Registered + Paid |

---

## Технические требования по этапам

### Stage 1.5–1.8 (Development)

| Параметр | Значение |
|----------|----------|
| CPU | 1 vCPU |
| RAM | 1 GB |
| Disk | 10 GB |
| OS | Debian 12 |

### Stage 2 (Telegram Bot MVP)

| Параметр | Минимум | Рекомендуется |
|----------|---------|---------------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 2 GB | 4 GB |
| Disk | 20 GB | 40 GB |

### Stage 3–4 (Production)

| Компонент | CPU | RAM | Disk |
|-----------|-----|-----|------|
| App Server | 4+ vCPU | 8+ GB | 40 GB |
| DB Server | 4+ vCPU | 8+ GB | 100 GB |
| Executor | 2+ vCPU | 4+ GB | 20 GB |
