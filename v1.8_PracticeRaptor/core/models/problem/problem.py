"""Problem models."""

from dataclasses import dataclass, field

from ..enums import (
    Category,
    Complexity,
    Difficulty,
    Language,
    ProblemStatus,
    ProgrammingLanguage,
)
from .localization import LocalizedText
from .example import Example


@dataclass(frozen=True)
class ProblemSummary:
    """Lightweight problem data for list display.

    Contains only essential fields needed for problem listing.
    Status is user-specific (computed from submissions).

    Example:
        summary = ProblemSummary(
            id=1,
            title=LocalizedText({"en": "Two Sum", "ru": "Сумма двух"}),
            difficulty=Difficulty.EASY,
            categories=(Category.ARRAY, Category.HASH_TABLE),
            tags=("array", "hash-table"),
            status=ProblemStatus.SOLVED,
        )
    """

    id: int
    title: LocalizedText
    difficulty: Difficulty
    complexity: Complexity = Complexity.O_N
    categories: tuple[Category, ...] = ()
    tags: tuple[str, ...] = ()
    supported_languages: tuple[Language, ...] = (Language.EN,)
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = (
        ProgrammingLanguage.PYTHON,
    )
    status: ProblemStatus = ProblemStatus.NOT_STARTED

    def get_title(self, locale: str = "en") -> str:
        """Get title in specified locale."""
        return self.title.get(locale)

    def has_category(self, category: Category) -> bool:
        """Check if problem has specified category."""
        return category in self.categories

    def has_tag(self, tag: str) -> bool:
        """Check if problem has specified tag."""
        return tag in self.tags

    def supports_language(self, lang: Language) -> bool:
        """Check if problem supports UI language."""
        return lang in self.supported_languages

    def supports_programming_language(self, lang: ProgrammingLanguage) -> bool:
        """Check if problem supports programming language."""
        return lang in self.supported_programming_languages


@dataclass(frozen=True)
class Problem:
    """Complete problem with all details.

    Rich domain model loaded when user views a specific problem.
    Contains all localized content (title, description, hints, editorial).

    Example:
        problem = Problem(
            id=1,
            title=LocalizedText({"en": "Two Sum"}),
            description=LocalizedText({"en": "Given an array..."}),
            difficulty=Difficulty.EASY,
            complexity=Complexity.O_N,
            categories=(Category.ARRAY,),
            examples=(...),
            hints=(...),
        )
    """

    id: int
    title: LocalizedText
    description: LocalizedText
    difficulty: Difficulty
    complexity: Complexity = Complexity.O_N
    categories: tuple[Category, ...] = ()
    tags: tuple[str, ...] = ()
    examples: tuple[Example, ...] = ()
    hints: tuple[LocalizedText, ...] = ()
    editorial: LocalizedText = field(default_factory=LocalizedText)
    supported_languages: tuple[Language, ...] = (Language.EN,)
    supported_programming_languages: tuple[ProgrammingLanguage, ...] = (
        ProgrammingLanguage.PYTHON,
    )

    def get_title(self, locale: str = "en") -> str:
        """Get title in specified locale."""
        return self.title.get(locale)

    def get_description(self, locale: str = "en") -> str:
        """Get description in specified locale."""
        return self.description.get(locale)

    def get_hints(self, locale: str = "en") -> tuple[str, ...]:
        """Get all hints in specified locale."""
        return tuple(h.get(locale) for h in self.hints if h.get(locale))

    def get_hint(self, index: int, locale: str = "en") -> str | None:
        """Get specific hint by index."""
        if 0 <= index < len(self.hints):
            return self.hints[index].get(locale)
        return None

    def get_editorial(self, locale: str = "en") -> str:
        """Get editorial in specified locale."""
        return self.editorial.get(locale)

    def has_editorial(self) -> bool:
        """Check if editorial exists."""
        return bool(self.editorial)

    def supports_language(self, lang: Language) -> bool:
        """Check if problem supports UI language."""
        return lang in self.supported_languages

    def supports_programming_language(self, lang: ProgrammingLanguage) -> bool:
        """Check if problem supports programming language."""
        return lang in self.supported_programming_languages

    def to_summary(self, status: ProblemStatus = ProblemStatus.NOT_STARTED) -> ProblemSummary:
        """Convert to lightweight summary for list display."""
        return ProblemSummary(
            id=self.id,
            title=self.title,
            difficulty=self.difficulty,
            complexity=self.complexity,
            categories=self.categories,
            tags=self.tags,
            supported_languages=self.supported_languages,
            supported_programming_languages=self.supported_programming_languages,
            status=status,
        )
