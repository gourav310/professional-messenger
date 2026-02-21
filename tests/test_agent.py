"""
Tests for Agent and Tool classes.

This test module demonstrates the Agent and Tool foundational classes
for building reasoning systems in the Professional Messenger. These tests
follow a test-driven development (TDD) approach to guide implementation.

The tests cover:
- Agent initialization with name, system prompt, and tools
- Tool registration and management
- Tool schema format compatibility with Claude API
- Serialization for API communication

Tests are designed to be educational, showing how agent systems are
structured and tested for correctness.
"""

import pytest
from src.agent import Agent, Tool


class TestToolClass:
    """Tests for the Tool class that represents callable functions for agents."""

    def test_tool_initialization(self):
        """Tool should initialize with name, description, and input schema.

        A Tool represents a function or capability that an agent can invoke.
        It requires a name for identification, description for Claude to understand
        its purpose, and an input_schema defining the parameters it accepts.

        Example:
            A tool to analyze sentiment in text would have:
            - name: "analyze_sentiment"
            - description: "Analyzes the sentiment of text..."
            - input_schema: describing the text parameter
        """
        tool = Tool(
            name="analyze_tone",
            description="Analyze tone of text",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}}
        )

        assert tool.name == "analyze_tone"
        assert tool.description == "Analyze tone of text"
        assert "type" in tool.input_schema
        assert tool.handler is None  # handler is optional

    def test_tool_with_handler_function(self):
        """Tool can optionally include a handler function for execution.

        The handler is a Python callable that implements the tool's logic.
        This allows tools to be both described for Claude API use AND
        actually executed within the Python application.
        """
        def my_handler(text: str) -> str:
            """Example handler implementation."""
            return f"Handled: {text}"

        tool = Tool(
            name="test_tool",
            description="Test tool",
            input_schema={},
            handler=my_handler
        )

        assert tool.handler is not None
        assert callable(tool.handler)

    def test_tool_to_claude_format(self):
        """Tool should be convertible to Claude API format.

        Claude's API expects tools in a specific JSON schema format.
        The to_claude_format() method ensures our Tool objects can be
        serialized for API requests to Claude.

        Why this matters:
        - Claude needs tools as JSON objects with name, description, input_schema
        - This method bridges our Python Tool objects and the API format
        - Allows us to maintain clean Python code while staying API-compatible
        """
        tool = Tool(
            name="summarize",
            description="Summarize text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "length": {"type": "string", "enum": ["short", "long"]}
                },
                "required": ["text"]
            }
        )

        schema = tool.to_claude_format()

        # Verify the schema has all required Claude API fields
        assert schema["name"] == "summarize"
        assert schema["description"] == "Summarize text"
        assert "input_schema" in schema
        assert schema["input_schema"]["type"] == "object"


class TestAgentClass:
    """Tests for the Agent base class that orchestrates tool use."""

    def test_agent_initialization(self):
        """Agent should initialize with name, system prompt, and tools.

        An Agent is the core entity in our reasoning system. It requires:
        1. name: Unique identifier and identity
        2. system_prompt: Instructions defining behavior/personality
        3. tools: List of capabilities it can invoke

        Why this design:
        - name allows agents to identify themselves in a system
        - system_prompt guides the agent's decision-making (like a personality)
        - tools enable the agent to gather information and accomplish tasks

        Example:
            A tone analyzer agent might have:
            - name: "ToneAnalyzer"
            - system_prompt: "You analyze the emotional tone of messages..."
            - tools: [analyze_tone_tool, detect_sarcasm_tool]
        """
        tools = [
            Tool(
                name="analyze_tone",
                description="Analyze tone of text",
                input_schema={"type": "object", "properties": {"text": {"type": "string"}}}
            )
        ]

        agent = Agent(
            name="ToneAnalyzer",
            system_prompt="You analyze tone",
            tools=tools
        )

        assert agent.name == "ToneAnalyzer"
        assert agent.system_prompt == "You analyze tone"
        assert len(agent.tools) == 1
        assert agent.tools[0].name == "analyze_tone"

    def test_agent_initialization_with_no_tools(self):
        """Agent should initialize with empty tools list when none provided.

        Tools are optional at initialization - agents can be created and
        tools added later. This flexibility allows for building agents
        incrementally and composing them dynamically.
        """
        agent = Agent(
            name="EmptyAgent",
            system_prompt="An agent with no tools"
        )

        assert agent.name == "EmptyAgent"
        assert len(agent.tools) == 0
        assert isinstance(agent.tools, list)

    def test_agent_can_define_tools(self):
        """Agents should be able to define and register tools after creation.

        The add_tool() method enables dynamic tool registration. This allows:
        - Building agents incrementally
        - Composing agents from modular pieces
        - Creating tool hierarchies (agents with sub-agents)

        Why this pattern:
        - Tools might be created in different parts of code
        - Some tools might be optional or context-dependent
        - Supports composition and dependency injection patterns
        """
        agent = Agent(name="TestAgent", system_prompt="Test")

        assert len(agent.tools) == 0

        tool = Tool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"}
        )

        agent.add_tool(tool)

        assert len(agent.tools) == 1
        assert agent.tools[0].name == "test_tool"

    def test_agent_multiple_tools(self):
        """Agent should support multiple tools with different capabilities.

        Real agents need multiple tools to accomplish complex tasks.
        For example, a message composer agent needs:
        - Tone analyzer (understand emotional context)
        - Grammar checker (ensure correctness)
        - Structure organizer (format message)
        - Clarity enhancer (improve readability)

        This test verifies that agents can manage multiple tools.
        """
        tone_tool = Tool("tone", "Analyze tone", {})
        grammar_tool = Tool("grammar", "Check grammar", {})
        clarity_tool = Tool("clarity", "Enhance clarity", {})

        agent = Agent(
            name="Composer",
            system_prompt="Compose messages",
            tools=[tone_tool, grammar_tool, clarity_tool]
        )

        assert len(agent.tools) == 3
        tool_names = [t.name for t in agent.tools]
        assert "tone" in tool_names
        assert "grammar" in tool_names
        assert "clarity" in tool_names

    def test_agent_tool_schema_format(self):
        """Tool schema should be in Claude API format when retrieved.

        When we send tools to Claude's API, they must be in the correct format.
        The get_tools_for_api() method converts our Tool objects to the format
        Claude expects, handling all the serialization details.

        Why this matters:
        - Claude API expects JSON-serializable dictionaries
        - Our Tool objects need transformation before API use
        - This separation keeps our domain code clean and API-aware
        """
        tool = Tool(
            name="summarize",
            description="Summarize text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "length": {"type": "string", "enum": ["short", "long"]}
                },
                "required": ["text"]
            }
        )

        agent = Agent(
            name="Summarizer",
            system_prompt="Summarize text",
            tools=[tool]
        )

        api_tools = agent.get_tools_for_api()

        assert len(api_tools) == 1
        assert api_tools[0]["name"] == "summarize"
        assert api_tools[0]["description"] == "Summarize text"
        assert "input_schema" in api_tools[0]

    def test_agent_get_tools_for_api_empty(self):
        """Agent with no tools should return empty list for API.

        Even agents without tools should work correctly - they just
        can't invoke any functions. get_tools_for_api() should handle
        this gracefully.
        """
        agent = Agent(
            name="NoTools",
            system_prompt="Agent without tools"
        )

        api_tools = agent.get_tools_for_api()

        assert isinstance(api_tools, list)
        assert len(api_tools) == 0

    def test_agent_repr(self):
        """Agent should have readable string representation for debugging.

        The __repr__ method provides a clear, concise string representation
        useful for logging and debugging. It should show the agent's name
        and tool count at a glance.

        Example:
            An agent with 2 tools should print as: Agent(name=MyAgent, tools=2)
        """
        tools = [
            Tool("tool1", "Tool 1", {}),
            Tool("tool2", "Tool 2", {})
        ]

        agent = Agent(
            name="MyAgent",
            system_prompt="Test",
            tools=tools
        )

        repr_str = repr(agent)

        assert "MyAgent" in repr_str
        assert "2" in repr_str
        assert "Agent" in repr_str
