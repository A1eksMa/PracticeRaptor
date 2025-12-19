# Step 6: Core Services

## Цель

Создать слой сервисов — чистые функции для бизнес-логики.

## Принципы

- **Чистые функции** — одинаковый вход → одинаковый выход
- **Без side effects** — не изменяют состояние, не обращаются к I/O
- **Композиция** — сложные операции собираются из простых функций
- **Зависимости через аргументы** — репозитории и executor передаются как параметры

## Задачи

### 6.1. Создать core/services/problems.py

```python
# core/services/problems.py
"""Problem-related pure functions."""
from core.domain.models import Problem, LocalizedText
from core.domain.enums import Difficulty, Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IProblemRepository


def get_problem(
    problem_id: int,
    repo: IProblemRepository,
) -> Result[Problem, NotFoundError]:
    """Get problem by ID."""
    return repo.get_by_id(problem_id)


def get_all_problems(repo: IProblemRepository) -> tuple[Problem, ...]:
    """Get all problems sorted by ID."""
    return repo.get_all()


def filter_problems(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
) -> tuple[Problem, ...]:
    """Filter problems by criteria."""
    return repo.filter(difficulty=difficulty, tags=tags, language=language)


def get_random_problem(
    repo: IProblemRepository,
    difficulty: Difficulty | None = None,
    tags: tuple[str, ...] | None = None,
    language: Language | None = None,
    exclude_ids: tuple[int, ...] = (),
) -> Result[Problem, NotFoundError]:
    """Get random problem matching criteria."""
    import random

    problems = filter_problems(repo, difficulty, tags, language)
    available = tuple(p for p in problems if p.id not in exclude_ids)

    if not available:
        return Err(NotFoundError(
            message="No problems match the criteria",
            entity="Problem",
            id="random",
        ))

    return Ok(random.choice(available))


def get_problem_display_text(
    problem: Problem,
    locale: str = "en",
) -> dict[str, str]:
    """Get problem text for display."""
    return {
        "title": problem.title.get(locale),
        "description": problem.description.get(locale),
        "difficulty": problem.difficulty.value,
        "tags": ", ".join(problem.tags),
    }


def format_examples(
    problem: Problem,
    locale: str = "en",
) -> list[dict]:
    """Format examples for display."""
    result = []
    for i, example in enumerate(problem.examples, 1):
        item = {
            "number": i,
            "input": example.input,
            "output": example.output,
        }
        if example.explanation:
            item["explanation"] = example.explanation.get(locale)
        result.append(item)
    return result
```

### 6.2. Создать core/services/execution.py

```python
# core/services/execution.py
"""Code execution pure functions."""
import ast
import re

from core.domain.models import Problem, TestCase, ExecutionResult
from core.domain.enums import Language
from core.domain.result import Ok, Err, Result
from core.domain.errors import ValidationError, ExecutionError
from core.ports.executors import ICodeExecutor


def validate_code_syntax(code: str) -> Result[str, ValidationError]:
    """Validate Python code syntax."""
    if not code or not code.strip():
        return Err(ValidationError(
            message="Code cannot be empty",
            field="code",
        ))

    try:
        ast.parse(code)
        return Ok(code)
    except SyntaxError as e:
        return Err(ValidationError(
            message=f"Syntax error at line {e.lineno}: {e.msg}",
            field="code",
        ))


def extract_function_name(signature: str) -> str:
    """Extract function name from signature."""
    # "def two_sum(nums: list[int], target: int) -> list[int]:"
    match = re.match(r'def\s+(\w+)\s*\(', signature)
    if match:
        return match.group(1)
    return "solution"


def run_tests(
    code: str,
    test_cases: tuple[TestCase, ...],
    function_name: str,
    executor: ICodeExecutor,
    timeout_sec: int = 5,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against test cases."""
    return executor.execute(
        code=code,
        test_cases=test_cases,
        function_name=function_name,
        timeout_sec=timeout_sec,
    )


def run_examples_only(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against example test cases only (quick check)."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    # Convert examples to test cases
    example_tests = tuple(
        TestCase(
            input=ex.input,
            expected=ex.output,
            description=f"Example {i+1}",
        )
        for i, ex in enumerate(problem.examples)
    )

    function_name = extract_function_name(lang_spec.function_signature)

    return run_tests(code, example_tests, function_name, executor)


def run_full_tests(
    code: str,
    problem: Problem,
    language: Language,
    executor: ICodeExecutor,
) -> Result[ExecutionResult, ExecutionError]:
    """Run code against all test cases."""
    lang_spec = problem.get_language_spec(language)
    if not lang_spec:
        return Err(ExecutionError(
            message=f"Language {language.value} not supported for this problem",
            error_type="validation",
        ))

    function_name = extract_function_name(lang_spec.function_signature)

    return run_tests(code, problem.test_cases, function_name, executor)
```

### 6.3. Создать core/services/progress.py

```python
# core/services/progress.py
"""Progress tracking pure functions."""
from datetime import datetime

from core.domain.models import Progress, Submission, User
from core.domain.enums import Difficulty, Language, ProgressStatus
from core.domain.result import Ok, Err, Result
from core.domain.errors import NotFoundError
from core.ports.repositories import IProgressRepository, ISubmissionRepository


def get_user_progress(
    user_id: str,
    problem_id: int,
    progress_repo: IProgressRepository,
) -> Progress:
    """Get user progress for a problem, creating initial if not exists."""
    result = progress_repo.get(user_id, problem_id)
    match result:
        case Ok(progress):
            return progress
        case Err(_):
            return Progress(
                user_id=user_id,
                problem_id=problem_id,
                status=ProgressStatus.NOT_STARTED,
                attempts=0,
                solved_languages=(),
            )


def update_progress_on_attempt(
    progress: Progress,
    solved: bool,
    language: Language,
) -> Progress:
    """Create updated progress after an attempt (immutable)."""
    new_attempts = progress.attempts + 1

    if solved:
        new_languages = progress.solved_languages
        if language not in new_languages:
            new_languages = (*new_languages, language)

        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=ProgressStatus.SOLVED,
            attempts=new_attempts,
            solved_languages=new_languages,
            first_solved_at=progress.first_solved_at or datetime.now(),
        )
    else:
        new_status = (
            ProgressStatus.SOLVED
            if progress.status == ProgressStatus.SOLVED
            else ProgressStatus.IN_PROGRESS
        )
        return Progress(
            user_id=progress.user_id,
            problem_id=progress.problem_id,
            status=new_status,
            attempts=new_attempts,
            solved_languages=progress.solved_languages,
            first_solved_at=progress.first_solved_at,
        )


def calculate_user_stats(
    user_id: str,
    progress_repo: IProgressRepository,
) -> dict:
    """Calculate overall user statistics."""
    all_progress = progress_repo.get_all_for_user(user_id)

    solved = [p for p in all_progress if p.status == ProgressStatus.SOLVED]
    in_progress = [p for p in all_progress if p.status == ProgressStatus.IN_PROGRESS]

    return {
        "total_solved": len(solved),
        "in_progress": len(in_progress),
        "total_attempts": sum(p.attempts for p in all_progress),
    }


def calculate_stats_by_difficulty(
    user_id: str,
    progress_repo: IProgressRepository,
    problem_difficulties: dict[int, Difficulty],
) -> dict[Difficulty, dict]:
    """Calculate stats grouped by difficulty."""
    all_progress = progress_repo.get_all_for_user(user_id)

    stats = {d: {"solved": 0, "total": 0} for d in Difficulty}

    for progress in all_progress:
        difficulty = problem_difficulties.get(progress.problem_id)
        if difficulty:
            stats[difficulty]["total"] += 1
            if progress.status == ProgressStatus.SOLVED:
                stats[difficulty]["solved"] += 1

    return stats
```

### 6.4. Создать core/services/drafts.py

```python
# core/services/drafts.py
"""Draft management pure functions."""
from datetime import datetime

from core.domain.models import Draft
from core.domain.enums import Language
from core.domain.result import Result
from core.domain.errors import NotFoundError, StorageError
from core.ports.repositories import IDraftRepository


def get_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[Draft, NotFoundError]:
    """Get existing draft."""
    return draft_repo.get(user_id, problem_id, language)


def save_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    code: str,
    draft_repo: IDraftRepository,
) -> Result[Draft, StorageError]:
    """Save or update draft."""
    draft = Draft(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        code=code,
        updated_at=datetime.now(),
    )
    return draft_repo.save(draft)


def delete_draft(
    user_id: str,
    problem_id: int,
    language: Language,
    draft_repo: IDraftRepository,
) -> Result[None, NotFoundError]:
    """Delete draft after successful submission."""
    return draft_repo.delete(user_id, problem_id, language)


def get_or_create_code(
    user_id: str,
    problem_id: int,
    language: Language,
    signature: str,
    draft_repo: IDraftRepository,
) -> str:
    """Get draft code or return template with signature."""
    result = get_draft(user_id, problem_id, language, draft_repo)
    match result:
        case Ok(draft):
            return draft.code
        case Err(_):
            # Return template with just the signature
            return f"{signature}\n    pass"
```

### 6.5. Обновить core/services/__init__.py

```python
# core/services/__init__.py
"""Service layer - pure functions for business logic."""
from .problems import (
    get_problem,
    get_all_problems,
    filter_problems,
    get_random_problem,
    get_problem_display_text,
    format_examples,
)
from .execution import (
    validate_code_syntax,
    extract_function_name,
    run_tests,
    run_examples_only,
    run_full_tests,
)
from .progress import (
    get_user_progress,
    update_progress_on_attempt,
    calculate_user_stats,
    calculate_stats_by_difficulty,
)
from .drafts import (
    get_draft,
    save_draft,
    delete_draft,
    get_or_create_code,
)

__all__ = [
    # Problems
    "get_problem",
    "get_all_problems",
    "filter_problems",
    "get_random_problem",
    "get_problem_display_text",
    "format_examples",
    # Execution
    "validate_code_syntax",
    "extract_function_name",
    "run_tests",
    "run_examples_only",
    "run_full_tests",
    # Progress
    "get_user_progress",
    "update_progress_on_attempt",
    "calculate_user_stats",
    "calculate_stats_by_difficulty",
    # Drafts
    "get_draft",
    "save_draft",
    "delete_draft",
    "get_or_create_code",
]
```

## Критерии готовности

- [ ] Все сервисные функции — чистые (без side effects)
- [ ] Зависимости передаются как аргументы
- [ ] Возвращают Result для операций с ошибками
- [ ] Документированы (docstrings)
- [ ] Тесты для каждой функции

## Тесты для Step 6

```python
# tests/unit/core/services/test_execution.py
import pytest
from core.services.execution import (
    validate_code_syntax,
    extract_function_name,
)


class TestValidateCodeSyntax:
    def test_valid_code_returns_ok(self):
        code = "def solution(x): return x * 2"
        result = validate_code_syntax(code)
        assert result.is_ok()
        assert result.unwrap() == code

    def test_empty_code_returns_error(self):
        result = validate_code_syntax("")
        assert result.is_err()
        assert "empty" in result.error.message.lower()

    def test_syntax_error_returns_error(self):
        code = "def solution(x) return x"
        result = validate_code_syntax(code)
        assert result.is_err()


class TestExtractFunctionName:
    def test_extracts_simple_name(self):
        sig = "def two_sum(nums, target):"
        assert extract_function_name(sig) == "two_sum"

    def test_extracts_name_with_types(self):
        sig = "def two_sum(nums: list[int], target: int) -> list[int]:"
        assert extract_function_name(sig) == "two_sum"

    def test_returns_default_for_invalid(self):
        sig = "invalid"
        assert extract_function_name(sig) == "solution"
```

## Следующий шаг

После завершения Step 6 переходите к [Step 7: DI Container](./07_di_container.md).
