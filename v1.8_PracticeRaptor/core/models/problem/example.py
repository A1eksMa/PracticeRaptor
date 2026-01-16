"""Problem example model."""

from dataclasses import dataclass, field

from .localization import LocalizedText


@dataclass(frozen=True)
class Example:
    """Problem example with input, output, and explanation.

    Value object embedded in Problem.
    Explanation is localized (multi-language).

    Example:
        example = Example(
            input="nums = [2, 7, 11, 15], target = 9",
            output="[0, 1]",
            explanation=LocalizedText({
                "en": "nums[0] + nums[1] = 2 + 7 = 9",
                "ru": "nums[0] + nums[1] = 2 + 7 = 9",
            }),
        )
    """

    input: str
    output: str
    explanation: LocalizedText = field(default_factory=LocalizedText)

    def get_explanation(self, locale: str = "en") -> str:
        """Get explanation in specified locale."""
        return self.explanation.get(locale)

    def has_explanation(self) -> bool:
        """Check if any explanation exists."""
        return bool(self.explanation)
