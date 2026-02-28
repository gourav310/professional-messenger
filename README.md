# Professional Messenger 📧

Transform unstructured thoughts into polished professional messages with AI-powered composition and adaptive learning.

**Input:** `"hey boss, project got delayed because the api was slow"`
**Output:** `"I wanted to inform you that we've encountered a delay in the project timeline due to API performance issues..."`

---

## ✨ What It Does

Professional Messenger helps you write better messages by:
1. **Analyzing** your unstructured input (tone, clarity, structure)
2. **Composing** 2-3 professional variants automatically
3. **Learning** from your feedback to adapt future messages to your style

Works for emails, Slack messages, updates to colleagues - anywhere you need professional communication.

---

## 🏗️ How It Works (Architecture)

The system uses two composition approaches:

### **Simple Mode** (Fast)
- Single LLM call with comprehensive prompt
- No tools or reasoning loop
- Best for: Quick messages, high-volume use, cost-sensitive scenarios
- Speed: ~500-800ms
- Usage: `pm compose "text" --mode=simple`

### **Agent Mode** (Thorough)
- Reasoning loop with multiple analysis steps
- Uses tools to analyze tone, structure, and clarity
- Best for: Complex messages, nuanced situations, detailed analysis
- Speed: ~1-3 seconds
- Usage: `pm compose "text" --mode=agent` (or just `pm compose "text"` - agent is default)

Both modes return the same output: primary message + 2 variants.

### **Smart Learning System**
After composing, the system asks for feedback (which variant you preferred, why). After 3+ samples, it learns your preferences (tone, formality) and automatically adapts future messages to match your style. Your preferences are stored locally in `feedback.yaml`.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free at https://console.groq.com/)

### Installation
```bash
git clone <repo-url> && cd professional-messenger
pip install -e .
export GROQ_API_KEY="your-key-here"
```

### Basic Usage
```bash
pm compose "your unstructured message"
```

**With options:**
```bash
pm compose "text" --show-variants      # See all variants
pm compose "text" --mode=agent         # Use reasoning loop (slower but thorough)
pm compose "text" --clipboard=false    # Don't copy to clipboard
pm compose "text" --config work.yaml   # Use custom config file
```

**Interactive mode:**
```bash
pm compose    # Paste multi-line messages, press Ctrl+D when done
```

---

## 📦 Features

- **Dual Composition Modes** - Choose between fast (simple) or thorough (agent) approaches
- **Multiple Variants** - Get 2-3 options to pick from
- **Adaptive Learning** - System learns your tone/formality preferences after a few messages
- **Tone Correction** - Transforms casual/informal to professional
- **Structure Improvement** - Organizes thoughts logically
- **Clarity Enhancement** - Fixes vague parts and grammar
- **Clipboard Integration** - Auto-copy best message to clipboard
- **Customizable Configuration** - Define voice rules (tone, formality, word preferences)
- **Feedback System** - Track what messages you prefer and why
- **CLI Tool** - Easy-to-use command-line interface

---

## ⚙️ Configuration

Create and customize `config.yaml`:

```bash
pm config    # Creates config.yaml from template
nano config.yaml    # Edit your preferences
```

**Key settings:**
```yaml
api:
  model: llama-3.3-70b-versatile
  max_tokens: 2048

voice_rules:
  tone: professional          # professional, casual, friendly, direct
  formality: medium           # low, medium, high
  avoid_words: ["like", "gonna"]
  key_phrases: ["I appreciate", "Looking forward"]

output:
  num_variants: 2
  copy_to_clipboard: true
```

Use different configs for different contexts:
```bash
pm compose "text" --config work-config.yaml
pm compose "text" --config personal-config.yaml
```

---

## 💬 Commands Reference

| Command | Purpose |
|---------|---------|
| `pm compose "text"` | Compose from argument |
| `pm compose` | Compose from interactive input |
| `pm compose "text" --show-variants` | Show all variants |
| `pm compose "text" --mode=agent` | Use agent mode (reasoning loop) |
| `pm compose "text" --mode=simple` | Use simple mode (single call) |
| `pm config` | Initialize/view configuration |
| `pm feedback` | View learned preferences |
| `pm feedback-reset` | Clear feedback history |
| `pm --help` | Show help |

---

## 🧠 Smart Learning System

The system learns from your choices:

```bash
pm compose "message"
# System asks: Which variant did you prefer?
# System asks: Why?
# System asks: Preferred tone/formality?

pm feedback        # After 3+ entries, see what was learned
pm feedback-reset  # Clear and start fresh
```

After 3+ feedback entries, the system automatically adapts new compositions to match your learned preferences. You'll see:
- `🧠 Adapting to your preferred [tone] tone...`

---

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Developer guide with architecture details and patterns
- **[docs/FEEDBACK_LOOP_GUIDE.md](docs/FEEDBACK_LOOP_GUIDE.md)** - Complete learning system guide
- **[docs/AGENT_FUNDAMENTALS.md](docs/AGENT_FUNDAMENTALS.md)** - Agent concepts explained
- **[docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md)** - Architecture diagrams
- **[docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md)** - Project overview

---

## 🔧 Development

**Run tests:**
```bash
python3 -m pytest tests/ -v          # All tests
python3 -m pytest tests/ --cov=src   # With coverage
```

**Manual testing:**
```bash
pm compose "test message"
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `pm: command not found` | Add Python bin to PATH: `echo 'export PATH="/Users/$(whoami)/Library/Python/3.13/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc` |
| `GROQ_API_KEY not set` | `export GROQ_API_KEY="your-key-here"` |
| Rate limit exceeded | Groq free tier: 100k tokens/day. Wait or upgrade at https://console.groq.com |
| Tests failing | Ensure dependencies installed: `pip install -e .` |

---

## 📁 Project Structure

```
professional-messenger/
├── src/
│   ├── agent.py                 # Base Agent/Tool classes
│   ├── llm_client.py            # Groq API wrapper
│   ├── config.py                # Configuration management
│   ├── cli.py                   # CLI interface
│   ├── feedback.py              # Feedback collection
│   ├── feedback_analyzer.py     # Learn from feedback
│   ├── adaptive_prompt.py       # Adapt based on learning
│   └── agents/
│       ├── message_composer.py      # Agent mode (reasoning loop)
│       └── simple_composer.py       # Simple mode (single call)
├── tests/                       # Unit tests (~29 tests)
├── docs/                        # Documentation
├── config.yaml.example          # Configuration template
└── CLAUDE.md                    # Developer guide
```

---

## 🎯 Next Steps

- ✅ Core agent infrastructure
- ✅ CLI tool with message composition
- ✅ Multiple variants generation
- ✅ Feedback system with learning
- ✅ Two composition modes (simple + agent)
- 🔄 Subagents for specialized analysis
- 📱 Telegram/Slack bot integration
- 🧠 Advanced learning (per-recipient, context-aware)

---

## 🤝 Contributing

This project is designed to be educational. Feel free to:
- Fork and experiment
- Modify prompts and system behaviors
- Add new composition modes
- Build integrations

See [docs/plans/](docs/plans/) for implementation roadmap.

---

## 📝 License

[Add your license here]

---

## 🙏 Acknowledgments

- Built with [Groq API](https://groq.com/) (fast open-source LLMs)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Agent pattern inspired by modern AI frameworks

---

## 📞 Support

- Check [CLAUDE.md](CLAUDE.md) for development help
- Run tests: `python3 -m pytest tests/ -v`
- See [docs/](docs/) for architecture and design decisions
