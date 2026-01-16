"""User-domain storage records.

Flat structures for database/JSON persistence.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass, field


@dataclass
class UserRecord:
    """User entity.

    Maps to: users.json / TABLE users
    Primary key: user_id
    """

    user_id: int
    user_name: str = ""
    hash_password: str = ""


@dataclass
class SettingsRecord:
    """User settings.

    Maps to: settings.json / TABLE user_settings
    Primary key: user_id
    """

    user_id: int

    # Persistent preferences
    language: str = "en"  # UI language
    programming_language: str = "python3"
    text_editor: str = "default"

    # Session state (filters)
    filter_problem_id: int | None = None
    filter_difficulty: str | None = None
    filter_category: str | None = None
    filter_tags: list[str] = field(default_factory=list)
    filter_status: str | None = None


@dataclass
class DraftRecord:
    """User's draft solution.

    Maps to: drafts.json / TABLE drafts
    Primary key: draft_id
    Unique constraint: (user_id, problem_id, language)
    """

    draft_id: int
    user_id: int
    problem_id: int
    language: str  # "python3"
    code: str
    created_at: str  # ISO format datetime
    updated_at: str  # ISO format datetime


@dataclass
class TestResultRecord:
    """Single test result (embedded in SubmissionRecord).

    Not stored as separate table - serialized as JSON array in submission.
    """

    test_index: int
    status: str  # "accepted", "wrong_answer", etc.
    time_ms: int = 0
    memory_kb: int = 0
    error_message: str | None = None


@dataclass
class SubmissionRecord:
    """Submission result.

    Maps to: submissions.json / TABLE submissions
    Primary key: submission_id
    """

    submission_id: int
    user_id: int
    problem_id: int
    language: str  # "python3"
    code: str
    result: str  # "accepted", "wrong_answer", etc.
    total_time_ms: int
    memory_used_kb: int
    error_message: str | None
    test_results_json: str  # JSON array of TestResultRecord
    created_at: str  # ISO format datetime
