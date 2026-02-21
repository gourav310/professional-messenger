# Professional Messenger - System Design

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT INTERFACES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  Terminal    │    │   Telegram   │    │ macOS        │       │
│  │  CLI         │    │   Bot        │    │ Shortcut     │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                    │                    │               │
└─────────┼────────────────────┼────────────────────┼───────────────┘
          │                    │                    │
          │                    ↓                    │
          │            ┌──────────────────┐        │
          │            │  Telegram Webhook│        │
          │            │  (FastAPI Server)│        │
          │            └──────┬───────────┘        │
          │                   │                     │
          └───────────────────┼─────────────────────┘
                              │
                              ↓
                    ┌─────────────────────┐
                    │  Message Composer   │
                    │  Agent              │
                    │  (Orchestrator)     │
                    └────────┬────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ↓                  ↓                  ↓
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Tone      │  │  Structure   │  │  Clarity     │
    │ Analyzer    │  │  Organizer   │  │  Enhancer    │
    │ (Subagent)  │  │  (Subagent)  │  │  (Subagent)  │
    └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
           │                │                 │
           └────────────────┼─────────────────┘
                            │
                            ↓
                ┌────────────────────────┐
                │ Claude API             │
                │ (LLMClient wrapper)    │
                └────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ↓                 ↓                 ↓
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Terminal │      │Clipboard │      │ Telegram │
    │ Output   │      │  Copy    │      │  Send    │
    └──────────┘      └──────────┘      └──────────┘
```

---

## Message Composition Flow (Detailed)

```
START: User Input
     │
     ↓
┌─────────────────────────────┐
│ Load Configuration          │
│ - API Key                   │
│ - Voice Rules               │
│ - Examples                  │
└────────────┬────────────────┘
             │
             ↓
┌─────────────────────────────┐
│ Initialize MessageComposer  │
│ Agent & Subagents           │
└────────────┬────────────────┘
             │
             ↓
    ┌────────────────────┐
    │ REASONING LOOP     │
    └────────────┬───────┘
                 │
                 ├─────────────────────────┐
                 │                         │
                 ↓                         │
         ┌──────────────────┐              │
         │ Send to Claude   │              │
         │ + Tools          │              │
         │ + System Prompt  │              │
         └────────┬─────────┘              │
                  │                        │
                  ↓                        │
         ┌──────────────────────┐          │
         │ Claude Decides:      │          │
         │ Use Tool? or Done?   │          │
         └────┬──────────┬──────┘          │
              │          │                 │
         YES  │          │  NO            │
              ↓          ↓                 │
      ┌───────────┐  ┌─────────────┐      │
      │ Tool Used │  │ Response    │      │
      │ (analyze) │  │ Generated   │      │
      └─────┬─────┘  └──────┬──────┘      │
            │               │              │
            ↓               ↓              │
      ┌──────────────┐  ┌──────────────┐  │
      │ Add to       │  │ Extract Text │  │
      │ Conversation │  │ & Variants   │  │
      │ & Retry      │  │              │  │
      └──────┬───────┘  └──────┬───────┘  │
             │                 │          │
             └────→ Loop? ────→┤ YES      │
                               │          │
                          NO ──┘          │
                               │          │
                               └──────────┘
                                   │
                                   ↓
                        ┌──────────────────┐
                        │ Format Output    │
                        │ - Primary        │
                        │ - Variants       │
                        │ - Reasoning      │
                        └────────┬─────────┘
                                 │
                                 ↓
                        ┌──────────────────┐
                        │ Return to User   │
                        │ via CLI/Telegram │
                        └──────────────────┘
                                 │
                                 ↓
                              END
```

---

## Agent Reasoning Loop (Zoom In)

```
┌──────────────────────────────────────────────────────────────┐
│                    AGENT REASONING LOOP                       │
└──────────────────────────────────────────────────────────────┘

Input: Raw Message + System Prompt + Available Tools

    ┌─────────────────────────────────────────────────┐
    │ Iteration 1: Initial Analysis                   │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │  User Prompt:                                   │
    │  "Analyze this message and decide what to fix" │
    │                                                 │
    │  ↓                                              │
    │                                                 │
    │  Claude Thinks:                                 │
    │  "This message has tone issues, needs          │
    │   structure, clarity problems. Let me use       │
    │   tools to analyze."                            │
    │                                                 │
    │  ↓                                              │
    │                                                 │
    │  Claude Calls Tools:                            │
    │  - Tool: analyze_tone                           │
    │    Input: {text: "...", target: "professional"}│
    │                                                 │
    │  - Tool: suggest_structure                      │
    │    Input: {message: "..."}                      │
    │                                                 │
    └─────────────────────────────────────────────────┘
                            │
                            ↓
    ┌─────────────────────────────────────────────────┐
    │ Tool Execution & Results                        │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │  analyze_tone returns:                          │
    │  "Current: informal/rushed                      │
    │   Suggest: add context, slow pacing,            │
    │   professional formality"                       │
    │                                                 │
    │  suggest_structure returns:                     │
    │  "Suggested: Key point → Context → Next steps" │
    │                                                 │
    └─────────────────────────────────────────────────┘
                            │
                            ↓
    ┌─────────────────────────────────────────────────┐
    │ Iteration 2: Synthesis                          │
    ├─────────────────────────────────────────────────┤
    │                                                 │
    │  Conversation now includes:                     │
    │  1. Original message                            │
    │  2. Claude's tool calls                         │
    │  3. Tool results (feedback)                     │
    │                                                 │
    │  Claude Thinks (with new context):             │
    │  "Based on the analysis, I should now           │
    │   generate polished variants"                   │
    │                                                 │
    │  ↓                                              │
    │                                                 │
    │  Claude Generates:                              │
    │  - Primary variant                              │
    │  - 2 alternative variants                       │
    │  - Explanations                                 │
    │                                                 │
    │  ↓                                              │
    │                                                 │
    │  Stop Reason: "end_turn"                        │
    │  (Claude decided it's done)                     │
    │                                                 │
    └─────────────────────────────────────────────────┘
                            │
                            ↓
                      RETURN RESULT
                   (Primary + Variants)
```

---

## Component Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   COMPONENT INTERACTION                      │
└─────────────────────────────────────────────────────────────┘

CLI Input (Text)
    │
    ├─→ Read from args
    ├─→ Or stdin if interactive
    └─→ Config loaded (YAML)
           │
           ↓
┌──────────────────────────────────────────┐
│ MessageComposerAgent                     │
│                                          │
│ system_prompt = "You compose messages"   │
│ tools = [analyze_tone, suggest_structure]
│                                          │
│ LLMClient (Claude API wrapper)           │
│ - Formats messages                       │
│ - Calls Claude                           │
│ - Extracts tool use                      │
└────────────────┬─────────────────────────┘
                 │
                 ├────→ ToneAnalyzer.analyze()
                 │      │
                 │      └─→ Returns: {current_tone, issues, suggestions}
                 │
                 ├────→ StructureOrganizer.analyze()
                 │      │
                 │      └─→ Returns: {message_type, structure, reorganized}
                 │
                 └────→ ClarityEnhancer.analyze()
                        │
                        └─→ Returns: {clarity_score, issues, improved}

                           All results fed back to agent
                           │
                           ↓
                      Agent synthesizes
                           │
                           ↓
                      Formatter.format_result()
                           │
                           ├─→ Terminal: print to console
                           ├─→ Clipboard: pbcopy on macOS
                           └─→ Telegram: send via API
```

---

## Low-Level: File Structure & Dependencies

```
professional-messenger/
│
├── src/
│   │
│   ├── __init__.py
│   │   └── Package metadata
│   │
│   ├── agent.py ─────────────────────┐
│   │   ├── Tool class                 │
│   │   └── Agent base class           │
│   │                                   │
│   ├── llm_client.py ────────────────┼─→ Uses: anthropic SDK
│   │   ├── LLMClient wrapper          │
│   │   ├── Message formatting         │
│   │   └── Tool use extraction        │
│   │                                   │
│   ├── config.py                      │
│   │   ├── Config loader (YAML)       │
│   │   └── Settings access            │
│   │                                   │
│   ├── formatter.py                   │
│   │   └── Format output for terminal │
│   │                                   │
│   ├── cli.py ───────────────────────→ Uses: click
│   │   ├── Compose command            │
│   │   ├── Config command             │
│   │   └── Output formatting          │
│   │                                   │
│   ├── webhook.py ──────────────────→ Uses: fastapi
│   │   ├── Telegram webhook endpoint  │
│   │   └── Response handling          │
│   │                                   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── message_composer.py
│   │       ├── Main orchestrating agent
│   │       ├── Tool definitions
│   │       ├── Reasoning loop
│   │       └── Subagent invocation
│   │
│   └── subagents/
│       ├── __init__.py
│       ├── base.py ──────────────────→ Extends: Agent
│       │   └── Subagent base class
│       │
│       ├── tone_analyzer.py
│       │   └── ToneAnalyzer (subagent)
│       │
│       ├── structure_organizer.py
│       │   └── StructureOrganizer (subagent)
│       │
│       └── clarity_enhancer.py
│           └── ClarityEnhancer (subagent)
│
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_llm_client.py
│   ├── test_message_composer.py
│   ├── test_subagents.py
│   ├── test_config.py
│   ├── test_cli.py
│   └── test_integration.py
│
├── docs/
│   ├── AGENT_FUNDAMENTALS.md
│   ├── ARCHITECTURE.md
│   ├── SYSTEM_DESIGN.md (this file)
│   ├── QUICK_START.md
│   ├── TELEGRAM_SETUP.md
│   └── plans/
│       └── 2026-02-22-agent-implementation.md
│
├── config.yaml.example
│   └── Voice rules + model config
│
├── .env.example
│   └── API keys template
│
├── requirements.txt
│   └── Main dependencies
│
└── requirements-webhook.txt
    └── Telegram webhook dependencies
```

---

## Class Hierarchy & Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    INHERITANCE                          │
└─────────────────────────────────────────────────────────┘

                    ┌──────────┐
                    │  Tool    │
                    └──────────┘
                    (name, description, schema)


                    ┌──────────┐
                    │  Agent   │
                    └────┬─────┘
                         │
                    ┌────┴─────────┐
                    │              │
            ┌───────▼────────┐    ┌▼────────────┐
            │ Message        │    │ Subagent    │
            │ Composer       │    │ (base)      │
            │ Agent          │    └┬────────────┘
            └────────────────┘     │
                                   ├─────────────┐
                                   │             │
                        ┌──────────▼──┐  ┌──────▼──────┐
                        │ Tone         │  │ Structure   │
                        │ Analyzer     │  │ Organizer   │
                        └──────────────┘  └─────────────┘

                        (plus ClarityEnhancer...)


┌─────────────────────────────────────────────────────────┐
│                 COMPOSITION & USAGE                     │
└─────────────────────────────────────────────────────────┘

CLI
  │
  ├─ uses → Config
  ├─ uses → MessageComposerAgent
  │          │
  │          ├─ has → LLMClient
  │          ├─ has → Tools (list)
  │          └─ invokes → Subagents
  │
  ├─ calls → Formatter
  └─ outputs → Terminal/Clipboard


Telegram Webhook
  │
  ├─ receives → Message (from Telegram API)
  ├─ uses → Config
  ├─ calls → MessageComposerAgent
  └─ sends → Response (to Telegram API)
```

---

## Data Structures

### Agent Interaction Flow (Data)

```
┌─────────────────────────────────────┐
│ User Input                          │
│ {                                   │
│   text: "hey project delayed"       │
│ }                                   │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│ Conversation List (Claude API)      │
│ [                                   │
│   {                                 │
│     "role": "user",                 │
│     "content": "Analyze this msg..."│
│   },                                │
│   {                                 │
│     "role": "assistant",            │
│     "content": [                    │
│       {type: "text", text: "..."},  │
│       {type: "tool_use", id: "...", │
│        name: "analyze_tone", ...}   │
│     ]                               │
│   },                                │
│   {                                 │
│     "role": "user",                 │
│     "content": "Tool result: ..."   │
│   }                                 │
│ ]                                   │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│ Subagent Result                     │
│ {                                   │
│   "current_tone": "informal",       │
│   "issues": ["too casual"],         │
│   "suggestions": ["be professional"]│
│ }                                   │
└────────────────┬────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────┐
│ Final Output                        │
│ {                                   │
│   "primary": "I want to inform...", │
│   "variants": [                     │
│     "Alternative 1...",             │
│     "Alternative 2..."              │
│   ],                                │
│   "reasoning": "Analysis shows..."  │
│ }                                   │
└─────────────────────────────────────┘
```

---

## State Flow: Tool Invocation

```
User: "hey i want tell my boss project delayed"
                    │
                    ↓
        ┌─────────────────────────┐
        │ MessageComposerAgent    │
        │ .compose(user_input)    │
        └────────────┬────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ↓                     ↓
    ┌──────────────┐      ┌──────────────┐
    │ Tool Call 1: │      │ Waiting for  │
    │ analyze_tone │      │ Claude...    │
    └──────┬───────┘      └──────────────┘
           │
           ├─ Input: {
           │   text: "hey i want tell...",
           │   target_tone: "professional"
           │ }
           │
           ↓
    ┌──────────────────────┐
    │ ToneAnalyzer         │
    │ .analyze()           │
    │ (simulated tool)     │
    └──────┬───────────────┘
           │
           ↓
    ┌──────────────────────────────┐
    │ Returns:                     │
    │ {                            │
    │   current_tone: "rushed",    │
    │   issues: ["informal"],      │
    │   suggestions: ["slow down"] │
    │ }                            │
    └──────┬───────────────────────┘
           │
           ↓
    ┌──────────────────────────────────┐
    │ Add to conversation + iterate    │
    │ Claude reads: "Tool result: ..." │
    └─────────┬────────────────────────┘
              │
              ├─ Does Claude want more?
              │  YES → Call more tools
              │  NO → Generate response
              │
              ↓
    ┌──────────────────────────┐
    │ Extract final variants:  │
    │ - Primary message        │
    │ - 2-3 alternatives       │
    │ - Reasoning              │
    └──────────────────────────┘
```

---

## API Integration Points

```
┌─────────────────────────────────────────────────┐
│         EXTERNAL INTEGRATIONS                   │
└─────────────────────────────────────────────────┘

1. ANTHROPIC CLAUDE API
   ├─ Endpoint: https://api.anthropic.com/v1/messages
   ├─ Method: POST
   ├─ Headers: Authorization, Content-Type
   ├─ Body: {
   │   model: "claude-3-5-haiku-20241022",
   │   max_tokens: 1024,
   │   system: "You are...",
   │   messages: [...],
   │   tools: [...]
   │ }
   └─ Response: {
       content: [...],
       stop_reason: "tool_use" | "end_turn"
     }


2. TELEGRAM BOT API
   ├─ Receive: Webhook POST
   │  └─ Body: {
   │      message: {
   │        chat: {id: 123},
   │        text: "user message"
   │      }
   │    }
   │
   └─ Send: POST https://api.telegram.org/bot{TOKEN}/sendMessage
      └─ Body: {
          chat_id: 123,
          text: "composed response"
        }


3. macOS SYSTEM
   └─ pbcopy: Copy to clipboard
      └─ Piped stdin → clipboard
```

---

## Testing Architecture

```
┌────────────────────────────────────────────────┐
│            TEST COVERAGE                       │
└────────────────────────────────────────────────┘

UNIT TESTS
├─ test_agent.py
│  ├─ Agent initialization
│  ├─ Tool registration
│  └─ Tool schema formatting
│
├─ test_llm_client.py
│  ├─ Client initialization
│  ├─ Message formatting
│  └─ Tool handling
│
├─ test_message_composer.py
│  ├─ Agent initialization
│  ├─ Tool definitions
│  └─ Reasoning loop
│
└─ test_subagents.py
   ├─ Subagent initialization
   ├─ Subagent analysis
   └─ Result structure


INTEGRATION TESTS
├─ test_integration.py
│  ├─ Full pipeline
│  ├─ Subagent coordination
│  └─ End-to-end composition
│
└─ test_cli.py
   ├─ CLI commands
   └─ Argument handling


TEST PATTERNS
├─ Failing test first (TDD)
├─ Minimal implementation
├─ Test passes
├─ Refactor if needed
└─ Commit
```

---

This system design provides:
✅ Clear separation of concerns
✅ Extensible agent/subagent architecture
✅ Testable components
✅ Multiple interfaces (CLI, Telegram, future shortcuts)
✅ Customizable via config
✅ Educational foundation for learning agents
