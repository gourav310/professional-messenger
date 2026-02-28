import pytest
from datetime import datetime
from src.feedback import FeedbackEntry, FeedbackCollector


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


def test_feedback_analyzer_tone_preference():
    """FeedbackAnalyzer should extract tone preferences."""
    from src.feedback_analyzer import FeedbackAnalyzer

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
        assert choice == 0  # 0-indexed, so choice 1 → index 0


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
    with patch('click.prompt', side_effect=['1', '2']):
        ui = FeedbackUI()
        tone = ui.prompt_tone_preference()
        formality = ui.prompt_formality_preference()

        assert tone == "professional"
        assert formality == "medium"


def test_simple_composer_with_learned_preferences():
    """SimpleComposer should respect learned preferences in system prompt."""
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.adaptive_prompt import AdaptivePromptGenerator
    from src.agents.simple_composer import SimpleComposer
    from unittest.mock import patch, MagicMock

    # Create feedback history with balanced preferences
    entries = [
        FeedbackEntry(1, True, "good tone", "test1", ["a", "b", "c"],
                     preferred_tone="balanced", preferred_formality="medium"),
        FeedbackEntry(1, True, "balanced", "test2", ["a", "b", "c"],
                     preferred_tone="balanced", preferred_formality="medium"),
        FeedbackEntry(1, True, "just right", "test3", ["a", "b", "c"],
                     preferred_tone="balanced", preferred_formality="medium"),
    ]

    # Analyze to get dominant preferences
    analyzer = FeedbackAnalyzer(entries)
    dominant = analyzer.get_dominant_preferences()

    # Create adaptive prompt
    adapter = AdaptivePromptGenerator(
        preferred_tone=dominant["tone"],
        preferred_formality=dominant["formality"],
        confidence=0.8
    )

    adapted = adapter.adapt_prompt("Test system prompt")

    # Verify adaptation happened
    assert adapted != "Test system prompt"
    assert "balanced" in adapted.lower()

    # Now test that SimpleComposer uses the adapted prompt
    # Mock the LLM client to verify the prompt is passed correctly
    with patch('src.agents.simple_composer.LLMClient') as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm
        mock_llm.extract_text.return_value = """
Professional Message 1: Formal message here
Professional Message 2: Balanced message here
Professional Message 3: Direct message here
"""

        composer = SimpleComposer(api_key="test-key")
        composer.llm_client = mock_llm

        # Call compose with adaptive prompt
        result = composer.compose("test input", adaptive_system_prompt=adapted)

        # Verify the mock was called with the adaptive prompt
        mock_llm.create_message.assert_called_once()
        call_kwargs = mock_llm.create_message.call_args[1]
        assert call_kwargs['system'] == adapted
        assert call_kwargs['system'] != "Test system prompt"


def test_message_composer_with_learned_preferences():
    """MessageComposerAgent should respect learned preferences in system prompt."""
    from src.feedback_analyzer import FeedbackAnalyzer
    from src.adaptive_prompt import AdaptivePromptGenerator
    from src.agents.message_composer import MessageComposerAgent
    from unittest.mock import patch, MagicMock

    # Create feedback history with professional tone preference
    entries = [
        FeedbackEntry(0, True, "formal", "test1", ["a", "b", "c"],
                     preferred_tone="professional", preferred_formality="high"),
        FeedbackEntry(0, True, "very formal", "test2", ["a", "b", "c"],
                     preferred_tone="professional", preferred_formality="high"),
    ]

    # Analyze to get dominant preferences
    analyzer = FeedbackAnalyzer(entries)
    dominant = analyzer.get_dominant_preferences()
    confidence = analyzer.confidence("tone")

    # Create adaptive prompt
    adapter = AdaptivePromptGenerator(
        preferred_tone=dominant["tone"],
        preferred_formality=dominant["formality"],
        confidence=confidence
    )

    adapted = adapter.adapt_prompt("Base system prompt")

    # Verify adaptation contains professional
    assert "professional" in adapted.lower()

    # Test that MessageComposerAgent uses the adapted prompt
    with patch('src.agents.message_composer.LLMClient') as mock_llm_class:
        mock_llm = MagicMock()
        mock_llm_class.return_value = mock_llm

        # Mock response: text response (no tool calls)
        mock_response = MagicMock()
        mock_llm.extract_tool_use.return_value = None  # No tool use
        mock_llm.extract_text.return_value = """
Professional Message 1: Formal variant
Professional Message 2: Balanced variant
Professional Message 3: Direct variant
"""
        mock_llm.create_message.return_value = mock_response

        agent = MessageComposerAgent(api_key="test-key")
        agent.llm_client = mock_llm

        # Call compose with adaptive prompt
        result = agent.compose("test input", adaptive_system_prompt=adapted)

        # Verify the mock was called with the adaptive prompt
        mock_llm.create_message.assert_called()
        # Get the first call
        call_kwargs = mock_llm.create_message.call_args_list[0][1]
        assert call_kwargs['system'] == adapted
        assert "professional" in call_kwargs['system'].lower()
