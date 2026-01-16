"""Submission model - persisted execution result."""

from dataclasses import dataclass
from datetime import datetime

from ..enums import ExecutionStatus
from ..problem import Problem, ProblemTemplate
from .user import User


@dataclass(frozen=True)
class TestResult:
    """Result of executing a single test case.

    Value object embedded in Submission.

    Example:
        result = TestResult(
            test_index=0,
            status=ExecutionStatus.ACCEPTED,
            time_ms=15,
            memory_kb=1024,
        )
    """

    test_index: int
    status: ExecutionStatus
    time_ms: int = 0
    memory_kb: int = 0
    error_message: str | None = None

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == ExecutionStatus.ACCEPTED

    @property
    def failed(self) -> bool:
        """Check if test failed."""
        return self.status != ExecutionStatus.ACCEPTED


@dataclass(frozen=True)
class Submission:
    """Persisted execution result.

    Rich domain model with full nested objects:
    - User who submitted
    - Problem that was solved
    - ProblemTemplate used
    - Code submitted
    - Execution results

    All submissions are stored (accepted, wrong_answer, etc.).
    User statistics computed from accepted submissions only.

    Example:
        submission = Submission(
            submission_id=1,
            user=user,
            problem=problem,
            template=template,
            code="def two_sum(...): ...",
            result=ExecutionStatus.ACCEPTED,
            total_time_ms=45,
            memory_used_kb=2048,
            test_results=(...),
            created_at=datetime.now(),
        )

        if submission.is_accepted:
            print(f"Solved in {submission.total_time_ms}ms")
    """

    submission_id: int
    user: User
    problem: Problem
    template: ProblemTemplate
    code: str
    result: ExecutionStatus
    total_time_ms: int
    memory_used_kb: int
    test_results: tuple[TestResult, ...]
    error_message: str | None
    created_at: datetime

    # ========================================
    # Convenience properties
    # ========================================

    @property
    def user_id(self) -> int:
        """User ID shortcut."""
        return self.user.user_id

    @property
    def problem_id(self) -> int:
        """Problem ID shortcut."""
        return self.problem.id

    @property
    def language(self):
        """Programming language shortcut."""
        return self.template.language

    # ========================================
    # Result analysis
    # ========================================

    @property
    def is_accepted(self) -> bool:
        """Check if submission was accepted (all tests passed)."""
        return self.result == ExecutionStatus.ACCEPTED

    @property
    def passed_count(self) -> int:
        """Count of passed tests."""
        return sum(1 for r in self.test_results if r.passed)

    @property
    def failed_count(self) -> int:
        """Count of failed tests."""
        return sum(1 for r in self.test_results if r.failed)

    @property
    def total_count(self) -> int:
        """Total number of tests run."""
        return len(self.test_results)

    @property
    def first_failed(self) -> TestResult | None:
        """Get first failed test result."""
        for r in self.test_results:
            if r.failed:
                return r
        return None

    def get_result_summary(self) -> str:
        """Get human-readable result summary."""
        if self.is_accepted:
            return f"Accepted ({self.total_time_ms}ms, {self.memory_used_kb}KB)"
        return f"{self.result.value}: {self.passed_count}/{self.total_count} tests passed"


def create_submission(
    submission_id: int,
    user: User,
    problem: Problem,
    template: ProblemTemplate,
    code: str,
    result: ExecutionStatus,
    total_time_ms: int,
    memory_used_kb: int,
    test_results: tuple[TestResult, ...],
    error_message: str | None = None,
) -> Submission:
    """Factory function to create a new Submission.

    Args:
        submission_id: Unique submission ID
        user: User who submitted
        problem: Problem that was solved
        template: Problem template used
        code: Submitted code
        result: Overall execution result
        total_time_ms: Total execution time
        memory_used_kb: Memory used
        test_results: Individual test results
        error_message: Error message if failed

    Returns:
        New Submission with current timestamp
    """
    return Submission(
        submission_id=submission_id,
        user=user,
        problem=problem,
        template=template,
        code=code,
        result=result,
        total_time_ms=total_time_ms,
        memory_used_kb=memory_used_kb,
        test_results=test_results,
        error_message=error_message,
        created_at=datetime.now(),
    )
