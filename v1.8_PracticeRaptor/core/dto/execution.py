"""Execution DTOs for executor service communication.

These DTOs are used for:
- Sending code execution requests to executor microservice
- Receiving execution results from executor microservice

All fields are primitives (str, int, bool) for easy JSON serialization.
"""

from dataclasses import dataclass

from ..models.context import WorkContext


@dataclass(frozen=True)
class ExecutionRequest:
    """Request to executor service.

    Flat structure with all data needed for code execution.
    Serialized to JSON for HTTP API call.

    Example:
        request = ExecutionRequest(
            user_id=1,
            problem_id=42,
            language="python3",
            code="def two_sum(nums, target): ...",
            test_cases=("assert two_sum([2,7], 9) == [0,1]",),
            timeout_sec=5,
            memory_limit_mb=256,
        )
    """

    user_id: int
    problem_id: int
    language: str  # "python3", "java", etc.
    code: str
    test_cases: tuple[str, ...]  # Test code strings
    timeout_sec: int = 5
    memory_limit_mb: int = 256

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "language": self.language,
            "code": self.code,
            "test_cases": list(self.test_cases),
            "timeout_sec": self.timeout_sec,
            "memory_limit_mb": self.memory_limit_mb,
        }


@dataclass(frozen=True)
class TestResultDTO:
    """Single test result from executor.

    Flat structure for API response.
    """

    test_index: int
    status: str  # "accepted", "wrong_answer", etc.
    time_ms: int = 0
    memory_kb: int = 0
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == "accepted"

    @classmethod
    def from_dict(cls, data: dict) -> "TestResultDTO":
        """Create from dictionary."""
        return cls(
            test_index=data["test_index"],
            status=data["status"],
            time_ms=data.get("time_ms", 0),
            memory_kb=data.get("memory_kb", 0),
            error=data.get("error"),
        )


@dataclass(frozen=True)
class ExecutionResult:
    """Response from executor service.

    Flat structure with execution results.
    Deserialized from JSON HTTP response.

    Example:
        result = ExecutionResult(
            status="accepted",
            test_results=(...),
            total_time_ms=45,
            memory_used_kb=2048,
        )
    """

    status: str  # "accepted", "wrong_answer", "runtime_error", etc.
    test_results: tuple[TestResultDTO, ...]
    total_time_ms: int
    memory_used_kb: int
    error_message: str | None = None

    @property
    def is_accepted(self) -> bool:
        return self.status == "accepted"

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.test_results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.test_results)

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionResult":
        """Create from dictionary (JSON response)."""
        test_results = tuple(
            TestResultDTO.from_dict(r)
            for r in data.get("test_results", [])
        )
        return cls(
            status=data["status"],
            test_results=test_results,
            total_time_ms=data.get("total_time_ms", 0),
            memory_used_kb=data.get("memory_used_kb", 0),
            error_message=data.get("error_message"),
        )


# ============================================================
# Factory functions
# ============================================================


def build_execution_request(
    context: WorkContext,
    code: str,
    examples_only: bool = False,
    timeout_sec: int = 5,
    memory_limit_mb: int = 256,
) -> ExecutionRequest:
    """Build ExecutionRequest from WorkContext.

    Args:
        context: Current work context with user, problem, template
        code: Code to execute
        examples_only: If True, run only example tests (quick check)
        timeout_sec: Execution timeout
        memory_limit_mb: Memory limit

    Returns:
        ExecutionRequest ready for executor service

    Raises:
        ValueError: If context is missing required data

    Example:
        request = build_execution_request(context, user_code)
        response = executor_client.execute(request)
    """
    if not context.has_problem or not context.has_template:
        raise ValueError("WorkContext must have problem and template")

    test_cases = context.template.get_test_strings(examples_only=examples_only)

    return ExecutionRequest(
        user_id=context.user_id,
        problem_id=context.problem_id,
        language=context.template.language.value,
        code=code,
        test_cases=test_cases,
        timeout_sec=timeout_sec,
        memory_limit_mb=memory_limit_mb,
    )
