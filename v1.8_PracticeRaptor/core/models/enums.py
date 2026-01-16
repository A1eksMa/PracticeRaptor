"""Domain enumerations.

All enums inherit from (str, Enum) for easy serialization.
"""

from enum import Enum


# ============================================================
# Localization
# ============================================================


class Language(str, Enum):
    """Supported UI languages."""

    EN = "en"
    RU = "ru"


# ============================================================
# Programming
# ============================================================


class ProgrammingLanguage(str, Enum):
    """Supported programming languages for code execution."""

    PYTHON = "python3"
    JAVA = "java"
    GO = "go"
    JAVASCRIPT = "javascript"


class TextEditor(str, Enum):
    """Preferred text editor for CLI."""

    DEFAULT = "default"
    NANO = "nano"
    VIM = "vim"
    VSCODE = "code"


# ============================================================
# Problem Classification
# ============================================================


class Difficulty(str, Enum):
    """Problem difficulty level."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Category(str, Enum):
    """Algorithmic problem category."""

    ARRAY = "array"
    STRING = "string"
    HASH_TABLE = "hash_table"
    LINKED_LIST = "linked_list"
    STACK = "stack"
    QUEUE = "queue"
    TREE = "tree"
    GRAPH = "graph"
    SORTING = "sorting"
    BINARY_SEARCH = "binary_search"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    GREEDY = "greedy"
    BACKTRACKING = "backtracking"
    RECURSION = "recursion"
    MATH = "math"
    BIT_MANIPULATION = "bit_manipulation"
    TWO_POINTERS = "two_pointers"
    SLIDING_WINDOW = "sliding_window"


class Complexity(str, Enum):
    """Algorithmic complexity (Big O notation)."""

    O_1 = "O(1)"
    O_LOG_N = "O(log n)"
    O_N = "O(n)"
    O_N_LOG_N = "O(n log n)"
    O_N_SQUARED = "O(n²)"
    O_N_CUBED = "O(n³)"
    O_2_N = "O(2ⁿ)"
    O_N_FACTORIAL = "O(n!)"


# ============================================================
# Status
# ============================================================


class ProblemStatus(str, Enum):
    """User's progress status on a problem."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"


class ExecutionStatus(str, Enum):
    """Code execution result status."""

    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SYNTAX_ERROR = "syntax_error"
