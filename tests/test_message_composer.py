"""
Tests for MessageComposerAgent.

These tests verify that the MessageComposerAgent initializes correctly,
has the required tools, and defines a system prompt for professional
message composition.

The tests follow a behavior-driven approach:
- Test what the agent does, not how it does it
- Verify agent identity (name, system prompt)
- Verify agent capabilities (tools)
- Tests are simple and focused on essential properties

This allows the implementation to change while tests remain stable.
"""

import pytest
from src.agents.message_composer import MessageComposerAgent


def test_message_composer_initialization():
    """
    MessageComposerAgent should initialize with API key.

    Verifies:
    - Agent creates successfully with test API key
    - Agent has correct name identifier
    - Agent has tools available (non-empty tools list)

    This tests the basic agent identity and capability setup.
    """
    agent = MessageComposerAgent(api_key=None)

    assert agent.name == "MessageComposer"
    assert len(agent.tools) > 0


def test_message_composer_has_required_tools():
    """
    Agent should have tools for analysis and composition.

    Verifies that the agent has the three core tools:
    - analyze_tone: for understanding emotional tone
    - suggest_structure: for organizing information
    - check_clarity: for identifying ambiguities

    These tools enable the reasoning loop where Claude
    analyzes the message from multiple perspectives.
    """
    agent = MessageComposerAgent(api_key=None)
    tool_names = [t.name for t in agent.tools]

    # Should have at least these tools
    assert "analyze_tone" in tool_names
    assert "suggest_structure" in tool_names or "organize_structure" in tool_names
    assert "check_clarity" in tool_names or "enhance_clarity" in tool_names


def test_message_composer_system_prompt_defined():
    """
    Agent should have a clear system prompt.

    Verifies:
    - System prompt exists (not None or empty)
    - System prompt mentions "professional" (core value)
    - System prompt mentions "message" (core domain)

    The system prompt is the agent's personality. This verifies
    that it's defined and relevant to message composition.
    """
    agent = MessageComposerAgent(api_key=None)

    assert agent.system_prompt
    assert "professional" in agent.system_prompt.lower()
    assert "message" in agent.system_prompt.lower()
