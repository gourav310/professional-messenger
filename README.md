# Professional Messenger 📧

An intelligent AI agent that transforms unstructured thoughts into professional, polished messages.

**Turn this:** `"hey boss, project got delayed because the api was slow"`
**Into this:** `"I wanted to inform you that we've encountered a delay in the project timeline due to API performance issues..."`

---

## ✨ Features

- 🤖 **AI-Powered Composition** - Uses Groq's LLM to analyze and improve messages
- 🎯 **Tone Analysis** - Detects and corrects informal, unclear, or awkward language
- 📋 **Multiple Variants** - Get 2-3 different professional versions to choose from
- ⚙️ **Customizable** - Configure tone, formality, and style via YAML config
- 📋 **CLI Tool** - Easy-to-use command-line interface
- 💾 **Clipboard Integration** - Auto-copy composed message to clipboard
- 🔄 **Agent Architecture** - Demonstrates modern AI agent patterns
- 💡 **Smart Learning System** - System learns your preferred tone and formality after a few compositions and adapts future messages automatically

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free account at https://console.groq.com/)

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/professional-messenger.git
cd professional-messenger
```

**2. Install the package**
```bash
pip install -e .
```

This installs the package and creates the `pm` command.

**3. Set up Groq API key**
```bash
export GROQ_API_KEY="your-api-key-here"
```

To make it permanent, add to your `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**4. Verify installation**
```bash
pm --help
```

You should see the help menu. If `pm: command not found`, add Python bin to your PATH:
```bash
echo 'export PATH="/Users/$(whoami)/Library/Python/3.13/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 💬 Usage

### Basic Usage
```bash
pm compose "your unstructured message"
```

**Example:**
```bash
pm compose "hey, can we reschedule the meeting? got swamped with other stuff"
```

**Output:**
```
✨ Composed Message:

   Would it be possible to reschedule our meeting? I've encountered
   some time constraints and would appreciate the flexibility.

✅ Copied to clipboard!
```

### Show Alternative Variants
```bash
pm compose "your message" --show-variants
```

This displays the primary variant plus 2-3 alternatives with different tones.

### Initialize Configuration
```bash
pm config init
```

Creates a `config.yaml` file where you can customize:
- **Tone**: professional, casual, friendly
- **Formality**: low, medium, high
- **Number of variants**: 1-3
- **Auto-copy**: true/false

### Using Custom Config
```bash
pm compose "message" --config my-config.yaml
```

### Smart Learning System (Optional)

After a few compositions, you can help the system learn your style:

```bash
pm compose "message"
# Choose preferred variant, optionally provide feedback
# System learns your preferred tone and formality
```

View your learned preferences:
```bash
pm feedback
```

Reset your preferences:
```bash
pm feedback-reset
```

See [Feedback Loop Guide](docs/FEEDBACK_LOOP_GUIDE.md) for complete details.

---

## 🏗️ Architecture

### How It Works

1. **Input** - User provides unstructured message
2. **Analysis** - LLM analyzes tone, clarity, structure
3. **Composition** - Generates professional variants
4. **Output** - Returns best variant + alternatives

### Core Components

| Component | Purpose |
|-----------|---------|
| **Agent** | Base class for autonomous reasoning systems |
| **Tool** | Functions agents can invoke (analyze_tone, check_clarity, etc.) |
| **MessageComposerAgent** | Main orchestrating agent |
| **LLMClient** | Wrapper around Groq API |
| **CLI** | Command-line interface using Click |

### Agent Reasoning Loop

```
Input Message
    ↓
LLM sees message + available tools
    ↓
LLM decides: analyze tone? check clarity? reorganize?
    ↓
Execute chosen tools
    ↓
LLM sees original + analysis results
    ↓
LLM composes professional variants
    ↓
Output variants to user
```

The LLM **decides** what's needed - it's adaptive, not pre-programmed.

---

## 📦 What's Included

```
professional-messenger/
├── src/
│   ├── agent.py              # Base Agent and Tool classes
│   ├── llm_client.py         # Groq API wrapper
│   ├── config.py             # Configuration management
│   ├── cli.py                # CLI interface (this becomes 'pm' command)
│   └── agents/
│       └── message_composer.py   # Main agent implementation
├── tests/                    # Unit tests (29 tests, all passing)
├── examples/                 # Example code
├── docs/                     # Documentation and plans
├── setup.py                  # Package configuration
└── README.md                 # This file
```

---

## 🔧 Development

### Run Tests
```bash
python3 -m pytest tests/ -v
```

Expected: 29 tests passing

### Run Tests with Coverage
```bash
python3 -m pytest tests/ --cov=src
```

### Manual Testing
```bash
# Test message composition
python3 -m src.cli compose "test message"

# Or use the installed command
pm compose "test message"
```

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Developer guide with architecture, commands, and patterns
- **[docs/FEEDBACK_LOOP_GUIDE.md](docs/FEEDBACK_LOOP_GUIDE.md)** - Complete guide to the learning system
- **[docs/AGENT_FUNDAMENTALS.md](docs/AGENT_FUNDAMENTALS.md)** - Educational guide to agent concepts
- **[docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md)** - System architecture diagrams
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project overview

---

## 🤖 How to Use

### Example 1: Casual to Professional
**Input:**
```
hey boss, just a heads up that we're gonna be a bit late on that deadline
```

**Output:**
```
I wanted to inform you that we anticipate a slight delay in meeting
the originally scheduled deadline. We are working diligently to minimize
this impact.
```

### Example 2: Unclear to Clear
**Input:**
```
i need to talk to you about the thing we discussed before regarding the project
```

**Output:**
```
I would like to discuss our previous conversation regarding the project
status and timeline. Could we schedule a brief meeting at your earliest
convenience?
```

### Example 3: Raw Notes to Email
**Input:**
```
exhausted from continuous work, need a day off
```

**Output:**
```
I wanted to inform you that I will be taking a personal day to rest and
recharge. Should you have any critical matters, please don't hesitate
to reach out to me.
```

---

## ⚙️ Configuration

Create `config.yaml`:
```yaml
api:
  model: llama-3.3-70b-versatile
  max_tokens: 2048

voice_rules:
  tone: professional        # professional, casual, friendly
  formality: medium         # low, medium, high
  avoid_words:
    - "like"
    - "gonna"
  key_phrases:
    - "I appreciate"
    - "Looking forward to"

output:
  num_variants: 2           # Number of alternatives
  include_explanations: true
  copy_to_clipboard: true   # Auto-copy to clipboard
```

---

## 🔑 API Key Setup

### Get a Groq API Key
1. Go to https://console.groq.com/
2. Sign up for free (includes 100,000 tokens/day)
3. Navigate to API Keys
4. Copy your key

### Set Environment Variable

**Temporary** (current session only):
```bash
export GROQ_API_KEY="gsk_..."
```

**Permanent** (add to ~/.zshrc or ~/.bashrc):
```bash
echo 'export GROQ_API_KEY="gsk_..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 🐛 Troubleshooting

### `pm: command not found`
**Solution:** Add Python bin directory to PATH:
```bash
echo 'export PATH="/Users/$(whoami)/Library/Python/3.13/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### `GROQ_API_KEY not set`
**Solution:** Set your API key:
```bash
export GROQ_API_KEY="your-key-here"
```

### Rate limit exceeded
**Solution:** Groq free tier has 100,000 tokens/day. Either:
- Wait until tomorrow (limit resets)
- Upgrade to Dev Tier at https://console.groq.com/settings/billing

### Tests failing
**Solution:** Ensure dependencies are installed:
```bash
pip install -e .
python3 -m pytest tests/ -v
```

---

## 🎯 What's Next

- ✅ Core agent infrastructure
- ✅ CLI tool with message composition
- ✅ Multiple variants generation
- ✅ Feedback system with learning and adaptation
- 🔄 Subagents (ToneAnalyzer, StructureOrganizer, ClarityEnhancer)
- 📱 Telegram bot integration
- 🧠 Advanced learning (per-recipient, context-aware preferences)

---

## 🤝 Contributing

This project is designed to be educational. Feel free to:
- Fork and experiment
- Modify prompts and tools
- Add new agent capabilities
- Build integrations

See [docs/plans/](docs/plans/) for implementation roadmap.

---

## 📝 License

[Add your license here]

---

## 👤 Author

[Your name/contact info]

---

## 🙏 Acknowledgments

- Built with [Groq API](https://groq.com/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Agent pattern inspired by modern AI frameworks

---

## 📞 Support

- Check [CLAUDE.md](CLAUDE.md) for development help
- Run tests: `python3 -m pytest tests/ -v`
- See [docs/](docs/) for architecture and design decisions
