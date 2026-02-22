# Testing Guide

## Where is the core API?

The messenger’s **core API** is the compose flow: turn raw input into professional message variants.

| Layer | Location | Role |
|-------|----------|------|
| **Core** | `src/agents/message_composer.py` → `MessageComposerAgent.compose(user_input, max_iterations=3)` | Runs the reasoning loop (tools + LLM), returns `{ "primary", "variants", "reasoning" }`. |
| **Entry** | `src/cli.py` → `compose(text, show_variants, clipboard, config)` | Loads config, calls the agent, formats output, optional clipboard. |
| **LLM** | `src/llm_client.py` → `LLMClient` | Talks to Groq (create_message, extract_text, extract_tool_use). |

There is no HTTP REST API yet; the “API” is the Python API above (used by the CLI).

---

## How to test

### 1. Unit tests (existing)

- **Agent/tools:** `tests/test_agent.py`, `tests/test_message_composer.py` — init, tools, system prompt.
- **LLM client:** `tests/test_llm_client.py` — init, message formatting, tool handling, response parsing (often with mocks).
- **CLI:** `tests/test_cli.py` — app exists, `compose` command and `--help`.

Run all:

```bash
python3 -m pytest tests/ -v
```

### 2. Integration test (compose with mocked LLM)

`tests/test_compose_integration.py` runs the **full compose path** without calling the real Groq API:

- Builds a `MessageComposerAgent` with a **mock `LLMClient`** that returns a fixed “final” text (e.g. professional sick-leave message).
- Calls `agent.compose("sick leave prompt")`.
- Asserts:
  - Return is a dict with `primary`, `variants`, `reasoning`.
  - `primary` is non-empty and looks professional (no raw “hey”/“i need” in the primary).

This checks that the core API’s output shape and minimal quality hold when the “LLM” is under our control.

Run:

```bash
python3 -m pytest tests/test_compose_integration.py -v
```

### 3. End-to-end (real API, optional)

To test **real production-like output** (e.g. one basic sick-leave prompt):

1. Set `GROQ_API_KEY` (or the key your project uses).
2. Run the CLI:

   ```bash
   pm compose "i need to take sick leave tomorrow"
   ```

3. Manually check:
   - Exit code 0.
   - Output shows a primary message and optionally variants.
   - Text is professional and on-topic.

You can later add an e2e test that runs the CLI with a real key in CI (or use a recorded response and still mock the client in the test).

---

## Summary

- **Core API:** `MessageComposerAgent.compose()` in `src/agents/message_composer.py`; CLI in `src/cli.py`; LLM in `src/llm_client.py`.
- **Production-level testing:** Use the integration test (mocked LLM) for deterministic checks; use the CLI with a real key (or recorded responses) for end-to-end checks.
