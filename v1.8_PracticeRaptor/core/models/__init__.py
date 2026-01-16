"""Core domain models.

This module provides the public API for all domain models.

Usage:
    from core.models import Problem, User, WorkContext
    from core.models import ExecutionStatus, Difficulty
    from core.models import Ok, Err, Result
"""

# Result type
from .result import Ok, Err, Result

# Errors
from .errors import (
    DomainError,
    NotFoundError,
    ValidationError,
    ExecutionError,
    StorageError,
    AuthError,
)

# Enums
from .enums import (
    Language,
    ProgrammingLanguage,
    TextEditor,
    Difficulty,
    Category,
    Complexity,
    ProblemStatus,
    ExecutionStatus,
)

# Problem-domain models
from .problem import (
    LocalizedText,
    text,
    Example,
    TestCase,
    CanonicalSolution,
    ProblemTemplate,
    Problem,
    ProblemSummary,
)

# User-domain models
from .user import (
    User,
    DEFAULT_USER,
    Settings,
    FilterState,
    DEFAULT_SETTINGS,
    Draft,
    TestResult,
    Submission,
)

# Context
from .context import WorkContext


__all__ = [
    # Result
    "Ok",
    "Err",
    "Result",
    # Errors
    "DomainError",
    "NotFoundError",
    "ValidationError",
    "ExecutionError",
    "StorageError",
    "AuthError",
    # Enums
    "Language",
    "ProgrammingLanguage",
    "TextEditor",
    "Difficulty",
    "Category",
    "Complexity",
    "ProblemStatus",
    "ExecutionStatus",
    # Problem-domain
    "LocalizedText",
    "text",
    "Example",
    "TestCase",
    "CanonicalSolution",
    "ProblemTemplate",
    "Problem",
    "ProblemSummary",
    # User-domain
    "User",
    "DEFAULT_USER",
    "Settings",
    "FilterState",
    "DEFAULT_SETTINGS",
    "Draft",
    "TestResult",
    "Submission",
    # Context
    "WorkContext",
]
