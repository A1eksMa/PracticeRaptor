"""WorkContext - runtime aggregate unifying both domains."""

from dataclasses import dataclass, replace

from ..enums import Language, ProgrammingLanguage
from ..problem import Problem, ProblemTemplate
from ..user import User, Settings, Draft, DEFAULT_USER, DEFAULT_SETTINGS


@dataclass(frozen=True)
class WorkContext:
    """Complete context for current work session.

    Runtime aggregate that unifies Problem-domain and User-domain.
    NOT stored - assembled by factory function when needed.

    Provides convenient access to all related data:
    - User and their settings
    - Currently selected problem and template
    - User's draft (if any)

    Example:
        context = WorkContext(
            user=user,
            settings=settings,
            problem=problem,
            template=template,
            draft=draft,
        )

        # Access nested data directly
        print(context.problem.get_title(context.locale))
        print(context.template.signature)
        print(context.code)  # From draft or empty
    """

    # User domain (always present)
    user: User = DEFAULT_USER
    settings: Settings = DEFAULT_SETTINGS

    # Problem domain (optional - may be None if no problem selected)
    problem: Problem | None = None
    template: ProblemTemplate | None = None

    # User's work on current problem (optional)
    draft: Draft | None = None

    # ========================================
    # User properties
    # ========================================

    @property
    def user_id(self) -> int:
        """Current user ID."""
        return self.user.user_id

    @property
    def user_name(self) -> str:
        """Current user name."""
        return self.user.user_name

    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        return self.user.is_anonymous

    # ========================================
    # Settings properties
    # ========================================

    @property
    def locale(self) -> str:
        """Current UI locale (e.g., 'en', 'ru')."""
        return self.settings.language.value

    @property
    def language(self) -> Language:
        """Current UI language."""
        return self.settings.language

    @property
    def programming_language(self) -> ProgrammingLanguage:
        """Current programming language."""
        return self.settings.programming_language

    # ========================================
    # Problem properties
    # ========================================

    @property
    def has_problem(self) -> bool:
        """Check if a problem is selected."""
        return self.problem is not None

    @property
    def problem_id(self) -> int | None:
        """Current problem ID or None."""
        return self.problem.id if self.problem else None

    @property
    def problem_title(self) -> str:
        """Problem title in current locale."""
        if self.problem:
            return self.problem.get_title(self.locale)
        return ""

    # ========================================
    # Template properties
    # ========================================

    @property
    def has_template(self) -> bool:
        """Check if template is loaded."""
        return self.template is not None

    @property
    def signature(self) -> str:
        """Function signature from template."""
        return self.template.signature if self.template else ""

    @property
    def test_cases(self):
        """Test cases from template."""
        return self.template.test_cases if self.template else ()

    @property
    def example_tests(self):
        """Example test cases from template."""
        return self.template.example_tests if self.template else ()

    # ========================================
    # Draft / Code properties
    # ========================================

    @property
    def has_draft(self) -> bool:
        """Check if draft exists."""
        return self.draft is not None

    @property
    def code(self) -> str:
        """Current code (from draft, or signature, or empty)."""
        if self.draft:
            return self.draft.code
        if self.template:
            return self.template.signature
        return ""

    # ========================================
    # Immutable updates
    # ========================================

    def with_problem(
        self,
        problem: Problem,
        template: ProblemTemplate,
        draft: Draft | None = None,
    ) -> "WorkContext":
        """Return new context with problem selected."""
        return replace(
            self,
            problem=problem,
            template=template,
            draft=draft,
        )

    def with_draft(self, draft: Draft) -> "WorkContext":
        """Return new context with draft updated."""
        return replace(self, draft=draft)

    def with_code(self, code: str) -> "WorkContext":
        """Return new context with draft code updated.

        Creates or updates draft with new code.
        """
        if self.draft:
            return replace(self, draft=self.draft.with_code(code))
        return self  # Can't update code without draft

    def with_settings(self, settings: Settings) -> "WorkContext":
        """Return new context with settings updated."""
        return replace(self, settings=settings)

    def clear_problem(self) -> "WorkContext":
        """Return new context with problem cleared."""
        return replace(
            self,
            problem=None,
            template=None,
            draft=None,
        )

    # ========================================
    # Validation
    # ========================================

    def can_submit(self) -> bool:
        """Check if context is ready for code submission."""
        return (
            self.has_problem
            and self.has_template
            and bool(self.code.strip())
        )

    def validate(self) -> list[str]:
        """Validate context state. Returns list of errors."""
        errors = []
        if not self.user:
            errors.append("User is required")
        if not self.settings:
            errors.append("Settings is required")
        if self.problem and not self.template:
            errors.append("Template is required when problem is selected")
        if self.draft:
            if self.draft.problem_id != self.problem_id:
                errors.append("Draft problem_id doesn't match context problem_id")
            if self.template and self.draft.language != self.template.language:
                errors.append("Draft language doesn't match template language")
        return errors
