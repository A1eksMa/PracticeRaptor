# Stage 1.5: Core Extraction — Overview

## Цель этапа

Рефакторинг существующего CLI-прототипа в архитектуру Hexagonal (Ports & Adapters) с выделением независимого ядра.

## Результат

После завершения Stage 1.5:
- CLI работает **идентично** текущему
- Код организован по принципу Hexagonal Architecture
- Бизнес-логика отделена от инфраструктуры
- Все зависимости инвертированы (DI)
- Покрытие тестами ≥80%

## Принцип рефакторинга

```
Текущее состояние:              После рефакторинга:

prototype/                      practiceraptor/
├── main.py                     ├── core/
├── models.py          ──►      │   ├── domain/
├── executor.py                 │   ├── ports/
├── task_loader.py              │   └── services/
├── ...                         ├── adapters/
└── tasks/                      ├── clients/cli/
                                ├── di/
                                └── tests/
```

## Шаги выполнения

| Step | Название | Описание | Зависит от |
|------|----------|----------|------------|
| 1 | [Project Setup](./01_project_setup.md) | Структура проекта, базовые модули | — |
| 2 | [Domain Models](./02_domain_models.md) | Immutable models, enums, errors | Step 1 |
| 3 | [Ports](./03_ports.md) | Protocol interfaces | Step 2 |
| 4 | [Storage Adapters](./04_storage_adapters.md) | JSON repositories | Step 3 |
| 5 | [Executor Adapter](./05_executor_adapter.md) | Local executor | Step 3 |
| 6 | [Core Services](./06_core_services.md) | Pure functions | Steps 2, 3 |
| 7 | [DI Container](./07_di_container.md) | Container, providers, config | Steps 4, 5, 6 |
| 8 | [CLI Refactoring](./08_cli_refactoring.md) | Переделка CLI | Step 7 |
| 9 | [Testing](./09_testing.md) | Тесты, Docker, CI | Steps 1-8 |

## Диаграмма зависимостей

```
Step 1 ─────────────────────────────────────────────────────►
   │
   ▼
Step 2 ─────────────────────────────────────────────────────►
   │
   ▼
Step 3 ─────────────────────────────────────────────────────►
   │
   ├──────────────┬──────────────┐
   ▼              ▼              ▼
Step 4         Step 5         Step 6
   │              │              │
   └──────────────┴──────────────┘
                  │
                  ▼
               Step 7 ──────────────────────────────────────►
                  │
                  ▼
               Step 8 ──────────────────────────────────────►
                  │
                  ▼
               Step 9 ──────────────────────────────────────►
```

## Критерии готовности Stage 1.5

- [ ] Все шаги (1-9) завершены
- [ ] CLI работает идентично прототипу
- [ ] Тесты проходят в Docker
- [ ] Coverage ≥80%
- [ ] mypy проходит без ошибок
- [ ] ruff не выдаёт warnings

## Не входит в Stage 1.5

- Новая функциональность CLI
- SQLite/PostgreSQL adapters
- Docker executor
- API/Telegram/Web clients

Эти задачи относятся к последующим этапам (Stage 1.6+).
