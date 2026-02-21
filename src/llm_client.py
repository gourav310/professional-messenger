"""
LLM Client wrapper for Claude API interactions.

This module provides a clean interface for agents to communicate with Claude.
It handles:
- Message formatting (agents think in conversations)
- Tool/function calling setup (how agents use tools)
- Response parsing (extracting what Claude decided to do)

Key concept: Agents communicate with Claude through messages and tools.
The reasoning loop sends messages, Claude responds with either:
1. Tool calls (agent needs more information)
2. Final answer (agent has what it needs)

This client makes it easy to implement that pattern.

WHY WE WRAP THE ANTHROPIC SDK:
The raw Anthropic SDK is powerful but requires developers to understand:
- API message format and requirements
- Tool definition structure
- Response parsing and edge cases
- Error handling and retries

By wrapping it, we provide:
- A single, clear interface for agents
- Consistent message handling
- Automatic validation
- Clear error messages
- Easy testing with mocks

Think of this as the "translator" between our agents and Claude.
Agents don't need to know about API details - they just call this client.

EDUCATIONAL ARCHITECTURE:
This module is designed to be educational. The methods include:
- Docstrings explaining purpose and parameters
- Inline comments explaining non-obvious logic
- Type hints for clarity
- Examples in docstrings

Future developers will learn agent patterns by reading this code.
"""

import os
from typing import Optional
from anthropic import Anthropic


class LLMClient:
    """
    Wrapper around Anthropic SDK for easier agent development.

    This class simplifies Claude API interactions for agents by:
    - Managing the Anthropic client
    - Formatting messages properly
    - Handling tool definitions
    - Extracting responses

    Think of this as the "translator" between our agents and Claude.
    Agents don't need to know about API details - they just call this client.

    DESIGN PHILOSOPHY:
    Rather than having agents directly import and use the Anthropic SDK,
    they use this client. This:
    - Makes testing easier (mock this client, not the SDK)
    - Centralizes API knowledge in one place
    - Allows us to add features (logging, retries, etc.) globally
    - Makes agent code cleaner and more readable

    REASONING LOOP PATTERN:
    The client enables this core agent pattern:
    1. Agent prepares a message describing the task
    2. Client sends message + tools to Claude
    3. Claude responds with either text or tool calls
    4. Agent extracts the response:
       - If text: task is done, return answer
       - If tool call: execute tool, go back to step 1
    5. Loop until Claude returns text (final answer)

    This pattern is how agents accomplish complex tasks.

    Attributes:
        api_key (str): Anthropic API key for authentication
        model (str): Model to use (e.g., "claude-3-5-haiku-20241022")
        client (Anthropic): The underlying Anthropic client from SDK

    Example:
        Using the client in an agent:
        >>> client = LLMClient(api_key="sk-...", model="claude-3-5-haiku-20241022")
        >>> response = client.create_message(
        ...     messages=[{"role": "user", "content": "Hello"}],
        ...     system="You are helpful",
        ...     max_tokens=100
        ... )
        >>> text = client.extract_text(response)
        >>> print(text)  # Claude's response
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022"
    ):
        """
        Initialize the LLM client.

        This sets up the client for communicating with Claude. It handles:
        1. API key configuration (parameter or environment variable)
        2. Model selection (which Claude version to use)
        3. SDK initialization

        CONFIGURATION PRIORITY:
        1. If api_key parameter is provided, use it
        2. Otherwise, look for CLAUDE_API_KEY environment variable
        3. If neither found, raise clear error

        This follows Python security best practices:
        - Code doesn't contain secrets
        - Secrets come from environment or parameters
        - Different for dev/staging/prod environments

        Args:
            api_key: Anthropic API key. If not provided, uses CLAUDE_API_KEY
                    environment variable. Must be provided one way or the other.
                    Format: starts with "sk-" for Anthropic API keys
                    Example: "sk-ant-v1-1234567890..."

            model: Model identifier to use. Defaults to Haiku for speed/cost.
                   Options:
                   - "claude-3-5-haiku-20241022" (default, fast/cheap)
                   - "claude-3-5-sonnet-20241022" (better, slower)
                   - "claude-opus-4-6" (best, slowest/expensive)

                   Choose based on:
                   - Speed vs Quality tradeoff
                   - Cost constraints
                   - Task complexity

        Raises:
            ValueError: If no API key is provided or found in environment.
                       Error message clearly states what to do.

        Example:
            >>> # Using environment variable (recommended for production)
            >>> client = LLMClient()
            >>> # Using explicit API key (for testing/scripts)
            >>> client = LLMClient(api_key="sk-...", model="claude-3-5-sonnet-20241022")
            >>> # Using different model
            >>> client = LLMClient(api_key="sk-...", model="claude-opus-4-6")

        DESIGN NOTE:
        The default model is Haiku because:
        - Agents often need multiple Claude calls (reasoning loops)
        - Haiku is fast and cheap, allowing more iterations
        - For production, use Sonnet or Opus as needed
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")

        # Validate that we have an API key
        # This fails fast and clear - better than silent API errors later
        if not self.api_key:
            raise ValueError(
                "API key must be provided or set in CLAUDE_API_KEY environment variable. "
                "Get your API key from https://console.anthropic.com/"
            )

        # Store the model identifier for use in API calls
        self.model = model

        # Initialize the Anthropic client
        # This is the actual SDK that communicates with Claude's servers
        # The SDK handles HTTP requests, retries, rate limiting, etc.
        self.client = Anthropic(api_key=self.api_key)

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """
        Validate and prepare messages for Claude API.

        Claude API expects messages in a specific format:
        - Each message must have "role" (who is speaking) and "content" (what they said)
        - Roles are either "user" (the human/agent) or "assistant" (Claude)
        - Content is a string with the message text

        This method validates the format and raises errors if invalid.
        Why? Because:
        1. Invalid messages will cause API errors anyway
        2. We validate early to give clear error messages
        3. Agents rely on this to be correct

        CONVERSATION FLOW:
        A multi-message conversation looks like:
        [
            {"role": "user", "content": "Analyze this message"},
            {"role": "assistant", "content": "I see... it's too formal"},
            {"role": "user", "content": "Now improve it"},
            {"role": "assistant", "content": "Here's a better version..."},
        ]

        This alternation of user/assistant is the "conversation" that Claude uses
        to understand context.

        Args:
            messages: List of message dicts from the conversation history.
                     Expected format: [{"role": "user" or "assistant", "content": "..."}, ...]
                     Each dict must have exactly "role" and "content" keys.
                     Other keys are ignored for simplicity.

        Returns:
            list[dict]: Validated messages ready for API.
                       Same format as input if all valid.
                       Raises ValueError if any message is invalid.

        Raises:
            ValueError: If any message is malformed.
                       Includes the problematic message in error text.

        Example:
            >>> client = LLMClient(api_key="test")
            >>> # Valid messages
            >>> valid = client._prepare_messages([
            ...     {"role": "user", "content": "Hi"},
            ...     {"role": "assistant", "content": "Hello"}
            ... ])
            >>> assert len(valid) == 2
            >>> # Invalid messages raise ValueError
            >>> try:
            ...     client._prepare_messages([{"content": "Missing role"}])
            ... except ValueError as e:
            ...     print("Error caught:", e)
        """
        prepared = []

        # Iterate through messages to validate each one
        for msg in messages:
            # Check that message has required "role" field
            if "role" not in msg:
                raise ValueError(
                    f"Message missing 'role' field. "
                    f"Must be 'user' or 'assistant'. "
                    f"Got: {msg}"
                )

            # Check that message has required "content" field
            if "content" not in msg:
                raise ValueError(
                    f"Message missing 'content' field. "
                    f"Content should be the message text. "
                    f"Got: {msg}"
                )

            # If we got here, message is valid - add to prepared list
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
        Create a message using Claude - the core agent-Claude interaction.

        This is the main method agents use to interact with Claude.
        It sends a conversation and optionally available tools,
        and Claude responds with either text or tool calls.

        THE AGENT REASONING LOOP:
        This method is the heart of agent reasoning. Here's how it works:

        ITERATION 1:
        1. Agent calls: create_message(
             messages=[{"role": "user", "content": "Compose a professional email"}],
             tools=[analyze_tone, check_grammar, ...]
           )
        2. Claude thinks: "The user wants an email. I need to analyze tone and check grammar"
        3. Claude responds: "I'll use analyze_tone tool with this text"
        4. Agent extracts tool call, executes it, gets result

        ITERATION 2:
        1. Agent calls: create_message(
             messages=[
               {"role": "user", "content": "Compose..."},
               {"role": "assistant", "content": "<tool_use>..."},
               {"role": "user", "content": <tool result>}
             ],
             tools=[analyze_tone, check_grammar, ...]
           )
        2. Claude reads results, refines: "Now I'll check grammar"
        3. Claude responds: "I'll use check_grammar tool"

        ITERATION 3:
        1. Agent adds grammar result to conversation
        2. Claude: "I have tone and grammar feedback. Let me refine the email."
        3. Claude responds: "Here's your polished email: ..."
        4. Agent extracts text (no more tool calls)
        5. Loop ends, return final answer

        This pattern (message → tool call → result → repeat) is how agents
        accomplish complex tasks with Claude.

        Args:
            messages: Conversation history. List of dicts with "role" and "content".
                     The full conversation up to this point.
                     First message usually describes the task.
                     Subsequent messages show the reasoning so far.
                     Format: [{"role": "user" or "assistant", "content": "..."}, ...]
                     Example:
                       [
                         {"role": "user", "content": "Compose professional message"},
                         {"role": "assistant", "content": "I'll analyze tone..."},
                         {"role": "user", "content": "Tone analysis: formal"}
                       ]

            system: System prompt - instructions for Claude's behavior.
                   This is like the agent's personality and instructions.
                   Claude will follow these instructions throughout the conversation.
                   Examples:
                   - "You are a professional message composer. Transform raw thoughts
                     into polished, professional messages..."
                   - "You analyze text tone. Classify as formal, casual, etc..."
                   If None, no system prompt is sent (Claude uses defaults).

            tools: Available tools Claude can call. Each tool is a dict with:
                   - name: function identifier (e.g., "analyze_tone")
                   - description: what it does (e.g., "Analyzes the emotional tone...")
                   - input_schema: JSON schema for parameters

                   Example:
                   [
                     {
                       "name": "analyze_tone",
                       "description": "Analyzes email tone: formal, casual, etc",
                       "input_schema": {
                         "type": "object",
                         "properties": {
                           "text": {"type": "string", "description": "Text to analyze"}
                         },
                         "required": ["text"]
                       }
                     },
                     ...
                   ]

                   If None or empty, Claude cannot use any tools (just responds with text).

            max_tokens: Maximum tokens in response. Controls response length.
                       - Agents usually need shorter responses to stay efficient
                       - Set higher for open-ended tasks, lower for quick answers
                       - Default 1024 is good for most agent tasks
                       - Each token is roughly 1/4 of a word

            temperature: Creativity/randomness level.
                        - 0.0: Deterministic, always same answer
                        - 0.5: Balanced, some variation
                        - 1.0: Creative, lots of variation
                        Default 0.7 is balanced, good for most tasks.
                        Use 0.3 for analytical tasks, 0.9 for creative tasks.

        Returns:
            Response object from Claude API containing:
            - content: List of content blocks (text, tool_use, etc.)
            - stop_reason: Why Claude stopped ("end_turn" or "tool_use")
            - usage: Token counts (input_tokens, output_tokens)

            You'll typically parse this with extract_text() or extract_tool_use().

        Raises:
            ValueError: If messages are malformed (from _prepare_messages)
            Various Anthropic exceptions: Network errors, API errors, etc.

        Example:
            >>> client = LLMClient(api_key="sk-...")
            >>> # Simple conversation
            >>> response = client.create_message(
            ...     messages=[{"role": "user", "content": "What is 2+2?"}],
            ...     system="You are a math tutor",
            ...     max_tokens=100
            ... )
            >>> text = client.extract_text(response)
            >>> print(text)  # "2 + 2 = 4"
            >>>
            >>> # With tools (agent reasoning)
            >>> response = client.create_message(
            ...     messages=[{"role": "user", "content": "Analyze this message"}],
            ...     tools=[analyze_tool],
            ...     system="You are helpful"
            ... )
            >>> tool_use = client.extract_tool_use(response)
            >>> if tool_use:
            ...     result = execute_tool(tool_use["name"], tool_use["input"])
            ...     # Loop: add result to messages, call create_message again

        Key insight: This method is called repeatedly in the agent's reasoning loop.
        Each call adds new information (tool results), and Claude refines its response.
        The loop continues until Claude returns text (no more tool calls).
        """
        # Build the API request parameters dictionary
        # This will be passed to the Anthropic SDK's messages.create() method
        params = {
            "model": self.model,
            # Which Claude model to use for this request
            # Set during __init__, could vary per request if needed

            "max_tokens": max_tokens,
            # Maximum length of Claude's response
            # Prevents unexpectedly long outputs

            "messages": self._prepare_messages(messages),
            # The conversation so far, validated by _prepare_messages()
            # This is the context Claude uses for reasoning

            "temperature": temperature,
            # Controls randomness of response
            # Lower = more deterministic, higher = more creative
        }

        # Add optional parameters if provided
        # These are only sent to the API if the user specified them

        if system:
            # System prompt provided - include it
            # System prompt is instructions for how Claude should behave
            # It's sent separately from messages for special handling
            params["system"] = system

        if tools:
            # Tools provided - include them
            # When tools are provided, Claude can decide to use them
            # This is what enables the agent reasoning loop
            params["tools"] = tools

        # Call Claude API
        # This is where the actual communication happens with Anthropic's servers
        # The SDK handles network, authentication, error handling, etc.
        response = self.client.messages.create(**params)

        # Return the response object for parsing
        # The caller will use extract_text() or extract_tool_use() to read it
        return response

    def extract_text(self, response) -> str:
        """
        Extract text content from Claude's response.

        Claude can return different types of content:
        - Text (the answer the agent needs)
        - Tool use (call to a tool)
        - Other types in future versions

        This method finds and extracts just the text part.

        WHY A SEPARATE METHOD:
        Response structure is complex. Extracting text should be simple.
        This method encapsulates that complexity, so callers don't need
        to understand the response structure.

        WHAT IS TEXT:
        Text is Claude's direct answer. Examples:
        - "The tone is too formal, here's a better version..."
        - "The grammar is correct."
        - "Here's the polished email..."

        TEXT VS TOOL USE:
        - Text response: Agent has the information needed
        - Tool use response: Agent should execute the tool

        After tool execution, agent adds result to conversation
        and calls create_message() again to get Claude's next action.

        Args:
            response: Response object from create_message()
                     This is the raw response from Claude API

        Returns:
            str: The text content of the response.
                 Empty string if response contains no text.
                 Never None - safe to use directly.

        Example:
            >>> client = LLMClient(api_key="sk-...")
            >>> response = client.create_message(
            ...     messages=[{"role": "user", "content": "Hello"}],
            ... )
            >>> text = client.extract_text(response)
            >>> print(text)  # Claude's reply
            >>> if text:
            ...     print("Claude said:", text)
            ... else:
            ...     print("No text in response (maybe tool call?)")
        """
        # response.content is a list of content blocks
        # Each block represents one piece of content Claude returned
        # We iterate through to find text blocks

        for block in response.content:
            # Check if this block has a 'text' attribute
            # Text blocks have a .text field with the actual text
            if hasattr(block, 'text'):
                # Found a text block - return its content
                return block.text

        # No text found in any block
        # This is normal if response only contains tool_use blocks
        return ""

    def extract_tool_use(self, response) -> Optional[dict]:
        """
        Extract tool use from Claude's response.

        When Claude decides to use a tool, it returns a tool_use block.
        This method extracts that information for the agent to act on.

        CRITICAL FOR AGENT REASONING LOOP:
        This is the key decision point:
        - If tool_use is found: agent should execute the tool and loop
        - If tool_use is None: agent should return the text answer

        THE DECISION LOGIC:
        >>> response = client.create_message(...)
        >>> tool_use = client.extract_tool_use(response)
        >>> if tool_use:
        ...     # Claude decided to use a tool
        ...     result = execute_tool(tool_use["name"], tool_use["input"])
        ...     # Add result to conversation and loop
        ... else:
        ...     # Claude returned text - we have the answer
        ...     text = client.extract_text(response)
        ...     return text  # End the loop

        This pattern is the foundation of agent reasoning.

        WHAT IS TOOL USE:
        When Claude calls a tool, it provides:
        - name: which tool to call
        - id: unique identifier for this call (for tracking)
        - input: parameters for the tool

        Example tool_use dict:
        {
            "name": "analyze_tone",
            "id": "call_abc123",
            "input": {"text": "Hello there"}
        }

        REAL-WORLD FLOW:
        1. Agent: "Compose a professional email. Use analyze_tone tool."
        2. Claude: "I'll use analyze_tone first. <tool_use name=analyze_tone ...>"
        3. Agent: "OK, Claude wants to analyze tone. Let me execute."
        4. Agent executes: analyze_tone(text="Hello there")
        5. Agent adds result to conversation
        6. Agent calls create_message() again with the result
        7. Claude: "Tone is too casual. Now use check_grammar..."
        8. Repeat until Claude returns text answer

        Args:
            response: Response object from create_message()
                     This is the raw response from Claude API

        Returns:
            dict with keys: "name", "id", "input"
            or None if no tool was called

            When returned:
            {
                "name": str,  # Tool identifier
                "id": str,    # Unique call ID for tracking
                "input": dict # Parameters for the tool
            }

        Example:
            >>> client = LLMClient(api_key="sk-...")
            >>> # In the agent's reasoning loop:
            >>> response = client.create_message(...)
            >>> tool_use = client.extract_tool_use(response)
            >>> if tool_use:
            ...     print(f"Claude wants to use: {tool_use['name']}")
            ...     print(f"With input: {tool_use['input']}")
            ...     # Execute the tool
            ...     result = get_tool(tool_use["name"]).execute(tool_use["input"])
            ...     # Add result to conversation and loop
            ... else:
            ...     # No tool use, get the text answer
            ...     text = client.extract_text(response)
            ...     return text  # Agent is done

        DESIGN NOTE:
        We return a dict instead of the raw block object because:
        - Simpler for callers to work with
        - Hides API structure details
        - Can be easily extended if Claude API changes
        """
        # response.content is a list of content blocks
        # We iterate through to find tool_use blocks

        for block in response.content:
            # Check if this block is a tool use
            # Tool use blocks have type == "tool_use"
            if block.type == "tool_use":
                # Found a tool use block - extract its details
                # Return as dict with name, id, input
                # (Don't include the raw block object - keep it simple)
                return {
                    "name": block.name,  # Tool identifier (e.g., "analyze_tone")
                    "id": block.id,      # Unique call ID for tracking
                    "input": block.input  # Parameters for the tool
                }

        # No tool use found
        # This is normal if Claude only returned text
        # Agent should extract text instead and end the loop
        return None
