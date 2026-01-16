"""Problem-domain storage records.

Flat structures for database/JSON persistence.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass, field


# ============================================================
# Problem Core Records
# ============================================================


@dataclass
class ProblemRecord:
    """Core problem data.

    Maps to: problems.json / TABLE problems
    Primary key: id
    """

    id: int
    difficulty: str  # "easy", "medium", "hard"
    complexity: str  # "O(n)", "O(n²)", etc.
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    supported_languages: list[str] = field(default_factory=lambda: ["en"])
    supported_programming_languages: list[str] = field(default_factory=lambda: ["python3"])


@dataclass
class TitleRecord:
    """Localized problem title.

    Maps to: titles.json / TABLE problem_titles
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str  # "en", "ru"
    title: str


@dataclass
class DescriptionRecord:
    """Localized problem description.

    Maps to: descriptions.json / TABLE problem_descriptions
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str
    description: str


@dataclass
class ExampleRecord:
    """Problem example (input/output).

    Maps to: examples.json / TABLE problem_examples
    Primary key: example_id
    """

    example_id: int
    problem_id: int
    input: str
    output: str


@dataclass
class ExplanationRecord:
    """Localized example explanation.

    Maps to: explanations.json / TABLE example_explanations
    Primary key: (example_id, language)
    """

    example_id: int
    language: str
    explanation: str


@dataclass
class HintRecord:
    """Localized problem hint.

    Maps to: hints.json / TABLE problem_hints
    Primary key: (problem_id, language, hint_index)
    """

    problem_id: int
    language: str
    hint_index: int
    hint: str


@dataclass
class TagRecord:
    """Problem tag (denormalized for search).

    Maps to: problem_tags.json / TABLE problem_tags
    Primary key: (problem_id, tag)
    """

    problem_id: int
    tag: str


@dataclass
class EditorialRecord:
    """Localized problem editorial.

    Maps to: editorials.json / TABLE problem_editorials
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str
    editorial: str


# ============================================================
# Template Records (Problem-domain, per programming language)
# ============================================================


@dataclass
class TemplateRecord:
    """Problem template for a programming language.

    Maps to: templates.json / TABLE problem_templates
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str  # "python3", "java"
    signature: str  # Function signature


@dataclass
class TestCaseRecord:
    """Executable test case.

    Maps to: test_cases.json / TABLE test_cases
    Primary key: test_case_id
    """

    test_case_id: int
    problem_id: int
    language: str  # "python3"
    test: str  # "assert two_sum([2, 7], 9) == [0, 1]"
    is_example: bool = False


@dataclass
class CanonicalSolutionRecord:
    """Reference solution.

    Maps to: canonical_solutions.json / TABLE canonical_solutions
    Primary key: canonical_solution_id
    """

    canonical_solution_id: int
    problem_id: int
    language: str  # "python3"
    name: str  # "Hash Map (One Pass)"
    complexity: str  # "O(n)"
    code: str
