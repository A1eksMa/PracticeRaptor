"""Domain models for PracticeRaptor v1.6 - immutable data structures.

This module contains all domain models following these principles:
- Immutability: all dataclasses are frozen
- Separation: Language (interface) vs ProgrammingLanguage (code)
- Normalization: multilingual data as separate records, not dictionaries
- Lazy loading: Problem split into lightweight (list) and heavyweight (details) parts
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


# ============================================================
# Enumerations
# ============================================================


class Language(str, Enum):
    """Supported interface languages."""
    EN = "en"  # English (default)
    RU = "ru"  # Russian


class ProgrammingLanguage(str, Enum):
    """Supported programming languages."""
    PYTHON = "python3"
    JAVA = "java"


class TextEditor(str, Enum):
    """Supported text editors for CLI."""
    DEFAULT = "default"
    NANO = "nano"
    VIM = "vim"


class Difficulty(str, Enum):
    """Problem difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(str, Enum):
    """Problem categories."""
    ARRAY = "Array"
    STRING = "String"
    HASH_TABLE = "Hash Table"
    TWO_POINTERS = "Two Pointers"
    LINKED_LIST = "Linked List"
    STACK = "Stack"
    QUEUE = "Queue"
    TREE = "Tree"
    GRAPH = "Graph"
    BINARY_SEARCH = "Binary Search"
    DYNAMIC_PROGRAMMING = "Dynamic Programming"
    GREEDY = "Greedy"
    BACKTRACKING = "Backtracking"
    BIT_MANIPULATION = "Bit Manipulation"
    MATH = "Math"
    SORTING = "Sorting"
    HEAP = "Heap"


class Complexity(str, Enum):
    """Algorithmic complexity (Big O notation)."""
    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N2 = "O(n²)"
    O_N3 = "O(n³)"
    O_2N = "O(2ⁿ)"
    O_N_FACTORIAL = "O(n!)"


class Status(str, Enum):
    """User progress status on a problem."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class SubmissionStatus(str, Enum):
    """Status of code execution result."""
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SYNTAX_ERROR = "syntax_error"


# ============================================================
# Value Objects (localized content)
# ============================================================


@dataclass(frozen=True)
class Title:
    """Localized problem title."""
    problem_id: int
    language: Language
    title: str = ""


@dataclass(frozen=True)
class Description:
    """Localized problem description."""
    problem_id: int
    language: Language
    description: str = ""


@dataclass(frozen=True)
class Editorial:
    """Localized problem editorial (solution explanation)."""
    problem_id: int
    language: Language
    editorial: str = ""


@dataclass(frozen=True)
class Explanation:
    """Localized example explanation."""
    example_id: int
    language: Language
    explanation: str = ""


@dataclass(frozen=True)
class Hint:
    """Localized problem hint."""
    problem_id: int
    language: Language
    hint: str = ""


# ============================================================
# Value Objects (language-specific content)
# ============================================================


@dataclass(frozen=True)
class Signature:
    """Function signature for a specific programming language."""
    problem_id: int
    programming_language: ProgrammingLanguage
    signature: str = ""


@dataclass(frozen=True)
class CanonicalSolution:
    """Reference solution for a specific programming language."""
    problem_id: int
    programming_language: ProgrammingLanguage
    canonical_solution: str = ""


@dataclass(frozen=True)
class Tag:
    """Problem tag (flexible labeling system)."""
    problem_id: int
    tag: str = ""


# ============================================================
# Entities - User Management
# ============================================================


@dataclass(frozen=True)
class User:
    """User entity with authentication data."""
    user_id: int = 0
    user_name: str = ""
    hash_password: str = ""  # Hashed password
    email: str = ""


@dataclass(frozen=True)
class Settings:
    """User preferences and current session state."""
    user_id: int = 0
    language: Language = Language.EN
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    text_editor: TextEditor = TextEditor.DEFAULT

    # Current selections (session state)
    select_problem_id: int | None = None
    select_difficulty: Difficulty | None = None
    select_tags: tuple[str, ...] = ()
    select_category: Category | None = None
    select_status: Status | None = None


# ============================================================
# Entities - Problem (lightweight for list view)
# ============================================================


@dataclass(frozen=True)
class Problem:
    """Minimal problem entity for list display."""
    problem_id: int = 0
    # Note: title is in separate Title entity
    # Note: status is user-specific, stored in Progress entity
    status: Status = Status.NOT_STARTED  # Current user's status


@dataclass(frozen=True)
class ProblemSelector:
    """Problem metadata for filtering and selection."""
    problem_id: int = 0
    supported_languages: tuple[Language, ...] = ()
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = ()
    difficulty: Difficulty = Difficulty.EASY
    tags: tuple[str, ...] = ()
    categories: tuple[Category, ...] = ()


# ============================================================
# Entities - Problem Details (heavyweight)
# ============================================================


@dataclass(frozen=True)
class Example:
    """Problem example with input/output."""
    example_id: int
    problem_id: int
    input: str = ""
    output: str = ""
    # Note: explanation is in separate Explanation entity


@dataclass(frozen=True)
class ProblemDescription:
    """Complete problem description with all details."""
    problem_id: int = 0
    complexity: Complexity = Complexity.O_N
    # Note: description, editorial, hints are in separate entities
    examples: tuple[Example, ...] = ()


# ============================================================
# Entities - Solution and Testing
# ============================================================


@dataclass(frozen=True)
class TestCase:
    """Test case as executable code for a specific language."""
    test_case_id: int
    problem_id: int
    programming_language: ProgrammingLanguage
    test: str = ""  # Executable test code (e.g., "assert solution([2,7], 9) == [0,1]")


@dataclass(frozen=True)
class Solution:
    """Working solution object (mutable in memory, frozen at boundaries).

    This represents the specification and user's work in progress:
    - Signature and canonical solutions (from problem)
    - User's code (initially empty, filled during solving)
    - Tests (all) and test_cases (indices for quick check)
    """
    problem_id: int
    programming_language: ProgrammingLanguage
    function_signature: Signature
    canonical_solutions: tuple[CanonicalSolution, ...] = ()
    code: str = ""  # User's code (initially empty)
    tests: tuple[TestCase, ...] = ()  # All tests (for submission)
    test_cases: tuple[int, ...] = ()  # Indices of tests for quick check (examples)


@dataclass(frozen=True)
class Draft:
    """Saved snapshot of user's solution.

    Created on events: code check, program exit, manual save.
    """
    solution: Solution
    created_at: datetime
    updated_at: datetime


# ============================================================
# Entities - Execution Results
# ============================================================


@dataclass(frozen=True)
class TestResult:
    """Result of executing a single test case."""
    test_case: TestCase
    result: SubmissionStatus
    error_message: str | None = None
    test_time_ms: int = 0
    test_memory_used_kb: int = 0


@dataclass(frozen=True)
class Execution:
    """Result of executing solution against test cases."""
    solution: Solution
    total_time_ms: int = 0
    memory_used_kb: int = 0
    test_results: tuple[TestResult, ...] = ()
    error_message: str | None = None
    result: SubmissionStatus = SubmissionStatus.ACCEPTED


@dataclass(frozen=True)
class Submission:
    """Successful submission record."""
    submission_id: int
    created_at: datetime
    execution: Execution
