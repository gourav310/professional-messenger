"""Generate adaptive system prompts based on learned user preferences."""

from typing import Optional


class AdaptivePromptGenerator:
    """Inject learned preferences into system prompts."""

    def __init__(
        self,
        preferred_tone: Optional[str] = None,
        preferred_formality: Optional[str] = None,
        confidence: float = 0.0,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize adaptive prompt generator.

        Args:
            preferred_tone: User's preferred tone (professional, casual, direct, etc.)
            preferred_formality: User's preferred formality (low, medium, high)
            confidence: Confidence in the preference (0.0 to 1.0)
            confidence_threshold: Only use preferences if confidence >= this (default 0.5)
        """
        self.preferred_tone = preferred_tone
        self.preferred_formality = preferred_formality
        self.confidence = confidence
        self.confidence_threshold = confidence_threshold

    def should_use_preferences(self) -> bool:
        """Check if learned preferences are strong enough to use."""
        if not self.preferred_tone and not self.preferred_formality:
            return False
        # If no confidence specified (default 0.0), allow use of preferences
        # Otherwise, only use if confidence meets threshold
        if self.confidence == 0.0:
            return True
        return self.confidence >= self.confidence_threshold

    def adapt_prompt(self, base_prompt: str) -> str:
        """
        Inject learned preferences into system prompt.

        Args:
            base_prompt: Original system prompt

        Returns:
            Enhanced prompt with preference guidance
        """
        if not self.should_use_preferences():
            return base_prompt

        # Build preference guidance
        preference_lines = []

        if self.preferred_tone:
            preference_lines.append(
                f"Based on past feedback, the user prefers a {self.preferred_tone} tone. "
                f"Prioritize this in all variants."
            )

        if self.preferred_formality:
            formality_map = {
                "low": "very casual with contractions",
                "medium": "professional but approachable",
                "high": "very formal and respectful"
            }
            desc = formality_map.get(self.preferred_formality, self.preferred_formality)
            preference_lines.append(
                f"The user prefers {self.preferred_formality} formality ({desc} language). "
                f"Apply this to all message variants."
            )

        preferences_text = "\n".join(preference_lines)

        # Insert preferences after the main instruction, before the variant generation
        adapted = base_prompt.replace(
            "FORMAT YOUR RESPONSE",
            f"LEARNED PREFERENCES:\n{preferences_text}\n\nFORMAT YOUR RESPONSE"
        )

        # Fallback: if FORMAT keyword not found, append at end
        if adapted == base_prompt:
            adapted = base_prompt + f"\n\nADAPTATION: {preferences_text}"

        return adapted

    def get_context_message(self) -> Optional[str]:
        """
        Generate friendly message explaining what's being applied.

        Returns:
            Human-readable message about learned preferences, or None
        """
        if not self.should_use_preferences():
            return None

        parts = []

        if self.preferred_tone and self.preferred_formality:
            parts.append(
                f"Using your learned preference: {self.preferred_tone} tone, "
                f"{self.preferred_formality} formality"
            )
        elif self.preferred_tone:
            parts.append(f"Using your learned preference: {self.preferred_tone} tone")
        elif self.preferred_formality:
            parts.append(f"Using your learned preference: {self.preferred_formality} formality")

        if self.confidence < 1.0:
            parts.append(f"(confidence: {self.confidence:.0%})")

        return " ".join(parts) if parts else None
