"""Analyze feedback patterns to extract learning."""

from typing import List, Dict, Optional
from collections import Counter
from src.feedback import FeedbackEntry


class FeedbackAnalyzer:
    """Extract patterns and preferences from feedback entries."""

    def __init__(self, entries: List[FeedbackEntry]):
        """
        Initialize analyzer with feedback entries.

        Args:
            entries: List of FeedbackEntry objects to analyze
        """
        self.entries = entries

    def get_summary(self) -> Dict:
        """
        Analyze all feedback and return summary of preferences.

        Returns:
            Dict with keys:
            - tone_preferences: Counter of preferred tones
            - formality_preferences: Counter of preferred formality levels
            - variant_preferences: Counter of which variants (0/1/2) were chosen
            - average_reason_keywords: Most common words in user feedback reasons
            - total_feedback: Number of entries analyzed
        """
        if not self.entries:
            return {
                "tone_preferences": {},
                "formality_preferences": {},
                "variant_preferences": {},
                "average_reason_keywords": [],
                "total_feedback": 0
            }

        # Count tone preferences (chosen variants)
        tone_counter = Counter()
        for entry in self.entries:
            if entry.chosen and entry.preferred_tone:
                tone_counter[entry.preferred_tone] += 1

        # Count formality preferences (chosen variants)
        formality_counter = Counter()
        for entry in self.entries:
            if entry.chosen and entry.preferred_formality:
                formality_counter[entry.preferred_formality] += 1

        # Count which variant indices are chosen most
        variant_counter = Counter()
        for entry in self.entries:
            if entry.chosen:
                variant_counter[str(entry.variant_index)] += 1

        # Extract keywords from feedback reasons
        keywords = self._extract_keywords()

        return {
            "tone_preferences": dict(tone_counter),
            "formality_preferences": dict(formality_counter),
            "variant_preferences": dict(variant_counter),
            "average_reason_keywords": keywords,
            "total_feedback": len(self.entries)
        }

    def get_dominant_preferences(self) -> Dict[str, Optional[str]]:
        """
        Get the single most-preferred settings.

        Returns:
            Dict with keys: tone, formality, preferred_variant_index
            Values are the most-chosen option (or None if no preference)
        """
        summary = self.get_summary()

        tone = None
        if summary["tone_preferences"]:
            tone = max(summary["tone_preferences"].items(), key=lambda x: x[1])[0]

        formality = None
        if summary["formality_preferences"]:
            formality = max(summary["formality_preferences"].items(), key=lambda x: x[1])[0]

        variant = None
        if summary["variant_preferences"]:
            variant = int(max(summary["variant_preferences"].items(), key=lambda x: x[1])[0])

        return {
            "tone": tone,
            "formality": formality,
            "preferred_variant_index": variant
        }

    def _extract_keywords(self, top_n: int = 5) -> List[str]:
        """Extract most common keywords from feedback reasons."""
        if not self.entries:
            return []

        # Collect all words from reasons
        words = []
        for entry in self.entries:
            if entry.reason:
                # Simple split, convert to lowercase, filter short words
                reason_words = [
                    w.lower().strip('.,!?;:')
                    for w in entry.reason.split()
                    if len(w) > 3 and w.lower() not in ['that', 'this', 'from', 'with', 'more']
                ]
                words.extend(reason_words)

        # Return top N most common
        counter = Counter(words)
        return [word for word, _ in counter.most_common(top_n)]

    def confidence(self, preference: str) -> float:
        """
        Get confidence score for a preference (0.0 to 1.0).
        Higher = more consistent user preference.

        Args:
            preference: One of 'tone', 'formality', 'variant'

        Returns:
            Confidence as proportion (e.g., 0.8 = 80% of chosen variants had this)
        """
        if not self.entries:
            return 0.0

        dominant = self.get_dominant_preferences()
        summary = self.get_summary()

        if preference == "tone" and dominant["tone"]:
            count = summary["tone_preferences"].get(dominant["tone"], 0)
            total = sum(summary["tone_preferences"].values())
            return count / total if total > 0 else 0.0

        elif preference == "formality" and dominant["formality"]:
            count = summary["formality_preferences"].get(dominant["formality"], 0)
            total = sum(summary["formality_preferences"].values())
            return count / total if total > 0 else 0.0

        elif preference == "variant" and dominant["preferred_variant_index"] is not None:
            count = summary["variant_preferences"].get(str(dominant["preferred_variant_index"]), 0)
            total = sum(summary["variant_preferences"].values())
            return count / total if total > 0 else 0.0

        return 0.0
