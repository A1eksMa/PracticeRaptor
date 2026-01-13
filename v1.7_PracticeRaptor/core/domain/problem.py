"""Problem domain models - rich objects with nested data."""

from dataclasses import dataclass, field

from .enums import Category, Complexity, Difficulty, ProblemStatus, ProgrammingLanguage
from .localization import LocalizedText


@dataclass(frozen=True)
class Example:
    """Problem example with input/output and explanation.

    All data is embedded - no ID references.
    """

    input: str
    output: str
    explanation: LocalizedText = field(default_factory=LocalizedText)


@dataclass(frozen=True)
class ProblemSummary:
    """Lightweight problem data for list display.

    Used when showing problem list - contains only
    essential data needed for filtering and display.
    Title is already resolved to user's locale.
    """

    id: int
    title: str  # Already localized (not LocalizedText)
    difficulty: Difficulty
    categories: tuple[Category, ...]
    tags: tuple[str, ...]
    status: ProblemStatus = ProblemStatus.NOT_STARTED


@dataclass(frozen=True)
class Problem:
    """Complete problem with all details.

    Rich domain model with nested objects.
    Loaded when user views a specific problem.

    Example:
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Two Sum", "ru": "Два числа"}),
            description=LocalizedText({"en": "Given an array..."}),
            difficulty=Difficulty.EASY,
            complexity=Complexity.O_N,
            categories=(Category.ARRAY, Category.HASH_TABLE),
            tags=("array", "hash-table"),
            examples=(
                Example(
                    input="nums = [2,7,11,15], target = 9",
                    output="[0, 1]",
                    explanation=LocalizedText({"en": "Because nums[0] + nums[1] == 9"})
                ),
            ),
            hints=(
                LocalizedText({"en": "Try using a hash map"}),
            ),
            supported_languages=(ProgrammingLanguage.PYTHON, ProgrammingLanguage.JAVA),
        )

        # Usage:
        print(problem.title.get("ru"))  # "Два числа"
        print(problem.examples[0].input)  # "nums = [2,7,11,15], target = 9"
    """

    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    complexity: Complexity
    categories: tuple[Category, ...] = ()
    tags: tuple[str, ...] = ()
    examples: tuple[Example, ...] = ()
    hints: tuple[LocalizedText, ...] = ()
    editorial: LocalizedText = field(default_factory=LocalizedText)
    supported_languages: tuple[ProgrammingLanguage, ...] = ()
    status: ProblemStatus = ProblemStatus.NOT_STARTED

    def get_title(self, locale: str = "en") -> str:
        """Get title in specified locale."""
        return self.title.get(locale)

    def get_description(self, locale: str = "en") -> str:
        """Get description in specified locale."""
        return self.description.get(locale)

    def supports_language(self, lang: ProgrammingLanguage) -> bool:
        """Check if problem supports given programming language."""
        return lang in self.supported_languages

    def to_summary(self, locale: str = "en") -> ProblemSummary:
        """Convert to lightweight summary for list display."""
        return ProblemSummary(
            id=self.id,
            title=self.title.get(locale),
            difficulty=self.difficulty,
            categories=self.categories,
            tags=self.tags,
            status=self.status,
        )
