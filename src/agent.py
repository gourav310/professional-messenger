"""
Agent base classes for building reasoning systems.

This module provides the foundational classes for the Professional Messenger
agent system. It demonstrates key agent architecture concepts:

CORE CONCEPTS:
1. Tools: Represent functions/capabilities agents can invoke to accomplish tasks
2. Agents: Autonomous systems with identity and tools for reasoning
3. API Compatibility: Tools and agents serialize to formats Claude understands

DESIGN PHILOSOPHY:
This module teaches you how to structure AI agents. Rather than directly calling
Claude, agents use a tool-use pattern where Claude decides what to do and agents
execute the decisions. This separation of concerns makes agents:
- Testable: We can mock tool execution
- Composable: Agents can have sub-agents
- Controllable: We control what tools are available
- Verifiable: We can log and audit tool use

EDUCATIONAL NOTE:
This code is intentionally verbose with comments and docstrings to show best
practices. In production, some detail could be condensed, but clarity is
prioritized here for learning.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional
import json


@dataclass
class Tool:
    """
    Represents a tool or capability that an agent can use.

    In agent systems, tools are how agents interact with the world. A tool:
    - Has a name for identification
    - Has a description so Claude understands what it does
    - Has an input schema describing parameters
    - Optionally has a handler function for execution

    This design allows tools to be:
    1. Declared and sent to Claude for decision-making
    2. Actually executed in Python for real work
    3. Composed into agents with multiple capabilities

    REAL-WORLD EXAMPLE:
    In our Professional Messenger:
    - MessageComposerAgent has tools: analyze_tone, check_grammar, organize_structure
    - When processing a message, Claude decides which tools to call
    - Our Python code actually executes those tool calls
    - Results feed back to Claude for iterative improvement

    Attributes:
        name (str): Unique identifier for this tool (e.g., "analyze_tone").
                   Should be lowercase with underscores. Used in API calls.

        description (str): What this tool does, in human-readable format.
                          Claude reads this to understand the tool's purpose.
                          Should be clear and specific about inputs/outputs.

        input_schema (dict): JSON Schema defining what parameters the tool accepts.
                            Format: {"type": "object", "properties": {...}}
                            Claude uses this to generate valid input.
                            See: https://json-schema.org/

        handler (Callable, optional): Python function that implements this tool.
                                     Can be None if tool is only for API communication.
                                     When provided, agents can actually execute the tool.
                                     Signature: handler(**kwargs) -> Any

    Example:
        Create a tool to analyze text sentiment:

        >>> def analyze_sentiment_impl(text: str) -> str:
        ...     '''Actual implementation would call an API or ML model.'''
        ...     return "positive" if "love" in text else "neutral"
        ...
        >>> sentiment_tool = Tool(
        ...     name="analyze_sentiment",
        ...     description="Analyzes the emotional sentiment of provided text. "
        ...                  "Returns: positive, negative, or neutral.",
        ...     input_schema={
        ...         "type": "object",
        ...         "properties": {
        ...             "text": {
        ...                 "type": "string",
        ...                 "description": "The text to analyze"
        ...             }
        ...         },
        ...         "required": ["text"]
        ...     },
        ...     handler=analyze_sentiment_impl
        ... )
        >>> result = sentiment_tool.handler(text="I love this!")
        >>> print(result)  # Output: positive
    """

    name: str
    # Why name is str: Unique identifier for tool, used in API calls and lookups
    # Must be lowercase with underscores for API compatibility (snake_case)

    description: str
    # Why description is str: Claude reads this to understand tool purpose
    # Should be detailed enough that Claude knows when/how to use it

    input_schema: dict
    # Why input_schema is dict: JSON Schema format Claude expects
    # Defines structure of arguments the tool accepts
    # Examples: {"type": "object", "properties": {...}, "required": [...]}

    handler: Optional[Callable] = None
    # Why optional: Tool can be described for API without implementation
    # Useful for API-only scenarios or when handler is added later
    # If provided, must be callable and accept **kwargs matching schema properties

    def to_claude_format(self) -> dict:
        """
        Convert this Tool to Claude API format.

        PROBLEM THIS SOLVES:
        Claude's API has specific requirements for how tools must be formatted
        as JSON. This method bridges our Python Tool objects and the API format,
        handling serialization details transparently.

        WHY A SEPARATE METHOD:
        - Keeps Tool class focused on Python representation
        - Makes it clear what format Claude expects
        - Allows future formatting changes in one place
        - Enables validation of API format

        WHAT CLAUDE EXPECTS:
        Claude needs tools as JSON objects with exactly these fields:
        {
            "name": "tool_name",
            "description": "what it does",
            "input_schema": { JSON Schema object }
        }

        Returns:
            dict: Tool formatted exactly as Claude API expects.
                 Keys: "name", "description", "input_schema"
                 Values are JSON-serializable (can be converted to JSON string)

        Raises:
            None: Always succeeds - formats what we have

        Example:
            >>> tool = Tool(
            ...     name="summarize",
            ...     description="Summarize text",
            ...     input_schema={
            ...         "type": "object",
            ...         "properties": {"text": {"type": "string"}},
            ...         "required": ["text"]
            ...     }
            ... )
            >>> api_format = tool.to_claude_format()
            >>> print(api_format["name"])  # Output: summarize
            >>> # Can now JSON-encode: json.dumps(api_format)
        """
        # Create dict with Claude API format
        # Note: We DON'T include handler - that's Python-only, not for API
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }

    def __repr__(self) -> str:
        """
        String representation for debugging.

        Useful in logging and debugging to quickly see tool details.

        Example:
            >>> tool = Tool("test", "test tool", {})
            >>> print(tool)  # Output: Tool(name=test)
        """
        return f"Tool(name={self.name})"


class Agent:
    """
    Base agent class that defines core agent capabilities and structure.

    An Agent is an autonomous reasoning system that:
    1. Has an IDENTITY (name and system prompt)
    2. Has CAPABILITIES (tools it can invoke)
    3. Uses LOGIC to decide what to do

    CORE PATTERN:
    The Professional Messenger uses a hierarchical agent architecture:
    - MessageComposerAgent (primary, orchestrates others)
    - ToneAnalyzerAgent (specialized subagent)
    - GrammarAgent (specialized subagent)
    - ClarityAgent (specialized subagent)

    Each agent has:
    - Identity: What it is (name, system prompt)
    - Capabilities: What it can do (tools)
    - Reasoning: How it decides (via Claude API)

    DESIGN BENEFITS:
    - Modularity: Each agent handles one concern
    - Testability: Can test agents independently
    - Composability: Main agent coordinates sub-agents
    - Clarity: Code mirrors the reasoning structure

    REAL-WORLD FLOW:
    1. User gives MessageComposerAgent raw thoughts
    2. Agent thinks about the task (consulting system_prompt)
    3. Claude decides which tools to use (based on available tools)
    4. Agent calls those tools (through handlers)
    5. Results feed back to Claude for refinement
    6. Iterate until satisfied, return polished message

    Example - Professional Message Composition:

        >>> # Create an agent to compose professional emails
        >>> tone_tool = Tool(
        ...     name="analyze_tone",
        ...     description="Analyze emotional tone",
        ...     input_schema={"type": "object", ...}
        ... )
        >>> composer = Agent(
        ...     name="MessageComposer",
        ...     system_prompt='''You are a professional message composer.
        ...                      Your job is to transform raw thoughts into
        ...                      polished, professional messages that are
        ...                      clear, appropriate, and effective.''',
        ...     tools=[tone_tool]
        ... )
        >>> assert composer.name == "MessageComposer"
        >>> assert len(composer.tools) == 1

    Attributes:
        name (str): The agent's unique identifier and personality.
                   Examples: "MessageComposer", "ToneAnalyzer", "GrammarChecker"
                   Used for identification and debugging.

        system_prompt (str): Instructions telling Claude how to behave.
                            Acts like the agent's personality and guidelines.
                            Claude will follow these instructions when using
                            this agent. Should be detailed and specific.
                            Examples:
                            - "You compose professional emails..."
                            - "You analyze text tone to detect..."

        tools (list[Tool]): Capabilities this agent can access.
                           Each tool is a function/capability Claude can use.
                           Empty list means agent can only think, not act.
                           Tools are consulted in order (though order rarely matters).

    IMPORTANT CONCEPTS:

    System Prompt:
        The system_prompt is the MOST important attribute. It's what makes
        this agent different from others. Good system prompts:
        - Are specific about role and responsibility
        - Give examples of correct behavior
        - Mention tone and style expectations
        - Define success criteria

    Tools:
        Tools are how agents affect the world. Without tools:
        - Agent can only provide analysis/recommendations
        - Cannot gather new information
        - Cannot execute plans

        With tools:
        - Agent can research, analyze, plan, execute
        - Tool use creates the iterative loop
        - Claude chooses which tools to use (not us)

    Name:
        The name identifies this agent instance. Useful for:
        - Logging (shows which agent is doing what)
        - Configuration (specifying which agent to use)
        - Composition (coordinating multiple agents)
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[list[Tool]] = None
    ):
        """
        Initialize an Agent with identity and capabilities.

        WHAT HAPPENS:
        Creates a new agent with the provided configuration. The agent
        won't do anything until we interact with it (in later tasks),
        but this initialization sets it up for use.

        WHY THESE PARAMETERS:
        - name: Identifies the agent in logs and code
        - system_prompt: Instructions Claude follows (the agent's personality)
        - tools: Capabilities available to the agent

        Args:
            name (str): The agent's unique name.
                       Examples: "ToneAnalyzer", "MessageComposer"
                       Should be descriptive of the agent's role.

            system_prompt (str): Instructions for Claude.
                                Examples:
                                "You are a tone analyzer. Classify text as..."
                                "You are a message composer. Polish and improve..."

            tools (list[Tool], optional): Tools the agent can use.
                                         Defaults to empty list if not provided.
                                         Can be extended later with add_tool().

        Example:
            >>> assistant = Agent(
            ...     name="Helper",
            ...     system_prompt="You are a helpful assistant",
            ...     tools=[]
            ... )
            >>> assert assistant.name == "Helper"

        DESIGN NOTE:
        Tools default to None/empty list to allow flexibility:
        - Some agents may not need tools initially
        - Tools can be added after creation
        - Supports testing with minimal setup
        """
        # Store identity attributes
        self.name = name
        # Purpose: Identifies this agent instance
        # Usage: Logging, configuration, debugging

        self.system_prompt = system_prompt
        # Purpose: Instructions for Claude (agent personality)
        # Usage: Sent to Claude API as system message
        # Impact: Controls how agent thinks and behaves

        self.tools = tools or []
        # Purpose: Tools the agent can invoke
        # Usage: Sent to Claude to enable tool use
        # Design: Default to empty list if None provided

    def add_tool(self, tool: Tool) -> None:
        """
        Register a new tool for this agent.

        WHY THIS METHOD EXISTS:
        Allows tools to be added after agent creation. This enables:
        - Building agents incrementally
        - Dynamic tool composition
        - Dependency injection patterns
        - Conditional tool registration (only add if available)

        WHEN TO USE THIS:
        1. Adding tools after initialization:
           >>> agent = Agent("Composer", "compose messages")
           >>> agent.add_tool(my_tool)

        2. Building tools progressively:
           >>> for tool_config in all_available_tools:
           ...     if tool_config.is_enabled():
           ...         agent.add_tool(tool_config.create_tool())

        3. Conditional capabilities:
           >>> if has_api_access():
           ...     agent.add_tool(research_tool)

        Args:
            tool (Tool): The Tool object to register.
                        Must have name, description, input_schema.
                        Should be created before calling this method.

        Returns:
            None: Modifies agent in-place, doesn't return anything

        Raises:
            None: Always succeeds (no validation done here)

        Example:
            >>> agent = Agent("TestAgent", "Test", tools=[])
            >>> tone_tool = Tool("tone", "Analyze tone", {})
            >>> agent.add_tool(tone_tool)
            >>> assert len(agent.tools) == 1
            >>> assert agent.tools[0].name == "tone"
        """
        # Add tool to the agent's tool list
        self.tools.append(tool)
        # Simple implementation: just append to list
        # Could be extended later with:
        # - Validation (check for duplicate names)
        # - Logging (track tool registration)
        # - Ordering (maintain specific order)

    def get_tools_for_api(self) -> list[dict]:
        """
        Get all tools formatted for Claude API use.

        PROBLEM THIS SOLVES:
        When we send a request to Claude, we need tools in a specific format.
        This method handles converting our Tool objects to what Claude expects,
        centralizing serialization logic in one place.

        WHY A SEPARATE METHOD:
        - Tool.to_claude_format() handles individual tools
        - This method coordinates multiple tools
        - Makes it clear what's sent to the API
        - Enables future transformations (filtering, sorting)

        WHAT IT RETURNS:
        A list of dictionaries in Claude API format:
        [
            {
                "name": "tool_name",
                "description": "what it does",
                "input_schema": { JSON Schema }
            },
            ...
        ]

        WHEN IT'S USED:
        When sending requests to Claude's API, we do:
        >>> agent = Agent("Composer", "compose", tools=[...])
        >>> client.messages.create(
        ...     model="claude-opus-4-6",
        ...     system=agent.system_prompt,
        ...     tools=agent.get_tools_for_api(),  # <-- Used here
        ...     messages=[...]
        ... )

        Returns:
            list[dict]: All tools formatted for Claude API.
                       Empty list if agent has no tools.
                       Each dict has keys: name, description, input_schema

        Example:
            >>> tool1 = Tool("analyze", "Analyze text", {})
            >>> tool2 = Tool("summarize", "Summarize text", {})
            >>> agent = Agent("Analyzer", "analyze", tools=[tool1, tool2])
            >>> api_tools = agent.get_tools_for_api()
            >>> assert len(api_tools) == 2
            >>> assert api_tools[0]["name"] == "analyze"
            >>> # Can now JSON-serialize: json.dumps(api_tools)
        """
        # Use list comprehension to convert each tool
        # For each Tool object, call its to_claude_format() method
        # Returns a new list of dictionaries in API format
        return [tool.to_claude_format() for tool in self.tools]

    def __repr__(self) -> str:
        """
        String representation for debugging and logging.

        WHAT IT SHOWS:
        A concise one-line representation showing:
        - Agent name (who this is)
        - Number of tools (what it can do)

        WHY THIS FORMAT:
        When you print an agent in logs or REPL, you want to quickly see:
        1. What agent is this? (name)
        2. Is it capable? (tool count)

        Example:
            >>> agent = Agent("Composer", "compose",
            ...               tools=[Tool("t1", "d1", {}), Tool("t2", "d2", {})])
            >>> print(agent)
            # Output: Agent(name=Composer, tools=2)

            >>> print(repr(agent))
            # Output: Agent(name=Composer, tools=2)

        Returns:
            str: Human-readable representation for debugging
        """
        # Format: Agent(name=<name>, tools=<count>)
        # Example: Agent(name=MessageComposer, tools=3)
        return f"Agent(name={self.name}, tools={len(self.tools)})"
