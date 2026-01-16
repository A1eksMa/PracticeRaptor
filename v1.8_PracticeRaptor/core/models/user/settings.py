"""User settings model."""

from dataclasses import dataclass

from ..enums import (
    Category,
    Difficulty,
    Language,
    ProblemStatus,
    ProgrammingLanguage,
    TextEditor,
)


@dataclass(frozen=True)
class FilterState:
    """Current filter state for problem listing.

    Ephemeral session state - can be reset.

    Example:
        filters = FilterState(
            difficulty=Difficulty.EASY,
            category=Category.ARRAY,
        )
    """

    problem_id: int | None = None
    difficulty: Difficulty | None = None
    category: Category | None = None
    tags: tuple[str, ...] = ()
    status: ProblemStatus | None = None

    def is_empty(self) -> bool:
        """Check if no filters are set."""
        return (
            self.problem_id is None
            and self.difficulty is None
            and self.category is None
            and not self.tags
            and self.status is None
        )

    def clear(self) -> "FilterState":
        """Return empty filter state."""
        return FilterState()


@dataclass(frozen=True)
class Settings:
    """User preferences and current session state.

    Contains:
    - Persistent preferences (language, editor)
    - Ephemeral session state (filters)

    Example:
        settings = Settings(
            user_id=1,
            language=Language.RU,
            programming_language=ProgrammingLanguage.PYTHON,
            filters=FilterState(difficulty=Difficulty.EASY),
        )
    """

    user_id: int = 0

    # Persistent preferences
    language: Language = Language.EN
    programming_language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    text_editor: TextEditor = TextEditor.DEFAULT

    # Session state
    filters: FilterState = FilterState()

    def with_filters(self, filters: FilterState) -> "Settings":
        """Return new Settings with updated filters."""
        from dataclasses import replace
        return replace(self, filters=filters)

    def with_language(self, language: Language) -> "Settings":
        """Return new Settings with updated UI language."""
        from dataclasses import replace
        return replace(self, language=language)

    def with_programming_language(self, lang: ProgrammingLanguage) -> "Settings":
        """Return new Settings with updated programming language."""
        from dataclasses import replace
        return replace(self, programming_language=lang)

    def with_editor(self, editor: TextEditor) -> "Settings":
        """Return new Settings with updated text editor."""
        from dataclasses import replace
        return replace(self, text_editor=editor)


# Default settings for new users
DEFAULT_SETTINGS = Settings()
