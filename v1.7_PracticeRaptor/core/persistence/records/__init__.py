"""Persistence records - flat structures for storage.

Records contain only primitive types (str, int, float, bool, None).
No datetime, Enum, or nested objects.
Designed to map 1:1 to JSON objects or SQL rows.
"""

from .execution_records import (
    DraftRecord,
    ExecutionRecord,
    SubmissionRecord,
    TestResultRecord,
)
from .problem_records import (
    EditorialRecord,
    ExampleRecord,
    ExplanationRecord,
    HintRecord,
    ProblemDescriptionRecord,
    ProblemRecord,
    TagRecord,
    TitleRecord,
)
from .settings_records import SettingsRecord
from .solution_records import (
    CanonicalSolutionRecord,
    SignatureRecord,
    SolutionRecord,
    TestCaseRecord,
)
from .user_records import UserRecord

__all__ = [
    # Problem
    "ProblemRecord",
    "TitleRecord",
    "ProblemDescriptionRecord",
    "ExampleRecord",
    "ExplanationRecord",
    "HintRecord",
    "TagRecord",
    "EditorialRecord",
    # Solution
    "SignatureRecord",
    "TestCaseRecord",
    "CanonicalSolutionRecord",
    "SolutionRecord",
    # Execution
    "TestResultRecord",
    "ExecutionRecord",
    "SubmissionRecord",
    # Draft
    "DraftRecord",
    # User
    "UserRecord",
    # Settings
    "SettingsRecord",
]