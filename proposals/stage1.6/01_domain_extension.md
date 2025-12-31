# Этап 1.6.1: Расширение доменной модели

## 1. Цель

Расширить доменную модель Core для поддержки:
- Пользовательских настроек (preferences)
- Фильтров задач как переиспользуемого value object
- Отображения списка задач с учётом прогресса пользователя

**Принцип:** Добавляем новое, не меняем существующее.

---

## 2. Новые компоненты

### 2.1. TaskFilters (Value Object)

**Файл:** `core/domain/models.py`

**Назначение:** Инкапсулирует критерии фильтрации задач. Используется:
- В `UserSettings` как фильтры по умолчанию
- В сервисах фильтрации как параметр
- В CLI/Telegram/Web для передачи фильтров от UI

```python
@dataclass(frozen=True)
class TaskFilters:
    """
    Criteria for filtering problems.

    Used as:
    - Default filters in UserSettings
    - Parameter for filter functions
    - DTO from UI to services

    All fields are optional - None means "no filter" (show all).
    """
    difficulty: Difficulty | None = None
    tags: tuple[str, ...] = ()
    status: ProgressStatus | None = None  # None = all, SOLVED = only solved, etc.

    def is_empty(self) -> bool:
        """Check if no filters are applied."""
        return (
            self.difficulty is None
            and len(self.tags) == 0
            and self.status is None
        )

    def with_difficulty(self, difficulty: Difficulty | None) -> "TaskFilters":
        """Create new filters with updated difficulty."""
        return TaskFilters(
            difficulty=difficulty,
            tags=self.tags,
            status=self.status,
        )

    def with_tags(self, tags: tuple[str, ...]) -> "TaskFilters":
        """Create new filters with updated tags."""
        return TaskFilters(
            difficulty=self.difficulty,
            tags=tags,
            status=self.status,
        )

    def with_status(self, status: ProgressStatus | None) -> "TaskFilters":
        """Create new filters with updated status."""
        return TaskFilters(
            difficulty=self.difficulty,
            tags=self.tags,
            status=status,
        )
```

**Почему frozen dataclass:**
- Immutable — безопасно передавать между слоями
- Методы `with_*` создают новый объект (функциональный стиль)
- Hashable — можно использовать как ключ кэша

---

### 2.2. UserSettings (Entity)

**Файл:** `core/domain/models.py`

**Назначение:** Хранит предпочтения пользователя, которые:
- Применяются по умолчанию при запуске
- Могут быть изменены пользователем
- Сохраняются между сессиями

```python
@dataclass(frozen=True)
class UserSettings:
    """
    User preferences stored separately from User identity.

    Separation rationale:
    - User = WHO (identity, authentication)
    - UserSettings = HOW (preferences, defaults)

    This allows:
    - Different storage strategies (User in auth service, Settings in local file)
    - Settings to exist before full authentication (anonymous users)
    - Easy reset to defaults without affecting identity
    """
    user_id: str

    # Language preferences
    default_language: Language = Language.PYTHON
    locale: str = "en"

    # Default filters for problem list
    default_filters: TaskFilters = field(default_factory=TaskFilters)

    # Pagination
    problems_per_page: int = 20

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def with_language(self, language: Language) -> "UserSettings":
        """Create new settings with updated language."""
        return UserSettings(
            user_id=self.user_id,
            default_language=language,
            locale=self.locale,
            default_filters=self.default_filters,
            problems_per_page=self.problems_per_page,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_locale(self, locale: str) -> "UserSettings":
        """Create new settings with updated locale."""
        return UserSettings(
            user_id=self.user_id,
            default_language=self.default_language,
            locale=locale,
            default_filters=self.default_filters,
            problems_per_page=self.problems_per_page,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )

    def with_filters(self, filters: TaskFilters) -> "UserSettings":
        """Create new settings with updated default filters."""
        return UserSettings(
            user_id=self.user_id,
            default_language=self.default_language,
            locale=self.locale,
            default_filters=filters,
            problems_per_page=self.problems_per_page,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )
```

**Связь с User:**
```
User (identity)              UserSettings (preferences)
┌──────────────┐            ┌────────────────────────┐
│ id: "abc123" │◄──────────►│ user_id: "abc123"      │
│ created_at   │   1:1      │ default_language       │
└──────────────┘            │ locale                 │
                            │ default_filters        │
                            └────────────────────────┘
```

---

### 2.3. ProblemListItem (DTO)

**Файл:** `core/domain/models.py`

**Назначение:** Объединяет данные из `Problem` и `Progress` для отображения в списке. Это **DTO (Data Transfer Object)**, а не entity.

```python
@dataclass(frozen=True)
class ProblemListItem:
    """
    Problem with user's progress status for list display.

    This is a DTO (Data Transfer Object), not an entity.
    It combines data from two sources:
    - Problem (from IProblemRepository)
    - Progress (from IProgressRepository)

    Used for rendering problem lists in UI where we need
    to show both problem info and user's status.
    """
    # From Problem
    id: int
    title: LocalizedText
    difficulty: Difficulty
    tags: tuple[str, ...]

    # From Progress (or defaults if no progress)
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    attempts: int = 0
    solved_languages: tuple[Language, ...] = ()

    @classmethod
    def from_problem_and_progress(
        cls,
        problem: Problem,
        progress: Progress | None,
    ) -> "ProblemListItem":
        """Create list item from problem and optional progress."""
        if progress is None:
            return cls(
                id=problem.id,
                title=problem.title,
                difficulty=problem.difficulty,
                tags=problem.tags,
            )
        return cls(
            id=problem.id,
            title=problem.title,
            difficulty=problem.difficulty,
            tags=problem.tags,
            status=progress.status,
            attempts=progress.attempts,
            solved_languages=progress.solved_languages,
        )
```

**Почему отдельный тип:**
- `Problem` не должен знать о `Progress` (разные aggregate roots)
- UI нуждается в объединённых данных
- DTO явно показывает, что это "склейка" для представления

---

### 2.4. IUserSettingsRepository (Port)

**Файл:** `core/ports/repositories.py`

**Назначение:** Интерфейс для хранения и извлечения пользовательских настроек.

```python
class IUserSettingsRepository(Protocol):
    """
    Interface for user settings storage.

    Separated from IUserRepository because:
    - Settings may be stored differently (local file vs remote DB)
    - Settings should work for anonymous users
    - Allows different caching strategies

    Implementations:
    - FileUserSettingsRepository (YAML files for CLI)
    - JsonUserSettingsRepository (JSON files)
    - PostgresUserSettingsRepository (DB for web/telegram)
    """

    def get(self, user_id: str) -> Result[UserSettings, NotFoundError]:
        """
        Get settings for user.

        Returns Err(NotFoundError) if settings don't exist.
        Caller should handle this by creating default settings.
        """
        ...

    def get_or_default(self, user_id: str) -> UserSettings:
        """
        Get settings for user, creating defaults if not found.

        This is a convenience method that never fails.
        """
        ...

    def save(self, settings: UserSettings) -> Result[UserSettings, StorageError]:
        """
        Save settings (create or update).

        Returns the saved settings on success.
        """
        ...

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """
        Delete settings for user.

        Returns Err(NotFoundError) if settings don't exist.
        """
        ...
```

**Почему отдельный репозиторий (не расширение IUserRepository):**
- **Single Responsibility:** User = identity, Settings = preferences
- **Разные стратегии хранения:** User может быть в auth-сервисе, Settings — в локальном файле
- **Анонимные пользователи:** Settings существуют даже без полной аутентификации

---

## 3. Изменения в существующих файлах

### 3.1. core/domain/models.py

**Добавить:**
- `TaskFilters` dataclass
- `UserSettings` dataclass
- `ProblemListItem` dataclass

**Не менять:**
- `User` — остаётся как есть (identity)
- `Problem`, `Draft`, `Submission`, `Progress` — без изменений

### 3.2. core/ports/repositories.py

**Добавить:**
- `IUserSettingsRepository` Protocol

**Не менять:**
- Существующие репозитории

### 3.3. core/domain/factories.py

**Добавить:**
- `create_default_settings(user_id: str) -> UserSettings`
- `create_default_filters() -> TaskFilters`

```python
def create_default_settings(user_id: str) -> UserSettings:
    """Create default settings for a new user."""
    return UserSettings(
        user_id=user_id,
        default_language=Language.PYTHON,
        locale="en",
        default_filters=TaskFilters(),
        problems_per_page=20,
    )

def create_default_filters() -> TaskFilters:
    """Create empty (no filter) task filters."""
    return TaskFilters()
```

---

## 4. Новый сервис: settings.py

**Файл:** `core/services/settings.py`

```python
"""User settings management pure functions."""
from core.domain.models import UserSettings, TaskFilters
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError
from core.domain.factories import create_default_settings
from core.ports.repositories import IUserSettingsRepository


def get_user_settings(
    user_id: str,
    settings_repo: IUserSettingsRepository,
) -> UserSettings:
    """
    Get settings for user, creating defaults if not found.

    This function never fails - it always returns valid settings.
    """
    return settings_repo.get_or_default(user_id)


def update_language(
    user_id: str,
    language: Language,
    settings_repo: IUserSettingsRepository,
) -> Result[UserSettings, StorageError]:
    """Update user's default programming language."""
    settings = settings_repo.get_or_default(user_id)
    updated = settings.with_language(language)
    return settings_repo.save(updated)


def update_locale(
    user_id: str,
    locale: str,
    settings_repo: IUserSettingsRepository,
) -> Result[UserSettings, StorageError]:
    """Update user's interface locale."""
    settings = settings_repo.get_or_default(user_id)
    updated = settings.with_locale(locale)
    return settings_repo.save(updated)


def update_default_filters(
    user_id: str,
    filters: TaskFilters,
    settings_repo: IUserSettingsRepository,
) -> Result[UserSettings, StorageError]:
    """Update user's default task filters."""
    settings = settings_repo.get_or_default(user_id)
    updated = settings.with_filters(filters)
    return settings_repo.save(updated)


def reset_settings(
    user_id: str,
    settings_repo: IUserSettingsRepository,
) -> Result[UserSettings, StorageError]:
    """Reset user settings to defaults."""
    default = create_default_settings(user_id)
    return settings_repo.save(default)
```

---

## 5. Расширение сервиса problems.py

**Файл:** `core/services/problems.py`

**Добавить функцию:**

```python
def get_problem_list(
    user_id: str,
    filters: TaskFilters,
    problem_repo: IProblemRepository,
    progress_repo: IProgressRepository,
    locale: str = "en",
) -> tuple[ProblemListItem, ...]:
    """
    Get list of problems with user's progress status.

    Combines data from problem and progress repositories
    to create a list suitable for UI display.
    """
    # Get problems matching difficulty and tags
    problems = problem_repo.filter(
        difficulty=filters.difficulty,
        tags=filters.tags if filters.tags else None,
    )

    # Get all progress for user
    all_progress = progress_repo.get_all_for_user(user_id)
    progress_map = {p.problem_id: p for p in all_progress}

    # Combine and filter by status
    items = []
    for problem in problems:
        progress = progress_map.get(problem.id)
        item = ProblemListItem.from_problem_and_progress(problem, progress)

        # Filter by status if specified
        if filters.status is not None:
            if item.status != filters.status:
                continue

        items.append(item)

    return tuple(items)
```

---

## 6. Обновление DI Container

**Файл:** `di/container.py`

```python
@dataclass(frozen=True)
class Container:
    """Immutable container holding all application dependencies."""
    # Existing
    problem_repo: IProblemRepository
    user_repo: IUserRepository
    draft_repo: IDraftRepository
    submission_repo: ISubmissionRepository
    progress_repo: IProgressRepository
    executor: ICodeExecutor
    auth: IAuthProvider

    # NEW
    settings_repo: IUserSettingsRepository

    # Configuration
    default_locale: str = "en"
    default_timeout_sec: int = 5
```

---

## 7. Тесты

### 7.1. Unit-тесты для моделей

**Файл:** `tests/unit/domain/test_task_filters.py`

```python
def test_task_filters_is_empty_when_no_filters():
    filters = TaskFilters()
    assert filters.is_empty() is True

def test_task_filters_is_not_empty_with_difficulty():
    filters = TaskFilters(difficulty=Difficulty.EASY)
    assert filters.is_empty() is False

def test_task_filters_with_difficulty_creates_new_instance():
    original = TaskFilters()
    updated = original.with_difficulty(Difficulty.MEDIUM)

    assert original.difficulty is None  # unchanged
    assert updated.difficulty == Difficulty.MEDIUM
```

**Файл:** `tests/unit/domain/test_user_settings.py`

```python
def test_user_settings_with_language_creates_new_instance():
    settings = UserSettings(user_id="test")
    updated = settings.with_language(Language.GO)

    assert settings.default_language == Language.PYTHON  # unchanged
    assert updated.default_language == Language.GO

def test_user_settings_updates_timestamp_on_change():
    settings = UserSettings(user_id="test")
    time.sleep(0.01)
    updated = settings.with_locale("ru")

    assert updated.updated_at > settings.updated_at
```

### 7.2. Unit-тесты для сервиса

**Файл:** `tests/unit/services/test_settings.py`

```python
def test_get_user_settings_returns_default_when_not_found():
    repo = MockUserSettingsRepository(returns_not_found=True)
    settings = get_user_settings("user1", repo)

    assert settings.user_id == "user1"
    assert settings.default_language == Language.PYTHON

def test_update_language_saves_updated_settings():
    repo = MockUserSettingsRepository()
    result = update_language("user1", Language.GO, repo)

    assert result.is_ok()
    assert repo.saved_settings.default_language == Language.GO
```

---

## 8. Критерии готовности

- [ ] `TaskFilters` добавлен в `models.py`
- [ ] `UserSettings` добавлен в `models.py`
- [ ] `ProblemListItem` добавлен в `models.py`
- [ ] `IUserSettingsRepository` добавлен в `repositories.py`
- [ ] Фабричные функции добавлены в `factories.py`
- [ ] `settings.py` сервис создан
- [ ] `get_problem_list` добавлен в `problems.py`
- [ ] `Container` обновлён
- [ ] Unit-тесты написаны и проходят
- [ ] Существующие тесты проходят (обратная совместимость)

---

## 9. Следующий этап

После завершения 1.6.1 переходим к **Этапу 1.6.2: CLI Context & Bootstrap**, где:
- Реализуем `FileUserSettingsRepository` (адаптер)
- Создаём `CLIConfig`, `Session`, `CLIContext`
- Реализуем цепочку инициализации CLI
