# Feedback Loop & Learning System

Professional Messenger includes a **learning system** that adapts to your preferences over time. After you compose a few messages and provide feedback, the system learns your style and future compositions automatically adapt to match your preferences.

## Overview

The feedback system is built on three core components:

1. **Feedback Collection**: Captures your preferences after each message composition
2. **Pattern Analysis**: Analyzes your feedback to identify dominant preferences
3. **Adaptive Composition**: Tailors future messages to match your learned style

## How It Works

### Phase 1: Compose a Message

```bash
pm compose "hey project delayed"
```

Results in 3 variants:
- [1] Formal: "Dear [recipient], I wanted to inform you that the project has experienced a delay..."
- [2] Balanced: "Hi, I wanted to let you know the project got delayed..."
- [3] Direct: "Project delayed."

### Phase 2: Provide Feedback

After composition, you're asked:

```
Which variant did you prefer? (1/2/3): 2
Why did you choose it? (optional): good balance of casual and professional
What's your preferred tone? (1=formal, 2=professional, 3=balanced, 4=casual): 2
What's your preferred formality? (1=low, 2=medium, 3=high): 2
```

### Phase 3: System Learns Your Pattern

After 3+ feedback samples, the system analyzes:
- Which tone you prefer (professional vs balanced vs casual)
- Your formality level preference (low, medium, or high)
- Which variant style you typically choose (formal, balanced, or direct)

For example, if your last 3 choices were all variant #2 (balanced) with tone preference "balanced" and formality "medium", the system identifies this pattern.

### Phase 4: Next Compositions Adapt

Future compositions are biased toward your preferences:

```
[1] Professional / [2] Very Balanced ✓ / [3] Direct
```

The LLM sees your learned preferences in the system prompt and generates variants that match your style.

## Viewing Your Preferences

See what the system has learned:

```bash
pm feedback
```

Output example:
```
Feedback Summary
════════════════════════════════════════════════════════════════════════════

Total samples collected: 5

Tone Preferences:
  balanced:      3 times (60%)
  professional:  2 times (40%)

Formality Preferences:
  medium:  5 times (100%)

Variant Preferences:
  Balanced [1]:  4 times (80%)
  Formal [0]:    1 time  (20%)

Dominant Pattern:
  Tone: balanced (confidence: 60%)
  Formality: medium (confidence: 100%)
  Most-chosen variant: Balanced

Confidence: Good! System has strong signal for adaptation.
```

## Resetting Your Learning

If you want the system to forget your preferences and start fresh:

```bash
pm feedback-reset
```

This clears all feedback data. The system returns to default behavior for future compositions.

## How the System Adapts

### Without Learning

```
System Prompt: "Generate 3 professional message variants (formal, balanced, direct).
Use different tones to give the user options..."
```

LLM generates variants with all possible tones equally.

### With Learning

```
System Prompt: "Generate 3 professional message variants (formal, balanced, direct).
Use different tones to give the user options.

LEARNED PREFERENCES (from user feedback):
Based on past feedback, the user prefers a balanced tone.
The user prefers medium formality (professional but approachable language).
Apply this to all message variants.
..."
```

LLM sees these preferences and biases all variants toward balanced tone and medium formality.

## Practical Examples

### Example 1: Executive Communication

You consistently choose balanced variants with high formality.

**Without learning:**
- Formal: "Dear [Recipient], I am writing to inform you..."
- Balanced: "Hi, I wanted to let you know..."
- Direct: "FYI, deadline extended."

**With learning (after 5 samples):**
- Formal: "Thank you for reaching out. I wanted to share an update..."
- Balanced: "Thanks for your patience. Here's an important update..." ✓
- Direct: "Update: Deadline extended to Friday."

The system shifts variant 2 (balanced) toward your formality preference while keeping variety.

### Example 2: Casual Team Communication

You consistently choose balanced/direct variants with low formality.

**Without learning:**
- Formal: "I would appreciate if you could consider..."
- Balanced: "Hey, could you check this out?..."
- Direct: "FYI"

**With learning (after 5 samples):**
- Formal: "Quick note—thought you'd want to know..."
- Balanced: "Hey! Wanted to give you a heads up..." ✓
- Direct: "Heads up: thing happened!"

The system shifts all variants toward casual tone while maintaining variant distinction.

## FAQ

**Q: Do I have to provide feedback?**
A: No, feedback is optional. The `pm compose` command works perfectly fine without it. Feedback is entirely voluntary—use it if you want the system to learn your style.

**Q: How many samples does the system need to start learning?**
A: The system learns from the first sample. However:
- 1-2 samples: Very low confidence (may be coincidence)
- 3-5 samples: Emerging pattern (useful for adaptation)
- 5-10 samples: Good confidence (reliable adaptation)
- 10+ samples: High confidence (strong signal)

The system tracks confidence and only adapts when confidence exceeds a threshold (default 50%).

**Q: Can I have different preferences for different modes?**
A: Currently, feedback is combined across all modes. However, you can manually maintain separate feedback files by:

```bash
cp feedback.yaml feedback-work.yaml
pm compose "message" --config work-config.yaml
```

Future versions may support mode-specific feedback.

**Q: Will the system force me to use my learned preferences?**
A: No! Feedback influences the system prompt, but the LLM still generates all three variants. You always have full choice, but the variants will be biased toward your style.

**Q: What if my preferences change over time?**
A: Keep providing feedback. The system uses frequency analysis, so new feedback gradually shifts the pattern. If you want to reset and start fresh, use `pm feedback-reset`.

**Q: How accurate is the learning?**
A: Simple but effective. The system uses frequency counting and confidence scoring:
- Tracks which tone/formality you choose most often
- Calculates confidence as a percentage (e.g., "80% of choices were balanced tone")
- Only adapts when confidence > 50%

This works well after 5-10 samples. For 20+ samples, the pattern becomes very stable.

**Q: Can I export my feedback history?**
A: Yes! Feedback is stored in `feedback.yaml` (in your project or home directory). You can:

```bash
cat feedback.yaml  # View raw YAML
cp feedback.yaml backup-$(date +%Y%m%d).yaml  # Backup
```

**Q: What if I want to see the adapted system prompt?**
A: You can use the internal API:

```python
from src.feedback_analyzer import FeedbackAnalyzer
from src.feedback import FeedbackCollector
from src.adaptive_prompt import AdaptivePromptGenerator

collector = FeedbackCollector()
analyzer = FeedbackAnalyzer(collector.get_all())
dominant = analyzer.get_dominant_preferences()

adapter = AdaptivePromptGenerator(
    preferred_tone=dominant["tone"],
    preferred_formality=dominant["formality"],
    confidence=analyzer.confidence("tone")
)

adapted = adapter.adapt_prompt("Base system prompt...")
print(adapted)
```

**Q: Does feedback affect my message content, or just the variants?**
A: Only the variants. Your original message is never modified. Feedback influences how the LLM generates the 3 professional variants, not your input.

**Q: Are my preferences stored securely?**
A: Preferences are stored locally in `feedback.yaml`. They are:
- NOT sent to any external service
- NOT shared
- Only used by the local system prompt adaptation

Your feedback history is completely private.

## Advanced: Understanding Confidence Scores

The system calculates confidence for each preference:

```
Tone Confidence = (count of dominant tone) / (total feedback samples)
```

Example:
- Last 5 feedback samples: [balanced, balanced, balanced, professional, balanced]
- Balanced chosen: 4 times
- Confidence: 4/5 = 80%

The `confidence_threshold` (default 50%) determines whether to adapt:
- Confidence ≥ 50%: System will adapt
- Confidence < 50%: System won't adapt (too uncertain)

You can adjust this threshold in code:

```python
from src.adaptive_prompt import AdaptivePromptGenerator

adapter = AdaptivePromptGenerator(
    preferred_tone="balanced",
    confidence=0.6,
    confidence_threshold=0.7  # Require 70% confidence
)
```

## Integration with Your Workflow

### Quick Start

1. Compose a message normally:
   ```bash
   pm compose "your message"
   ```

2. Choose your preferred variant and provide optional feedback

3. After 5-10 compositions with feedback, check your pattern:
   ```bash
   pm feedback
   ```

4. Future compositions will adapt automatically

### For Different Personas

If you send different types of messages, you might want separate feedback:

```bash
# Work communication (formal, professional)
mkdir -p work-config
pm compose "project update" --config work-config/

# Personal messages (casual, friendly)
mkdir -p personal-config
pm compose "catching up soon" --config personal-config/
```

(Note: This is a manual workaround. Full multi-persona support coming in future versions.)

## Troubleshooting

**"System isn't adapting even though I've given feedback"**
- Check confidence: `pm feedback`
- Confidence must be ≥ 50% for adaptation
- Provide 2-3 more consistent feedback samples

**"Adapted prompts look weird or contain errors"**
- This indicates inconsistent feedback patterns
- Try a few more samples with clear preferences
- Or reset with `pm feedback-reset` to start fresh

**"I can't find my feedback.yaml file"**
- Default location: current working directory
- Check: `ls -la feedback.yaml`
- It's created after first feedback submission

**"Feedback isn't being saved"**
- Verify write permissions in current directory
- Check for error messages when providing feedback
- Try providing feedback again with explicit paths if needed

## See Also

- [AGENT_FUNDAMENTALS.md](AGENT_FUNDAMENTALS.md) - How agents work
- [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) - System architecture
- [README.md](../README.md) - Quick start guide
