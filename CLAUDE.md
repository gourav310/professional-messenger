# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Installation

Professional Messenger is installed as a Python package, providing the `pm` command for use in your terminal.

### Installation Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd professional-messenger
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

   This installs the package and makes the `pm` command available in your terminal.

3. **Set your Groq API key**:
   ```bash
   export GROQ_API_KEY="gsk-proj_..."
   ```

   Get your API key from https://console.groq.com/

4. **Use the pm command**:
   ```bash
   pm --help                      # Show help
   pm config                      # Initialize configuration
   pm compose "your message"      # Compose a message
   ```

### Usage Examples

**Compose from command line:**
```bash
pm compose "hey i wanted to tell my boss the project got delayed"
```

**Compose interactively** (for longer messages):
```bash
pm compose
# (paste your message, then press Ctrl+D)
```

**See all variants:**
```bash
pm compose "your text" --show-variants
```

**Use custom configuration:**
```bash
pm compose "your text" --config work-config.yaml
```

**Initialize configuration:**
```bash
pm config
# (then edit config.yaml to customize voice rules)
```

### What the `pm` Command Does

The `pm` command is created by the `setup.py` entry point configuration:
- It maps to the `app()` function in `src/cli.py`
- Provides professional message composition
- Offers configuration management
- Works across your entire system once installed

## Quick Start

### Environment Setup
```bash
# Set Groq API key (get from https://console.groq.com/)
export GROQ_API_KEY="gsk-proj_..."
source ~/.zshrc  # Reload shell to apply changes

# Verify setup
python3 -c "from src.llm_client import LLMClient; c = LLMClient(); print('✓ Ready')"
```

### Common Commands
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_agent.py -v

# Run specific test
python3 -m pytest tests/test_agent.py::TestToolClass::test_tool_initialization -v

# Run with coverage
python3 -m pytest tests/ --cov=src

# Test agent composition (manual integration test)
source ~/.zshrc && python3 << 'EOF'
from src.agents.message_composer import MessageComposerAgent
agent = MessageComposerAgent()
result = agent.compose("hey, project got delayed")
print(result['primary'])
EOF
```

## Architecture Overview

### High-Level Flow
```
User Input (raw thoughts)
    ↓
MessageComposerAgent (Orchestrator)
    ├─ Reasoning Loop: Iterate, decide, act
    ├─ Tools: analyze_tone, suggest_structure, check_clarity
    └─ LLMClient (Groq API communication)
    ↓
Groq LLM (llama-3.3-70b-versatile)
    ├─ Analyzes message
    ├─ Decides which tools to call
    └─ Synthesizes variants
    ↓
Output: Primary variant + alternatives
```

### Core Concepts

#### 1. The Agent Pattern
**File:** `src/agent.py` (base classes: `Tool`, `Agent`)

An agent is an autonomous system with:
- **Identity**: name + system_prompt (defines behavior/personality)
- **Capabilities**: tools list (what it can do)
- **Reasoning**: loops via LLM (decides what to do)

Example from codebase:
```python
agent = Agent(
    name="MessageComposer",
    system_prompt="You compose professional messages...",
    tools=[tone_tool, structure_tool, clarity_tool]
)
```

#### 2. The Reasoning Loop
**File:** `src/agents/message_composer.py` (see `compose()` method, lines ~1045-1161)

Pattern:
1. Send conversation + available tools to LLM
2. LLM decides: call a tool OR return final answer
3. If tool call: execute tool, add result to conversation, loop
4. If final answer: extract text, return result

Why this matters: LLM decides WHAT to do, agent handles HOW to do it.

#### 3. Tool Use (Function Calling)
**File:** `src/agent.py` (class `Tool`)

Tools are JSON schemas that LLMs understand. Groq expects:
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "what it does",
    "parameters": { JSON_SCHEMA }
  }
}
```

Key: `to_claude_format()` method converts Tool objects to this format.

#### 4. LLM Provider Abstraction
**File:** `src/llm_client.py`

The `LLMClient` wraps Groq API. It:
- Manages authentication (GROQ_API_KEY)
- Formats messages for Groq
- Parses responses (extracts text or tool calls)

**Important design**: The interface stays the same if we swap providers (Claude → OpenAI → Groq). Only `LLMClient` implementation changes.

### Component Breakdown

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Agent Base** | Foundation for all agents | `src/agent.py` |
| **MessageComposerAgent** | Main orchestrating agent | `src/agents/message_composer.py` |
| **LLMClient** | Groq API wrapper | `src/llm_client.py` |
| **Configuration** | YAML-based settings | `src/config.py` |
| **CLI** | Terminal interface | `src/cli.py` |

## Development Patterns

### Test-Driven Development
All tests use mocking to avoid actual API calls:
- `unittest.mock` for patching Groq client
- Real API calls only in manual integration tests
- All unit tests pass instantly (no network latency)

### Response Handling
**Critical difference with Groq**: Response structure differs from Claude SDK.

```python
# Groq response structure
response.choices[0].message.content      # Text content
response.choices[0].message.tool_calls   # Tool calls

# LLMClient handles this:
client.extract_text(response)            # Get text
client.extract_tool_use(response)        # Get tool call
```

### Adding New Features

1. **New Tool**:
   - Create `Tool` object in `message_composer.py`
   - Add handler function (e.g., `_analyze_tone()`)
   - Register with `self.add_tool()`

2. **New Agent**:
   - Create subclass of `Agent` in `src/agents/`
   - Define system_prompt
   - Add tools
   - Implement reasoning logic

3. **Groq Model Updates**:
   - Update in `src/config.py` line 231 (default config)
   - Update in `src/llm_client.py` line 66 (parameter default)
   - Update in test files
   - Current model: `llama-3.3-70b-versatile`

## Known Issues & Workarounds

### MessageComposerAgent Hitting Iteration Limit
**Status**: In progress (was hitting max iterations during testing)

**Context**: The reasoning loop was exiting at iteration limit before synthesizing final answer.

**Solution attempted**: Increased `max_iterations` from 3 to 5, but issue persists.

**Investigation needed**:
- Add debug logging to `compose()` method (lines ~1060-1120)
- Check if Groq tool calls match expected format
- Verify tool results are being added correctly to conversation
- Consider increasing max_tokens (currently 2048) for complex reasoning

**Files involved**:
- `src/agents/message_composer.py` (compose method, _execute_tool method)
- `src/llm_client.py` (extract_tool_use, extract_text)

## File Structure

```
src/
├── agent.py                    # Base Agent and Tool classes
├── llm_client.py              # Groq API wrapper
├── config.py                  # Configuration management
├── cli.py                     # CLI interface (Click-based)
├── agents/
│   └── message_composer.py    # Main orchestrating agent
└── subagents/                 # (Not yet implemented in Phase 1)

tests/
├── test_agent.py              # Agent/Tool base class tests
├── test_llm_client.py         # LLMClient tests (with mocking)
├── test_message_composer.py   # Agent initialization tests
├── test_cli.py                # CLI tests
└── test_config.py             # Configuration tests

docs/
├── AGENT_FUNDAMENTALS.md      # Educational guide
├── SYSTEM_DESIGN.md           # Architecture diagrams
├── PROJECT_SUMMARY.md         # Project overview
└── plans/
    └── 2026-02-22-agent-implementation.md  # 19-task implementation plan
```

## Configuration

**File**: `config.yaml` (user-created, .gitignored)

**Template**: `config.yaml.example`

Key settings:
```yaml
api:
  model: llama-3.3-70b-versatile

voice_rules:
  tone: professional
  formality: medium

output:
  num_variants: 2
  include_explanations: true
  copy_to_clipboard: true
```

## Testing Strategy

- **Unit tests**: Mock Groq client, test logic in isolation
- **Integration tests**: Use real GROQ_API_KEY, test end-to-end
- **Manual tests**: Ad-hoc testing of agent composition

All unit tests in `tests/` should pass without API calls:
```bash
python3 -m pytest tests/ -v
# Expected: ~29 tests pass in <1 second
```

## Important Notes for Future Work

1. **Phase 1 Status**: Core agent infrastructure complete (Agent, Tool, MessageComposerAgent, LLMClient)
2. **Next Phase**: Subagents (ToneAnalyzer, StructureOrganizer, ClarityEnhancer)
3. **Tool Format**: Recently migrated to Groq format (type=function wrapper). Don't revert to old format.
4. **API Abstraction**: LLMClient interface should remain stable when swapping providers
5. **Model Deprecation**: Both llama-3.1-70b-versatile and mixtral-8x7b-32768 have been decommissioned. Current model is llama-3.3-70b-versatile. Check deprecation page before updating.

## Implementation Plan

See `docs/plans/2026-02-22-agent-implementation.md` for the full 19-task implementation plan across 5 phases.
