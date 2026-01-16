"""Storage Records - flat structures for persistence.

Records contain only primitive types (str, int, float, bool, None).
No datetime, Enum, or nested objects.
Designed to map 1:1 to JSON objects or SQL rows.
"""

from .problem_records import (
    ProblemRecord,
    TitleRecord,
    DescriptionRecord,
    ExampleRecord,
    ExplanationRecord,
    HintRecord,
    TagRecord,
    EditorialRecord,
    TemplateRecord,
    TestCaseRecord,
    CanonicalSolutionRecord,
)
from .user_records import (
    UserRecord,
    SettingsRecord,
    DraftRecord,
    SubmissionRecord,
    TestResultRecord,
)

__all__ = [
    # Problem records
    "ProblemRecord",
    "TitleRecord",
    "DescriptionRecord",
    "ExampleRecord",
    "ExplanationRecord",
    "HintRecord",
    "TagRecord",
    "EditorialRecord",
    "TemplateRecord",
    "TestCaseRecord",
    "CanonicalSolutionRecord",
    # User records
    "UserRecord",
    "SettingsRecord",
    "DraftRecord",
    "SubmissionRecord",
    "TestResultRecord",
]
