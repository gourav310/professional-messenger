"""
Tests for the LLMClient wrapper around the Anthropic SDK.

This test file demonstrates how to test agent infrastructure in isolation.
We use mocking to avoid actual API calls while still verifying behavior.

TEST STRATEGY:
The tests in this file use unittest.mock to simulate Claude API responses.
This allows us to:
1. Test without API keys or network access
2. Test error cases and edge cases
3. Verify the client properly formats requests
4. Check response parsing logic

REAL vs MOCKED TESTING:
- Unit tests (here): Mock the API, test client logic
- Integration tests (later): Use real API with test keys
- End-to-end tests (later): Full agent reasoning loops
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_client import LLMClient


class TestLLMClientInitialization:
    """Tests for LLMClient initialization and setup."""

    @patch('src.llm_client.Anthropic')
    def test_llm_client_initialization(self, mock_anthropic_class):
        """
        Test that LLMClient initializes properly with API key and model.

        This test verifies the basic initialization flow:
        1. Client accepts api_key and model parameters
        2. Client stores these for later use
        3. Client initializes the underlying Anthropic client

        Why this matters:
        - Ensures client is properly configured before use
        - Verifies parameters are stored correctly
        - Foundation for all other tests
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        assert client.api_key == "test-key"
        assert client.model == "claude-3-5-haiku-20241022"

    def test_llm_client_missing_api_key(self):
        """
        Test that LLMClient raises error if API key is missing.

        This test verifies error handling:
        1. If no API key is provided
        2. And CLAUDE_API_KEY environment variable is not set
        3. Then initialization should raise ValueError with clear message

        Why this matters:
        - Prevents silent failures with missing credentials
        - Clear error message helps developers debug
        - Enforces security best practice (fail fast on bad config)
        """
        # This test runs with environment variable not set
        with pytest.raises(ValueError) as exc_info:
            LLMClient(api_key=None, model="claude-3-5-haiku-20241022")

        # Verify error message is helpful
        assert "API key" in str(exc_info.value)

    @patch('src.llm_client.Anthropic')
    def test_llm_client_uses_environment_variable(self, mock_anthropic_class, monkeypatch):
        """
        Test that LLMClient reads API key from CLAUDE_API_KEY environment variable.

        This test verifies configuration from environment:
        1. If api_key parameter is None
        2. And CLAUDE_API_KEY is set in environment
        3. Then client should use the environment variable

        Why this matters:
        - Allows secure configuration (API key not in code)
        - Matches Python best practices (env vars for secrets)
        - Supports different environments (dev, staging, prod)
        """
        # Set environment variable for this test
        monkeypatch.setenv("CLAUDE_API_KEY", "env-key")

        # Create client without explicit api_key
        client = LLMClient(api_key=None, model="claude-3-5-haiku-20241022")

        # Should use environment variable
        assert client.api_key == "env-key"


class TestMessageFormatting:
    """Tests for message preparation and formatting."""

    @patch('src.llm_client.Anthropic')
    def test_llm_client_formats_messages(self, mock_anthropic_class):
        """
        Test that client validates and formats messages correctly.

        This test verifies message handling:
        1. Client accepts a list of message dicts
        2. Each message should have "role" and "content"
        3. Client returns formatted messages ready for API

        Why this matters:
        - Claude API has strict message format requirements
        - Early validation catches errors before API call
        - Clear error messages help debugging
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        messages = [
            {"role": "user", "content": "Hello, Claude"}
        ]

        # This should not raise an error
        formatted = client._prepare_messages(messages)

        # Verify the result
        assert isinstance(formatted, list)
        assert len(formatted) == 1
        assert formatted[0]["role"] == "user"
        assert formatted[0]["content"] == "Hello, Claude"

    @patch('src.llm_client.Anthropic')
    def test_llm_client_handles_multiple_messages(self, mock_anthropic_class):
        """
        Test that client handles multi-turn conversations correctly.

        This test verifies multi-message handling:
        1. Agent reasoning often requires multiple messages
        2. Messages alternate between user and assistant
        3. Client should preserve order and content

        Why this matters:
        - Professional Messenger needs to maintain conversation history
        - Message order affects Claude's reasoning
        - Agents reason by building on previous exchanges
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        messages = [
            {"role": "user", "content": "Analyze this message"},
            {"role": "assistant", "content": "I'll analyze it..."},
            {"role": "user", "content": "Now improve it"}
        ]

        formatted = client._prepare_messages(messages)

        # Verify all messages preserved and ordered
        assert len(formatted) == 3
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"
        assert formatted[2]["role"] == "user"

    @patch('src.llm_client.Anthropic')
    def test_llm_client_rejects_invalid_messages(self, mock_anthropic_class):
        """
        Test that client rejects malformed messages with clear errors.

        This test verifies validation:
        1. Messages without "role" field should be rejected
        2. Messages without "content" field should be rejected
        3. Error message should indicate what's wrong

        Why this matters:
        - Prevents silent failures from bad message format
        - Helps developers quickly fix message structure
        - Critical for robust agent implementations
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Message missing "role"
        invalid_message = [{"content": "Hello"}]
        with pytest.raises(ValueError):
            client._prepare_messages(invalid_message)

        # Message missing "content"
        invalid_message = [{"role": "user"}]
        with pytest.raises(ValueError):
            client._prepare_messages(invalid_message)


class TestToolHandling:
    """Tests for tool/function calling setup and handling."""

    @patch('src.llm_client.Anthropic')
    def test_llm_client_call_with_tools(self, mock_anthropic_class):
        """
        Test that client properly handles tool definitions.

        This test verifies tool handling:
        1. Client should accept tools parameter
        2. Tools should be in Claude API format
        3. Client should pass tools to API in requests

        Why this matters:
        - Tools enable agents to do real work
        - Proper tool formatting is critical for Claude
        - Tests verify this works before real reasoning loops

        Note: This test just verifies the method exists and accepts parameters.
        The actual create_message method will be tested more thoroughly below.
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        tools = [
            {
                "name": "test_tool",
                "description": "A test tool for unit testing",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        ]

        # Verify the method exists
        assert hasattr(client, 'create_message')
        assert callable(client.create_message)


class TestMessageCreation:
    """Tests for creating messages via Claude API."""

    @patch('src.llm_client.Anthropic')
    def test_create_message_sends_request(self, mock_anthropic_class):
        """
        Test that create_message properly constructs and sends API request.

        This test verifies API request handling:
        1. Client should call Anthropic API with correct parameters
        2. Request should include model, messages, and max_tokens
        3. System prompt should be included if provided

        Why this matters:
        - Ensures requests are properly formatted
        - Verifies parameters are passed to API
        - Critical for agent reasoning to work

        MOCKING STRATEGY:
        We mock the Anthropic client to avoid actual API calls.
        We verify the mock was called with correct parameters.
        """
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_client.messages.create.return_value = mock_response

        # Create real client with mocked Anthropic
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a message
        messages = [{"role": "user", "content": "Hello"}]
        response = client.create_message(
            messages=messages,
            system="You are helpful",
            max_tokens=100
        )

        # Verify API was called
        mock_client.messages.create.assert_called_once()

        # Get the arguments to verify they're correct
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == "claude-3-5-haiku-20241022"
        assert call_kwargs['max_tokens'] == 100
        assert call_kwargs['system'] == "You are helpful"
        assert call_kwargs['messages'] == messages

    @patch('src.llm_client.Anthropic')
    def test_create_message_with_tools(self, mock_anthropic_class):
        """
        Test that create_message includes tools in API request.

        This test verifies tool passing:
        1. Tools should be passed to API when provided
        2. Tools should be in correct format
        3. Agent can use tools for reasoning

        Why this matters:
        - Tools are how agents take action in the world
        - Proper tool setup enables agent reasoning loops
        - Critical for task completion
        """
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client
        mock_response = MagicMock()
        mock_client.messages.create.return_value = mock_response

        # Create real client with mocked Anthropic
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a message with tools
        tools = [
            {
                "name": "analyze_tone",
                "description": "Analyze message tone",
                "input_schema": {"type": "object"}
            }
        ]
        messages = [{"role": "user", "content": "Analyze this"}]
        response = client.create_message(
            messages=messages,
            tools=tools
        )

        # Verify API was called with tools
        call_kwargs = mock_client.messages.create.call_args[1]
        assert 'tools' in call_kwargs
        assert call_kwargs['tools'] == tools


class TestResponseParsing:
    """Tests for extracting information from Claude responses."""

    @patch('src.llm_client.Anthropic')
    def test_extract_text_from_response(self, mock_anthropic_class):
        """
        Test that client extracts text from Claude's response.

        This test verifies response parsing:
        1. Claude returns different types of content
        2. Client should extract just the text content
        3. Return empty string if no text found

        Why this matters:
        - Agents need to read what Claude responded
        - Response might contain text, tool calls, or both
        - Must handle different response structures
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a mock response with text content
        mock_text_block = MagicMock()
        mock_text_block.text = "Claude's response text"

        mock_response = MagicMock()
        mock_response.content = [mock_text_block]

        # Extract text
        text = client.extract_text(mock_response)

        assert text == "Claude's response text"

    @patch('src.llm_client.Anthropic')
    def test_extract_text_returns_empty_when_no_text(self, mock_anthropic_class):
        """
        Test that extract_text returns empty string when no text in response.

        This test verifies graceful handling:
        1. Some responses might not contain text
        2. (e.g., only tool calls)
        3. Should return empty string, not error

        Why this matters:
        - Agent might get tool_use response (no text)
        - Code should handle this gracefully
        - Prevents crashes in reasoning loops
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a mock response with no text
        # Use spec to prevent auto-creation of attributes
        mock_tool_use_block = MagicMock(spec=['type'])
        mock_tool_use_block.type = "tool_use"
        # No text attribute - spec prevents it

        mock_response = MagicMock()
        mock_response.content = [mock_tool_use_block]

        # Extract text
        text = client.extract_text(mock_response)

        # Should return empty string, not error
        assert text == ""

    @patch('src.llm_client.Anthropic')
    def test_extract_tool_use_from_response(self, mock_anthropic_class):
        """
        Test that client extracts tool use from Claude's response.

        This test verifies tool extraction:
        1. Claude can decide to use a tool
        2. Client should extract tool call details
        3. Return dict with name, id, input

        Why this matters:
        - Tool use is key to agent reasoning
        - Agent needs to know: what tool, what parameters
        - Enables execution of agent decisions

        AGENT REASONING LOOP:
        1. Agent sends message + tools to Claude
        2. Claude responds with tool_use block
        3. Agent extracts and executes the tool
        4. Agent adds result to conversation
        5. Loop continues until no more tool calls
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a mock response with tool use
        mock_tool_use_block = MagicMock()
        mock_tool_use_block.type = "tool_use"
        mock_tool_use_block.name = "analyze_tone"
        mock_tool_use_block.id = "call_123"
        mock_tool_use_block.input = {"text": "Hello"}

        mock_response = MagicMock()
        mock_response.content = [mock_tool_use_block]

        # Extract tool use
        tool_use = client.extract_tool_use(mock_response)

        # Verify extraction
        assert tool_use is not None
        assert tool_use["name"] == "analyze_tone"
        assert tool_use["id"] == "call_123"
        assert tool_use["input"] == {"text": "Hello"}

    @patch('src.llm_client.Anthropic')
    def test_extract_tool_use_returns_none_when_not_present(self, mock_anthropic_class):
        """
        Test that extract_tool_use returns None when no tool is called.

        This test verifies graceful handling:
        1. Claude might respond with only text (no tool use)
        2. Client should return None to indicate no tool call
        3. Agent checks for None to decide next action

        Why this matters:
        - Signals end of reasoning loop
        - Agent knows: if None, return final answer
        - If tool_use, execute and continue loop
        """
        client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

        # Create a mock response with only text
        mock_text_block = MagicMock()
        mock_text_block.text = "Here is my answer"

        mock_response = MagicMock()
        mock_response.content = [mock_text_block]

        # Extract tool use
        tool_use = client.extract_tool_use(mock_response)

        # Should return None
        assert tool_use is None
