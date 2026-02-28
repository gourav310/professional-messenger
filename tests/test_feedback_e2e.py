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
        # PHASE 1: Collect 3 feedback entries
        collector = FeedbackCollector(storage_path=temp_feedback_path)

        for i in range(3):
            entry = FeedbackEntry(
                variant_index=1,
                chosen=True,
                reason="balanced tone" if i % 2 == 0 else "perfect balance",
                original_message=f"message {i}",
                composed_variants=["Formal", "Balanced", "Direct"],
                preferred_tone="balanced",
                preferred_formality="medium",
                mode="simple"
            )
            collector.add(entry)

        # PHASE 2: Analyze patterns
        analyzer = FeedbackAnalyzer(collector.get_all())
        summary = analyzer.get_summary()
        dominant = analyzer.get_dominant_preferences()
        confidence = analyzer.confidence("tone")

        # Verify learning
        assert collector.count() == 3
        assert summary["variant_preferences"]["1"] == 3
        assert dominant["tone"] == "balanced"
        assert dominant["formality"] == "medium"
        assert confidence >= 0.9

        # PHASE 3: Generate adaptive prompt
        adapter = AdaptivePromptGenerator(
            preferred_tone=dominant["tone"],
            preferred_formality=dominant["formality"],
            confidence=confidence,
            confidence_threshold=0.5
        )

        adapted_prompt = adapter.adapt_prompt("Base prompt here")
        context_msg = adapter.get_context_message()

        # Verify adaptation
        assert adapted_prompt != "Base prompt here"
        assert "balanced" in adapted_prompt.lower()
        assert context_msg is not None
        assert "balanced" in context_msg.lower()

    finally:
        Path(temp_feedback_path).unlink()


def test_feedback_learning_increases_with_samples():
    """Confidence increases with more consistent feedback."""
    entries = []

    # 1 sample
    entries.append(FeedbackEntry(
        1, True, "good", "msg", ["a", "b", "c"],
        preferred_tone="balanced", preferred_formality="medium"
    ))

    analyzer1 = FeedbackAnalyzer(entries)
    conf1 = analyzer1.confidence("tone")

    # 3 samples (all same preference)
    entries.append(FeedbackEntry(
        1, True, "good", "msg", ["a", "b", "c"],
        preferred_tone="balanced", preferred_formality="medium"
    ))
    entries.append(FeedbackEntry(
        1, True, "good", "msg", ["a", "b", "c"],
        preferred_tone="balanced", preferred_formality="medium"
    ))

    analyzer3 = FeedbackAnalyzer(entries)
    conf3 = analyzer3.confidence("tone")

    # Confidence should not decrease
    assert conf3 >= conf1


def test_agents_accept_adaptive_prompts():
    """Both agents should accept and use adaptive prompts."""
    from src.agents.message_composer import MessageComposerAgent
    import inspect

    # SimpleComposer
    simple = SimpleComposer(api_key="test-key")
    assert hasattr(simple, 'compose')
    # Check method signature accepts adaptive_system_prompt
    sig = inspect.signature(simple.compose)
    assert 'adaptive_system_prompt' in sig.parameters

    # MessageComposerAgent
    agent = MessageComposerAgent(api_key="test-key")
    assert hasattr(agent, 'compose')
    sig = inspect.signature(agent.compose)
    assert 'adaptive_system_prompt' in sig.parameters


def test_feedback_loop_variant_tracking():
    """Test that variant preferences are tracked correctly."""
    entries = [
        FeedbackEntry(0, True, "formal good", "msg1", ["a", "b", "c"]),
        FeedbackEntry(1, True, "balanced", "msg2", ["a", "b", "c"]),
        FeedbackEntry(1, True, "perfect", "msg3", ["a", "b", "c"]),
    ]

    analyzer = FeedbackAnalyzer(entries)
    summary = analyzer.get_summary()
    dominant = analyzer.get_dominant_preferences()

    # Variant 1 (balanced) should be most preferred
    assert summary["variant_preferences"]["1"] == 2
    assert summary["variant_preferences"]["0"] == 1
    assert dominant["preferred_variant_index"] == 1


def test_feedback_loop_mixed_preferences():
    """Test feedback with mixed tone and formality preferences."""
    entries = [
        FeedbackEntry(0, True, "professional", "msg1", ["a", "b", "c"],
                     preferred_tone="professional", preferred_formality="high"),
        FeedbackEntry(1, True, "balanced", "msg2", ["a", "b", "c"],
                     preferred_tone="balanced", preferred_formality="medium"),
        FeedbackEntry(0, True, "formal", "msg3", ["a", "b", "c"],
                     preferred_tone="professional", preferred_formality="high"),
    ]

    analyzer = FeedbackAnalyzer(entries)
    dominant = analyzer.get_dominant_preferences()
    tone_conf = analyzer.confidence("tone")
    formality_conf = analyzer.confidence("formality")

    # Professional should be dominant (2/3)
    assert dominant["tone"] == "professional"
    assert dominant["formality"] == "high"
    assert tone_conf >= 0.6
    assert formality_conf >= 0.6


def test_adaptive_prompt_respects_confidence_threshold():
    """Test that adaptive prompt respects confidence threshold."""
    # Low confidence - should not adapt
    low_conf_adapter = AdaptivePromptGenerator(
        preferred_tone="balanced",
        preferred_formality="medium",
        confidence=0.3,
        confidence_threshold=0.5
    )

    base = "Generate messages"
    adapted_low = low_conf_adapter.adapt_prompt(base)
    assert adapted_low == base  # Should return unchanged

    # High confidence - should adapt
    high_conf_adapter = AdaptivePromptGenerator(
        preferred_tone="balanced",
        preferred_formality="medium",
        confidence=0.8,
        confidence_threshold=0.5
    )

    adapted_high = high_conf_adapter.adapt_prompt(base)
    assert adapted_high != base  # Should be modified
    assert "balanced" in adapted_high.lower()


def test_feedback_no_learning_without_samples():
    """Test that no learning occurs with empty feedback."""
    analyzer = FeedbackAnalyzer([])
    summary = analyzer.get_summary()
    dominant = analyzer.get_dominant_preferences()

    assert summary["total_feedback"] == 0
    assert summary["tone_preferences"] == {}
    assert dominant["tone"] is None
    assert dominant["formality"] is None


def test_feedback_analyzer_confidence_calculation():
    """Test confidence calculation for different sample sizes."""
    # 1 out of 1 = 100% confidence
    entries1 = [FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"],
                             preferred_tone="balanced")]
    conf1 = FeedbackAnalyzer(entries1).confidence("tone")
    assert conf1 == 1.0

    # 2 out of 3 = 66% confidence
    entries2 = [
        FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"], preferred_tone="balanced"),
        FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"], preferred_tone="balanced"),
        FeedbackEntry(0, True, "formal", "msg", ["a", "b", "c"], preferred_tone="formal"),
    ]
    conf2 = FeedbackAnalyzer(entries2).confidence("tone")
    assert 0.6 < conf2 < 0.7

    # 5 out of 5 = 100% confidence
    entries5 = [
        FeedbackEntry(1, True, "good", "msg", ["a", "b", "c"], preferred_tone="balanced")
        for _ in range(5)
    ]
    conf5 = FeedbackAnalyzer(entries5).confidence("tone")
    assert conf5 == 1.0


def test_feedback_persistence_across_sessions():
    """Test that feedback is persisted correctly across collector instances."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name

    try:
        # Session 1: Add feedback
        collector1 = FeedbackCollector(storage_path=temp_path)
        entry1 = FeedbackEntry(
            1, True, "good", "msg1", ["a", "b", "c"],
            preferred_tone="balanced", preferred_formality="medium"
        )
        collector1.add(entry1)

        # Session 2: Load and add more
        collector2 = FeedbackCollector(storage_path=temp_path)
        assert collector2.count() == 1
        entry2 = FeedbackEntry(
            1, True, "balanced", "msg2", ["a", "b", "c"],
            preferred_tone="balanced", preferred_formality="medium"
        )
        collector2.add(entry2)

        # Session 3: Verify both entries persist
        collector3 = FeedbackCollector(storage_path=temp_path)
        assert collector3.count() == 2
        all_entries = collector3.get_all()
        assert all_entries[0].original_message == "msg1"
        assert all_entries[1].original_message == "msg2"

    finally:
        Path(temp_path).unlink()
