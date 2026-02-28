"""CLI prompts for feedback collection."""

import click
from typing import Optional


class FeedbackUI:
    """Helper for feedback-related CLI prompts."""

    def prompt_variant_choice(self, variants: list) -> int:
        """
        Prompt user to choose which variant they preferred.

        Args:
            variants: List of variant descriptions

        Returns:
            Index of chosen variant (0-indexed, so 0, 1, or 2)
        """
        click.echo("\n📋 Which variant did you prefer?")
        for i, variant in enumerate(variants, 1):
            click.echo(f"   [{i}] {variant}")

        while True:
            try:
                choice_str = click.prompt("   Your choice (1-3)")
                choice = int(choice_str)
                if 1 <= choice <= 3:
                    return choice - 1  # Convert to 0-indexed
                click.echo("   ❌ Please enter 1, 2, or 3")
            except ValueError:
                click.echo("   ❌ Invalid input, please enter a number")

    def prompt_feedback_reason(self) -> str:
        """
        Prompt user for reason they chose that variant.

        Returns:
            User's explanation for their choice
        """
        click.echo("")
        reason = click.prompt(
            "📝 Why did you choose it? (e.g., 'good tone', 'clear', 'professional')",
            default="no reason"
        )
        return reason.strip()

    def prompt_tone_preference(self) -> Optional[str]:
        """
        Prompt user to specify their preferred tone.

        Returns:
            Tone preference ('professional', 'casual', 'direct') or None if skipped
        """
        click.echo("")
        click.echo("🎯 What tone do you prefer for messages?")
        click.echo("   [1] Professional")
        click.echo("   [2] Casual")
        click.echo("   [3] Direct")

        choice = click.prompt("   Your choice (1-3 or skip)", default="skip")

        tone_map = {"1": "professional", "2": "casual", "3": "direct"}
        return tone_map.get(choice)

    def prompt_formality_preference(self) -> Optional[str]:
        """
        Prompt user to specify their preferred formality level.

        Returns:
            Formality preference ('low', 'medium', 'high') or None if skipped
        """
        click.echo("")
        click.echo("📊 How formal should messages be?")
        click.echo("   [1] Low (very casual)")
        click.echo("   [2] Medium (professional)")
        click.echo("   [3] High (very formal)")

        choice = click.prompt("   Your choice (1-3 or skip)", default="skip")

        formality_map = {"1": "low", "2": "medium", "3": "high"}
        return formality_map.get(choice)

    def show_learning_status(self, feedback_count: int) -> None:
        """
        Show how much the system has learned.

        Args:
            feedback_count: Number of feedback samples collected
        """
        if feedback_count == 0:
            click.echo("\n💭 Help the system learn by providing feedback!")
        elif feedback_count < 3:
            click.echo(f"\n📚 Learning ({feedback_count} feedback samples)...")
        elif feedback_count < 10:
            click.echo(f"\n📈 Adapting to your style ({feedback_count} samples)...")
        else:
            click.echo(f"\n🎓 Personalized to your preferences ({feedback_count} samples)")
