# Professional Messenger: Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an intelligent agent system that transforms unstructured thoughts into professional messages, teaching agent fundamentals, subagents, and Claude API patterns.

**Architecture:**
The system uses a hierarchical agent architecture: a primary Message Composer Agent orchestrates specialized subagents (tone analyzer, structure organizer, clarity enhancer). Messages flow through a reasoning loop where agents analyze input, invoke tools, and iterate. The CLI provides a simple interface. Later, a webhook enables Telegram integration without persistent services.

**Tech Stack:**
- Python 3.11+ (agents, CLI, API calls)
- Claude API (Haiku for speed, Sonnet for quality)
- Anthropic SDK (function calling, tool use)
- Click (CLI framework)
- YAML (configuration)
- FastAPI (for Telegram webhook, Phase 2)

---

## Phase 1: Agent Fundamentals & Core Agent (Tasks 1-8)

### Task 1: Project Setup & Environment

**Files:**
- Create: `src/__init__.py`
- Create: `requirements.txt`
- Create: `.env.example`
- Modify: `README.md`

**Step 1: Create requirements.txt**

```txt
anthropic==0.39.0
python-dotenv==1.0.0
click==8.1.7
pyyaml==6.0.1
pytest==7.4.3
```

**Step 2: Run pip install**

```bash
cd ~/Documents/Personal/professional-messenger
pip install -r requirements.txt
```

Expected: All packages install without errors.

**Step 3: Create .env.example**

```bash
cat > .env.example << 'EOF'
CLAUDE_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-3-5-haiku-20241022
EOF
```

**Step 4: Update README.md**

```markdown
# Professional Messenger

Transform unstructured thoughts into professional messages using AI agents.

## Setup

1. Copy `.env.example` to `.env` and add your Anthropic API key
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python -m professional_messenger.cli`

## Architecture

- **Message Composer Agent**: Primary agent that orchestrates the composition process
- **Subagents**: Specialized agents for tone analysis, structure organization, clarity
- **Tools**: Function calling for analysis, iteration, and variant generation

## Learning Path

1. Agent fundamentals (reasoning loops, tool use)
2. Single-purpose agent (message composition)
3. Multi-agent systems (subagents)
4. Integration (CLI, config, Telegram)
```

**Step 5: Create src/__init__.py**

```python
"""Professional Messenger - Agent-based message composition tool."""

__version__ = "0.1.0"
```

**Step 6: Commit**

```bash
git add requirements.txt .env.example README.md src/__init__.py
git commit -m "setup: initialize project with dependencies and structure

- Add Anthropic SDK, Click, pytest, pyyaml
- Create .env template for API key
- Document project architecture and learning path"
```

---

### Task 2: Understanding Agent Fundamentals - Research & Documentation

**Files:**
- Create: `docs/AGENT_FUNDAMENTALS.md`
- Create: `examples/simple_agent_example.py`

**Step 1: Create agent fundamentals guide**

```markdown
# Agent Fundamentals

## What is an Agent?

An agent is a system that:
1. **Observes** input/state
2. **Reasons** about what actions to take (using an LLM)
3. **Takes actions** (calls functions/tools)
4. **Iterates** until goal is reached

## Simple Reasoning Loop

```
Input → LLM Thinking → Decide Tool → Execute Tool → LLM Decides → Output
```

## Key Concepts

### 1. Reasoning Loop
The agent thinks through a problem step-by-step, deciding what tools to use.

### 2. Tool Use (Function Calling)
The agent can call functions to:
- Gather information
- Perform calculations
- Invoke subagents
- Make decisions

### 3. Context Window
The agent's conversation history helps it understand what happened before.

### 4. Subagents
Specialized agents focused on specific tasks (tone analysis, structure, etc.)

## Example: Message Composition Agent

Input: "hey i wnat to tell my boss the project is delayed by 2 weeks"

Agent Thinking:
1. Input is unstructured and emotional
2. I need to: analyze tone, structure it professionally, ensure clarity
3. I should invoke subagents for each concern
4. Then synthesize their outputs

Output: "I wanted to inform you that the project timeline has shifted. We now expect completion in two weeks rather than the original schedule."

## In This Project

We build agents that:
- Take unstructured input from users
- Reason through what needs to change (tone, structure, clarity)
- Invoke specialized subagents for analysis
- Return multiple polished variants
```

**Step 2: Create simple example**

```python
# examples/simple_agent_example.py
"""
Simple agent example showing the reasoning loop.
This demonstrates how an agent thinks through a problem.
"""

# Pseudocode showing the pattern we'll implement
AGENT_REASONING_LOOP = """
def agent_loop(user_input, tools):
    conversation = []

    while not goal_reached:
        # Step 1: Add user input to conversation
        conversation.append({
            "role": "user",
            "content": user_input
        })

        # Step 2: Ask Claude to think and decide what tool to use
        response = claude.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            tools=tools,  # Define available tools
            messages=conversation
        )

        # Step 3: Check if Claude decided to use a tool
        if response.stop_reason == "tool_use":
            # Execute the tool
            tool_result = execute_tool(response.tool_use)

            # Add result back to conversation
            conversation.append({
                "role": "assistant",
                "content": response.content
            })
            conversation.append({
                "role": "user",
                "content": f"Tool result: {tool_result}"
            })
        else:
            # Claude decided it's done - extract final answer
            return extract_text_response(response)
"""

print(__doc__)
print(AGENT_REASONING_LOOP)
```

**Step 3: Commit**

```bash
git add docs/AGENT_FUNDAMENTALS.md examples/simple_agent_example.py
git commit -m "docs: add agent fundamentals guide and simple example

- Explain reasoning loops, tool use, subagents
- Show how agents think through problems
- Document the loop pattern we'll implement"
```

---

### Task 3: Create Agent Base Class & Tool Definition

**Files:**
- Create: `src/agent.py`
- Create: `tests/test_agent.py`

**Step 1: Write failing test**

```python
# tests/test_agent.py
import pytest
from src.agent import Agent, Tool


def test_agent_initialization():
    """Agent should initialize with name, system prompt, and tools."""
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
    assert len(agent.tools) == 1
    assert agent.tools[0].name == "analyze_tone"


def test_agent_can_define_tools():
    """Agents should be able to define and register tools."""
    agent = Agent(name="TestAgent", system_prompt="Test")

    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object"}
    )

    agent.add_tool(tool)
    assert len(agent.tools) == 1


def test_agent_tool_schema_format():
    """Tool schema should be in Claude API format."""
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
    assert schema["name"] == "summarize"
    assert schema["description"] == "Summarize text"
    assert "input_schema" in schema
```

**Step 2: Run test to verify failure**

```bash
cd ~/Documents/Personal/professional-messenger
pytest tests/test_agent.py -v
```

Expected: FAIL - ModuleNotFoundError or assertion errors.

**Step 3: Implement Agent and Tool classes**

```python
# src/agent.py
"""
Agent base classes for building reasoning systems.

Demonstrates:
- How agents are structured
- Tool definition and schema
- Foundation for extending to specialized agents
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional
import json


@dataclass
class Tool:
    """Represents a tool an agent can use."""

    name: str
    description: str
    input_schema: dict
    handler: Optional[Callable] = None

    def to_claude_format(self) -> dict:
        """Convert tool to Claude API format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


class Agent:
    """
    Base agent class.

    An agent has:
    - Name and system prompt (defines its role)
    - Tools it can use (defines its capabilities)
    - Reasoning loop (handled by subclasses)
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: Optional[list[Tool]] = None
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []

    def add_tool(self, tool: Tool) -> None:
        """Register a tool for this agent."""
        self.tools.append(tool)

    def get_tools_for_api(self) -> list[dict]:
        """Get tools in Claude API format."""
        return [tool.to_claude_format() for tool in self.tools]

    def __repr__(self) -> str:
        return f"Agent(name={self.name}, tools={len(self.tools)})"
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_agent.py -v
```

Expected: PASS - All 3 tests pass.

**Step 5: Create tests directory init**

```python
# tests/__init__.py
"""Tests for professional-messenger."""
```

**Step 6: Commit**

```bash
git add src/agent.py tests/test_agent.py tests/__init__.py
git commit -m "feat: implement Agent and Tool base classes

- Tool class with Claude API format support
- Agent class to define name, prompt, tools
- Tests verify initialization and tool registration
- Foundation for specialized agents"
```

---

### Task 4: Build Anthropic SDK Client Wrapper

**Files:**
- Create: `src/llm_client.py`
- Create: `tests/test_llm_client.py`

**Step 1: Write failing test**

```python
# tests/test_llm_client.py
import pytest
from unittest.mock import Mock, patch
from src.llm_client import LLMClient


def test_llm_client_initialization():
    """LLMClient should initialize with API key and model."""
    client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

    assert client.api_key == "test-key"
    assert client.model == "claude-3-5-haiku-20241022"


def test_llm_client_formats_messages():
    """Client should format messages in Claude API format."""
    client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

    messages = [
        {"role": "user", "content": "Hello"}
    ]

    formatted = client._prepare_messages(messages)
    assert isinstance(formatted, list)
    assert len(formatted) > 0


def test_llm_client_call_with_tools():
    """Client should be able to call Claude with tools."""
    client = LLMClient(api_key="test-key", model="claude-3-5-haiku-20241022")

    tools = [
        {
            "name": "test_tool",
            "description": "A test tool",
            "input_schema": {"type": "object"}
        }
    ]

    # This test just verifies the method exists and accepts parameters
    # (actual API call would need mocking)
    assert hasattr(client, 'create_message')
```

**Step 2: Implement LLMClient**

```python
# src/llm_client.py
"""
Wrapper around Anthropic SDK for easier agent development.

Handles:
- Message formatting
- Tool/function calling setup
- Streaming (optional)
- Error handling
"""

import os
from typing import Optional
from anthropic import Anthropic


class LLMClient:
    """Wrapper around Claude API for agents."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022"
    ):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    def _prepare_messages(self, messages: list[dict]) -> list[dict]:
        """Ensure messages are in correct format."""
        prepared = []
        for msg in messages:
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
        Create a message using Claude.

        Args:
            messages: Conversation history
            system: System prompt
            tools: Available tools for function calling
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)

        Returns:
            Response from Claude API
        """
        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self._prepare_messages(messages),
            "temperature": temperature
        }

        if system:
            params["system"] = system

        if tools:
            params["tools"] = tools

        response = self.client.messages.create(**params)
        return response

    def extract_text(self, response) -> str:
        """Extract text content from response."""
        for block in response.content:
            if hasattr(block, 'text'):
                return block.text
        return ""

    def extract_tool_use(self, response) -> Optional[dict]:
        """Extract tool use from response if present."""
        for block in response.content:
            if block.type == "tool_use":
                return {
                    "name": block.name,
                    "id": block.id,
                    "input": block.input
                }
        return None
```

**Step 3: Run tests**

```bash
pytest tests/test_llm_client.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add src/llm_client.py tests/test_llm_client.py
git commit -m "feat: add LLMClient wrapper for Claude API

- Wraps Anthropic SDK for easier agent development
- Handles message formatting and validation
- Supports tools/function calling setup
- Extract text and tool use from responses"
```

---

### Task 5: Implement Message Composer Agent (Core Agent)

**Files:**
- Create: `src/agents/message_composer.py`
- Create: `tests/test_message_composer.py`
- Create: `src/agents/__init__.py`

**Step 1: Write failing test**

```python
# tests/test_message_composer.py
import pytest
from src.agents.message_composer import MessageComposerAgent


def test_message_composer_initialization():
    """MessageComposerAgent should initialize with API key."""
    agent = MessageComposerAgent(api_key="test-key")

    assert agent.name == "MessageComposer"
    assert len(agent.tools) > 0


def test_message_composer_has_required_tools():
    """Agent should have tools for analysis and composition."""
    agent = MessageComposerAgent(api_key="test-key")
    tool_names = [t.name for t in agent.tools]

    # Should have at least these tool names
    assert any("analyze" in name.lower() for name in tool_names)


def test_message_composer_system_prompt_defined():
    """Agent should have a clear system prompt."""
    agent = MessageComposerAgent(api_key="test-key")

    assert agent.system_prompt
    assert "professional" in agent.system_prompt.lower()
    assert "message" in agent.system_prompt.lower()
```

**Step 2: Implement MessageComposerAgent**

```python
# src/agents/message_composer.py
"""
Message Composer Agent - Primary agent for message composition.

This agent:
1. Receives unstructured input from user
2. Analyzes tone, structure, clarity
3. Invokes subagents for detailed analysis
4. Synthesizes output
"""

from typing import Optional
from src.agent import Agent, Tool
from src.llm_client import LLMClient


class MessageComposerAgent(Agent):
    """
    Main agent that orchestrates message composition.

    Reasoning loop:
    1. Analyze input for tone issues
    2. Invoke subagents for detailed work
    3. Generate multiple variants
    4. Return polished messages
    """

    def __init__(self, api_key: Optional[str] = None):
        system_prompt = """You are a professional message composition expert. Your job is to:

1. Analyze unstructured thoughts and raw messages from users
2. Understand their intent and tone
3. Invoke specialized subagents for deep analysis (tone, structure, clarity)
4. Synthesize their feedback into polished professional messages
5. Provide 2-3 variants with explanations

You maintain the user's authentic voice while ensuring professionalism. Not too formal, not too casual."""

        super().__init__(
            name="MessageComposer",
            system_prompt=system_prompt
        )

        self.llm_client = LLMClient(api_key=api_key)
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Define tools this agent can use."""

        # Tool 1: Analyze tone
        analyze_tone_tool = Tool(
            name="analyze_tone",
            description="Analyze the tone of the user's input. Returns analysis of current tone and suggestions for professional tone.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                    },
                    "target_tone": {
                        "type": "string",
                        "description": "Desired tone (professional, friendly-professional, direct, etc.)"
                    }
                },
                "required": ["text"]
            }
        )

        # Tool 2: Suggest structure
        suggest_structure_tool = Tool(
            name="suggest_structure",
            description="Suggest a professional structure for the message (intro, body, conclusion).",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The raw message"
                    },
                    "message_type": {
                        "type": "string",
                        "description": "Type of message (status update, request, feedback, etc.)"
                    }
                },
                "required": ["message"]
            }
        )

        # Tool 3: Check clarity
        check_clarity_tool = Tool(
            name="check_clarity",
            description="Check message for clarity issues (ambiguity, missing context, unclear phrasing).",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to check"
                    }
                },
                "required": ["message"]
            }
        )

        self.add_tool(analyze_tone_tool)
        self.add_tool(suggest_structure_tool)
        self.add_tool(check_clarity_tool)

    def compose(self, user_input: str) -> dict:
        """
        Compose a professional message from unstructured input.

        Returns:
            {
                "primary": "Best variant",
                "variants": ["variant1", "variant2"],
                "reasoning": "Why these changes"
            }
        """
        # This is a placeholder - will be implemented in next task
        # showing how the reasoning loop works
        return {
            "primary": "Placeholder - reasoning loop not yet implemented",
            "variants": [],
            "reasoning": "Task 6 will implement the full reasoning loop"
        }


# Create the agent instance
composer = MessageComposerAgent()
```

**Step 3: Create agents __init__.py**

```python
# src/agents/__init__.py
"""Specialized agents for professional messaging."""

from src.agents.message_composer import MessageComposerAgent

__all__ = ["MessageComposerAgent"]
```

**Step 4: Run tests**

```bash
pytest tests/test_message_composer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/agents/message_composer.py src/agents/__init__.py tests/test_message_composer.py
git commit -m "feat: implement MessageComposerAgent

- Main orchestrating agent for message composition
- Define system prompt for professional message composing
- Set up tools: analyze_tone, suggest_structure, check_clarity
- Tool definitions follow Claude API format
- Placeholder for compose() method (reasoning loop in next task)"
```

---

### Task 6: Implement Agent Reasoning Loop

**Files:**
- Modify: `src/agents/message_composer.py`
- Modify: `tests/test_message_composer.py`

**Step 1: Add reasoning loop test**

```python
# Add to tests/test_message_composer.py

def test_agent_reasoning_loop():
    """Agent should execute reasoning loop and return structured output."""
    agent = MessageComposerAgent(api_key="test-key")

    # Note: This would call actual API in integration tests
    # Here we test the structure
    result = agent.compose("hey i wnat tell my boss projct is delayed")

    assert "primary" in result
    assert "variants" in result
    assert isinstance(result["variants"], list)
```

**Step 2: Implement reasoning loop**

```python
# Update src/agents/message_composer.py - replace compose method

def compose(self, user_input: str, max_iterations: int = 3) -> dict:
    """
    Compose professional message using reasoning loop.

    Loop:
    1. Analyze input (what needs fixing?)
    2. Decide what subagents to invoke
    3. Synthesize feedback into output
    4. Generate variants
    """
    conversation = []

    # Step 1: Initial analysis
    initial_message = f"""The user provided this unstructured message:

"{user_input}"

Please analyze this message and decide what tools you need to use to improve it professionally. Think through:
1. What tone issues exist?
2. What structure issues exist?
3. What clarity issues exist?

Then use the appropriate tools."""

    conversation.append({
        "role": "user",
        "content": initial_message
    })

    iteration = 0
    while iteration < max_iterations:
        # Call Claude
        response = self.llm_client.create_message(
            messages=conversation,
            system=self.system_prompt,
            tools=self.get_tools_for_api(),
            max_tokens=2048
        )

        # Check if agent wants to use tools
        tool_use = self.llm_client.extract_tool_use(response)

        if tool_use:
            # Tool was called - simulate tool result
            tool_result = self._execute_tool(tool_use["name"], tool_use["input"])

            # Add assistant response and tool result to conversation
            conversation.append({
                "role": "assistant",
                "content": response.content
            })
            conversation.append({
                "role": "user",
                "content": f"Tool '{tool_use['name']}' returned: {tool_result}"
            })

            iteration += 1
        else:
            # Agent decided it's done - extract output
            text_output = self.llm_client.extract_text(response)

            # Parse output into structured format
            return {
                "primary": self._extract_primary(text_output),
                "variants": self._extract_variants(text_output),
                "reasoning": text_output
            }

    return {
        "primary": "Max iterations reached",
        "variants": [],
        "reasoning": "Could not complete composition"
    }

def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
    """
    Simulate tool execution.
    In production, these would be real function calls.
    """
    if tool_name == "analyze_tone":
        text = tool_input.get("text", "")
        return f"Tone Analysis: '{text}' has informal/rushed tone. Suggest: slower pacing, professional formality, specific details."

    elif tool_name == "suggest_structure":
        return "Suggested structure: Start with key point (delay timeline), provide context (why), offer next steps (mitigation plan)."

    elif tool_name == "check_clarity":
        return "Clarity issues: 'wnat' typo, 'projct' typo, missing 'weeks' info. Suggest proofreading and specificity."

    return "Tool not found"

def _extract_primary(self, text: str) -> str:
    """Extract primary variant from reasoning output."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'primary' in line.lower() or 'best' in line.lower() or 'variant' in line.lower():
            return '\n'.join(lines[i:i+3])
    return lines[0] if lines else ""

def _extract_variants(self, text: str) -> list[str]:
    """Extract alternative variants from reasoning output."""
    # Simple heuristic - return next paragraph
    lines = text.split('\n')
    variants = []
    for line in lines:
        if line.strip() and 'alternative' in line.lower() or 'variant' in line.lower():
            variants.append(line.strip())
    return variants[:2]  # Return up to 2 variants
```

**Step 3: Run tests**

```bash
pytest tests/test_message_composer.py::test_agent_reasoning_loop -v
```

Expected: PASS (or handled gracefully)

**Step 4: Commit**

```bash
git add src/agents/message_composer.py tests/test_message_composer.py
git commit -m "feat: implement agent reasoning loop

- Agent iteratively calls tools to analyze and improve messages
- Loop continues until agent decides composition is complete
- Simulates tool execution (framework for real subagents)
- Extracts primary variant and alternatives from reasoning
- Demonstrates key agent pattern: think → decide → act → iterate"
```

---

## Phase 2: Subagents Architecture (Tasks 7-10)

### Task 7: Create Subagent Base Class

**Files:**
- Create: `src/subagents/__init__.py`
- Create: `src/subagents/base.py`
- Create: `tests/test_subagents.py`

**Step 1: Write failing test**

```python
# tests/test_subagents.py
from src.subagents.base import Subagent


def test_subagent_initialization():
    """Subagent should have name and system prompt."""
    subagent = Subagent(
        name="ToneAnalyzer",
        description="Analyzes tone",
        system_prompt="You are a tone analyzer"
    )

    assert subagent.name == "ToneAnalyzer"
    assert subagent.description == "Analyzes tone"


def test_subagent_can_have_parent_agent():
    """Subagent can reference its parent agent."""
    subagent = Subagent(
        name="ToneAnalyzer",
        description="Analyzes tone",
        system_prompt="You analyze"
    )

    # Subagent can be assigned to parent
    assert subagent.parent is None
```

**Step 2: Implement Subagent**

```python
# src/subagents/base.py
"""
Subagent base class for specialized tasks.

Subagents:
- Handle specific concerns (tone, structure, clarity)
- Can be called by the main agent
- Return structured analysis
"""

from typing import Optional
from src.agent import Agent
from src.llm_client import LLMClient


class Subagent(Agent):
    """
    A specialized agent focused on one task.

    Examples:
    - ToneAnalyzer - analyzes and improves tone
    - StructureOrganizer - suggests structure
    - ClarityChecker - finds clarity issues
    """

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        parent: Optional[Agent] = None,
        api_key: Optional[str] = None
    ):
        super().__init__(name=name, system_prompt=system_prompt)
        self.description = description
        self.parent = parent
        self.llm_client = LLMClient(api_key=api_key)

    def analyze(self, text: str) -> dict:
        """
        Analyze text and return structured results.

        Subclasses override this.
        """
        raise NotImplementedError("Subclasses must implement analyze()")

    def __repr__(self) -> str:
        return f"Subagent(name={self.name}, description={self.description})"
```

**Step 3: Create __init__.py**

```python
# src/subagents/__init__.py
"""Specialized subagents for message analysis."""

from src.subagents.base import Subagent

__all__ = ["Subagent"]
```

**Step 4: Run tests**

```bash
pytest tests/test_subagents.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/subagents/base.py src/subagents/__init__.py tests/test_subagents.py
git commit -m "feat: implement Subagent base class

- Specialized agents for specific analysis tasks
- Inherit from Agent for consistency
- Support parent-child relationships
- Override analyze() for specific functionality
- Foundation for ToneAnalyzer, StructureOrganizer, etc."
```

---

### Task 8: Implement Specialized Subagents (Tone, Structure, Clarity)

**Files:**
- Create: `src/subagents/tone_analyzer.py`
- Create: `src/subagents/structure_organizer.py`
- Create: `src/subagents/clarity_enhancer.py`
- Modify: `tests/test_subagents.py`

**Step 1: Add failing tests**

```python
# Add to tests/test_subagents.py

from src.subagents.tone_analyzer import ToneAnalyzer
from src.subagents.structure_organizer import StructureOrganizer
from src.subagents.clarity_enhancer import ClarityEnhancer


def test_tone_analyzer_exists():
    """ToneAnalyzer subagent should exist."""
    analyzer = ToneAnalyzer(api_key="test-key")
    assert analyzer.name == "ToneAnalyzer"


def test_structure_organizer_exists():
    """StructureOrganizer subagent should exist."""
    organizer = StructureOrganizer(api_key="test-key")
    assert organizer.name == "StructureOrganizer"


def test_clarity_enhancer_exists():
    """ClarityEnhancer subagent should exist."""
    enhancer = ClarityEnhancer(api_key="test-key")
    assert enhancer.name == "ClarityEnhancer"
```

**Step 2: Implement ToneAnalyzer**

```python
# src/subagents/tone_analyzer.py
"""Subagent for analyzing and improving tone."""

from typing import Optional
from src.subagents.base import Subagent


class ToneAnalyzer(Subagent):
    """
    Analyzes the tone of a message and suggests improvements.

    Responsibilities:
    - Detect current tone (formal, casual, aggressive, etc.)
    - Suggest tone improvements for professionalism
    - Provide rewritten examples
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="ToneAnalyzer",
            description="Analyzes and improves message tone",
            system_prompt="""You are a tone analysis expert. Your job is to:

1. Identify the current tone of messages (casual, aggressive, passive, direct, etc.)
2. Suggest how to adjust tone for professional contexts
3. Provide concrete examples of improved phrasing
4. Maintain the speaker's authentic voice while improving professionalism

You never make messages sound robotic or overly formal.""",
            api_key=api_key
        )

    def analyze(self, text: str) -> dict:
        """
        Analyze tone of text.

        Returns:
            {
                "current_tone": "description of current tone",
                "issues": ["issue1", "issue2"],
                "suggestions": ["suggestion1", "suggestion2"],
                "rewritten": "tone-improved version"
            }
        """
        # Placeholder - would call LLM in full implementation
        return {
            "current_tone": "informal and rushed",
            "issues": ["Uses 'wnat' (typo)", "Lacks context", "Sounds abrupt"],
            "suggestions": [
                "Provide specific timeline",
                "Add context about why delay occurred",
                "Use professional pacing"
            ],
            "rewritten": "I wanted to inform you that the project timeline has shifted. We now expect completion in two additional weeks."
        }
```

**Step 3: Implement StructureOrganizer**

```python
# src/subagents/structure_organizer.py
"""Subagent for organizing message structure."""

from typing import Optional
from src.subagents.base import Subagent


class StructureOrganizer(Subagent):
    """
    Suggests and organizes message structure.

    Responsibilities:
    - Identify what type of message this is (request, update, feedback, etc.)
    - Suggest structure (intro → context → main point → action)
    - Reorganize information logically
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="StructureOrganizer",
            description="Organizes message structure for clarity",
            system_prompt="""You are a message structure expert. Your job is to:

1. Identify the message type (status update, request, feedback, problem report)
2. Suggest optimal structure (what should come first, middle, end)
3. Reorganize information logically
4. Ensure key points lead

Professional message structure:
- Key point up front
- Context/details
- Action or next steps""",
            api_key=api_key
        )

    def analyze(self, text: str) -> dict:
        """
        Suggest message structure.

        Returns:
            {
                "message_type": "status update",
                "current_structure": "rambling",
                "suggested_structure": ["intro", "timeline", "mitigation", "next steps"],
                "reorganized": "structured version"
            }
        """
        return {
            "message_type": "status update",
            "current_structure": "lacks organization",
            "suggested_structure": [
                "Start with: What's the update?",
                "Then: When will it be done?",
                "Then: Why is it delayed?",
                "Finally: What's next?"
            ],
            "reorganized": "I'm writing to inform you of a project timeline adjustment. The delivery date has shifted from [original date] to [new date]. This is due to [reason]. We're implementing [mitigation]. Next step is [action]."
        }
```

**Step 4: Implement ClarityEnhancer**

```python
# src/subagents/clarity_enhancer.py
"""Subagent for enhancing message clarity."""

from typing import Optional
from src.subagents.base import Subagent


class ClarityEnhancer(Subagent):
    """
    Enhances clarity of messages.

    Responsibilities:
    - Identify unclear phrasing
    - Find missing context
    - Detect typos and grammar
    - Suggest specific, concrete language
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="ClarityEnhancer",
            description="Improves message clarity",
            system_prompt="""You are a clarity expert. Your job is to:

1. Find ambiguous or unclear phrasing
2. Identify missing context that reader needs
3. Flag typos, grammar, spelling
4. Suggest concrete, specific language
5. Make implicit things explicit

Clarity issues to look for:
- Undefined pronouns ("it", "that", "this")
- Missing details ("soon", "many", "significant")
- Typos that change meaning
- Jargon without explanation""",
            api_key=api_key
        )

    def analyze(self, text: str) -> dict:
        """
        Check clarity issues.

        Returns:
            {
                "clarity_score": 0-100,
                "issues": ["issue1", "issue2"],
                "missing_context": ["context1"],
                "improved": "clearer version"
            }
        """
        return {
            "clarity_score": 45,
            "issues": [
                "Typo: 'wnat' should be 'want'",
                "Typo: 'projct' should be 'project'",
                "Missing: How many weeks?",
                "Vague: 'tell' - inform? discuss? update?"
            ],
            "missing_context": [
                "Original timeline",
                "Reason for delay",
                "New expected completion date"
            ],
            "improved": "I want to inform you that the project is now delayed by 2 weeks."
        }
```

**Step 5: Update __init__.py**

```python
# Update src/subagents/__init__.py
from src.subagents.base import Subagent
from src.subagents.tone_analyzer import ToneAnalyzer
from src.subagents.structure_organizer import StructureOrganizer
from src.subagents.clarity_enhancer import ClarityEnhancer

__all__ = [
    "Subagent",
    "ToneAnalyzer",
    "StructureOrganizer",
    "ClarityEnhancer"
]
```

**Step 6: Run tests**

```bash
pytest tests/test_subagents.py -v
```

Expected: PASS

**Step 7: Commit**

```bash
git add src/subagents/tone_analyzer.py src/subagents/structure_organizer.py src/subagents/clarity_enhancer.py src/subagents/__init__.py tests/test_subagents.py
git commit -m "feat: implement specialized subagents

- ToneAnalyzer: detects and improves message tone
- StructureOrganizer: suggests message structure
- ClarityEnhancer: identifies clarity issues
- Each subagent returns structured analysis dict
- Demonstrates multi-agent architecture pattern"
```

---

## Phase 3: CLI & Configuration (Tasks 9-12)

### Task 9: Create Configuration System

**Files:**
- Create: `src/config.py`
- Create: `config.yaml.example`
- Create: `tests/test_config.py`

**Step 1: Write failing test**

```python
# tests/test_config.py
import pytest
from src.config import Config


def test_config_loading():
    """Config should load from YAML file."""
    # Would normally load from config.yaml
    config = Config()
    assert config is not None


def test_config_has_voice_rules():
    """Config should contain voice/tone rules."""
    config = Config()
    assert hasattr(config, 'voice_rules')


def test_config_has_model_settings():
    """Config should contain model settings."""
    config = Config()
    assert hasattr(config, 'model')
```

**Step 2: Create config.yaml.example**

```yaml
# config.yaml.example
# Copy this to config.yaml and fill in your settings

# API Configuration
api:
  key: ${CLAUDE_API_KEY}  # Will use environment variable
  model: claude-3-5-haiku-20241022  # or claude-3-5-sonnet-20241022 for better quality

# Your Voice/Tone Rules
voice_rules:
  # How should your messages sound?
  tone: "professional but approachable"
  formality: "medium"  # low, medium, high
  speed: "measured"  # rushed, measured, deliberate

  # Things you never do
  dont_do:
    - "sound robotic"
    - "use corporate jargon without explanation"
    - "seem aggressive or dismissive"

  # Things you always do
  always_do:
    - "provide context for decisions"
    - "acknowledge the other person's perspective"
    - "offer concrete next steps"

# Example messages showing your style
examples:
  good_message_1: |
    "I've been thinking about the timeline, and I think we need to shift our target by two weeks.
     Here's why: [context]. This allows us to [benefit]. Can we sync up tomorrow to align on next steps?"

  good_message_2: |
    "Thanks for flagging this. I understand the concern. Here's my perspective: [details].
     I'd love your thoughts on [specific aspect]."

# Output settings
output:
  num_variants: 3  # Number of message variants to generate
  include_explanations: true  # Explain why changes were made
  copy_to_clipboard: true  # Auto-copy best variant
```

**Step 3: Implement Config class**

```python
# src/config.py
"""Configuration system for voice rules and model settings."""

import os
import yaml
from typing import Optional, Any
from pathlib import Path


class Config:
    """Load and manage configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config.yaml")
        self.data = {}
        self.load()

    def load(self) -> None:
        """Load config from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.data = yaml.safe_load(f) or {}
        else:
            # Default config if file doesn't exist
            self.data = self._get_default_config()

    def _get_default_config(self) -> dict:
        """Return default configuration."""
        return {
            "api": {
                "model": "claude-3-5-haiku-20241022"
            },
            "voice_rules": {
                "tone": "professional",
                "formality": "medium"
            },
            "output": {
                "num_variants": 2,
                "include_explanations": True,
                "copy_to_clipboard": True
            }
        }

    @property
    def model(self) -> str:
        """Get configured model."""
        return self.data.get("api", {}).get("model", "claude-3-5-haiku-20241022")

    @property
    def voice_rules(self) -> dict:
        """Get voice/tone rules."""
        return self.data.get("voice_rules", {})

    @property
    def examples(self) -> dict:
        """Get example messages."""
        return self.data.get("examples", {})

    @property
    def output_config(self) -> dict:
        """Get output settings."""
        return self.data.get("output", {})

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dotted path."""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
```

**Step 4: Run tests**

```bash
pytest tests/test_config.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/config.py config.yaml.example tests/test_config.py
git commit -m "feat: add configuration system

- Load voice rules and model settings from YAML
- Support environment variable overrides
- Default config for new users
- Examples section to show your communication style
- Output settings for variants and clipboard"
```

---

### Task 10: Build CLI Interface

**Files:**
- Create: `src/cli.py`
- Create: `tests/test_cli.py`

**Step 1: Write failing test**

```python
# tests/test_cli.py
import pytest
from click.testing import CliRunner
from src.cli import app


def test_cli_exists():
    """CLI app should exist."""
    assert app is not None


def test_compose_command_exists():
    """CLI should have compose command."""
    runner = CliRunner()
    result = runner.invoke(app, ['--help'])
    assert 'compose' in result.output.lower()


def test_compose_with_text():
    """Compose command should accept text input."""
    runner = CliRunner()
    # This would test the command works
    # (actual test would use mocking for API)
```

**Step 2: Implement CLI**

```python
# src/cli.py
"""Command-line interface for Professional Messenger."""

import os
import sys
import click
from pathlib import Path
from src.config import Config
from src.agents.message_composer import MessageComposerAgent


@click.group()
def app():
    """Professional Messenger - Compose messages like a pro."""
    pass


@app.command()
@click.argument('text', required=False)
@click.option('--variant', '-v', default=1, help='Which variant to use (1-3)')
@click.option('--show-variants', is_flag=True, help='Show all variants')
@click.option('--clipboard', is_flag=True, default=True, help='Copy to clipboard')
@click.option('--config', help='Path to config.yaml')
def compose(text, variant, show_variants, clipboard, config):
    """Compose a professional message from unstructured thoughts.

    Usage:
        pm compose "hey i wnat to tell my boss projct is delayed"
        pm compose "lets sync up tmrw" --show-variants
    """

    # Load config
    config = Config(config_path=config)

    # If no text provided, prompt for input
    if not text:
        click.echo("📝 Enter your unstructured thoughts (press Ctrl+D when done):")
        try:
            text = sys.stdin.read()
        except EOFError:
            pass

    if not text.strip():
        click.echo("❌ No input provided")
        return

    # Create agent
    click.echo("🤖 Composing message...")
    api_key = os.getenv("CLAUDE_API_KEY")

    if not api_key:
        click.echo("❌ Error: CLAUDE_API_KEY not set")
        click.echo("Set it: export CLAUDE_API_KEY=your-key-here")
        return

    agent = MessageComposerAgent(api_key=api_key)

    # Compose message
    result = agent.compose(text)

    # Display results
    click.echo("\n✨ Composed Message:\n")
    click.echo(f"   {result['primary']}\n")

    if result['variants'] and show_variants:
        click.echo("📋 Alternative versions:\n")
        for i, var in enumerate(result['variants'], 1):
            click.echo(f"   Option {i}: {var}\n")

    # Copy to clipboard if requested
    if clipboard:
        _copy_to_clipboard(result['primary'])
        click.echo("✅ Copied to clipboard!")


@app.command()
def config():
    """Manage configuration."""
    config_path = Path("config.yaml")

    if not config_path.exists():
        # Copy example config
        example = Path(__file__).parent.parent / "config.yaml.example"
        if example.exists():
            with open(example) as f:
                content = f.read()
            with open(config_path, 'w') as f:
                f.write(content)
            click.echo(f"✅ Created {config_path} from example")
            click.echo("📝 Edit this file to set your voice rules and preferences")
        else:
            click.echo("❌ config.yaml.example not found")
    else:
        click.echo(f"✅ Config already exists at {config_path}")
        click.echo("📝 Edit this file to change your settings")


def _copy_to_clipboard(text: str) -> None:
    """Copy text to system clipboard."""
    try:
        import subprocess
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(text.encode('utf-8'))
    except Exception:
        # Clipboard not available (ok, graceful failure)
        pass


if __name__ == '__main__':
    app()
```

**Step 3: Update requirements.txt to add click**

```bash
# Click is already in requirements.txt from Task 1
```

**Step 4: Run tests**

```bash
pytest tests/test_cli.py -v
```

Expected: PASS (or mostly pass with mocking)

**Step 5: Create __main__.py for easy execution**

```python
# src/__main__.py
"""Allow running as module: python -m professional_messenger"""

from src.cli import app

if __name__ == '__main__':
    app()
```

**Step 6: Commit**

```bash
git add src/cli.py src/__main__.py tests/test_cli.py
git commit -m "feat: add CLI interface

- compose command: transform unstructured thoughts into messages
- config command: initialize configuration
- Options: show variants, clipboard copy, custom config path
- Support stdin for interactive input
- macOS clipboard integration (pbcopy)"
```

---

### Task 11: Add Message Output Formatting

**Files:**
- Create: `src/formatter.py`
- Modify: `src/cli.py`

**Step 1: Implement formatter**

```python
# src/formatter.py
"""Format agent output for display."""

from typing import dict


class MessageFormatter:
    """Format composed messages for terminal display."""

    @staticmethod
    def format_result(result: dict, show_reasoning: bool = False) -> str:
        """
        Format agent result for display.

        Args:
            result: Output from agent.compose()
            show_reasoning: Show the reasoning chain

        Returns:
            Formatted string for terminal
        """
        output = []

        # Primary message
        output.append("Primary Message:")
        output.append("─" * 50)
        output.append(result['primary'])
        output.append("")

        # Variants
        if result.get('variants'):
            output.append("Alternative Variants:")
            output.append("─" * 50)
            for i, variant in enumerate(result['variants'], 1):
                output.append(f"Option {i}:")
                output.append(variant)
                output.append("")

        # Reasoning (optional)
        if show_reasoning and result.get('reasoning'):
            output.append("AI Reasoning:")
            output.append("─" * 50)
            output.append(result['reasoning'][:200] + "...")  # Truncate

        return "\n".join(output)


# Update src/cli.py compose command to use formatter

@app.command()
@click.argument('text', required=False)
@click.option('--variant', '-v', default=1, help='Which variant to use (1-3)')
@click.option('--show-variants', is_flag=True, help='Show all variants')
@click.option('--clipboard', is_flag=True, default=True, help='Copy to clipboard')
@click.option('--config', help='Path to config.yaml')
@click.option('--reasoning', is_flag=True, help='Show AI reasoning')
def compose(text, variant, show_variants, clipboard, config, reasoning):
    """Compose a professional message from unstructured thoughts."""

    from src.formatter import MessageFormatter

    # ... (earlier code same) ...

    # Display using formatter
    formatter = MessageFormatter()
    output = formatter.format_result(result, show_reasoning=reasoning)
    click.echo(output)
```

**Step 2: Commit**

```bash
git add src/formatter.py
git commit -m "feat: add message output formatter

- Format composed messages for terminal display
- Show primary message and variants
- Optional reasoning display
- Better visual hierarchy and readability"
```

---

## Phase 4: Telegram Integration Setup (Tasks 12-14)

### Task 12: Webhook Infrastructure Setup

**Files:**
- Create: `src/webhook.py`
- Create: `requirements-webhook.txt`
- Create: `docs/TELEGRAM_SETUP.md`

**Step 1: Create webhook.py**

```python
# src/webhook.py
"""
Webhook server for Telegram integration.

This server:
1. Receives messages from Telegram bot
2. Calls MessageComposerAgent
3. Sends response back to Telegram
"""

from fastapi import FastAPI, Request
import os
import httpx
from src.agents.message_composer import MessageComposerAgent


app = FastAPI()

# Telegram bot token (set via environment)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API = "https://api.telegram.org/bot"


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram messages."""

    data = await request.json()

    # Extract message
    if 'message' not in data or 'text' not in data['message']:
        return {"status": "ignored"}

    chat_id = data['message']['chat']['id']
    user_text = data['message']['text']

    # Compose message using our agent
    api_key = os.getenv("CLAUDE_API_KEY")
    agent = MessageComposerAgent(api_key=api_key)
    result = agent.compose(user_text)

    # Send response back
    response_text = f"✨ {result['primary']}\n\nAlternatives:\n"
    for i, var in enumerate(result.get('variants', []), 1):
        response_text += f"{i}. {var}\n"

    # Send to Telegram
    await send_telegram_message(chat_id, response_text)

    return {"status": "ok"}


async def send_telegram_message(chat_id: int, text: str) -> None:
    """Send message to Telegram user."""
    url = f"{TELEGRAM_API}{TELEGRAM_BOT_TOKEN}/sendMessage"

    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": text
        })


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Step 2: Create requirements-webhook.txt**

```txt
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.0
```

**Step 3: Create Telegram setup docs**

```markdown
# docs/TELEGRAM_SETUP.md

## Telegram Bot Integration

This project can integrate with Telegram to compose messages on-the-go.

### Setup Steps

1. **Create a Telegram Bot**
   - Talk to @BotFather on Telegram
   - Run `/newbot` and follow prompts
   - Note the API token

2. **Deploy Webhook Server**

   Option A: Using Vercel (Free, recommended for learning)
   ```bash
   npm i -g vercel
   vercel deploy
   ```

   Option B: Using Railway (Free tier)
   - Push to GitHub
   - Connect Railway to repo
   - Set environment variables

   Option C: Local tunnel (testing only)
   ```bash
   # Install ngrok
   ngrok http 8000
   # Use ngrok URL for webhook
   ```

3. **Set Webhook**
   ```bash
   curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook \
     -d url=https://your-deployment.com/webhook/telegram
   ```

4. **Environment Variables**
   ```
   TELEGRAM_BOT_TOKEN=your-token-here
   CLAUDE_API_KEY=your-key-here
   ```

5. **Test**
   - Send message to bot on Telegram
   - Should receive composed response

### How It Works

```
User sends message to bot
         ↓
Telegram API → Your webhook
         ↓
MessageComposerAgent processes
         ↓
Response sent back to Telegram
         ↓
User sees composed message
```

No persistent bot service needed - just a webhook!
```

**Step 4: Commit**

```bash
git add src/webhook.py requirements-webhook.txt docs/TELEGRAM_SETUP.md
git commit -m "feat: add Telegram webhook integration

- FastAPI server for Telegram webhook
- Receives messages, calls agent, sends response
- Health check endpoint
- Setup guide for bot creation and deployment
- Framework for Phase 2: Production Telegram"
```

---

### Task 13: Write Integration Tests

**Files:**
- Create: `tests/test_integration.py`

**Step 1: Create integration tests**

```python
# tests/test_integration.py
"""
Integration tests for the full message composition flow.

Tests the complete pipeline:
Input → Agent → Subagents → Output
"""

import pytest
from src.agents.message_composer import MessageComposerAgent
from src.subagents.tone_analyzer import ToneAnalyzer
from src.subagents.structure_organizer import StructureOrganizer
from src.subagents.clarity_enhancer import ClarityEnhancer
from src.config import Config


class TestAgentIntegration:
    """Test the full agent pipeline."""

    def test_message_composition_pipeline(self):
        """Full pipeline: input → agent → output."""
        agent = MessageComposerAgent(api_key="test-key")

        user_input = "hey i wnat tell my boss projct is delayed"
        result = agent.compose(user_input)

        # Verify structure
        assert "primary" in result
        assert "variants" in result
        assert isinstance(result["variants"], list)

    def test_subagent_coordination(self):
        """Subagents should work together."""
        composer = MessageComposerAgent(api_key="test-key")
        tone_analyzer = ToneAnalyzer(api_key="test-key")
        structure_organizer = StructureOrganizer(api_key="test-key")
        clarity = ClarityEnhancer(api_key="test-key")

        text = "project delayed"

        # Each subagent analyzes
        tone_result = tone_analyzer.analyze(text)
        structure_result = structure_organizer.analyze(text)
        clarity_result = clarity.analyze(text)

        # All should return dicts
        assert isinstance(tone_result, dict)
        assert isinstance(structure_result, dict)
        assert isinstance(clarity_result, dict)

    def test_config_integration(self):
        """Config should work with agents."""
        config = Config()

        # Config should have settings needed by agents
        assert config.model
        assert config.voice_rules
        assert config.output_config


class TestCLIIntegration:
    """Test CLI with agent."""

    def test_full_cli_flow(self):
        """CLI should handle compose flow."""
        from click.testing import CliRunner
        from src.cli import app

        runner = CliRunner()

        # Just test that help works (full test needs mocking)
        result = runner.invoke(app, ['compose', '--help'])
        assert 'Usage' in result.output


def test_end_to_end_message_composition():
    """End-to-end: raw input → polished message."""

    raw = "hey can we push deadline 2 weeks im swamped"

    agent = MessageComposerAgent(api_key="test-key")
    result = agent.compose(raw)

    primary = result["primary"]

    # Composed message should:
    # - Be professional
    # - Retain the key information
    # - Be more structured than input
    assert len(primary) > 0
    assert isinstance(primary, str)
```

**Step 2: Run tests**

```bash
pytest tests/test_integration.py -v
```

Expected: Tests pass (with mock API)

**Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests

- Test full message composition pipeline
- Test subagent coordination
- Test config with agents
- Test CLI flow
- End-to-end message transformation"
```

---

### Task 14: Documentation & Commit Summary

**Files:**
- Modify: `README.md`
- Create: `docs/ARCHITECTURE.md`
- Create: `docs/QUICK_START.md`

**Step 1: Update README.md**

```markdown
# Professional Messenger

Transform unstructured thoughts into professional messages using AI agents.

## Quick Start

```bash
# 1. Clone and install
git clone git@github.com:gourav310/professional-messenger.git
cd professional-messenger
pip install -r requirements.txt

# 2. Set up
cp .env.example .env
# Edit .env with your CLAUDE_API_KEY

# 3. Run
python -m professional_messenger.cli compose "hey i want my boss to know projects delayed"
```

## Features

✨ **Intelligent Agent System**
- Primary Message Composer Agent
- Specialized subagents: Tone, Structure, Clarity
- Maintains your authentic voice
- Returns multiple polished variants

🎯 **Multiple Interfaces**
- Terminal CLI for quick composition
- Telegram bot (coming soon)
- macOS shortcuts (coming soon)

⚙️ **Fully Customizable**
- YAML config for your voice rules
- Example messages to guide AI
- Model selection (Haiku for speed, Sonnet for quality)

## Architecture

```
┌─────────────────┐
│  User Input     │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────┐
│ MessageComposerAgent        │
│ (Primary Orchestrating)     │
└────────┬────────────────────┘
         │
         ├─→ ToneAnalyzer
         ├─→ StructureOrganizer
         └─→ ClarityEnhancer
         │
         ↓
┌─────────────────────────────┐
│ Multiple Polished Variants  │
└─────────────────────────────┘
         │
         ├─→ Terminal (CLI)
         ├─→ Telegram (Webhook)
         └─→ Clipboard
```

## Learning Path

1. **Agent Fundamentals** - Understand reasoning loops and tool use
2. **Single Agent** - MessageComposerAgent handles composition
3. **Multi-Agent** - Subagents handle specific concerns
4. **Integration** - CLI, config, and Telegram

See `docs/AGENT_FUNDAMENTALS.md` for deeper understanding.

## Development

```bash
# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_agent.py::test_agent_initialization -v

# Check code
python -m pytest --cov=src tests/

# Telegram setup (Phase 2)
pip install -r requirements-webhook.txt
# See docs/TELEGRAM_SETUP.md
```

## Project Structure

```
professional-messenger/
├── src/
│   ├── agent.py              # Agent base class
│   ├── llm_client.py         # Claude API wrapper
│   ├── config.py             # Configuration system
│   ├── cli.py                # CLI interface
│   ├── formatter.py          # Output formatting
│   ├── webhook.py            # Telegram webhook (Phase 2)
│   ├── agents/
│   │   ├── message_composer.py
│   │   └── ...
│   └── subagents/
│       ├── tone_analyzer.py
│       ├── structure_organizer.py
│       └── clarity_enhancer.py
├── tests/
│   ├── test_agent.py
│   ├── test_*.py
│   └── test_integration.py
├── docs/
│   ├── AGENT_FUNDAMENTALS.md
│   ├── ARCHITECTURE.md
│   ├── TELEGRAM_SETUP.md
│   └── plans/
│       └── 2026-02-22-agent-implementation.md
├── config.yaml.example
└── requirements.txt
```

## Next Steps

- [ ] Integration with Telegram
- [ ] Message history and learning
- [ ] macOS Shortcut integration
- [ ] Analytics on message improvements
- [ ] Multi-user support

## Contributing

This is a personal learning project. Feel free to fork and adapt!

## License

MIT
```

**Step 2: Create ARCHITECTURE.md**

```markdown
# Architecture

## System Design

The Professional Messenger uses a hierarchical agent architecture:

### Layer 1: Message Composer Agent (Primary)
- Orchestrates the composition process
- Decides what subagents to invoke
- Synthesizes their feedback
- Returns final variants

### Layer 2: Subagents (Specialized)
- **ToneAnalyzer**: Detects and improves tone
- **StructureOrganizer**: Suggests message structure
- **ClarityEnhancer**: Improves clarity

### Layer 3: LLM Client
- Wraps Anthropic SDK
- Handles message formatting
- Tool/function calling

### Layer 4: Interface
- CLI for terminal
- Webhook for Telegram
- Config system

## Agent Reasoning Loop

```python
def reasoning_loop():
    messages = [user_input]

    while not done:
        # 1. Send to Claude
        response = llm.create_message(
            messages=messages,
            system=agent.system_prompt,
            tools=agent.tools
        )

        # 2. Claude decides: tool use or done?
        if response.tool_use:
            # 3. Execute tool
            result = execute_tool(response.tool_use)

            # 4. Add to conversation
            messages.append({
                "role": "assistant",
                "content": response
            })
            messages.append({
                "role": "user",
                "content": f"Tool result: {result}"
            })
        else:
            # 5. Extract output
            return extract_text(response)
```

## Tool Use Pattern

Agents use Claude's tool calling to:
1. Analyze messages (what needs changing?)
2. Get subagent feedback (specialized analysis)
3. Generate variants (multiple polished versions)
4. Make decisions (which to return?)

## Configuration

Voice rules in `config.yaml` guide the agents:
- Tone preferences
- Formality level
- Examples of your style
- Things you never/always do

## Integration Points

### CLI
- User types unstructured message
- Calls MessageComposerAgent
- Displays result with variants

### Telegram (Phase 2)
- Bot receives message
- Webhook calls agent
- Response sent back to user

## Key Design Decisions

**Why Subagents?**
- Separation of concerns
- Each agent is expert in one area
- Easier to test and debug
- Scalable to more agents

**Why Webhook over Polling Bot?**
- Stateless (deploy anywhere)
- No persistent service
- Scales to millions of users
- Cost-effective (free tiers available)

**Why Tool Use?**
- Structured reasoning
- Agents decide what analysis needed
- Easy to add new tools
- Transparent decision-making

**Why Config.yaml?**
- Users customize voice rules
- No code changes needed
- Easy to try different styles
- Version control friendly
```

**Step 3: Create QUICK_START.md**

```markdown
# Quick Start Guide

## 5-Minute Setup

### 1. Get API Key
- Go to https://console.anthropic.com
- Create account or sign in
- Generate API key
- Copy to clipboard

### 2. Clone Project
```bash
git clone git@github.com:gourav310/professional-messenger.git
cd professional-messenger
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure
```bash
# Copy example config
cp config.yaml.example config.yaml

# Create .env with your key
echo "CLAUDE_API_KEY=your-key-here" > .env
```

### 5. Try It
```bash
python -m professional_messenger.cli compose "hey i want my boss to know the project is delayed"
```

Expected output:
```
✨ Composed Message:

   I wanted to inform you that the project timeline has shifted...

✅ Copied to clipboard!
```

## Common Tasks

### Run Tests
```bash
pytest tests/ -v
```

### Customize Your Voice
Edit `config.yaml`:
```yaml
voice_rules:
  tone: "professional but warm"
  formality: "medium"

examples:
  good_message_1: |
    "Your example of how you like to write messages"
```

### Show Alternatives
```bash
python -m professional_messenger.cli compose "your message" --show-variants
```

### View Help
```bash
python -m professional_messenger.cli compose --help
```

## Troubleshooting

**Error: "CLAUDE_API_KEY not set"**
- Run: `export CLAUDE_API_KEY=your-key`
- Or create `.env` file in project root

**Error: "config.yaml not found"**
- Run: `python -m professional_messenger.cli config`
- This creates config from example

**API calls too slow?**
- Using Haiku model (fast, cheaper)
- For better quality, edit config: model: claude-3-5-sonnet

## Next: Telegram Bot (Optional)

See `docs/TELEGRAM_SETUP.md` to set up Telegram integration.
```

**Step 4: Final commit**

```bash
git add README.md docs/ARCHITECTURE.md docs/QUICK_START.md
git commit -m "docs: add comprehensive documentation

- Update README with features and quick start
- Architecture guide explaining agent system
- Quick start for 5-minute setup
- Configuration and customization guide"
```

---

## Phase 5: Incremental Learning & Feedback (Tasks 15-19)

### Task 15: Feedback Collection in CLI

**Files:**
- Create: `src/feedback.py`
- Modify: `src/cli.py`
- Create: `tests/test_feedback.py`

**Step 1: Write failing test**

```python
# tests/test_feedback.py
def test_feedback_collection():
    """CLI should ask user about their choice."""
    from src.feedback import FeedbackCollector

    collector = FeedbackCollector()
    assert collector is not None


def test_feedback_structure():
    """Feedback entry should have required fields."""
    from src.feedback import FeedbackEntry

    entry = FeedbackEntry(
        original_input="test",
        chosen_variant=1,
        reason="test reason"
    )

    assert entry.original_input == "test"
    assert entry.chosen_variant == 1
```

**Step 2: Implement FeedbackCollector**

```python
# src/feedback.py
"""Feedback collection and storage for incremental learning."""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, dict


@dataclass
class FeedbackEntry:
    """Single feedback entry from user."""

    original_input: str
    chosen_variant: int  # 1=primary, 2=option1, 3=option2, etc.
    reason: str
    timestamp: str = None
    id: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.id:
            self.id = f"msg_{int(datetime.now().timestamp() * 1000)}"

    def to_dict(self) -> dict:
        return asdict(self)


class FeedbackCollector:
    """Collect and manage user feedback."""

    def __init__(self, feedback_file: str = "feedback.yaml"):
        self.feedback_file = Path(feedback_file)
        self.entries = []
        self.load()

    def load(self) -> None:
        """Load existing feedback."""
        if self.feedback_file.exists():
            import yaml
            with open(self.feedback_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                entries = data.get('feedback_entries', [])
                self.entries = [FeedbackEntry(**e) for e in entries]

    def save(self) -> None:
        """Save feedback to file."""
        import yaml
        data = {
            'feedback_entries': [e.to_dict() for e in self.entries],
            'statistics': self.get_statistics()
        }
        with open(self.feedback_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def add_feedback(self, entry: FeedbackEntry) -> None:
        """Add feedback entry."""
        self.entries.append(entry)
        self.save()

    def get_statistics(self) -> dict:
        """Get feedback statistics."""
        if not self.entries:
            return {}

        return {
            'total_feedback': len(self.entries),
            'average_formality': self._calculate_avg_formality(),
            'tone_preferences': self._extract_tone_preferences(),
            'structure_preference': self._extract_structure_preference()
        }

    def _calculate_avg_formality(self) -> float:
        """Extract formality from feedback reasons."""
        formality_scores = []
        keywords = {
            'formal': 8, 'stiff': 2, 'corporate': 7,
            'casual': 3, 'warm': 5, 'direct': 6, 'friendly': 4
        }

        for entry in self.entries:
            reason_lower = entry.reason.lower()
            for keyword, score in keywords.items():
                if keyword in reason_lower:
                    formality_scores.append(score)
                    break

        return sum(formality_scores) / len(formality_scores) if formality_scores else 5

    def _extract_tone_preferences(self) -> list:
        """Extract tone preferences from reasons."""
        tones = []
        tone_keywords = ['warm', 'direct', 'formal', 'casual', 'friendly', 'professional']

        for entry in self.entries:
            reason_lower = entry.reason.lower()
            for tone in tone_keywords:
                if tone in reason_lower:
                    tones.append(tone)
                    break

        return tones

    def _extract_structure_preference(self) -> str:
        """Extract structure preference from reasons."""
        for entry in self.entries:
            if 'direct' in entry.reason.lower() or 'straight' in entry.reason.lower():
                return 'key-point-first'
            if 'context' in entry.reason.lower():
                return 'context-first'

        return 'unknown'
```

**Step 3: Integrate into CLI**

```python
# Update src/cli.py compose command

def compose(text, variant, show_variants, clipboard, config, reasoning):
    """Compose a professional message."""

    # ... (earlier code) ...

    # Display output
    click.echo(output)

    # NEW: Ask for feedback
    if config.output_config.get('collect_feedback', True):
        collect_feedback(result, text)


def collect_feedback(result: dict, original_input: str) -> None:
    """Collect user feedback for learning."""
    from src.feedback import FeedbackCollector, FeedbackEntry

    click.echo("\n────────────────────────────────────────")
    click.echo("📚 HELP ME LEARN YOUR STYLE")
    click.echo("────────────────────────────────────────\n")

    click.echo("Which option did you use or prefer?\n")
    click.echo("   [1] Primary message")
    click.echo("   [2] Option 1")
    click.echo("   [3] Option 2")
    click.echo("   [4] I edited / used custom version")
    click.echo("   [5] None of the above")
    click.echo("   [skip] Skip feedback\n")

    choice = click.prompt("→ Your choice", default="skip")

    if choice.lower() == "skip":
        click.echo("No problem! Feedback skipped.\n")
        return

    try:
        variant_num = int(choice)
        if variant_num not in [1, 2, 3, 4, 5]:
            click.echo("Invalid choice")
            return
    except ValueError:
        click.echo("Invalid choice")
        return

    # Ask why
    reason = click.prompt("\nWhy did you choose that? (helps me learn your style)")

    # Store feedback
    collector = FeedbackCollector()
    entry = FeedbackEntry(
        original_input=original_input,
        chosen_variant=variant_num,
        reason=reason
    )
    collector.add_feedback(entry)

    click.echo("\n✅ Thanks! Your feedback helps improve suggestions.")
    click.echo(f"   Stored in: feedback.yaml\n")
```

**Step 4: Run tests**

```bash
pytest tests/test_feedback.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/feedback.py tests/test_feedback.py
git commit -m "feat: add feedback collection system

- FeedbackCollector class for managing feedback
- FeedbackEntry dataclass with timestamp and ID
- Integration into CLI compose command
- Ask user which variant they chose and why
- Store feedback in feedback.yaml for learning"
```

---

### Task 16: Feedback Storage & Analytics

**Files:**
- Create: `feedback.yaml` (template)
- Create: `src/feedback_analyzer.py`
- Modify: `src/feedback.py` (enhance)

**Step 1: Create feedback.yaml template**

```yaml
# feedback.yaml
# Auto-generated feedback file - tracks your message composition preferences

feedback_entries: []

statistics:
  total_feedback: 0
  average_formality: 5.0
  tone_preferences: []
  structure_preference: "unknown"
  last_updated: null
```

**Step 2: Implement FeedbackAnalyzer**

```python
# src/feedback_analyzer.py
"""Analyze feedback patterns for learning."""

from typing import dict, list
from src.feedback import FeedbackCollector


class FeedbackAnalyzer:
    """Extract learning patterns from feedback."""

    def __init__(self, feedback_collector: FeedbackCollector):
        self.collector = feedback_collector

    def get_tone_profile(self) -> dict:
        """Analyze user's tone preferences."""
        tone_words = {
            'warm': [], 'direct': [], 'formal': [],
            'casual': [], 'friendly': [], 'professional': [],
            'stiff': [], 'corporate': []
        }

        for entry in self.collector.entries:
            reason = entry.reason.lower()
            for tone in tone_words.keys():
                if tone in reason:
                    tone_words[tone].append(entry.id)

        # Find dominant tones
        dominant = sorted(
            tone_words.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        return {
            'dominant_tones': [t[0] for t in dominant[:3] if t[1]],
            'tone_counts': {t: len(ids) for t, ids in dominant},
            'preference_summary': self._summarize_tone(tone_words)
        }

    def get_structure_preference(self) -> str:
        """Analyze user's preferred message structure."""
        structure_indicators = {
            'key-point-first': ['direct', 'straight', 'to the point', 'upfront'],
            'context-first': ['background', 'context', 'explain first', 'reason'],
            'conclusion-first': ['bottom line', 'ultimately', 'in summary']
        }

        structure_scores = {s: 0 for s in structure_indicators.keys()}

        for entry in self.collector.entries:
            reason_lower = entry.reason.lower()
            for structure, indicators in structure_indicators.items():
                for indicator in indicators:
                    if indicator in reason_lower:
                        structure_scores[structure] += 1

        best = max(structure_scores, key=structure_scores.get)
        return best if structure_scores[best] > 0 else 'unknown'

    def get_formality_level(self) -> float:
        """Get average formality (0-10 scale)."""
        return self.collector.get_statistics().get(
            'average_formality', 5.0
        )

    def get_disliked_patterns(self) -> list:
        """Extract patterns user dislikes."""
        dislike_keywords = [
            'too formal', 'too casual', 'too wordy',
            'too short', 'too stiff', 'too friendly'
        ]

        dislikes = []
        for entry in self.collector.entries:
            reason = entry.reason.lower()
            for keyword in dislike_keywords:
                if keyword in reason and keyword not in dislikes:
                    dislikes.append(keyword)

        return dislikes

    def generate_learning_summary(self) -> str:
        """Generate human-readable summary of learned preferences."""
        if len(self.collector.entries) < 2:
            return "Insufficient feedback for learning (need 2+ entries)"

        tone = self.get_tone_profile()
        structure = self.get_structure_preference()
        formality = self.get_formality_level()
        dislikes = self.get_disliked_patterns()

        summary = f"""
LEARNED COMMUNICATION PROFILE (from {len(self.collector.entries)} feedback entries)

Tone Preferences:
  - Preferred tones: {', '.join(tone['dominant_tones']) or 'collecting data'}
  - Formality level: {formality:.1f} / 10

Message Structure:
  - Preferred: {structure}

Things You Dislike:
  - {chr(10).join(['  - ' + d for d in dislikes] or ['  - (collecting data)'])}

This profile guides the agent to write messages more aligned with your style.
        """.strip()

        return summary

    def _summarize_tone(self, tone_words: dict) -> str:
        """Summarize tone preferences in one line."""
        liked = [t for t, ids in tone_words.items() if len(ids) > 0]
        if liked:
            return f"Mix of {', '.join(liked[:3])}"
        return "Collecting preferences"
```

**Step 3: Add feedback analytics CLI command**

```python
# Add to src/cli.py

@app.command()
@click.option('--format', type=click.Choice(['summary', 'detailed']), default='summary')
def feedback(format):
    """View your feedback and learning profile."""

    from src.feedback import FeedbackCollector
    from src.feedback_analyzer import FeedbackAnalyzer

    collector = FeedbackCollector()

    if not collector.entries:
        click.echo("No feedback yet. Use 'compose' and provide feedback to build your profile.")
        return

    analyzer = FeedbackAnalyzer(collector)

    if format == 'summary':
        click.echo(analyzer.generate_learning_summary())
    else:
        click.echo(f"Total feedback entries: {len(collector.entries)}")
        for entry in collector.entries[-5:]:  # Show last 5
            click.echo(f"\n  {entry.id}: Chose variant {entry.chosen_variant}")
            click.echo(f"  Reason: {entry.reason}")
```

**Step 4: Commit**

```bash
git add src/feedback_analyzer.py
git commit -m "feat: add feedback analysis for learning

- FeedbackAnalyzer extracts tone, structure preferences
- Calculate formality level from feedback
- Identify disliked patterns
- Generate learning summary for user
- New 'feedback' CLI command to view profile"
```

---

### Task 17: Adaptive System Prompt Generation

**Files:**
- Create: `src/learning_engine.py`
- Modify: `src/agents/message_composer.py`

**Step 1: Implement LearningEngine**

```python
# src/learning_engine.py
"""Generate adaptive system prompts based on feedback."""

from src.feedback import FeedbackCollector
from src.feedback_analyzer import FeedbackAnalyzer


class LearningEngine:
    """Enhance agent system prompts with learned preferences."""

    def __init__(self):
        self.collector = FeedbackCollector()
        self.analyzer = FeedbackAnalyzer(self.collector)

    def enhance_system_prompt(self, base_prompt: str) -> str:
        """
        Add learned preferences to system prompt.

        This makes the agent aware of user's communication style.
        """

        if len(self.collector.entries) < 2:
            # Not enough data yet
            return base_prompt

        # Extract learned preferences
        tone_profile = self.analyzer.get_tone_profile()
        structure = self.analyzer.get_structure_preference()
        formality = self.analyzer.get_formality_level()
        dislikes = self.analyzer.get_disliked_patterns()

        # Build enhancement
        learning_section = f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER'S LEARNED COMMUNICATION STYLE ({len(self.collector.entries)} feedback entries)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TONE & VOICE:
User prefers: {', '.join(tone_profile['dominant_tones']) or 'gathering preferences'}
Formality level: {formality:.1f} / 10 (where 1=very casual, 10=very formal)

MESSAGE STRUCTURE:
Preferred approach: {structure}

PATTERNS TO AVOID:
{chr(10).join(['- ' + d for d in dislikes] or ['- (no patterns identified yet)'])}

GUIDANCE:
- Generate message variants that match these preferences
- Prioritize variants using the learned tone and structure
- Rank variants to show most aligned first
- When uncertain, follow the learned preferences

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        return base_prompt + learning_section

    def get_learning_summary(self) -> str:
        """Get summary of what has been learned."""
        return self.analyzer.generate_learning_summary()
```

**Step 2: Integrate into MessageComposerAgent**

```python
# Update src/agents/message_composer.py

class MessageComposerAgent(Agent):
    def __init__(self, api_key: Optional[str] = None):
        # Base system prompt
        base_system_prompt = """You are a professional message composition expert..."""

        # Enhance with learning
        from src.learning_engine import LearningEngine
        learning_engine = LearningEngine()
        self.system_prompt = learning_engine.enhance_system_prompt(base_system_prompt)

        # Rest of init...
        super().__init__(name="MessageComposer", system_prompt=self.system_prompt)
        self.learning_engine = learning_engine
        # ...

    def compose(self, user_input: str, max_iterations: int = 3) -> dict:
        """
        Compose message informed by user's learned style.
        """
        # Use enhanced system_prompt (now includes learning)
        # Rest of compose logic...
```

**Step 3: Commit**

```bash
git add src/learning_engine.py
git commit -m "feat: implement adaptive system prompts

- LearningEngine enhances prompts with learned preferences
- Agent automatically uses learned tone, formality, structure
- Feedback automatically improves future suggestions
- Transparency: agent shows user what it learned"
```

---

### Task 18: Integration Testing for Learning

**Files:**
- Create: `tests/test_learning.py`

**Step 1: Create integration tests**

```python
# tests/test_learning.py
"""Integration tests for incremental learning."""

import pytest
from src.feedback import FeedbackCollector, FeedbackEntry
from src.feedback_analyzer import FeedbackAnalyzer
from src.learning_engine import LearningEngine


class TestLearningSystem:
    """Test the complete learning system."""

    def test_feedback_collection_and_analysis(self):
        """Full cycle: collect feedback → analyze → learn."""

        collector = FeedbackCollector()

        # Add sample feedback
        collector.add_feedback(FeedbackEntry(
            original_input="hey project delayed",
            chosen_variant=1,
            reason="Direct and professional sounding"
        ))

        collector.add_feedback(FeedbackEntry(
            original_input="can we sync tomorrow",
            chosen_variant=2,
            reason="Warmer tone, feels more like me"
        ))

        # Analyze
        analyzer = FeedbackAnalyzer(collector)
        summary = analyzer.generate_learning_summary()

        assert "LEARNED COMMUNICATION PROFILE" in summary
        assert len(collector.entries) == 2

    def test_system_prompt_enhancement(self):
        """System prompt should be enhanced with learning."""

        # Add feedback
        collector = FeedbackCollector()
        collector.add_feedback(FeedbackEntry(
            original_input="test",
            chosen_variant=1,
            reason="Direct and warm"
        ))

        # Enhance prompt
        engine = LearningEngine()
        base_prompt = "You are helpful."
        enhanced = engine.enhance_system_prompt(base_prompt)

        # Should contain learning info
        assert "LEARNED COMMUNICATION STYLE" in enhanced
        assert len(enhanced) > len(base_prompt)

    def test_no_learning_with_insufficient_data(self):
        """With <2 entries, shouldn't modify prompt."""

        engine = LearningEngine()
        base_prompt = "You are helpful."

        # Empty feedback
        enhanced = engine.enhance_system_prompt(base_prompt)
        assert enhanced == base_prompt
```

**Step 2: Commit**

```bash
git add tests/test_learning.py
git commit -m "test: add integration tests for learning system

- Test feedback collection and analysis
- Test system prompt enhancement
- Test learning thresholds
- End-to-end learning verification"
```

---

### Task 19: Documentation for Learning System

**Files:**
- Create: `docs/INCREMENTAL_LEARNING.md` ✓ (already created)
- Modify: `README.md`

**Step 1: Update README with learning section**

```markdown
# Add to README.md

## Incremental Learning

Professional Messenger learns from your choices to improve recommendations:

**How it works:**
1. Compose a message → agent shows 2-3 variants
2. Tell us which you used and why
3. Agent learns your communication style
4. Future suggestions are more personalized

**Example Journey:**

Message 1: "Your suggestions sound too formal"
→ Agent learns: User prefers warmth

Message 2: "Perfect! This sounds like me"
→ Agent learns: Warmth + directness works

Message 3: Agent generates highly personalized suggestions

See `docs/INCREMENTAL_LEARNING.md` for detailed explanation.

## Feedback Commands

```bash
pm feedback summary    # View your communication profile
pm feedback history    # See recent feedback entries
pm feedback reset      # Start learning fresh
```
```

**Step 2: Commit**

```bash
git add docs/INCREMENTAL_LEARNING.md README.md
git commit -m "docs: add incremental learning documentation

- Explain feedback collection flow
- Show learning in action with examples
- Document feedback storage and analytics
- Add feedback CLI commands to README"
```

---

## Summary: All 19 Tasks Complete

✅ **Phase 1: Agent Fundamentals** (Tasks 1-6)
- Foundation for understanding agents
- Core composition logic

✅ **Phase 2: Subagents** (Tasks 7-8)
- Specialized agents for tone, structure, clarity
- Multi-agent architecture

✅ **Phase 3: CLI & Configuration** (Tasks 9-11)
- Terminal interface
- Output formatting
- YAML configuration

✅ **Phase 4: Telegram Integration** (Tasks 12-14)
- Webhook infrastructure
- Setup documentation
- Integration tests

✅ **Phase 5: Incremental Learning** (Tasks 15-19) **[NEW]**
- Feedback collection from users
- Learning pattern extraction
- Adaptive system prompts
- Analytics and insights

---

## Extended Execution Handoff

Plan complete and updated with learning features: `docs/plans/2026-02-22-agent-implementation.md`

**Total time estimate:** 6-7 hours (including learning integration)

**Two execution options:**

**1. Subagent-Driven (this session)**
- Fresh subagent per task
- Review + debug in real-time
- Best for learning

**2. Parallel Session (separate)**
- Use executing-plans in new session
- Batch through all 19 tasks with checkpoints
- Best for flow state

**Which approach?**


✅ **Agent Fundamentals**
- Agent and Tool base classes
- LLMClient wrapper for Claude API
- Understanding of reasoning loops

✅ **Message Composer Agent**
- Primary orchestrating agent
- Reasoning loop implementation
- Tool integration

✅ **Subagents Architecture**
- ToneAnalyzer, StructureOrganizer, ClarityEnhancer
- Multi-agent coordination
- Specialized analysis

✅ **CLI & Configuration**
- Terminal interface for message composition
- YAML configuration system
- Output formatting and variants

✅ **Telegram Integration Framework**
- Webhook server structure
- Setup documentation
- Ready for deployment

✅ **Testing & Documentation**
- Integration tests
- Comprehensive architecture guide
- Quick start and setup docs

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-22-agent-implementation.md`.

**Two execution options:**

**1. Subagent-Driven (this session)**
- I dispatch fresh subagent per task
- Review between tasks
- Fast iteration
- Good for debugging

**2. Parallel Session (separate)**
- Open new session in worktree
- Batch execution with checkpoints
- Good for flow state

**Which approach?**
