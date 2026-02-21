# Agent Fundamentals

## What is an Agent?

An **agent** is a program that uses an AI model (in our case, Claude) to make decisions and take actions to accomplish a goal. Unlike a simple function call or API request, agents have the ability to:

- **Think** through problems step-by-step
- **Choose** among multiple possible actions
- **Use tools** to gather information or perform tasks
- **Learn** from results and iterate
- **Reason** about when they've achieved their goal

The key insight: An agent is intelligent because it decides what to do, not because we tell it exactly what to do.

## Characteristics of Agents

1. **Autonomy**: Agents make decisions without explicit instructions for each step
2. **Tool Use**: Agents can call functions/APIs to gather data or perform actions
3. **Iterative**: Agents loop, analyze results, and make new decisions
4. **Goal-Oriented**: Agents work toward a defined objective
5. **Flexible**: Agents adapt their approach based on intermediate results

## The Reasoning Loop: How Agents Work

The core of any agent is its **reasoning loop**. This is a cycle that repeats until the agent achieves its goal.

### Simple Reasoning Loop Diagram

```
┌─────────────────────────────────────────────────────────┐
│                                                           │
│  USER: "Write a professional email about Q1 results"    │
│                                                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  ADD MESSAGE   │
        │  TO HISTORY    │
        └────────┬───────┘
                 │
                 ▼
    ┌────────────────────────┐
    │ SEND TO CLAUDE WITH    │
    │ TOOLS & CONVERSATION   │
    │ HISTORY                │
    └────────┬───────────────┘
             │
             ▼
    ┌─────────────────────┐
    │ CLAUDE RESPONDS     │
    │ WITH:               │
    │ - Text             │
    │ - Tool choice      │
    │ - Stop reason      │
    └────────┬────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ DID CLAUDE CALL A TOOL?  │
    └────┬───────────────┬─────┘
         │ YES           │ NO
         ▼               ▼
    ┌──────────┐    ┌────────────┐
    │ EXECUTE  │    │ RETURN     │
    │ THE TOOL │    │ FINAL TEXT │
    │          │    │ RESPONSE   │
    └────┬─────┘    └────────────┘
         │               (END)
         ▼
    ┌─────────────┐
    │ ADD RESULT  │
    │ TO HISTORY  │
    └────┬────────┘
         │
         ▼
    ┌──────────────────┐
    │ LOOP AGAIN       │
    └──────────────────┘
```

### Step-by-Step Explanation

1. **Initialize Conversation**: Start with an empty conversation history
2. **Add User Message**: User input becomes the first message
3. **Call Claude API**: Send the conversation and available tools to Claude
4. **Claude Reasons**: Claude analyzes the problem and decides:
   - Should I call a tool? (e.g., look up data, run code)
   - Or should I give a final answer?
5. **Check Response**:
   - If `stop_reason == "tool_use"`: Claude chose a tool
   - Otherwise: Claude is ready with a final answer
6. **If Tool Called**:
   - Execute the tool with the parameters Claude specified
   - Add both Claude's response and the tool result to conversation history
   - Go back to step 3 (call Claude again with new information)
7. **If No Tool Called**:
   - Extract the text response
   - Return it as the final answer
   - Loop ends

## Key Concepts

### Reasoning Loop

The **reasoning loop** is the heartbeat of any agent. It's the cycle that allows an agent to think, decide, act, and learn. Here's why it's so powerful:

- **Without a loop**: You ask Claude a question, get an answer, done
- **With a loop**: Claude can say "I need more information" and ask for it, then continue reasoning with that information

Example: If asked "What's the best email structure for a business proposal?", Claude might:
1. Decide: "I need to check what format the recipient prefers"
2. Call a tool: `get_email_preferences("recipient@company.com")`
3. Receive: "They prefer concise, bulleted formats"
4. Decide: "Now I have the info, I can write the email"
5. Return: The well-formatted email

### Tool Use (Function Calling)

A **tool** is any external capability that Claude can call. In the Anthropic SDK, tools are functions with:
- A name (how Claude refers to it)
- A description (why Claude should use it)
- Parameters (what information Claude needs to provide)

Example tool:

```python
{
    "name": "analyze_tone",
    "description": "Analyze the emotional tone of text and suggest improvements",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text to analyze"
            }
        },
        "required": ["text"]
    }
}
```

When Claude decides to use this tool, it provides the `text` parameter. Your code executes the actual function and returns the result. Claude then sees this result and continues reasoning.

### Context Window

The **context window** is the amount of conversation history that Claude can see when making decisions. Each call to the API includes:
- Previous messages (both user and assistant)
- All tool results from previous steps
- The current user message

This is why we maintain `conversation` history in the loop. Claude learns from everything that's happened so far in this agent session.

Example timeline:
1. User: "Analyze this email"
2. Claude: "I'll use the analyze_tone tool"
3. Tool: Returns tone analysis
4. Claude: (can now see: original request + analysis) "The tone is too harsh. I'll suggest changes"
5. User: Sees the suggestion

### Subagents

A **subagent** is a specialized agent that handles one part of a larger task. Instead of one agent doing everything, you can have:

- **Primary Agent**: "Message Composer" - orchestrates the overall task
- **Subagent 1**: "Tone Analyzer" - specializes in analyzing emotional tone
- **Subagent 2**: "Structure Organizer" - specializes in message organization
- **Subagent 3**: "Clarity Enhancer" - specializes in readability

Why use subagents?
- **Specialization**: Each agent is an expert in its domain
- **Modularity**: Easy to update or replace one subagent
- **Clear Responsibilities**: Each agent has one job
- **Reusability**: Subagents can be used by multiple primary agents

In this project:
- The Message Composer Agent will orchestrate the process
- It will call specialized subagents for analysis and enhancement
- Each subagent runs its own reasoning loop
- Results flow back to the primary agent

## Example: Message Composition Agent

Let's walk through how our Message Composer Agent thinks about transforming a user's thoughts into a professional message.

### Scenario
User input: "Hey, so like, we crushed Q1 numbers but idk how to tell the team without sounding like I'm bragging"

### Agent's Thought Process

#### Step 1: User's Request Added to History
The agent receives this messy, informal input.

#### Step 2: Claude Reasons
Claude thinks: "This person has good news but wants to communicate it professionally. They need:
1. A structured message format
2. A confident but not arrogant tone
3. Clear, actionable language"

Claude's decision: "I should call the tone_analyzer subagent first to understand what tone would work best"

#### Step 3: Tone Analyzer Called
The agent calls: `tone_analyzer("We had strong Q1 results and want to communicate them professionally")`

Tone Analyzer returns:
```
{
  "current_tone": "informal, uncertain",
  "recommended_tone": "confident, inclusive, data-driven",
  "specific_tips": [
    "Use 'we achieved' instead of 'we crushed'",
    "Focus on team effort, not individual credit",
    "Lead with specific numbers/metrics"
  ]
}
```

#### Step 4: Claude Continues Reasoning
Claude now knows the target tone. It thinks: "Now I should structure the message using these insights"

Claude's decision: "I should call the structure_organizer subagent"

#### Step 4: Structure Organizer Called
The agent calls: `structure_organizer("Q1 results announcement", tone="confident, inclusive, data-driven")`

Structure Organizer returns:
```
{
  "recommended_structure": [
    "Opening: Brief celebration of results",
    "Body: Specific metrics (should include 3-5 key numbers)",
    "Team recognition: Credit shared efforts",
    "Forward look: What this means for Q2"
  ],
  "template": "See detailed template in response"
}
```

#### Step 5: Claude Generates Message
Claude now has:
- Original request
- Tone guidance
- Structure template

Claude generates:
```
Subject: Q1 Results - Team Achievement

I'm pleased to share that our team achieved strong results in Q1:
- Revenue: 15% above target
- Customer satisfaction: 92% (up from 87%)
- New product adoption: 8,500 customers

These results reflect our collective effort and focus. Each of you contributed to this success.

As we move into Q2, we're well-positioned to build on this momentum...
```

#### Step 6: Claude Checks Quality
Claude decides: "This could be even more polished. I should call the clarity_enhancer"

#### Step 7: Clarity Enhancer Called
Claude calls: `clarity_enhancer(draft_message)`

Clarity Enhancer returns:
```
{
  "suggestions": [
    "Add specific deadline for Q2 goals",
    "Strengthen final sentence with action items"
  ],
  "readability_score": 8.5,
  "improved_version": "Final polished version..."
}
```

#### Step 8: Final Response
Claude returns the final, polished message ready to send.

### Key Insights from This Example

1. **Claude Made Decisions**: It chose which tools to call and in what order
2. **Iterative Process**: Each tool provided information that influenced the next decision
3. **Subagent Specialization**: Each subagent was an expert in its domain
4. **Conversation History Matters**: Claude could reference all previous steps
5. **Quality Checking**: Claude even decided to run an extra quality check

This is exactly what makes agents powerful—they think and decide, they don't just follow scripts.

## In This Project

### Our Agent Architecture

```
┌────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│              (User types unstructured thought)           │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Message Composer Agent     │
        │ (Primary Agent - runs      │
        │  reasoning loop)           │
        └────────┬────────────────────┘
                 │
        ┌────────┴────────┬───────────────┬──────────────┐
        │                 │               │              │
        ▼                 ▼               ▼              ▼
   ┌─────────┐      ┌──────────┐   ┌──────────┐   ┌───────────┐
   │  Tone   │      │Structure │   │ Clarity  │   │Validation │
   │Analyzer │      │Organizer │   │ Enhancer │   │  Subagent │
   │Subagent │      │Subagent  │   │Subagent  │   │           │
   └─────────┘      └──────────┘   └──────────┘   └───────────┘
        │                 │               │              │
        └────────┬────────┴───────────────┴──────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Professional Message  │
        │      (Delivered)        │
        └────────────────────────┘
```

### What You'll Learn

By studying agents in this project, you'll understand:

1. **How Claude Powers Autonomy**: Using tool use and the reasoning loop
2. **Subagent Architecture**: Building specialized agents that work together
3. **Claude API Patterns**: How to structure calls for tool use
4. **Iteration and Refinement**: How agents improve through loops
5. **Real-World Application**: Building a practical system that transforms thoughts into professional communication

### Where to Go Next

- **See it in action**: Check `examples/simple_agent_example.py` for a pseudocode walkthrough
- **Learn tool use**: See Task 6 for the actual reasoning loop implementation
- **Build subagents**: Tasks 7-8 show how to create specialized agents

---

## Quick Reference: The Reasoning Loop in 30 Seconds

```
while agent_not_done:
    1. Add user message to conversation history
    2. Send conversation + tools to Claude
    3. Get response from Claude
    4. If Claude called a tool:
       a. Execute the tool
       b. Add result to history
       c. Loop again
    5. Else:
       a. Return Claude's text response
       b. Done
```

Remember: Agents are powerful because they **think** about what to do, not because they follow a predetermined path.
