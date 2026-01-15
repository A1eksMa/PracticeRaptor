"""Execution-related persistence records.

Each record corresponds to a JSON file or SQL table.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass


@dataclass
class TestResultRecord:
    """Result of executing a single test case.

    Maps to: test_results.json / TABLE test_results
    Primary key: test_result_id
    """

    test_result_id: int
    test_case_id: int
    result: str  # e.g., "accepted", "wrong_answer"
    error_message: str | None = None
    test_time_ms: int = 0
    test_memory_used_kb: int = 0


@dataclass
class ExecutionRecord:
    """Aggregated results of running all tests for a solution.

    Maps to: executions.json / TABLE executions
    Primary key: execution_id
    """

    execution_id: int
    user_id: int
    solution_id: int

    test_result_ids: list[int]  # References TestResultRecord.test_result_id

    total_time_ms: int = 0
    memory_used_kb: int = 0
    error_message: str | None = None
    result: str  # e.g., "accepted", "wrong_answer"


@dataclass
class SubmissionRecord:
    """Submission record (any execution result).

    Maps to: submissions.json / TABLE submissions
    Primary key: submission_id
    """

    submission_id: int
    created_at: str  # ISO formatted datetime string
    execution_id: int  # References ExecutionRecord.execution_id


@dataclass
class DraftRecord:
    """User-specific solution draft.

    Maps to: drafts.json / TABLE drafts
    Primary key: draft_id
    """

    draft_id: int
    user_id: int  # References UserRecord.user_id
    problem_id: int
    code: str
    created_at: str  # ISO formatted datetime string
    updated_at: str  # ISO formatted datetime string
