"""Persistence records - flat structures for storage.

Records contain only primitive types (str, int, float, bool, None).
No datetime, Enum, or nested objects.
Designed to map 1:1 to JSON objects or SQL rows.
"""

from .problem_records import (
    ExampleRecord,
    ExplanationRecord,
    HintRecord,
    ProblemDescriptionRecord,
    ProblemRecord,
    TagRecord,
    TitleRecord,
)
from .solution_records import (
    CanonicalSolutionRecord,
    SignatureRecord,
    TestCaseRecord,
)

__all__ = [
    # Problem
    "ProblemRecord",
    "TitleRecord",
    "ProblemDescriptionRecord",
    "ExampleRecord",
    "ExplanationRecord",
    "HintRecord",
    "TagRecord",
    # Solution
    "SignatureRecord",
    "TestCaseRecord",
    "CanonicalSolutionRecord",
]
