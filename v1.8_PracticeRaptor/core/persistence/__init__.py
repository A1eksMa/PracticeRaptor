"""Persistence layer - storage records and mappers.

This layer handles conversion between rich domain models
and flat storage records.

Usage:
    from core.persistence.records import ProblemRecord, UserRecord
    from core.persistence.mappers import ProblemMapper
"""

from .records import (
    # Problem records
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
    # User records
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
