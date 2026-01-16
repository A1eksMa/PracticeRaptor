"""Localization support for multi-language content."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LocalizedText:
    """Multi-language text with fallback support.

    Stores translations as a frozen dictionary and provides
    convenient access with automatic fallback to English.

    Example:
        title = LocalizedText({"en": "Two Sum", "ru": "Сумма двух"})
        title.get("ru")   # "Сумма двух"
        title.get("de")   # "Two Sum" (fallback to en)
        title.get("de", fallback="ru")  # "Сумма двух" (custom fallback)
    """

    translations: dict[str, str] = field(default_factory=dict)

    def get(self, locale: str = "en", fallback: str = "en") -> str:
        """Get text for locale with fallback.

        Args:
            locale: Desired language code (e.g., "ru", "en")
            fallback: Fallback language if locale not found

        Returns:
            Translated text or empty string if neither found
        """
        if locale in self.translations:
            return self.translations[locale]
        return self.translations.get(fallback, "")

    def has(self, locale: str) -> bool:
        """Check if translation exists for locale."""
        return locale in self.translations

    @property
    def locales(self) -> tuple[str, ...]:
        """Get all available locales."""
        return tuple(self.translations.keys())

    def __str__(self) -> str:
        """Default string representation (English)."""
        return self.get("en")

    def __bool__(self) -> bool:
        """Check if any translations exist."""
        return bool(self.translations)

    def __len__(self) -> int:
        """Number of translations."""
        return len(self.translations)


def text(en: str, ru: str = "") -> LocalizedText:
    """Convenience constructor for LocalizedText.

    Args:
        en: English text (required)
        ru: Russian text (optional)

    Returns:
        LocalizedText with provided translations

    Example:
        title = text("Two Sum", "Сумма двух")
    """
    translations = {"en": en}
    if ru:
        translations["ru"] = ru
    return LocalizedText(translations)
