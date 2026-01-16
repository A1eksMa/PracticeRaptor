"""Draft model - user's work in progress."""

from dataclasses import dataclass, replace
from datetime import datetime

from ..problem import Problem, ProblemTemplate
from .user import User, DEFAULT_USER


@dataclass(frozen=True)
class Draft:
    """User's work-in-progress solution.

    Rich domain model with full nested objects:
    - User who created the draft
    - Problem being solved
    - ProblemTemplate for the chosen language
    - User's code

    Unique constraint: (user_id, problem_id, language)
    Only one draft per user per problem per language.

    Example:
        draft = Draft(
            draft_id=1,
            user=user,
            problem=problem,
            template=template,
            code="def two_sum(nums, target):\\n    pass",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Update code
        draft = draft.with_code("def two_sum(nums, target):\\n    ...")
    """

    draft_id: int
    user: User
    problem: Problem
    template: ProblemTemplate
    code: str
    created_at: datetime
    updated_at: datetime

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

    @property
    def signature(self) -> str:
        """Function signature shortcut."""
        return self.template.signature

    # ========================================
    # Immutable updates
    # ========================================

    def with_code(self, code: str) -> "Draft":
        """Return new Draft with updated code and timestamp."""
        return replace(
            self,
            code=code,
            updated_at=datetime.now(),
        )


def create_draft(
    draft_id: int,
    user: User,
    problem: Problem,
    template: ProblemTemplate,
    code: str = "",
) -> Draft:
    """Factory function to create a new Draft.

    Args:
        draft_id: Unique draft ID
        user: User creating the draft
        problem: Problem being solved
        template: Problem template for chosen language
        code: Initial code (default: empty)

    Returns:
        New Draft with current timestamps
    """
    now = datetime.now()
    return Draft(
        draft_id=draft_id,
        user=user,
        problem=problem,
        template=template,
        code=code or template.signature,
        created_at=now,
        updated_at=now,
    )
