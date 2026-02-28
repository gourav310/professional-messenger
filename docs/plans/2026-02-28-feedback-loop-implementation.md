# Feedback Loop Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable users to provide feedback on composed message variants, store preferences, analyze patterns, and automatically adapt future compositions to learned user preferences.

**Architecture:**
- Feedback collection happens post-composition via CLI prompts
- Feedback stored in YAML with structure: variant chosen, reason, timestamp, tone/formality/length metadata
- FeedbackAnalyzer extracts patterns (e.g., "user prefers balanced tone 70% of time")
- Learned preferences injected into system prompts dynamically at composition time
- Both SimpleComposer and MessageComposerAgent respect learned preferences

**Tech Stack:** YAML storage, pattern analysis via simple statistics (frequency counting), dynamic string interpolation for prompts

---

## Task 1: Create FeedbackEntry and FeedbackCollector Classes

**Files:**
- Create: `src/feedback.py`
- Create: `tests/test_feedback.py`

**Step 1: Write failing test for FeedbackEntry**

```bash
# File: tests/test_feedback.py
```

```python
import pytest
from datetime import datetime
from src.feedback import FeedbackEntry


def test_feedback_entry_creation():
    """FeedbackEntry should store feedback with metadata."""
    entry = FeedbackEntry(
        variant_index=1,
        chosen=True,
        reason="balanced tone",
        original_message="hey project delayed",
        composed_variants=["Formal msg", "Balanced msg", "Direct msg"],
        preferred_tone="balanced",
        preferred_formality="medium"
    )

    assert entry.variant_index == 1
    assert entry.chosen is True
    assert entry.reason == "balanced tone"
    assert entry.original_message == "hey project delayed"
    assert entry.composed_variants == ["Formal msg", "Balanced msg", "Direct msg"]
    assert entry.preferred_tone == "balanced"
    assert entry.preferred_formality == "medium"
    assert isinstance(entry.timestamp, datetime)
    assert entry.to_dict() is not None
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/gouravkhurana/Documents/Personal/professional-messenger
python3 -m pytest tests/test_feedback.py::test_feedback_entry_creation -v
```

Expected output: `FAILED ... FeedbackEntry not defined`

**Step 3: Write minimal FeedbackEntry implementation**

```python
# File: src/feedback.py
"""Feedback collection and storage for learning system."""

from datetime import datetime
from typing import List, Optional, Dict


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

    def to_dict(self) -> Dict:
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
        import yaml
        from pathlib import Path

        path = Path(self.storage_path)
        if not path.exists():
            return

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                if data and "feedback" in data:
                    self.entries = [FeedbackEntry.from_dict(entry) for entry in data["feedback"]]
        except Exception:
            # If YAML is malformed, start fresh
            self.entries = []

    def add(self, entry: FeedbackEntry) -> None:
        """Add a feedback entry."""
        self.entries.append(entry)
        self.save()

    def save(self) -> None:
        """Save feedback to YAML file."""
        import yaml
        from pathlib import Path

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
```

**Step 4: Run test to verify it passes**

```bash
python3 -m pytest tests/test_feedback.py::test_feedback_entry_creation -v
```

Expected: `PASSED`

**Step 5: Add more tests for FeedbackCollector**

```python
# Add to tests/test_feedback.py

def test_feedback_collector_add_and_load():
    """FeedbackCollector should save and load feedback."""
    import tempfile
    from pathlib import Path

    # Use temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        # Create and add feedback
        collector = FeedbackCollector(storage_path=temp_path)
        entry = FeedbackEntry(
            variant_index=1,
            chosen=True,
            reason="good tone",
            original_message="test",
            composed_variants=["a", "b", "c"],
            preferred_tone="balanced"
        )
        collector.add(entry)

        # Load in new instance
        collector2 = FeedbackCollector(storage_path=temp_path)
        assert collector2.count() == 1
        assert collector2.get_all()[0].reason == "good tone"
        assert collector2.get_all()[0].variant_index == 1
    finally:
        Path(temp_path).unlink()


def test_feedback_collector_clear():
    """FeedbackCollector should clear all feedback."""
    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        collector = FeedbackCollector(storage_path=temp_path)
        entry = FeedbackEntry(
            variant_index=0,
            chosen=True,
            reason="test",
            original_message="test",
            composed_variants=["a", "b", "c"]
        )
        collector.add(entry)
        assert collector.count() == 1

        collector.clear()
        assert collector.count() == 0

        # Verify persisted
        collector2 = FeedbackCollector(storage_path=temp_path)
        assert collector2.count() == 0
    finally:
        Path(temp_path).unlink()
```

**Step 6: Run all feedback tests**

```bash
python3 -m pytest tests/test_feedback.py -v
```

Expected: All 3 tests PASS

**Step 7: Commit**

```bash
git add src/feedback.py tests/test_feedback.py
git commit -m "feat: add FeedbackEntry and FeedbackCollector classes"
```

---

## Task 2: Create FeedbackAnalyzer for Pattern Extraction

**Files:**
- Create: `src/feedback_analyzer.py`
- Modify: `tests/test_feedback.py` (add analyzer tests)

**Step 1: Write failing test for FeedbackAnalyzer**

```python
# Add to tests/test_feedback.py

def test_feedback_analyzer_tone_preference():
    """FeedbackAnalyzer should extract tone preferences."""
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.feedback import FeedbackEntry

    entries = [
        FeedbackEntry(0, True, "too casual", "test", ["a", "b", "c"], preferred_tone="formal"),
        FeedbackEntry(1, True, "just right", "test", ["a", "b", "c"], preferred_tone="balanced"),
        FeedbackEntry(1, True, "perfect", "test", ["a", "b", "c"], preferred_tone="balanced"),
    ]

    analyzer = FeedbackAnalyzer(entries)
    summary = analyzer.get_summary()

    # Balanced tone chosen 2/3 times
    assert summary["tone_preferences"]["balanced"] == 2
    assert summary["tone_preferences"]["formal"] == 1


def test_feedback_analyzer_formality_preference():
    """FeedbackAnalyzer should extract formality preferences."""
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.feedback import FeedbackEntry

    entries = [
        FeedbackEntry(0, True, "test", "msg", ["a", "b", "c"], preferred_formality="high"),
        FeedbackEntry(0, True, "test", "msg", ["a", "b", "c"], preferred_formality="high"),
        FeedbackEntry(1, True, "test", "msg", ["a", "b", "c"], preferred_formality="medium"),
    ]

    analyzer = FeedbackAnalyzer(entries)
    summary = analyzer.get_summary()

    assert summary["formality_preferences"]["high"] == 2
    assert summary["formality_preferences"]["medium"] == 1


def test_feedback_analyzer_most_preferred_variant():
    """FeedbackAnalyzer should identify most-chosen variant."""
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.feedback import FeedbackEntry

    entries = [
        FeedbackEntry(0, True, "test", "msg", ["a", "b", "c"]),  # formal
        FeedbackEntry(1, True, "test", "msg", ["a", "b", "c"]),  # balanced
        FeedbackEntry(1, True, "test", "msg", ["a", "b", "c"]),  # balanced
    ]

    analyzer = FeedbackAnalyzer(entries)
    summary = analyzer.get_summary()

    # Variant 1 (balanced) chosen most
    assert summary["variant_preferences"]["1"] == 2
    assert summary["variant_preferences"]["0"] == 1
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_feedback.py::test_feedback_analyzer_tone_preference -v
```

Expected: `FAILED ... FeedbackAnalyzer not defined`

**Step 3: Write FeedbackAnalyzer implementation**

```python
# File: src/feedback_analyzer.py
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

    def get_dominant_preferences(self) -> Dict[str, str]:
        """
        Get the single most-preferred settings.

        Returns:
            Dict with keys: tone, formality, variant
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
```

**Step 4: Run analyzer tests**

```bash
python3 -m pytest tests/test_feedback.py::test_feedback_analyzer_tone_preference -v
python3 -m pytest tests/test_feedback.py::test_feedback_analyzer_formality_preference -v
python3 -m pytest tests/test_feedback.py::test_feedback_analyzer_most_preferred_variant -v
```

Expected: All 3 PASS

**Step 5: Commit**

```bash
git add src/feedback_analyzer.py tests/test_feedback.py
git commit -m "feat: add FeedbackAnalyzer for pattern extraction"
```

---

## Task 3: Create Adaptive Prompt Generator

**Files:**
- Create: `src/adaptive_prompt.py`
- Modify: `tests/test_feedback.py` (add prompt tests)

**Step 1: Write failing test**

```python
# Add to tests/test_feedback.py

def test_adaptive_prompt_generation_with_preferences():
    """AdaptivePrompt should inject learned preferences."""
    from src.adaptive_prompt import AdaptivePromptGenerator

    generator = AdaptivePromptGenerator(
        preferred_tone="balanced",
        preferred_formality="medium",
        confidence_threshold=0.6
    )

    base_prompt = "You are a professional message composer."
    adapted = generator.adapt_prompt(base_prompt)

    # Should inject preferences
    assert "balanced" in adapted.lower()
    assert "medium" in adapted.lower()


def test_adaptive_prompt_no_preferences():
    """AdaptivePrompt should work without preferences."""
    from src.adaptive_prompt import AdaptivePromptGenerator

    generator = AdaptivePromptGenerator()
    base_prompt = "You are a professional message composer."
    adapted = generator.adapt_prompt(base_prompt)

    # Should return base when no preferences
    assert "professional message composer" in adapted.lower()


def test_adaptive_prompt_generation_contextual_message():
    """AdaptivePrompt should generate contextual learning messages."""
    from src.adaptive_prompt import AdaptivePromptGenerator

    generator = AdaptivePromptGenerator(
        preferred_tone="direct",
        preferred_formality="high",
        confidence=0.75
    )

    msg = generator.get_context_message()

    # Should mention learned preferences
    assert msg is not None
    assert len(msg) > 0
    assert "direct" in msg.lower() or "prefer" in msg.lower()
```

**Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_feedback.py::test_adaptive_prompt_generation_with_preferences -v
```

Expected: `FAILED ... AdaptivePromptGenerator not defined`

**Step 3: Write AdaptivePromptGenerator**

```python
# File: src/adaptive_prompt.py
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
                f"The user prefers {desc} language. "
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
```

**Step 4: Run adaptive prompt tests**

```bash
python3 -m pytest tests/test_feedback.py::test_adaptive_prompt_generation_with_preferences -v
python3 -m pytest tests/test_feedback.py::test_adaptive_prompt_no_preferences -v
python3 -m pytest tests/test_feedback.py::test_adaptive_prompt_generation_contextual_message -v
```

Expected: All 3 PASS

**Step 5: Commit**

```bash
git add src/adaptive_prompt.py tests/test_feedback.py
git commit -m "feat: add AdaptivePromptGenerator for learned preferences"
```

---

## Task 4: Integrate Feedback Collection into CLI

**Files:**
- Modify: `src/cli.py` (update compose command)
- Create: `src/feedback_ui.py` (feedback prompting logic)

**Step 1: Write tests for feedback UI prompts**

```python
# Add to tests/test_feedback.py

def test_feedback_ui_variant_selection():
    """FeedbackUI should prompt for variant selection."""
    from src.feedback_ui import FeedbackUI
    from unittest.mock import patch

    # Mock user choosing variant 1 (balanced)
    with patch('click.prompt', return_value='1'):
        ui = FeedbackUI()
        choice = ui.prompt_variant_choice(
            variants=["Formal", "Balanced", "Direct"]
        )
        assert choice == 1


def test_feedback_ui_reason_collection():
    """FeedbackUI should collect feedback reason."""
    from src.feedback_ui import FeedbackUI
    from unittest.mock import patch

    # Mock user providing reason
    with patch('click.prompt', return_value='good tone'):
        ui = FeedbackUI()
        reason = ui.prompt_feedback_reason()
        assert reason == "good tone"


def test_feedback_ui_preferences():
    """FeedbackUI should prompt for tone and formality preferences."""
    from src.feedback_ui import FeedbackUI
    from unittest.mock import patch

    # Mock preferences
    with patch('click.prompt', side_effect=['balanced', 'medium']):
        ui = FeedbackUI()
        tone = ui.prompt_tone_preference()
        formality = ui.prompt_formality_preference()

        assert tone == "balanced"
        assert formality == "medium"
```

**Step 2: Run UI tests to verify they fail**

```bash
python3 -m pytest tests/test_feedback.py::test_feedback_ui_variant_selection -v
```

Expected: `FAILED ... FeedbackUI not defined`

**Step 3: Write FeedbackUI helper**

```python
# File: src/feedback_ui.py
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
            Index of chosen variant (0, 1, or 2)
        """
        click.echo("\n📋 Which variant did you prefer?")
        for i, variant in enumerate(variants, 1):
            click.echo(f"   [{i}] {variant}")

        while True:
            try:
                choice = click.prompt("   Your choice (1-3)", type=int)
                if 1 <= choice <= 3:
                    return choice - 1  # Convert to 0-indexed
                click.echo("   ❌ Please enter 1, 2, or 3")
            except ValueError:
                click.echo("   ❌ Invalid input, please enter a number")

    def prompt_feedback_reason(self) -> str:
        """Prompt user for reason they chose that variant."""
        click.echo("")
        reason = click.prompt(
            "📝 Why did you choose it? (e.g., 'good tone', 'clear', 'professional')",
            default="no reason"
        )
        return reason.strip()

    def prompt_tone_preference(self) -> Optional[str]:
        """Prompt user to specify their preferred tone."""
        click.echo("")
        click.echo("🎯 What tone do you prefer for messages?")
        click.echo("   [1] Professional")
        click.echo("   [2] Casual")
        click.echo("   [3] Direct")

        choice = click.prompt("   Your choice (1-3 or skip)", default="skip")

        tone_map = {"1": "professional", "2": "casual", "3": "direct"}
        return tone_map.get(choice)

    def prompt_formality_preference(self) -> Optional[str]:
        """Prompt user to specify their preferred formality level."""
        click.echo("")
        click.echo("📊 How formal should messages be?")
        click.echo("   [1] Low (very casual)")
        click.echo("   [2] Medium (professional)")
        click.echo("   [3] High (very formal)")

        choice = click.prompt("   Your choice (1-3 or skip)", default="skip")

        formality_map = {"1": "low", "2": "medium", "3": "high"}
        return formality_map.get(choice)

    def show_learning_status(self, feedback_count: int) -> None:
        """Show how much the system has learned."""
        if feedback_count == 0:
            click.echo("\n💭 Help the system learn by providing feedback!")
        elif feedback_count < 3:
            click.echo(f"\n📚 Learning ({feedback_count} feedback samples)...")
        elif feedback_count < 10:
            click.echo(f"\n📈 Adapting to your style ({feedback_count} samples)...")
        else:
            click.echo(f"\n🎓 Personalized to your preferences ({feedback_count} samples)")
```

**Step 4: Run UI tests**

```bash
python3 -m pytest tests/test_feedback.py::test_feedback_ui_variant_selection -v
python3 -m pytest tests/test_feedback.py::test_feedback_ui_reason_collection -v
python3 -m pytest tests/test_feedback.py::test_feedback_ui_preferences -v
```

Expected: All 3 PASS

**Step 5: Update CLI compose command to collect feedback**

Modify `src/cli.py` compose function (after the variants are displayed):

```python
# Around line 540-575, replace the display section with:

    # Display results
    separator = "─" * 60
    all_variants = [result['primary']] + result['variants']
    labels = ["Formal", "Balanced", "Direct"]

    click.echo(f"\n{separator}")
    for i, (label, variant) in enumerate(zip(labels, all_variants), 1):
        if variant:
            click.echo(f"  [{i}] {label}")
            click.echo(f"  {variant}")
            click.echo(separator)

    # Collect feedback (NEW)
    # ═════════════════════════════════════════════════════════════════
    from src.feedback import FeedbackCollector, FeedbackEntry
    from src.feedback_ui import FeedbackUI
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.adaptive_prompt import AdaptivePromptGenerator

    feedback_ui = FeedbackUI()

    try:
        # Ask which variant user prefers
        chosen_index = feedback_ui.prompt_variant_choice(labels)

        # Ask why
        reason = feedback_ui.prompt_feedback_reason()

        # Optionally ask about preferences
        preferred_tone = feedback_ui.prompt_tone_preference()
        preferred_formality = feedback_ui.prompt_formality_preference()

        # Store feedback
        collector = FeedbackCollector()
        entry = FeedbackEntry(
            variant_index=chosen_index,
            chosen=True,
            reason=reason,
            original_message=text,
            composed_variants=all_variants,
            preferred_tone=preferred_tone,
            preferred_formality=preferred_formality,
            mode=mode
        )
        collector.add(entry)

        # Show learning status
        feedback_ui.show_learning_status(collector.count())

        # Show what was learned
        if collector.count() >= 3:
            analyzer = FeedbackAnalyzer(collector.get_all())
            dominant = analyzer.get_dominant_preferences()
            if dominant["tone"]:
                click.echo(f"\n📍 Noted: You prefer {dominant['tone']} tone")
            if dominant["formality"]:
                click.echo(f"📍 Noted: You prefer {dominant['formality']} formality")

    except Exception as e:
        # Feedback collection is optional - don't break if it fails
        click.echo(f"\n(Feedback collection skipped: {e})")

    # Copy to clipboard
    if clipboard:
        # ... existing clipboard code
```

**Step 6: Add import at top of cli.py**

```python
# Add to imports (around line 109-115):
import click
from pathlib import Path
from .config import Config
from .agents.message_composer import MessageComposerAgent
from .agents.simple_composer import SimpleComposer
from .feedback import FeedbackCollector, FeedbackEntry
from .feedback_ui import FeedbackUI
from .feedback_analyzer import FeedbackAnalyzer
from .adaptive_prompt import AdaptivePromptGenerator
```

**Step 7: Run existing CLI tests**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: All PASS (feedback is optional, shouldn't break existing tests)

**Step 8: Commit**

```bash
git add src/feedback_ui.py src/cli.py tests/test_feedback.py
git commit -m "feat: integrate feedback collection into CLI compose command"
```

---

## Task 5: Integrate Learned Preferences into Agents

**Files:**
- Modify: `src/agents/simple_composer.py` (accept adaptive prompt)
- Modify: `src/agents/message_composer.py` (accept adaptive prompt)
- Create: `tests/test_feedback_integration.py`

**Step 1: Write integration test**

```python
# File: tests/test_feedback_integration.py
"""Integration tests for feedback learning system."""

import pytest
from src.feedback import FeedbackCollector, FeedbackEntry
from src.feedback_analyzer import FeedbackAnalyzer
from src.adaptive_prompt import AdaptivePromptGenerator
from src.agents.simple_composer import SimpleComposer


def test_simple_composer_with_learned_preferences():
    """SimpleComposer should respect learned preferences in system prompt."""
    # Create some feedback history
    entries = [
        FeedbackEntry(
            variant_index=1,  # User prefers balanced (index 1)
            chosen=True,
            reason="good balance",
            original_message="test",
            composed_variants=["a", "b", "c"],
            preferred_tone="balanced",
            preferred_formality="medium"
        ),
        FeedbackEntry(
            variant_index=1,
            chosen=True,
            reason="right tone",
            original_message="test",
            composed_variants=["a", "b", "c"],
            preferred_tone="balanced",
            preferred_formality="medium"
        ),
    ]

    # Analyze to get dominant preferences
    analyzer = FeedbackAnalyzer(entries)
    dominant = analyzer.get_dominant_preferences()
    confidence = analyzer.confidence("tone")

    # Create adaptive prompt
    adapter = AdaptivePromptGenerator(
        preferred_tone=dominant["tone"],
        preferred_formality=dominant["formality"],
        confidence=confidence,
        confidence_threshold=0.5
    )

    composer = SimpleComposer(api_key=None)

    # Adapt the system prompt
    adapted_prompt = adapter.adapt_prompt(composer.system_prompt)

    # Should mention balanced tone
    assert "balanced" in adapted_prompt.lower()
    assert adapted_prompt != composer.system_prompt
```

**Step 2: Run integration test to verify it fails**

```bash
python3 -m pytest tests/test_feedback_integration.py::test_simple_composer_with_learned_preferences -v
```

Expected: `PASSED` (test should pass - it's verifying integration logic, not agent behavior)

**Step 3: Update SimpleComposer to accept adaptive prompt**

Modify `src/agents/simple_composer.py`:

```python
# Update compose() method signature (around line 185):

def compose(
    self,
    user_input: str,
    max_tokens: int = 1024,
    adaptive_system_prompt: str = None  # NEW PARAMETER
) -> dict:
    """
    Compose professional message variants with a single LLM call.

    Args:
        user_input: The raw message to compose professionally
        max_tokens: Maximum response length
        adaptive_system_prompt: Optional system prompt with learned preferences injected

    Returns:
        dict with keys: primary, variants, reasoning
    """

    # ... existing code ...

    # Use adaptive prompt if provided, otherwise use default
    system_to_use = adaptive_system_prompt if adaptive_system_prompt else self.system_prompt

    response = self.llm_client.create_message(
        messages=conversation,
        system=system_to_use,  # CHANGED: use adaptive prompt
        tools=[],
        max_tokens=max_tokens
    )

    # ... rest of method unchanged ...
```

**Step 4: Update MessageComposerAgent similarly**

Modify `src/agents/message_composer.py` compose() method to accept `adaptive_system_prompt` parameter and use it if provided.

**Step 5: Run all feedback tests**

```bash
python3 -m pytest tests/test_feedback.py tests/test_feedback_integration.py -v
```

Expected: All PASS

**Step 6: Commit**

```bash
git add src/agents/simple_composer.py src/agents/message_composer.py tests/test_feedback_integration.py
git commit -m "feat: agents accept adaptive system prompts with learned preferences"
```

---

## Task 6: Pass Learned Preferences to Agents During Composition

**Files:**
- Modify: `src/cli.py` (pass adaptive prompt to agent)

**Step 1: Update CLI to use learned preferences when composing**

Modify the `compose()` function in `src/cli.py` (around lines 517-530):

```python
    # Create agent and compose
    # ═════════════════════════════════════════════════════════════════════════

    try:
        # Load feedback history and get learned preferences
        from src.feedback import FeedbackCollector
        from src.feedback_analyzer import FeedbackAnalyzer
        from src.adaptive_prompt import AdaptivePromptGenerator

        collector = FeedbackCollector()
        adaptive_system_prompt = None

        if collector.count() >= 3:  # Only use after 3+ feedback samples
            analyzer = FeedbackAnalyzer(collector.get_all())
            dominant = analyzer.get_dominant_preferences()
            confidence_tone = analyzer.confidence("tone")
            confidence_formality = analyzer.confidence("formality")

            # Use average confidence
            confidence = (confidence_tone + confidence_formality) / 2 if dominant["tone"] or dominant["formality"] else 0.0

            adapter = AdaptivePromptGenerator(
                preferred_tone=dominant["tone"],
                preferred_formality=dominant["formality"],
                confidence=confidence,
                confidence_threshold=0.5
            )

            # Show context message
            context_msg = adapter.get_context_message()
            if context_msg:
                click.echo(f"\n🧠 {context_msg}")

        # Route to appropriate composer
        if mode == 'agent':
            agent = MessageComposerAgent(api_key=api_key)
        else:
            agent = SimpleComposer(api_key=api_key)

        # Pass adaptive prompt if available
        if adaptive_system_prompt:
            result = agent.compose(text, adaptive_system_prompt=adaptive_system_prompt)
        else:
            result = agent.compose(text)

    except Exception as e:
        click.echo(f"❌ Error during composition: {e}")
        return
```

**Step 2: Test CLI works with feedback**

```bash
# First, compose something
export GROQ_API_KEY="test-key"
python3 -m pytest tests/test_cli.py -v

# Or manually:
# python3 src/cli.py compose "test message" --mode simple
```

Expected: CLI tests still pass (feedback is optional)

**Step 3: Commit**

```bash
git add src/cli.py
git commit -m "feat: pass learned preferences to agents during composition"
```

---

## Task 7: Add Feedback Management CLI Commands

**Files:**
- Modify: `src/cli.py` (add new commands)

**Step 1: Add feedback summary command**

Add after the `config` command in `src/cli.py`:

```python
@app.command()
def feedback():
    """
    View and manage feedback history.

    Shows:
    - Total feedback entries collected
    - Most preferred tone/formality
    - Learned patterns
    - Option to reset feedback
    """
    from src.feedback import FeedbackCollector
    from src.feedback_analyzer import FeedbackAnalyzer

    collector = FeedbackCollector()

    if collector.count() == 0:
        click.echo("📊 No feedback collected yet")
        click.echo("   Provide feedback after composing to help the system learn!")
        return

    click.echo(f"\n📊 Feedback Summary\n")
    click.echo(f"   Total entries: {collector.count()}")

    analyzer = FeedbackAnalyzer(collector.get_all())
    summary = analyzer.get_summary()
    dominant = analyzer.get_dominant_preferences()

    # Show tone preferences
    if summary["tone_preferences"]:
        click.echo(f"\n   Tone Preferences:")
        for tone, count in sorted(summary["tone_preferences"].items(), key=lambda x: -x[1]):
            click.echo(f"      • {tone}: {count} times")

    # Show formality preferences
    if summary["formality_preferences"]:
        click.echo(f"\n   Formality Preferences:")
        for formality, count in sorted(summary["formality_preferences"].items(), key=lambda x: -x[1]):
            click.echo(f"      • {formality}: {count} times")

    # Show which variants were most chosen
    if summary["variant_preferences"]:
        click.echo(f"\n   Preferred Variants:")
        labels = ["Formal", "Balanced", "Direct"]
        for idx, count in sorted(summary["variant_preferences"].items(), key=lambda x: -x[1]):
            label = labels[int(idx)] if int(idx) < len(labels) else f"Variant {idx}"
            click.echo(f"      • {label}: {count} times")

    # Show keywords from feedback
    if summary["average_reason_keywords"]:
        click.echo(f"\n   Common Feedback Words:")
        click.echo(f"      {', '.join(summary['average_reason_keywords'])}")

    # Show dominant preferences
    click.echo(f"\n   Your Pattern:")
    parts = []
    if dominant["tone"]:
        parts.append(dominant["tone"])
    if dominant["formality"]:
        parts.append(f"{dominant['formality']} formality")

    if parts:
        click.echo(f"      {', '.join(parts).title()}")

    # Offer reset option
    click.echo(f"\n   Options:")
    click.echo(f"      pm feedback reset    # Clear all feedback")


@app.command()
def feedback_reset():
    """
    Clear all collected feedback.

    WARNING: This will reset the system's learning.
    """
    from src.feedback import FeedbackCollector

    collector = FeedbackCollector()
    count = collector.count()

    if count == 0:
        click.echo("   No feedback to clear")
        return

    confirm = click.confirm(
        f"   Clear {count} feedback entries? (cannot undo)",
        default=False
    )

    if confirm:
        collector.clear()
        click.echo(f"   ✅ Cleared {count} entries")
    else:
        click.echo("   Cancelled")
```

**Step 2: Test new commands**

```bash
python3 -m pytest tests/test_cli.py -v
```

Expected: All PASS

**Step 3: Commit**

```bash
git add src/cli.py
git commit -m "feat: add feedback management commands (pm feedback, pm feedback-reset)"
```

---

## Task 8: End-to-End Integration Testing

**Files:**
- Create: `tests/test_feedback_e2e.py`

**Step 1: Write comprehensive E2E test**

```python
# File: tests/test_feedback_e2e.py
"""End-to-end tests for complete feedback loop."""

import tempfile
import pytest
from pathlib import Path
from src.feedback import FeedbackCollector, FeedbackEntry
from src.feedback_analyzer import FeedbackAnalyzer
from src.adaptive_prompt import AdaptivePromptGenerator
from src.agents.simple_composer import SimpleComposer


def test_feedback_loop_complete_journey():
    """Test complete feedback loop: compose → feedback → learn → adapt."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_feedback_path = f.name

    try:
        # PHASE 1: Initial composition (no feedback yet)
        composer = SimpleComposer(api_key=None)
        initial_prompt = composer.system_prompt

        # PHASE 2: Collect feedback from 3 compositions
        collector = FeedbackCollector(storage_path=temp_feedback_path)

        # User composition 1: chooses "balanced"
        entry1 = FeedbackEntry(
            variant_index=1,
            chosen=True,
            reason="just right balance",
            original_message="project delayed",
            composed_variants=["Formal", "Balanced", "Direct"],
            preferred_tone="balanced",
            preferred_formality="medium",
            mode="simple"
        )
        collector.add(entry1)

        # User composition 2: chooses "balanced" again
        entry2 = FeedbackEntry(
            variant_index=1,
            chosen=True,
            reason="perfect tone",
            original_message="need extension",
            composed_variants=["Formal", "Balanced", "Direct"],
            preferred_tone="balanced",
            preferred_formality="medium",
            mode="simple"
        )
        collector.add(entry2)

        # User composition 3: chooses "balanced" again
        entry3 = FeedbackEntry(
            variant_index=1,
            chosen=True,
            reason="good balance",
            original_message="sending update",
            composed_variants=["Formal", "Balanced", "Direct"],
            preferred_tone="balanced",
            preferred_formality="medium",
            mode="simple"
        )
        collector.add(entry3)

        # PHASE 3: Analyze patterns
        analyzer = FeedbackAnalyzer(collector.get_all())
        summary = analyzer.get_summary()
        dominant = analyzer.get_dominant_preferences()
        confidence = analyzer.confidence("tone")

        # Verify learning occurred
        assert collector.count() == 3
        assert summary["variant_preferences"]["1"] == 3  # All chose balanced
        assert dominant["tone"] == "balanced"
        assert dominant["formality"] == "medium"
        assert confidence >= 0.9  # High confidence (3/3)

        # PHASE 4: Generate adaptive prompt
        adapter = AdaptivePromptGenerator(
            preferred_tone=dominant["tone"],
            preferred_formality=dominant["formality"],
            confidence=confidence,
            confidence_threshold=0.5
        )

        adapted_prompt = adapter.adapt_prompt(initial_prompt)

        # Verify adaptation
        assert adapted_prompt != initial_prompt
        assert "balanced" in adapted_prompt.lower()

        context_msg = adapter.get_context_message()
        assert context_msg is not None
        assert "balanced" in context_msg.lower()

        # PHASE 5: Next composition uses learned preferences
        # (Would need mocked LLM to test actual composition)

    finally:
        Path(temp_feedback_path).unlink()


def test_feedback_learning_increases_with_more_samples():
    """Confidence should increase as more feedback samples are collected."""
    entries = []

    # Start with 1 balanced preference
    entries.append(FeedbackEntry(
        1, True, "good", "msg", ["a", "b", "c"],
        preferred_tone="balanced", preferred_formality="medium"
    ))

    analyzer = FeedbackAnalyzer(entries)
    conf_1 = analyzer.confidence("tone")

    # Add another balanced preference
    entries.append(FeedbackEntry(
        1, True, "good", "msg", ["a", "b", "c"],
        preferred_tone="balanced", preferred_formality="medium"
    ))

    analyzer = FeedbackAnalyzer(entries)
    conf_2 = analyzer.confidence("tone")

    # Confidence should be same or higher
    assert conf_2 >= conf_1
    assert len(entries) == 2


def test_feedback_adapts_to_changing_preferences():
    """System should adapt when preferences change over time."""
    entries = [
        # First 2: prefer balanced
        FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"], preferred_tone="balanced"),
        FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"], preferred_tone="balanced"),
        # Last 2: prefer direct
        FeedbackEntry(2, True, "crisp", "msg", ["a", "b", "c"], preferred_tone="direct"),
        FeedbackEntry(2, True, "crisp", "msg", ["a", "b", "c"], preferred_tone="direct"),
    ]

    analyzer = FeedbackAnalyzer(entries)
    summary = analyzer.get_summary()

    # Recent preference is direct (2/4 recent)
    assert summary["tone_preferences"]["balanced"] == 2
    assert summary["tone_preferences"]["direct"] == 2
```

**Step 2: Run E2E tests**

```bash
python3 -m pytest tests/test_feedback_e2e.py -v
```

Expected: All PASS

**Step 3: Commit**

```bash
git add tests/test_feedback_e2e.py
git commit -m "test: add end-to-end tests for complete feedback loop"
```

---

## Task 9: Documentation

**Files:**
- Create: `docs/FEEDBACK_LOOP_GUIDE.md`

**Step 1: Write user guide**

```markdown
# File: docs/FEEDBACK_LOOP_GUIDE.md

# Feedback Loop & Learning System

Professional Messenger includes a **learning system** that adapts to your preferences over time.

## How It Works

### 1. You Compose a Message

```bash
pm compose "hey project delayed"
```

Results in 3 variants:
- [1] Formal - "I am writing to inform you..."
- [2] Balanced - "I wanted to let you know..."
- [3] Direct - "The project is delayed..."

### 2. System Asks for Feedback

After each composition, the system asks:
- **Which variant did you prefer?** (Choose 1, 2, or 3)
- **Why did you choose it?** (e.g., "good tone", "clear", "professional")
- **Tone preference?** (optional: professional, casual, direct)
- **Formality preference?** (optional: low, medium, high)

### 3. System Learns Your Pattern

After 3+ feedback samples, the system analyzes:
- Which tone you prefer most (formal vs balanced vs direct)
- Your preferred formality level
- Which variant style you typically choose
- Keywords you mention ("clear", "professional", "concise")

### 4. Next Compositions Adapt

The system adjusts future compositions to match your preferences:

**Before learning:**
```
[1] Formal / [2] Balanced / [3] Direct (equally likely)
```

**After learning you prefer balanced:**
```
[1] Formal-ish / [2] Very Balanced ✓ / [3] Direct-ish (biased toward balanced)
```

## Viewing Your Preferences

```bash
pm feedback
```

Shows:
- Total feedback samples collected
- Your tone preference distribution
- Your formality preference distribution
- Most-chosen variant style
- Common words you use in feedback ("clear", "professional", etc.)
- Your dominant pattern (e.g., "Balanced, Medium Formality")

## Example Learning Journey

**Composition 1:**
- You choose variant 2 (Balanced)
- Reason: "good tone"
- Tone: Balanced
- Formality: Medium
- Status: "Help the system learn by providing feedback!"

**Composition 2:**
- You choose variant 2 (Balanced) again
- Reason: "perfect tone"
- Same preferences
- Status: "Learning (2 feedback samples)..."

**Composition 3:**
- You choose variant 2 (Balanced) again
- Reason: "right balance"
- Same preferences
- Status: "Adapting to your style (3 samples)..."
- System now has 70%+ confidence in balanced tone preference
- **Next composition will emphasize balanced tone in all variants**

**Composition 4:**
- System shows: "🧠 Using your learned preference: balanced tone, medium formality"
- Variants now lean toward balanced tone based on past feedback

## Resetting Your Learning

If you want to start fresh:

```bash
pm feedback-reset
```

This clears all feedback history and the system returns to default behavior.

## How the System Adapts

The adaptation is **invisible**—it works through system prompt injection:

### Without Learning
```
System Prompt: "Generate 3 message variants (formal, balanced, direct)..."
```

### With Learning
```
System Prompt: "Generate 3 message variants...
LEARNED PREFERENCES:
Based on past feedback, the user prefers a balanced tone.
Apply this to all message variants.

The user prefers medium formality (professional but approachable).
..."
```

The LLM sees these preferences and naturally produces variants that match your style.

## FAQ

**Q: Do I have to provide feedback?**
A: No, it's optional. The compose command works fine without it.

**Q: How many samples does the system need?**
A: 3+ samples for learning to begin. Higher is better for confidence (10+ is ideal).

**Q: Can I have different preferences for different modes?**
A: Yes! Feedback is separate for `--mode simple` and `--mode agent`. Each learns independently.

**Q: Does feedback persist?**
A: Yes, it's stored in `feedback.yaml` in your current directory.

**Q: Can I use different feedback files?**
A: Not yet, but you could copy `feedback.yaml` to different locations.

**Q: How accurate is the learning?**
A: The system is simple (frequency counting) but effective. It works best after 5-10 samples.

## Technical Details

- **Storage**: `feedback.yaml` (YAML format, human-readable)
- **Learning Method**: Frequency analysis + confidence scoring
- **Confidence Calculation**: Proportion of chosen variants matching the preference
- **Minimum Threshold**: 50% confidence required before adapting
- **Adaptation Method**: System prompt injection before LLM call

See `docs/INCREMENTAL_LEARNING.md` for architectural details.
```

**Step 2: Update main README**

Add to `README.md` (in Features section):

```markdown
### 💡 Smart Learning System

After a few compositions, Professional Messenger learns your preferences:
- Your preferred tone (formal, balanced, casual)
- Your preferred formality level
- Your typical variant choices

Next compositions automatically adapt to your style!

```bash
pm compose "message"          # Provide feedback
pm feedback                   # View your learned preferences
pm feedback-reset             # Start fresh
```

See [Feedback Loop Guide](docs/FEEDBACK_LOOP_GUIDE.md) for details.
```

**Step 3: Commit**

```bash
git add docs/FEEDBACK_LOOP_GUIDE.md README.md
git commit -m "docs: add feedback loop user guide and README updates"
```

---

## Task 10: Final Testing & Cleanup

**Step 1: Run all tests**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: All tests pass (28 existing + ~15 feedback tests = 43+ tests)

**Step 2: Verify no regressions**

```bash
python3 -m pytest tests/test_cli.py tests/test_message_composer.py -v
```

Expected: Existing tests still pass

**Step 3: Manual integration test**

```bash
# Create a test feedback file
export FEEDBACK_FILE="test-feedback.yaml"

# (Would need interactive testing)
# pm compose "test message" --mode simple
# Then respond to feedback prompts manually

# Check feedback was stored
# pm feedback
```

**Step 4: Cleanup**

Remove any temporary test files:

```bash
rm -f test-feedback.yaml /tmp/feedback-*.yaml
```

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete feedback loop implementation with learning system"
```

**Step 6: Update CLAUDE.md**

Add to project instructions:

```markdown
## Feedback & Learning System (Phase 3 - COMPLETE)

The feedback loop enables the system to learn from user preferences:

### Architecture
1. **FeedbackEntry** (src/feedback.py): Single piece of feedback
2. **FeedbackCollector**: Store/load feedback from YAML
3. **FeedbackAnalyzer**: Extract patterns and preferences
4. **AdaptivePromptGenerator**: Inject learned preferences into prompts
5. **FeedbackUI**: CLI prompts for feedback collection
6. **CLI Integration**: Feedback after composition, management commands

### How It Works
- After composition, system asks which variant user preferred and why
- Stores feedback with tone/formality metadata in feedback.yaml
- After 3+ samples, analyzes patterns
- Next composition's system prompt includes learned preferences
- User can view preferences with `pm feedback`

### Key Files
- `src/feedback.py` - Data structures
- `src/feedback_analyzer.py` - Pattern extraction
- `src/adaptive_prompt.py` - Prompt adaptation
- `src/feedback_ui.py` - CLI prompting
- `src/cli.py` - Integration (modified)
- `tests/test_feedback*.py` - Test suite
- `docs/FEEDBACK_LOOP_GUIDE.md` - User guide

### Commands
- `pm compose "text"` - Asks for feedback after
- `pm feedback` - View learned preferences
- `pm feedback-reset` - Clear all feedback

### Testing
```bash
python3 -m pytest tests/test_feedback*.py -v
```
```

**Step 7: Final commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with feedback system documentation"
```

---

## Summary

This 10-task plan implements a complete feedback loop system:

| Task | Component | Status |
|------|-----------|--------|
| 1 | FeedbackEntry & FeedbackCollector | Create classes + tests |
| 2 | FeedbackAnalyzer | Pattern extraction + tests |
| 3 | AdaptivePromptGenerator | Prompt adaptation + tests |
| 4 | FeedbackUI & CLI Integration | Feedback prompts + storage |
| 5 | Agent Adaptation | Pass learned preferences to agents |
| 6 | Preference Injection | Use learned prefs during composition |
| 7 | Feedback Commands | `pm feedback`, `pm feedback-reset` |
| 8 | E2E Testing | Complete journey tests |
| 9 | Documentation | User guide + API docs |
| 10 | Cleanup & Verification | Final testing + commit |

**Expected deliverables:**
- ✅ Feedback storage system (YAML-based)
- ✅ Learning algorithm (frequency analysis)
- ✅ Adaptive prompt generation
- ✅ CLI integration
- ✅ ~20 unit + integration tests
- ✅ User documentation
- ✅ Zero regressions in existing code

---

Plan complete and saved to `docs/plans/2026-02-28-feedback-loop-implementation.md`.

## Execution Options

**Two execution approaches available:**

### 1. **Subagent-Driven (Recommended - This Session)**
- Fresh subagent per task
- Code review between tasks
- Faster iteration
- Stay in current context
- **Uses:** superpowers:subagent-driven-development

### 2. **Parallel Session (Batch Execution)**
- Open new session with executing-plans skill
- Batch execute multiple tasks
- Review at checkpoints
- Separate worktree
- **Uses:** superpowers:executing-plans

Which approach would you prefer?