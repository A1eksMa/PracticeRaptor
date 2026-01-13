"""Repository interfaces (Ports)."""

from typing import Protocol

from core.domain.problem import Problem, ProblemSummary
from core.domain.enums import Difficulty, Category, ProblemStatus


class IProblemRepository(Protocol):
    """Interface for problem storage.

    Implementations: JsonProblemRepository, SqliteProblemRepository
    """

    def get_by_id(self, problem_id: int, locale: str = "en") -> Problem | None:
        """Get complete problem by ID.

        Args:
            problem_id: Problem ID
            locale: Preferred language for localized content

        Returns:
            Problem with all details or None if not found
        """
        ...

    def get_all_summaries(
        self,
        locale: str = "en",
        difficulty: Difficulty | None = None,
        category: Category | None = None,
        tag: str | None = None,
    ) -> list[ProblemSummary]:
        """Get lightweight problem list for display.

        Args:
            locale: Language for titles
            difficulty: Filter by difficulty
            category: Filter by category
            tag: Filter by tag

        Returns:
            List of ProblemSummary for list view
        """
        ...

    def get_problem_ids(self) -> list[int]:
        """Get all problem IDs."""
        ...

    def count(self) -> int:
        """Get total number of problems."""
        ...
