"""Feedback collection and storage for learning system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
import yaml
from pathlib import Path


class FeedbackEntry:
    """Single piece of feedback from user about composed message."""

    def __init__(
        self,
        variant_index: int,
        chosen: bool,
        reason: str,
        original_message: str,
        composed_variants: List[str],
        preferred_tone: Optional[str] = None,
        preferred_formality: Optional[str] = None,
        mode: str = "simple"
    ):
        """
        Store user feedback about message composition.

        Args:
            variant_index: Which variant user preferred (0=formal, 1=balanced, 2=direct)
            chosen: True if this was the actually selected variant
            reason: User's explanation of why they chose it
            original_message: The raw input the user provided
            composed_variants: List of 3 composed variants
            preferred_tone: Tone preference (professional, casual, etc.)
            preferred_formality: Formality level (low, medium, high)
            mode: Composition mode used (simple or agent)
        """
        self.variant_index = variant_index
        self.chosen = chosen
        self.reason = reason
        self.original_message = original_message
        self.composed_variants = composed_variants
        self.preferred_tone = preferred_tone
        self.preferred_formality = preferred_formality
        self.mode = mode
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML storage."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "variant_index": self.variant_index,
            "chosen": self.chosen,
            "reason": self.reason,
            "original_message": self.original_message,
            "preferred_tone": self.preferred_tone,
            "preferred_formality": self.preferred_formality,
            "mode": self.mode,
            "composed_variants": self.composed_variants
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FeedbackEntry":
        """Create FeedbackEntry from dictionary (loaded from YAML)."""
        entry = cls(
            variant_index=data["variant_index"],
            chosen=data["chosen"],
            reason=data["reason"],
            original_message=data["original_message"],
            composed_variants=data["composed_variants"],
            preferred_tone=data.get("preferred_tone"),
            preferred_formality=data.get("preferred_formality"),
            mode=data.get("mode", "simple")
        )
        # Preserve original timestamp when loading
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        return entry


class FeedbackCollector:
    """Collect and manage feedback entries."""

    def __init__(self, storage_path: str = "feedback.yaml"):
        """
        Initialize feedback collector.

        Args:
            storage_path: Path to feedback.yaml file
        """
        self.storage_path = storage_path
        self.entries: List[FeedbackEntry] = []
        self.load()

    def load(self) -> None:
        """Load feedback from YAML file."""
        path = Path(self.storage_path)
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                if data and "feedback" in data:
                    self.entries = [FeedbackEntry.from_dict(entry) for entry in data["feedback"]]
        except (yaml.YAMLError, IOError):
            # If YAML is malformed or file can't be read, start fresh
            self.entries = []

    def add(self, entry: FeedbackEntry) -> None:
        """Add a feedback entry."""
        self.entries.append(entry)
        self.save()

    def save(self) -> None:
        """Save feedback to YAML file."""
        data = {
            "feedback": [entry.to_dict() for entry in self.entries]
        }

        path = Path(self.storage_path)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def get_all(self) -> List[FeedbackEntry]:
        """Get all feedback entries."""
        return self.entries.copy()

    def clear(self) -> None:
        """Clear all feedback."""
        self.entries = []
        self.save()

    def count(self) -> int:
        """Get number of feedback entries."""
        return len(self.entries)
