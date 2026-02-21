"""
LLM Client wrapper for OpenAI API interactions.

This module provides a clean interface for agents to communicate with OpenAI's GPT models.
It handles:
- Message formatting (agents think in conversations)
- Tool/function calling setup (how agents use tools)
- Response parsing (extracting what OpenAI decided to do)

Key difference from Claude:
- OpenAI uses 'tools' parameter (similar to Claude)
- Response format is slightly different
- But the interface stays the same!

This demonstrates good API abstraction:
- External API changes (Claude → OpenAI)
- Interface stays the same
- Rest of code doesn't need updates
"""

import os
import json
from typing import Optional
from openai import OpenAI


class LLMClient:
    """
    Wrapper around OpenAI SDK for easier agent development.

    This class simplifies OpenAI API interactions for agents by:
    - Managing the OpenAI client
    - Formatting messages properly
    - Handling tool definitions
    - Extracting responses

    Think of this as the "translator" between our agents and OpenAI.
    Agents don't need to know about API details - they just call this client.

    Attributes:
        api_key (str): OpenAI API key
        model (str): Model to use (e.g., "gpt-3.5-turbo")
        client (OpenAI): The underlying OpenAI client

    Example:
        Using the client in an agent:
        >>> client = LLMClient(api_key="sk-...", model="gpt-3.5-turbo")
        >>> response = client.create_message(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     system="You are helpful",
        ...     max_tokens=100
        ... )
        >>> text = client.extract_text(response)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo"
    ):
        """
        Initialize the LLM client for OpenAI.

        Args:
            api_key: OpenAI API key. If not provided, uses OPENAI_API_KEY environment variable.
            model: Model identifier to use. Defaults to GPT-3.5 Turbo (free tier).

        Raises:
            ValueError: If no API key is provided or found in environment.

        Example:
            >>> client = LLMClient()  # Uses OPENAI_API_KEY env var
            >>> client2 = LLMClient(api_key="sk-...", model="gpt-4")
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "API key must be provided or set in OPENAI_API_KEY environment variable"
            )

        # Initialize the OpenAI client
        # This is the actual SDK that communicates with OpenAI's servers
        self.client = OpenAI(api_key=self.api_key)

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """
        Validate and prepare messages for OpenAI API.

        OpenAI API expects messages in a specific format:
        - Each message must have "role" (user/assistant) and "content"
        - This method validates the format and raises errors if invalid

        This is important because:
        1. Invalid messages will cause API errors
        2. We validate early to give clear error messages
        3. Agents rely on this to be correct

        Args:
            messages: List of message dicts from the conversation history

        Returns:
            list[dict]: Validated messages ready for API

        Raises:
            ValueError: If any message is malformed

        Example:
            >>> client = LLMClient(api_key="test")
            >>> valid = client._prepare_messages([{"role": "user", "content": "Hi"}])
            >>> assert len(valid) == 1
        """
        prepared = []
        for msg in messages:
            # Check that message has required fields
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"Invalid message format: {msg}")

            prepared.append(msg)

        return prepared

    def create_message(
        self,
        messages: list[dict],
        system: Optional[str] = None,
        tools: Optional[list[dict]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> dict:
        """
        Create a message using OpenAI.

        This is the main method agents use to interact with OpenAI.
        It sends a conversation and optionally available tools,
        and OpenAI responds with either text or tool calls.

        The reasoning loop calls this repeatedly:
        1. Agent sends: messages + system prompt + available tools
        2. OpenAI responds: either "here's my answer" or "I need to call this tool"
        3. Agent acts on response and calls this again

        Args:
            messages: Conversation history. List of dicts with "role" and "content".
                     First user message is typically the task description.
            system: System prompt - instructions for OpenAI's behavior.
                   This is like the agent's personality and instructions.
            tools: Available tools OpenAI can call. Each tool is a dict with:
                   - name: function name
                   - description: what it does
                   - parameters: JSON schema for parameters (OpenAI format)
            max_tokens: Maximum tokens in response. Limits response length.
            temperature: Creativity level (0.0 = deterministic, 1.0 = creative).
                        0.7 is default balanced setting.

        Returns:
            Response object from OpenAI API containing:
            - choices[0].message: Message with content and tool calls
            - usage: Token counts

        Example:
            >>> client = LLMClient(api_key="test")
            >>> response = client.create_message(
            ...     messages=[{"role": "user", "content": "What is 2+2?"}],
            ...     system="You are a math tutor",
            ...     max_tokens=100
            ... )

        Key insight: This method is called repeatedly in the agent's reasoning loop.
        Each call adds new information (tool results), and OpenAI refines its response.
        """
        # Build the API request parameters
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self._prepare_messages(messages),
            "temperature": temperature
        }

        # Add system message if provided
        # In OpenAI, system is part of messages, but we handle it separately for interface compatibility
        if system:
            # Prepend system message to conversation
            params["messages"] = [
                {"role": "system", "content": system}
            ] + params["messages"]

        # Add tools if provided
        if tools:
            # Convert tools to OpenAI format if needed
            params["tools"] = tools

        # Call OpenAI API
        # This is where the actual communication happens
        response = self.client.chat.completions.create(**params)

        return response

    def extract_text(self, response) -> str:
        """
        Extract text content from OpenAI's response.

        OpenAI can return different types of content:
        - Text (the answer)
        - Tool calls (call to a tool)
        - Other types

        This method finds and extracts just the text part.

        Args:
            response: Response object from create_message()

        Returns:
            str: The text content, or empty string if no text

        Example:
            >>> client = LLMClient(api_key="test")
            >>> response = client.create_message(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ... )
            >>> text = client.extract_text(response)
            >>> print(text)  # OpenAI's reply
        """
        # OpenAI response structure: response.choices[0].message.content
        try:
            message = response.choices[0].message
            
            # Check if message has text content
            if hasattr(message, 'content') and message.content:
                return message.content
        except (AttributeError, IndexError):
            pass

        # No text found
        return ""

    def extract_tool_use(self, response) -> Optional[dict]:
        """
        Extract tool use from OpenAI's response.

        When OpenAI decides to use a tool, it returns a tool_call in the response.
        This method extracts that information for the agent to act on.

        Important for the reasoning loop:
        - If tool_use is found: agent should execute the tool and loop
        - If tool_use is None: agent should return the text answer

        Args:
            response: Response object from create_message()

        Returns:
            dict with keys: name, id, input (as string to parse)
            or None if no tool was called

        Example:
            >>> # In the reasoning loop:
            >>> response = client.create_message(...)
            >>> tool_use = client.extract_tool_use(response)
            >>> if tool_use:
            ...     # Execute the tool
            ...     result = execute_tool(tool_use["name"], tool_use["input"])
            ...     # Add result to conversation and loop
            >>> else:
            ...     # No tool, we have the final answer
            ...     return response
        """
        try:
            message = response.choices[0].message
            
            # Check if message has tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Get the first tool call
                tool_call = message.tool_calls[0]
                
                return {
                    "name": tool_call.function.name,
                    "id": tool_call.id,
                    # OpenAI provides arguments as JSON string, parse it
                    "input": json.loads(tool_call.function.arguments)
                }
        except (AttributeError, IndexError, json.JSONDecodeError):
            pass

        # No tool use found
        return None
