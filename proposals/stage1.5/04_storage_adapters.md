# Step 4: Storage Adapters (JSON)

## Цель

Реализовать JSON-адаптеры для всех репозиториев, совместимые с Protocol интерфейсами.

## Задачи

### 4.1. Создать базовый класс для JSON storage

```python
# adapters/storage/json_base.py
"""Base utilities for JSON storage."""
import json
from pathlib import Path
from typing import TypeVar, Generic
from dataclasses import asdict

from core.domain.result import Ok, Err, Result
from core.domain.errors import StorageError, NotFoundError

T = TypeVar('T')


class JsonStorageBase(Generic[T]):
    """Base class for JSON file storage."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _read_json(self, file_path: Path) -> Result[dict, StorageError]:
        """Read JSON file."""
        try:
            if not file_path.exists():
                return Err(StorageError(
                    message=f"File not found: {file_path}",
                    operation="read",
                ))
            with open(file_path, 'r', encoding='utf-8') as f:
                return Ok(json.load(f))
        except json.JSONDecodeError as e:
            return Err(StorageError(
                message=f"Invalid JSON: {e}",
                operation="read",
            ))
        except OSError as e:
            return Err(StorageError(
                message=f"IO error: {e}",
                operation="read",
            ))

    def _write_json(self, file_path: Path, data: dict) -> Result[None, StorageError]:
        """Write JSON file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return Ok(None)
        except OSError as e:
            return Err(StorageError(
                message=f"IO error: {e}",
                operation="write",
            ))

    def _delete_file(self, file_path: Path) -> Result[None, NotFoundError]:
        """Delete file."""
        try:
            if not file_path.exists():
                return Err(NotFoundError(
                    message=f"File not found: {file_path}",
                    entity="file",
                    id=str(file_path),
                ))
            file_path.unlink()
            return Ok(None)
        except OSError as e:
            return Err(NotFoundError(
                message=f"Cannot delete: {e}",
                entity="file",
                id=str(file_path),
            ))
```

### 4.2. Создать JsonProblemRepository

```python
# adapters/storage/json_problem_repository.py
"""JSON implementation of IProblemRepository."""
from pathlib import Path

from core.domain.models import (
    Problem,
    LocalizedText,
    Example,
    TestCase,
    Solution,
    LanguageSpec,
)
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IProblemRepository

from .json_base import JsonStorageBase


class JsonProblemRepository(JsonStorageBase[Problem]):
    """JSON file-based problem repository."""

    def __init__(self, problems_path: Path):
        super().__init__(problems_path)
        self._cache: dict[int, Problem] | None = None

    def _load_all(self) -> dict[int, Problem]:
        """Load all problems from files (with caching)."""
        if self._cache is not None:
            return self._cache

        problems = {}
        for file_path in self.base_path.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                problem = self._parse_problem(result.value)
                if problem:
                    problems[problem.id] = problem

        self._cache = problems
        return problems

    def _parse_problem(self, data: dict) -> Problem | None:
        """Parse JSON to Problem model."""
        try:
            # Parse localized text fields
            title = self._parse_localized(data.get("title", {}))
            description = self._parse_localized(data.get("description", {}))

            # Parse examples
            examples = tuple(
                Example(
                    input=ex["input"],
                    output=ex["output"],
                    explanation=self._parse_localized(ex.get("explanation"))
                    if ex.get("explanation") else None,
                )
                for ex in data.get("examples", [])
            )

            # Parse test cases
            test_cases = tuple(
                TestCase(
                    input=tc["input"],
                    expected=tc["expected"],
                    description=tc.get("description"),
                    is_hidden=tc.get("is_hidden", False),
                )
                for tc in data.get("test_cases", [])
            )

            # Parse language specs
            languages = []
            for lang_key, lang_data in data.get("languages", {}).items():
                # Also support old format with direct keys like "python3"
                if lang_key in ("python3", "go", "java", "javascript"):
                    lang_enum = Language(lang_key)
                    solutions = tuple(
                        Solution(
                            name=s["name"],
                            complexity=s["complexity"],
                            code=s["code"],
                        )
                        for s in lang_data.get("solutions", [])
                    )
                    languages.append(LanguageSpec(
                        language=lang_enum,
                        function_signature=lang_data["function_signature"],
                        solutions=solutions,
                    ))

            # Support old format (python3 at root level)
            if "python3" in data and "languages" not in data:
                lang_data = data["python3"]
                solutions = tuple(
                    Solution(
                        name=s["name"],
                        complexity=s["complexity"],
                        code=s["code"],
                    )
                    for s in lang_data.get("solutions", [])
                )
                languages.append(LanguageSpec(
                    language=Language.PYTHON,
                    function_signature=lang_data["function_signature"],
                    solutions=solutions,
                ))

            # Parse hints
            hints = tuple(
                self._parse_localized(h) for h in data.get("hints", [])
            )

            return Problem(
                id=data["id"],
                title=title,
                description=description,
                difficulty=Difficulty(data["difficulty"]),
                tags=tuple(data.get("tags", [])),
                examples=examples,
                test_cases=test_cases,
                languages=tuple(languages),
                hints=hints,
            )
        except (KeyError, ValueError) as e:
            # Log error and skip malformed problems
            print(f"Warning: Failed to parse problem: {e}")
            return None

    def _parse_localized(self, data: str | dict | None) -> LocalizedText:
        """Parse localized text (supports string or dict)."""
        if data is None:
            return LocalizedText({})
        if isinstance(data, str):
            return LocalizedText({"en": data})
        return LocalizedText(data)

    def get_by_id(self, problem_id: int) -> Result[Problem, NotFoundError]:
        """Get problem by ID."""
        problems = self._load_all()
        if problem_id in problems:
            return Ok(problems[problem_id])
        return Err(NotFoundError(
            message=f"Problem {problem_id} not found",
            entity="Problem",
            id=problem_id,
        ))

    def get_all(self) -> tuple[Problem, ...]:
        """Get all problems."""
        problems = self._load_all()
        return tuple(sorted(problems.values(), key=lambda p: p.id))

    def filter(
        self,
        difficulty: Difficulty | None = None,
        tags: tuple[str, ...] | None = None,
        language: Language | None = None,
    ) -> tuple[Problem, ...]:
        """Filter problems by criteria."""
        problems = self.get_all()

        if difficulty:
            problems = tuple(p for p in problems if p.difficulty == difficulty)

        if tags:
            problems = tuple(
                p for p in problems
                if any(tag in p.tags for tag in tags)
            )

        if language:
            problems = tuple(
                p for p in problems
                if p.get_language_spec(language) is not None
            )

        return problems

    def count(self) -> int:
        """Get total number of problems."""
        return len(self._load_all())

    def invalidate_cache(self) -> None:
        """Clear the cache to reload from files."""
        self._cache = None
```

### 4.3. Создать JsonUserRepository

```python
# adapters/storage/json_user_repository.py
"""JSON implementation of IUserRepository."""
from pathlib import Path
from datetime import datetime

from core.domain.models import User
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError
from core.ports.repositories import IUserRepository

from .json_base import JsonStorageBase


class JsonUserRepository(JsonStorageBase[User]):
    """JSON file-based user repository."""

    def __init__(self, users_path: Path):
        super().__init__(users_path)

    def _user_file(self, user_id: str) -> Path:
        return self.base_path / f"{user_id}.json"

    def _parse_user(self, data: dict) -> User:
        return User(
            id=data["id"],
            locale=data.get("locale", "en"),
            preferred_language=Language(data.get("preferred_language", "python3")),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at") else datetime.now(),
        )

    def _serialize_user(self, user: User) -> dict:
        return {
            "id": user.id,
            "locale": user.locale,
            "preferred_language": user.preferred_language.value,
            "created_at": user.created_at.isoformat(),
        }

    def get_by_id(self, user_id: str) -> Result[User, NotFoundError]:
        """Get user by ID."""
        result = self._read_json(self._user_file(user_id))
        match result:
            case Ok(data):
                return Ok(self._parse_user(data))
            case Err(_):
                return Err(NotFoundError(
                    message=f"User {user_id} not found",
                    entity="User",
                    id=user_id,
                ))

    def save(self, user: User) -> Result[User, StorageError]:
        """Save user."""
        data = self._serialize_user(user)
        result = self._write_json(self._user_file(user.id), data)
        match result:
            case Ok(_):
                return Ok(user)
            case Err(e):
                return Err(e)

    def delete(self, user_id: str) -> Result[None, NotFoundError]:
        """Delete user."""
        return self._delete_file(self._user_file(user_id))
```

### 4.4. Создать JsonDraftRepository

```python
# adapters/storage/json_draft_repository.py
"""JSON implementation of IDraftRepository."""
from pathlib import Path
from datetime import datetime

from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError, StorageError
from core.ports.repositories import IDraftRepository

from .json_base import JsonStorageBase


class JsonDraftRepository(JsonStorageBase[Draft]):
    """JSON file-based draft repository."""

    def __init__(self, drafts_path: Path):
        super().__init__(drafts_path)

    def _draft_file(self, user_id: str, problem_id: int, language: Language) -> Path:
        return self.base_path / user_id / f"{problem_id}_{language.value}.json"

    def _parse_draft(self, data: dict) -> Draft:
        return Draft(
            user_id=data["user_id"],
            problem_id=data["problem_id"],
            language=Language(data["language"]),
            code=data["code"],
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def _serialize_draft(self, draft: Draft) -> dict:
        return {
            "user_id": draft.user_id,
            "problem_id": draft.problem_id,
            "language": draft.language.value,
            "code": draft.code,
            "updated_at": draft.updated_at.isoformat(),
        }

    def get(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[Draft, NotFoundError]:
        """Get draft."""
        file_path = self._draft_file(user_id, problem_id, language)
        result = self._read_json(file_path)
        match result:
            case Ok(data):
                return Ok(self._parse_draft(data))
            case Err(_):
                return Err(NotFoundError(
                    message=f"Draft not found",
                    entity="Draft",
                    id=f"{user_id}/{problem_id}/{language.value}",
                ))

    def save(self, draft: Draft) -> Result[Draft, StorageError]:
        """Save draft."""
        file_path = self._draft_file(draft.user_id, draft.problem_id, draft.language)
        data = self._serialize_draft(draft)
        result = self._write_json(file_path, data)
        match result:
            case Ok(_):
                return Ok(draft)
            case Err(e):
                return Err(e)

    def delete(
        self,
        user_id: str,
        problem_id: int,
        language: Language,
    ) -> Result[None, NotFoundError]:
        """Delete draft."""
        file_path = self._draft_file(user_id, problem_id, language)
        return self._delete_file(file_path)

    def get_all_for_user(self, user_id: str) -> tuple[Draft, ...]:
        """Get all drafts for user."""
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return ()

        drafts = []
        for file_path in user_dir.glob("*.json"):
            result = self._read_json(file_path)
            if result.is_ok():
                drafts.append(self._parse_draft(result.value))

        return tuple(sorted(drafts, key=lambda d: d.updated_at, reverse=True))
```

### 4.5. Обновить adapters/storage/__init__.py

```python
# adapters/storage/__init__.py
"""Storage adapters."""
from .json_problem_repository import JsonProblemRepository
from .json_user_repository import JsonUserRepository
from .json_draft_repository import JsonDraftRepository
# from .json_submission_repository import JsonSubmissionRepository  # TODO
# from .json_progress_repository import JsonProgressRepository  # TODO

__all__ = [
    "JsonProblemRepository",
    "JsonUserRepository",
    "JsonDraftRepository",
]
```

## Критерии готовности

- [ ] JsonProblemRepository реализован и совместим с IProblemRepository
- [ ] JsonUserRepository реализован
- [ ] JsonDraftRepository реализован
- [ ] Поддержка старого формата JSON (без i18n)
- [ ] Тесты для всех репозиториев
- [ ] mypy проходит

## Тесты для Step 4

```python
# tests/unit/adapters/storage/test_json_problem_repository.py
import pytest
from pathlib import Path
import tempfile
import json

from adapters.storage.json_problem_repository import JsonProblemRepository
from core.domain.enums import Difficulty, Language


@pytest.fixture
def temp_problems_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_problem_json():
    return {
        "id": 1,
        "title": {"en": "Two Sum", "ru": "Сумма двух"},
        "description": {"en": "Given an array..."},
        "difficulty": "easy",
        "tags": ["array", "hash-table"],
        "examples": [
            {"input": {"nums": [2, 7], "target": 9}, "output": [0, 1]}
        ],
        "test_cases": [
            {"input": {"nums": [2, 7], "target": 9}, "expected": [0, 1]}
        ],
        "languages": {
            "python3": {
                "function_signature": "def two_sum(nums, target):",
                "solutions": []
            }
        }
    }


class TestJsonProblemRepository:
    def test_get_by_id_returns_problem(self, temp_problems_dir, sample_problem_json):
        # Arrange
        (temp_problems_dir / "1.json").write_text(
            json.dumps(sample_problem_json)
        )
        repo = JsonProblemRepository(temp_problems_dir)

        # Act
        result = repo.get_by_id(1)

        # Assert
        assert result.is_ok()
        problem = result.unwrap()
        assert problem.id == 1
        assert problem.title.get("en") == "Two Sum"

    def test_get_by_id_returns_error_for_missing(self, temp_problems_dir):
        repo = JsonProblemRepository(temp_problems_dir)

        result = repo.get_by_id(999)

        assert result.is_err()

    def test_filter_by_difficulty(self, temp_problems_dir, sample_problem_json):
        (temp_problems_dir / "1.json").write_text(
            json.dumps(sample_problem_json)
        )
        repo = JsonProblemRepository(temp_problems_dir)

        result = repo.filter(difficulty=Difficulty.EASY)

        assert len(result) == 1
        assert result[0].difficulty == Difficulty.EASY
```

## Следующий шаг

После завершения Step 4 переходите к [Step 5: Executor Adapter](./05_executor_adapter.md).
