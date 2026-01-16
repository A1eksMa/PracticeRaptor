"""Problem template models for code execution.

ProblemTemplate contains everything needed to solve a problem
in a specific programming language. It is purely Problem-domain
and has no User-specific data.
"""

from dataclasses import dataclass

from ..enums import Complexity, ProgrammingLanguage


@dataclass(frozen=True)
class TestCase:
    """Executable test case.

    Value object. Contains the test code as a string
    that will be executed by the executor service.

    Example:
        test = TestCase(
            test="assert two_sum([2, 7, 11, 15], 9) == [0, 1]",
            is_example=True,
        )
    """

    test: str
    is_example: bool = False

    def __str__(self) -> str:
        return self.test


@dataclass(frozen=True)
class CanonicalSolution:
    """Reference solution shown after user solves the problem.

    Value object. Multiple solutions per problem supported
    (different algorithmic approaches).

    Example:
        solution = CanonicalSolution(
            name="Hash Map (One Pass)",
            complexity=Complexity.O_N,
            code="def two_sum(nums, target):\\n    seen = {}\\n    ...",
        )
    """

    name: str
    complexity: Complexity
    code: str

    def __str__(self) -> str:
        return f"{self.name} - {self.complexity.value}"


@dataclass(frozen=True)
class ProblemTemplate:
    """Everything needed to solve a problem in a specific language.

    This is the "working material" for problem solving:
    - Function signature (what user must implement)
    - Test cases (for validation)
    - Canonical solutions (shown after solving)

    Purely Problem-domain. No User-specific data.
    One ProblemTemplate per (problem_id, language) pair.

    Example:
        template = ProblemTemplate(
            problem_id=1,
            language=ProgrammingLanguage.PYTHON,
            signature="def two_sum(nums: list[int], target: int) -> list[int]:",
            test_cases=(...),
            canonical_solutions=(...),
        )

        # Get example tests for quick check
        examples = template.example_tests

        # Get all tests for full submission
        all_tests = template.test_cases
    """

    problem_id: int
    language: ProgrammingLanguage
    signature: str
    test_cases: tuple[TestCase, ...] = ()
    canonical_solutions: tuple[CanonicalSolution, ...] = ()

    @property
    def example_tests(self) -> tuple[TestCase, ...]:
        """Get only example test cases (for quick check)."""
        return tuple(t for t in self.test_cases if t.is_example)

    @property
    def hidden_tests(self) -> tuple[TestCase, ...]:
        """Get only hidden test cases."""
        return tuple(t for t in self.test_cases if not t.is_example)

    @property
    def test_count(self) -> int:
        """Total number of test cases."""
        return len(self.test_cases)

    @property
    def example_count(self) -> int:
        """Number of example test cases."""
        return len(self.example_tests)

    def get_test_strings(self, examples_only: bool = False) -> tuple[str, ...]:
        """Get test code strings for execution.

        Args:
            examples_only: If True, return only example tests

        Returns:
            Tuple of test code strings
        """
        tests = self.example_tests if examples_only else self.test_cases
        return tuple(t.test for t in tests)
