# Incremental Learning & Feedback System

## Overview

The Professional Messenger learns from your choices to improve recommendations over time.

**Loop:**
```
1. Compose message → 2. Show variants → 3. Ask which you chose →
4. Ask why you chose it → 5. Store feedback → 6. Learn from it →
7. Next composition uses learning
```

---

## Feedback Collection Flow

```
┌────────────────────────────────────┐
│ Compose & Show Variants            │
├────────────────────────────────────┤
│                                    │
│ Primary: "I wanted to inform you"  │
│                                    │
│ Option 1: "Let me tell you"        │
│ Option 2: "I need to discuss"      │
│                                    │
└────────────┬───────────────────────┘
             │
             ↓
    ┌─────────────────────────┐
    │ Ask User:               │
    │ "Which option did you   │
    │  use or prefer?"        │
    │                         │
    │ [1] Primary             │
    │ [2] Option 1            │
    │ [3] Option 2            │
    │ [4] Edited/custom       │
    │ [5] None of above       │
    └────────┬────────────────┘
             │
             ↓
    ┌────────────────────────────────┐
    │ Ask Why?                       │
    │                                │
    │ "Why did you choose that one?" │
    │ (Open text response)           │
    │                                │
    │ User: "Too formal sounding,    │
    │  wanted warmer tone"           │
    └────────┬───────────────────────┘
             │
             ↓
    ┌────────────────────────────────┐
    │ Store Feedback                 │
    │ {                              │
    │   timestamp: "2026-02-22...",  │
    │   original_input: "hey...",    │
    │   chosen_variant: 1,           │
    │   reason: "Too formal...",     │
    │   tone_preference: "warmer"    │
    │ }                              │
    └────────┬───────────────────────┘
             │
             ↓
    ┌────────────────────────────────┐
    │ Extract Learning               │
    │                                │
    │ Pattern: "User prefers warmer  │
    │ tone than what agent produces" │
    │                                │
    │ Action: Adjust future system   │
    │ prompts to emphasize warmth    │
    └─────────────────────────────────┘
```

---

## Feedback Storage Structure

### Option 1: Separate `feedback.yaml` (Recommended)

```yaml
# feedback.yaml
feedback_entries:
  - id: "msg_001"
    timestamp: "2026-02-22T10:30:00Z"
    original_input: "hey i want tell my boss project delayed"
    variants_shown:
      - primary: "I wanted to inform you..."
      - option1: "Let me tell you..."
      - option2: "I need to discuss..."

    user_choice:
      selected: "primary"
      reason: "Direct and professional"

    extracted_learning:
      tone_preference: "direct"
      formality: "high"
      structure_preference: "key-point-first"
      style_notes: "User liked the straightforward approach"

    helpful: true  # Was this feedback useful?

  - id: "msg_002"
    timestamp: "2026-02-22T11:00:00Z"
    original_input: "we need to sync up tomorrow"
    user_choice:
      selected: "option2"
      reason: "Too formal, wanted warmer tone"

    extracted_learning:
      tone_preference: "warm"
      formality: "medium"
      feedback_for_agent: "Agent was too formal, user prefers approachable tone"

# Statistics
statistics:
  total_compositions: 2
  feedback_collected: 2
  feedback_rate: 100%

  learning_patterns:
    - tone_trend: "User prefers mix of formal + warm"
    - structure_trend: "Key point first works well"
    - formality_avg: 6.5  # on scale of 1-10
```

### Option 2: Integrated in `config.yaml`

```yaml
config.yaml

voice_rules:
  tone: "professional but approachable"
  formality: "medium"

# User's feedback patterns (auto-updated)
learned_preferences:
  tone_preferences:
    - "direct and professional" (2 times)
    - "warm and approachable" (1 time)

  formality_level: "6.5 / 10"

  structure_preference: "key-point-first"

  rejected_patterns:
    - "too formal"
    - "too wordy"

  preferred_patterns:
    - "concise"
    - "context-aware"

feedback_history: feedback.yaml  # Reference
```

---

## CLI Integration: Feedback Flow

### Current Compose Flow (Phase 1)

```bash
$ pm compose "hey project delayed"

✨ Composed Message:
   I wanted to inform you that the project timeline has shifted...

Alternative versions:

   Option 1: Let me tell you about the timeline...

   Option 2: I need to discuss something important...

✅ Copied to clipboard!
```

### Enhanced Compose Flow (Phase 2 - With Learning)

```bash
$ pm compose "hey project delayed"

✨ Composed Message:
   I wanted to inform you that the project timeline has shifted...

Alternative versions:

   Option 1: Let me tell you about the timeline...

   Option 2: I need to discuss something important...

✅ Copied to clipboard!

────────────────────────────────────────
📚 INCREMENTAL LEARNING
────────────────────────────────────────

Which option did you use or prefer?

   [1] Primary message
   [2] Option 1
   [3] Option 2
   [4] I edited/used custom version
   [5] None of the above
   [skip] Skip feedback

→ [enter choice]: 1

Why did you choose that one? (Help me learn your style)
→ Direct and professional sounding

Thanks! Your feedback helps improve future suggestions.
Stored in: feedback.yaml
```

---

## Agent Learning Integration

### System Prompt Enhancement

**Original System Prompt:**
```
You are a professional message composition expert.
Your job is to analyze unstructured thoughts and
transform them into professional messages.
```

**Enhanced System Prompt (with learning):**
```
You are a professional message composition expert.
Your job is to analyze unstructured thoughts and
transform them into professional messages.

IMPORTANT - User's Communication Style (learned from feedback):
- Tone: Direct, with warmth when appropriate
- Formality: Medium (not too stiff, not too casual)
- Structure: Lead with key point
- Preferences: Concise, context-aware
- Avoid: Over-explaining, excessive jargon

Recent patterns:
- User chose "direct" option 2 times
- User chose "warm" option 1 time
- User prefers key-point-first structure

Use this knowledge to adapt your suggestions.
```

### Dynamic System Prompt Generation

```python
def generate_system_prompt(config, feedback_stats):
    """
    Build system prompt that includes learned preferences.
    """

    base_prompt = config.voice_rules['system_base']

    # Add learned patterns
    if feedback_stats:
        learned_section = f"""

USER'S LEARNED PREFERENCES (from {feedback_stats['total_feedback']} feedback entries):
- Tone preference: {feedback_stats['tone_avg']}
- Formality level: {feedback_stats['formality_avg']} / 10
- Structure preference: {feedback_stats['structure_preference']}
- Patterns user likes: {', '.join(feedback_stats['liked_patterns'])}
- Patterns to avoid: {', '.join(feedback_stats['disliked_patterns'])}

Use this learning to better match the user's authentic voice.
        """
        return base_prompt + learned_section

    return base_prompt
```

---

## Feedback Commands

### CLI Commands (Future)

```bash
# Show feedback summary
pm feedback summary
→ Total feedback: 15 entries
→ Tone preferences: Direct (8), Warm (5), Formal (2)
→ Formality average: 6.2/10
→ Structure: Key-point-first 100%

# View feedback history
pm feedback history [--limit 5]
→ Shows last 5 feedback entries with decisions made

# Reset learning
pm feedback reset
→ Clear all feedback (start fresh learning)

# Export feedback
pm feedback export --format json
→ Export to JSON for analysis

# Adjust learned preferences manually
pm feedback adjust --tone warm --formality 5
→ Manually tweak learned preferences
```

---

## Feedback Prompt File (Alternative)

For users who prefer writing feedback separately:

```
# feedback_prompt.txt
# Add your feedback here - the agent will learn from it

FEEDBACK #1:
Message: "hey project delayed"
What worked: Direct, got straight to point
What didn't work: Felt a bit corporate
Preference: Slightly warmer tone while staying professional

FEEDBACK #2:
Message: "can we sync tomorrow"
What worked: Casual opening
What didn't work: Too casual in main body
Preference: Balance between friendly and business-like
```

Agent reads this and extracts patterns.

---

## Learning Algorithm

### Pattern Extraction

```python
def extract_learning_from_feedback(feedback_entry):
    """
    Extract patterns from user's choice and reasoning.
    """

    choice_id = feedback_entry['selected']
    reason = feedback_entry['reason']

    patterns = {
        'tone': extract_tone(reason),        # "warm", "direct", etc.
        'formality': extract_formality(reason),  # 1-10 scale
        'structure': extract_structure(reason),  # "key-first", etc.
        'liked': extract_positive(reason),       # What they liked
        'disliked': extract_negative(reason),    # What they didn't like
    }

    return patterns


def update_user_profile(feedback_entries):
    """
    Aggregate feedback into user profile.
    """

    profile = {
        'tone_preferences': [],
        'formality_level': 0,
        'structure_preference': '',
        'liked_patterns': [],
        'disliked_patterns': [],
    }

    for entry in feedback_entries:
        patterns = extract_learning_from_feedback(entry)

        # Update tone preferences
        profile['tone_preferences'].append(patterns['tone'])

        # Update formality (rolling average)
        profile['formality_level'] = (
            profile['formality_level'] * 0.7 +
            patterns['formality'] * 0.3
        )

        # Track patterns
        profile['liked_patterns'].extend(patterns['liked'])
        profile['disliked_patterns'].extend(patterns['disliked'])

    return profile
```

### Using Learning in Next Composition

```python
def compose_with_learning(user_input, feedback_history):
    """
    Compose message informed by past feedback.
    """

    # 1. Load learned preferences
    learned_profile = update_user_profile(feedback_history)

    # 2. Generate adaptive system prompt
    system_prompt = generate_system_prompt(
        config=get_config(),
        learned_preferences=learned_profile
    )

    # 3. Add learning context to user message
    enhanced_input = f"""
    User input: {user_input}

    Based on their previous feedback, this user prefers:
    - Tone: {learned_profile['tone_preferences'][-3:]}  # Last 3 choices
    - Formality: {learned_profile['formality_level']:.1f} / 10
    - Structure: {learned_profile['structure_preference']}

    Incorporate these preferences into your suggestions.
    """

    # 4. Compose with enhanced context
    result = agent.compose(
        text=enhanced_input,
        system_prompt=system_prompt
    )

    return result
```

---

## Incremental Learning Timeline

### Week 1: Initial Learning
```
Feedback entry 1: User chooses "formal"
Feedback entry 2: User chooses "casual"
Feedback entry 3: User chooses "warm"
→ Pattern emerging: Mix of tones, prefers warmth
```

### Week 2: Pattern Recognition
```
Entries 4-6: Consistently prefer "key-point-first"
Entries 7-8: Reject "over-explanation"
→ Clear structure preference identified
→ Adjust agent suggestions accordingly
```

### Week 3+: Personalization
```
Agent learns and adapts:
✓ Formality level stabilizes (e.g., 6.2/10)
✓ Tone patterns clear (e.g., "warm but direct")
✓ Structure preferences confirmed
✓ Future suggestions highly personalized
```

---

## Benefits

✅ **Personalization Over Time**: Messages get better as agent learns your style
✅ **Transparent Learning**: You see what it learns from your choices
✅ **User Agency**: You can provide feedback anytime
✅ **Feedback Loop**: Your choices guide future recommendations
✅ **Educational**: Learn how agents adapt and improve

---

## Implementation in Plan

This will be added as **Phase 3 Tasks** in the main implementation plan:

**Task 15**: Feedback Collection in CLI
- Ask which variant user chose
- Ask why they chose it
- Validate and sanitize input

**Task 16**: Feedback Storage System
- Create feedback.yaml structure
- Save feedback entries
- Manage feedback history

**Task 17**: Learning Pattern Extraction
- Parse feedback for patterns
- Update user profile
- Extract tone/formality/structure preferences

**Task 18**: Adaptive System Prompt
- Generate system prompt with learned preferences
- Pass learning to agent
- Verify learning is used

**Task 19**: Feedback Commands & Analytics
- `feedback summary` command
- `feedback history` command
- `feedback reset` command
- Statistics and reporting

---

## Example: 3-Message Learning Journey

### Message 1: Initial Composition
```
User: "hey i wnat tell boss project delayed"

Agent (generic): "I wanted to inform you that the project
timeline has shifted by two weeks."

User feedback: "Too formal sounding. I like a warmer tone."
→ Learns: tone_preference = "warm", formality = 5
```

### Message 2: Adapting
```
User: "can we sync up tomorrow"

Agent (with learning): "I'd like to connect with you tomorrow
to discuss something. Does your schedule work?"

User feedback: "Perfect! This sounds like me."
→ Learns: warmth_effective, personal_touch_good
→ Updates: tone_confidence = "warm", formality = 5.5
```

### Message 3: Personalized
```
User: "project on track but budget concerns"

Agent (highly personalized): "The project is progressing well.
I wanted to touch base about budget—I think we should chat
about options. Are you free this week?"

User feedback: "Exactly what I would say!"
→ Learns: structure_confirmed, tone_mastered
→ Profile confidence: HIGH
```

**Result**: After just 3 interactions, agent understands user's voice.

---

This incremental learning system transforms the tool from "one-off composer" to "personalized writing assistant that knows your voice."
