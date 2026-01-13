"""Problem-related persistence records.

Each record corresponds to a JSON file or SQL table.
All fields are primitives - ready for serialization.
"""

from dataclasses import dataclass


@dataclass
class ProblemRecord:
    """Core problem data.

    Maps to: problems.json / TABLE problems
    """

    problem_id: int
    difficulty: str  # "easy", "medium", "hard"
    complexity: str  # "O(n)", "O(n²)", etc.
    categories: list[str]  # ["Array", "Hash Table"]
    supported_languages: list[str]  # ["python3", "java"]


@dataclass
class TitleRecord:
    """Localized problem title.

    Maps to: titles.json / TABLE titles
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str  # "en", "ru"
    title: str


@dataclass
class ProblemDescriptionRecord:
    """Localized problem description.

    Maps to: descriptions.json / TABLE descriptions
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str
    description: str


@dataclass
class ExampleRecord:
    """Problem example (input/output).

    Maps to: examples.json / TABLE examples
    Primary key: example_id
    """

    example_id: int
    problem_id: int
    input: str  # "nums = [2,7,11,15], target = 9"
    output: str  # "[0, 1]"


@dataclass
class ExplanationRecord:
    """Localized example explanation.

    Maps to: explanations.json / TABLE explanations
    Primary key: (example_id, language)
    """

    example_id: int
    language: str
    explanation: str


@dataclass
class HintRecord:
    """Localized problem hint.

    Maps to: hints.json / TABLE hints
    Primary key: (problem_id, language, hint_index)
    """

    problem_id: int
    language: str
    hint_index: int  # Order within problem
    hint: str


@dataclass
class TagRecord:
    """Problem tag.

    Maps to: tags.json / TABLE tags
    Primary key: (problem_id, tag)
    """

    problem_id: int
    tag: str  # "array", "hash-table", etc.


@dataclass
class EditorialRecord:
    """Localized problem editorial.

    Maps to: editorials.json / TABLE editorials
    Primary key: (problem_id, language)
    """

    problem_id: int
    language: str
    editorial: str
