# PracticeRaptor

## Как запустить

```bash
  cd /root/github/PracticeRaptor/practiceraptor

  # Интерактивный режим (выбор задачи из списка)
  python3 -m clients.cli.main

  # Конкретная задача
  python3 -m clients.cli.main --task 1

  # Решение из файла
  python3 -m clients.cli.main --task 1 --file solution.py

```

## Доступные задачи

  | #   | Задача           |
  |-----|------------------|
  | 1   | Two Sum          |
  | 2   | Reverse String   |
  | 3   | Valid Palindrome |


## Архитектурные решения

### Hexagonal Architecture

  ┌─────────────────────────────────────────────────────────────┐
  │                         CLIENTS                              │
  │         CLI │ Telegram │ Web │ Widget                        │
  └──────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                      CORE (ядро)                             │
  │                                                              │
  │   Работает через интерфейсы (Ports):                         │
  │   • IProblemRepository                                       │
  │   • ICodeExecutor                                            │
  │   • IAuthProvider                                            │
  └──────────────────────────┬──────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │   STORAGE   │    │  EXECUTOR   │    │    AUTH     │
  │ JSON        │    │ Local       │    │ Anonymous   │
  │ SQLite      │    │ Docker      │    │ Telegram    │
  │ PostgreSQL  │    │ Remote API  │    │ Token/OAuth │
  └─────────────┘    └─────────────┘    └─────────────┘

### Примеры конфигураций

  Разработка / CLI:
  storage: json
  executor: local
  auth: anonymous

  Конфигурация интрефейса командной строки в файле `config/config.yaml`

  Telegram на VPS:
  storage: postgresql
  executor: docker
  auth: telegram

  Экзотическая комбинация:
  storage: json           # файлы локально
  executor: remote        # сервис на другом сервере
    url: http://executor.example.com:8080
  auth: telegram

### Текущее состояние

  | Компонент | Реализовано | Планируется                |
  |-----------|-------------|----------------------------|
  | Storage   | JSON        | SQLite, PostgreSQL (1.7)   |
  | Executor  | Local       | Docker, Remote (1.8)       |
  | Auth      | Anonymous   | Telegram, Token (Stage 2+) |
  | Clients   | CLI         | Telegram (2), Web (3)      |

