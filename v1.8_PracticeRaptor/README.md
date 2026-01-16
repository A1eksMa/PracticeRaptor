# PracticeRaptor v1.8: Core Architecture

## Overview

Version 1.8 introduces a clear separation between **Problem-domain** and **User-domain**,
with a rich **WorkContext** object that unifies both domains for business logic,
and a dedicated **DTO layer** for microservice communication.

## Key Changes from v1.7

| Aspect | v1.7 | v1.8 |
|--------|------|------|
| Domain structure | Flat (all models together) | Split into Problem-domain and User-domain |
| Solution | Mixed concern (template + user code) | Split: ProblemTemplate (Problem) + user code in Draft/Submission |
| Context | None | Rich WorkContext aggregating both domains |
| DTOs | None | Dedicated layer for executor service communication |
| Execution | Domain model with nested Solution | DTO for transport, result merged into Submission |

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DOMAIN LAYER                                   │
│  ┌─────────────────────────────┐    ┌─────────────────────────────────────┐ │
│  │      PROBLEM-DOMAIN         │    │          USER-DOMAIN                │ │
│  │  (static, from DB)          │    │  (dynamic, user-generated)          │ │
│  │                             │    │                                     │ │
│  │  • Problem                  │    │  • User                             │ │
│  │  • ProblemSummary           │    │  • Settings                         │ │
│  │  • ProblemTemplate          │    │  • Draft                            │ │
│  │  • Example                  │    │  • Submission                       │ │
│  │  • TestCase (VO)            │    │  • TestResult (VO)                  │ │
│  │  • CanonicalSolution        │    │                                     │ │
│  │  • LocalizedText (VO)       │    │                                     │ │
│  └──────────────┬──────────────┘    └──────────────┬──────────────────────┘ │
│                 │                                   │                       │
│                 └───────────────┬───────────────────┘                       │
│                                 ▼                                           │
│                    ┌────────────────────────┐                               │
│                    │      WORK CONTEXT      │                               │
│                    │  (runtime aggregate)   │                               │
│                    │                        │                               │
│                    │  • user: User          │                               │
│                    │  • settings: Settings  │                               │
│                    │  • problem: Problem    │                               │
│                    │  • template: Template  │                               │
│                    │  • draft: Draft        │                               │
│                    └────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────────┐   ┌─────────────────────────┐
│   DTO LAYER     │   │  PERSISTENCE LAYER  │   │    PORTS (Protocols)    │
│                 │   │                     │   │                         │
│ ExecutionRequest│   │  Storage Records    │   │  IProblemRepository     │
│ ExecutionResult │   │  (flat, with IDs)   │   │  IUserRepository        │
│                 │   │                     │   │  IExecutorService       │
│ For executor    │   │  Mappers            │   │                         │
│ microservice    │   │  (Domain ↔ Records) │   │                         │
└─────────────────┘   └─────────────────────┘   └─────────────────────────┘
```

## Domain Model Details

### Problem-Domain (Static Content)

These models represent the problem bank — content that exists independently of users.

```
Problem                          ProblemTemplate
├── id: int                      ├── problem_id: int
├── title: LocalizedText         ├── language: ProgrammingLanguage
├── description: LocalizedText   ├── signature: str
├── difficulty: Difficulty       ├── test_cases: tuple[TestCase, ...]
├── complexity: Complexity       └── canonical_solutions: tuple[CanonicalSolution, ...]
├── categories: tuple[Category, ...]
├── tags: tuple[str, ...]
├── examples: tuple[Example, ...]
├── hints: tuple[LocalizedText, ...]
└── editorial: LocalizedText

ProblemSummary                   TestCase (Value Object)
├── id: int                      ├── test: str
├── title: LocalizedText         └── is_example: bool
├── difficulty: Difficulty
├── complexity: Complexity       CanonicalSolution (Value Object)
├── categories                   ├── name: str
├── tags                         ├── complexity: Complexity
└── status: ProblemStatus        └── code: str
```

**Key insight**: `ProblemTemplate` replaces the "template" part of old `Solution`.
It contains everything needed to solve a problem in a specific programming language,
but has NO user-specific data.

### User-Domain (Dynamic Content)

These models represent user-generated content and state.

```
User                             Settings
├── user_id: int                 ├── user_id: int
├── user_name: str               ├── language: Language
└── hash_password: str           ├── programming_language: ProgrammingLanguage
                                 ├── text_editor: TextEditor
                                 └── filters: FilterState

Draft                            Submission
├── draft_id: int                ├── submission_id: int
├── user: User                   ├── user: User
├── problem: Problem             ├── problem: Problem
├── template: ProblemTemplate    ├── template: ProblemTemplate
├── code: str                    ├── code: str
├── created_at: datetime         ├── result: ExecutionStatus
└── updated_at: datetime         ├── total_time_ms: int
                                 ├── memory_used_kb: int
                                 ├── test_results: tuple[TestResult, ...]
                                 ├── error_message: str | None
                                 └── created_at: datetime
```

**Key insight**: `Draft` and `Submission` are rich domain models containing
full nested objects (`User`, `Problem`, `ProblemTemplate`). This makes them
convenient for business logic — no need to fetch related data separately.

### WorkContext (Runtime Aggregate)

`WorkContext` is assembled at runtime and provides unified access to both domains.
It is NOT stored — it's created by a factory function when needed.

```python
@dataclass(frozen=True)
class WorkContext:
    """Complete context for current work session."""

    # User domain
    user: User
    settings: Settings

    # Problem domain (optional - may be None if no problem selected)
    problem: Problem | None = None
    template: ProblemTemplate | None = None

    # User's work on current problem
    draft: Draft | None = None

    # Convenience properties
    @property
    def code(self) -> str:
        """Current code (from draft or empty)."""
        return self.draft.code if self.draft else ""

    @property
    def problem_id(self) -> int | None:
        return self.problem.id if self.problem else None

    @property
    def language(self) -> ProgrammingLanguage:
        return self.settings.programming_language
```

**Factory function**:
```python
def build_work_context(
    user_id: int,
    problem_id: int | None,
    repos: RepositoryContainer,
) -> WorkContext:
    """Assemble WorkContext from repositories."""
    user = repos.users.get_by_id(user_id)
    settings = repos.settings.get_by_user_id(user_id)

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

## DTO Layer (Microservice Communication)

DTOs are used for communication with the executor microservice.
They are flat, serializable, and contain only the data needed for execution.

```python
@dataclass(frozen=True)
class ExecutionRequest:
    """Request to executor service."""
    user_id: int
    problem_id: int
    language: str  # "python3"
    code: str
    test_cases: tuple[str, ...]  # Test code strings
    timeout_sec: int = 5
    memory_limit_mb: int = 256

@dataclass(frozen=True)
class ExecutionResult:
    """Response from executor service."""
    status: str  # "accepted", "wrong_answer", etc.
    test_results: tuple[TestResultDTO, ...]
    total_time_ms: int
    memory_used_kb: int
    error_message: str | None = None

@dataclass(frozen=True)
class TestResultDTO:
    """Single test result from executor."""
    test_index: int
    status: str
    time_ms: int
    memory_kb: int
    error: str | None = None
```

**Conversion flow**:
```
WorkContext + user_code
       ↓
build_execution_request(context, code) → ExecutionRequest
       ↓
[Executor Service]
       ↓
ExecutionResult
       ↓
create_submission(context, code, result) → Submission (rich domain model)
       ↓
[Repository saves as SubmissionRecord]
```

## Storage Records (Persistence Layer)

Records remain flat with ID references, as in v1.7.

```
SubmissionRecord                 DraftRecord
├── submission_id: int           ├── draft_id: int
├── user_id: int                 ├── user_id: int
├── problem_id: int              ├── problem_id: int
├── language: str                ├── language: str
├── code: str                    ├── code: str
├── result: str                  ├── created_at: str
├── total_time_ms: int           └── updated_at: str
├── memory_used_kb: int
├── error_message: str | None
├── test_results_json: str       # Embedded as JSON array
└── created_at: str
```

**Mappers** convert between rich domain models and flat records:
- `SubmissionMapper.to_domain(record, user, problem, template) → Submission`
- `SubmissionMapper.to_record(submission) → SubmissionRecord`

## Directory Structure

```
v1.8_PracticeRaptor/
├── core/
│   ├── models/
│   │   ├── __init__.py           # Public API
│   │   ├── enums.py              # All enumerations
│   │   ├── result.py             # Ok[T] | Err[E]
│   │   ├── errors.py             # Domain errors
│   │   │
│   │   ├── problem/              # Problem-domain models
│   │   │   ├── __init__.py
│   │   │   ├── localization.py   # LocalizedText
│   │   │   ├── problem.py        # Problem, ProblemSummary
│   │   │   ├── template.py       # ProblemTemplate, TestCase, CanonicalSolution
│   │   │   └── example.py        # Example
│   │   │
│   │   ├── user/                 # User-domain models
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # User
│   │   │   ├── settings.py       # Settings
│   │   │   ├── draft.py          # Draft
│   │   │   └── submission.py     # Submission, TestResult
│   │   │
│   │   └── context/              # Runtime context
│   │       ├── __init__.py
│   │       └── work_context.py   # WorkContext
│   │
│   ├── dto/                      # Data Transfer Objects
│   │   ├── __init__.py
│   │   └── execution.py          # ExecutionRequest, ExecutionResult
│   │
│   ├── persistence/              # Storage layer
│   │   ├── records/              # Flat storage structures
│   │   │   ├── __init__.py
│   │   │   ├── problem_records.py
│   │   │   ├── user_records.py
│   │   │   └── execution_records.py
│   │   │
│   │   └── mappers/              # Domain ↔ Records conversion
│   │       ├── __init__.py
│   │       ├── problem_mapper.py
│   │       ├── user_mapper.py
│   │       └── submission_mapper.py
│   │
│   ├── ports/                    # Interfaces (Protocols)
│   │   ├── __init__.py
│   │   └── repositories.py
│   │
│   └── services/                 # Business logic (pure functions)
│       ├── __init__.py
│       ├── problems.py
│       └── execution.py
│
└── README.md                     # This file
```

## Key Design Decisions

### 1. No Inheritance

Following the functional preference, we use composition over inheritance:
- No `BaseSolution` parent class
- No `CanonicalSolution extends Solution`
- Models are flat dataclasses with embedded value objects

### 2. Rich Domain Models

Domain models (`Submission`, `Draft`) contain full nested objects:
```python
submission.user.user_name        # Direct access
submission.problem.title.get("ru")  # Deep access
submission.template.test_cases   # Access to test cases
```

This is convenient for business logic but requires mappers for storage.

### 3. Separation of Concerns

| Layer | Contains | Responsibility |
|-------|----------|----------------|
| Domain Models | Rich objects with behavior | Business logic, validation |
| DTOs | Flat transport objects | Microservice communication |
| Storage Records | Flat primitives + IDs | Database/JSON serialization |
| Mappers | Conversion functions | Layer translation |

### 4. WorkContext as Aggregate

Instead of a God-object with methods, `WorkContext` is a frozen dataclass
that aggregates related data. Business logic lives in service functions
that receive `WorkContext` as a parameter.

### 5. Execution is Transient

`Execution` (from v1.6/v1.7) is replaced by:
- `ExecutionRequest` / `ExecutionResult` (DTOs for executor service)
- `Submission` (persisted result with full context)

There's no need for a separate `Execution` domain model —
the executor returns a DTO, which is immediately converted to `Submission`.

## Migration from v1.7

1. **Solution → ProblemTemplate + code**
   - Extract signature, test_cases, canonical_solutions into `ProblemTemplate`
   - User's code is stored in `Draft.code` or `Submission.code`

2. **Execution → ExecutionResult (DTO) + Submission**
   - Remove `Execution` domain model
   - Use `ExecutionResult` DTO for executor communication
   - Persist results directly as `Submission`

3. **Add WorkContext**
   - Create factory function to build context
   - Update services to accept `WorkContext` instead of individual objects

4. **Reorganize files**
   - Move models to `problem/` and `user/` subdirectories
   - Create `dto/` directory
   - Update imports
