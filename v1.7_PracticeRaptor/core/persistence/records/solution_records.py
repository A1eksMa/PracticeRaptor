"""Solution-related persistence records.

Each record corresponds to a JSON file or SQL table.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass


@dataclass
class SignatureRecord:
    """Function signature for a programming language.

    Maps to: signatures.json / TABLE signatures
    Primary key: (problem_id, programming_language)
    """

    problem_id: int
    programming_language: str  # "python3", "java"
    template: str  # "def two_sum(nums: list[int], target: int) -> list[int]:"
    function_name: str  # "two_sum"


@dataclass
class TestCaseRecord:
    """Executable test case.

    Maps to: test_cases.json / TABLE test_cases
    Primary key: test_case_id
    """

    test_case_id: int
    problem_id: int
    programming_language: str
    code: str  # "assert two_sum([2, 7, 11, 15], 9) == [0, 1]"
    is_example: bool  # True = shown in problem examples


@dataclass
class CanonicalSolutionRecord:
    """Reference solution.

    Maps to: canonical_solutions.json / TABLE canonical_solutions
    Primary key: canonical_solution_id
    """

    canonical_solution_id: int
    problem_id: int
    programming_language: str
    name: str  # "Hash Map (One Pass)"
    complexity: str  # "O(n)"
    code: str
