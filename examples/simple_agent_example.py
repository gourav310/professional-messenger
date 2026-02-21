"""
Simple Agent Example: The Reasoning Loop Pattern

This file demonstrates the core pattern of how an agent works using pseudocode.
It's educational - it shows the logic and flow without actual API calls.

The key concept: An agent runs a loop where it repeatedly:
1. Sends its current state to Claude
2. Receives a decision (use a tool or return answer)
3. If using a tool: executes it and loops again
4. If done: returns the answer

This pattern enables agents to think, decide, act, and iterate.
"""


# ============================================================================
# PSEUDOCODE: The Agent Reasoning Loop
# ============================================================================

def agent_loop(user_input: str, tools: list) -> str:
    """
    The core reasoning loop that makes an agent autonomous.

    This pseudocode shows the actual pattern we implement in the project.
    The real version uses the Anthropic SDK, but the logic is identical.

    Args:
        user_input: The initial user message (e.g., "Write a professional email")
        tools: List of tools Claude can choose to use

    Returns:
        The final text response from Claude

    The Loop:
        This function repeatedly:
        - Sends conversation history to Claude
        - Gets back either a tool use or final answer
        - If tool use: executes it and adds result to history
        - If final answer: returns it and stops
    """

    # Step 1: Initialize conversation history
    # This is a list of all messages exchanged in this agent session.
    # Each message is a dict with "role" (user/assistant) and "content".
    # Claude will use this entire history when deciding what to do.
    conversation = []

    # Step 2: Add initial user message
    # This kicks off the agent session.
    conversation.append({
        "role": "user",
        "content": user_input
    })
    print(f"\n[USER MESSAGE ADDED TO CONVERSATION]")
    print(f"  Content: {user_input}")
    print(f"  Conversation length: {len(conversation)}")

    # Step 3: Main reasoning loop
    # This loop continues until Claude decides to stop (no tool use).
    iteration = 0
    max_iterations = 10  # Safety limit to prevent infinite loops

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*70}")
        print(f"ITERATION {iteration}: SEND TO CLAUDE")
        print(f"{'='*70}")

        # Step 3a: Call Claude with the conversation and available tools
        # In production, this would be:
        #   response = client.messages.create(
        #       model="claude-3-5-haiku-20241022",
        #       max_tokens=1024,
        #       tools=tools,
        #       messages=conversation
        #   )
        #
        # Claude sees:
        # - The entire conversation history (all previous messages and results)
        # - The list of available tools with descriptions
        # - The current context (what's been decided so far)
        #
        # Claude returns a response that includes:
        # - stop_reason: Either "tool_use" or "end_turn"
        # - content: Text and/or tool use blocks

        print(f"\n[CALLING CLAUDE API]")
        print(f"  Model: claude-3-5-haiku-20241022")
        print(f"  Conversation history length: {len(conversation)} messages")
        print(f"  Available tools: {len(tools)} tools")
        print(f"  Tools: {[t['name'] for t in tools]}")

        # FOR THIS EXAMPLE: Simulate Claude's response
        # (In real code, this would call the actual API)
        response = simulate_claude_response(conversation, tools)

        # Step 3b: Analyze Claude's response
        print(f"\n[CLAUDE'S RESPONSE]")
        print(f"  Stop reason: {response['stop_reason']}")

        # Step 3c: Decision point - did Claude choose to use a tool?
        if response['stop_reason'] == "tool_use":
            # ================================================================
            # PATH A: Claude chose to use a tool
            # ================================================================
            print(f"\n[DECISION] Claude is using a tool (not done yet)")

            # Step 3c-i: Extract the tool Claude chose to use
            tool_use_block = response['tool_use']
            tool_name = tool_use_block['name']
            tool_input = tool_use_block['input']

            print(f"  Tool chosen: {tool_name}")
            print(f"  Tool input: {tool_input}")

            # Step 3c-ii: Add Claude's response to conversation
            # We save what Claude said/decided so it stays in context.
            # Claude's response includes the decision to use a tool.
            conversation.append({
                "role": "assistant",
                "content": response['content']
            })
            print(f"\n[CONVERSATION UPDATED]")
            print(f"  Added assistant response (with tool choice)")

            # Step 3c-iii: Execute the tool
            # This is where the agent actually DOES something (not just thinks).
            # We run the tool function with the parameters Claude provided.
            print(f"\n[EXECUTING TOOL: {tool_name}]")
            tool_result = execute_tool(tool_name, tool_input)
            print(f"  Tool result: {tool_result}")

            # Step 3c-iv: Add tool result to conversation
            # Claude will see this result in the next loop iteration.
            # It will then decide what to do next based on this new information.
            conversation.append({
                "role": "user",
                "content": f"Tool result from {tool_name}:\n{tool_result}"
            })
            print(f"\n[CONVERSATION UPDATED]")
            print(f"  Added tool result to history")
            print(f"  Conversation length now: {len(conversation)}")

            # Step 3c-v: Loop continues
            # Go back to the top of the while loop.
            # Claude will now have more information and can make a better decision.
            print(f"\n[LOOP CONTINUES]")
            print(f"  Sending updated conversation to Claude...")
            continue

        else:
            # ================================================================
            # PATH B: Claude is done - no tool use, just returning answer
            # ================================================================
            print(f"\n[DECISION] Claude is done (stop_reason == 'end_turn')")

            # Step 3d-i: Extract the final text response
            # Claude has analyzed everything and reached a conclusion.
            final_response = response['final_text']

            print(f"\n[FINAL RESPONSE FROM CLAUDE]")
            print(f"  {final_response}")

            # Step 3d-ii: Return the result and exit loop
            print(f"\n[AGENT COMPLETE]")
            print(f"  Total iterations: {iteration}")
            print(f"  Final conversation length: {len(conversation)}")
            return final_response

    # Safety fallback if we hit max iterations
    raise RuntimeError(
        f"Agent loop exceeded max iterations ({max_iterations}). "
        "This usually means the agent is stuck in a loop."
    )


# ============================================================================
# SIMULATION FUNCTIONS (for educational pseudocode)
# ============================================================================

def simulate_claude_response(conversation: list, tools: list) -> dict:
    """
    SIMULATION ONLY: Pretends to be Claude's API response.

    In real code, this would be:
        client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            tools=tools,
            messages=conversation
        )

    For this educational example, we simulate different responses to show
    how the loop handles both "use tool" and "done" scenarios.
    """

    # This is just for demonstration - showing what Claude might return
    # In a real agent, Claude would actually analyze the conversation
    # and decide intelligently what to do

    if len(conversation) == 1:
        # First iteration: Claude decides to use a tool
        return {
            "stop_reason": "tool_use",
            "content": "I'll analyze the tone of your message first.",
            "tool_use": {
                "name": "analyze_tone",
                "input": {
                    "text": conversation[0]['content']
                }
            }
        }
    else:
        # Second or later iteration: Claude has enough information
        return {
            "stop_reason": "end_turn",
            "content": "Now I have all the information I need.",
            "final_text": (
                "Based on my analysis, here's the professional version:\n\n"
                "Subject: Q1 Results - Team Achievement\n\n"
                "I'm pleased to share that our team achieved strong results in Q1. "
                "These results reflect our collective effort and focus on delivering "
                "value to our customers."
            )
        }


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    SIMULATION ONLY: Executes a tool and returns a result.

    In real code, this would dispatch to actual Python functions:
    - analyze_tone() -> analyzes emotional tone
    - structure_organizer() -> suggests message structure
    - clarity_enhancer() -> improves readability
    - etc.

    Args:
        tool_name: Name of the tool to execute
        tool_input: Parameters for the tool

    Returns:
        The result from executing the tool (as a string)
    """

    if tool_name == "analyze_tone":
        # Simulate tone analysis
        return (
            "Tone Analysis:\n"
            "- Current tone: Informal, casual\n"
            "- Recommended tone: Professional, confident\n"
            "- Key improvements:\n"
            "  1. Replace 'crushed' with 'achieved'\n"
            "  2. Add specific metrics\n"
            "  3. Emphasize team contribution"
        )

    elif tool_name == "structure_organizer":
        # Simulate structure suggestion
        return (
            "Recommended structure:\n"
            "1. Opening: Brief acknowledgment of results\n"
            "2. Key metrics: 3-5 specific numbers\n"
            "3. Team recognition: Credit the team\n"
            "4. Forward look: Next steps"
        )

    else:
        return f"Tool '{tool_name}' executed successfully"


# ============================================================================
# EXAMPLE: How to use the agent
# ============================================================================

def main():
    """
    Example of running the agent with a sample message.

    This demonstrates the complete flow:
    1. User provides unstructured thoughts
    2. Agent runs its reasoning loop
    3. Agent returns a polished, professional message
    """

    print("\n" + "="*70)
    print("SIMPLE AGENT EXAMPLE: MESSAGE COMPOSITION")
    print("="*70)

    # Define what tools the agent can use
    # In real code, these would be actual callable functions
    available_tools = [
        {
            "name": "analyze_tone",
            "description": "Analyze the emotional tone of text and suggest improvements"
        },
        {
            "name": "structure_organizer",
            "description": "Suggest the best structure for a message"
        },
        {
            "name": "clarity_enhancer",
            "description": "Improve the clarity and readability of text"
        }
    ]

    # User's unstructured input
    user_message = (
        "Hey, so like, we crushed Q1 numbers but idk how to tell the team "
        "without sounding like I'm bragging"
    )

    print(f"\n[USER INPUT]")
    print(f"  {user_message}")

    print(f"\n[AVAILABLE TOOLS]")
    for tool in available_tools:
        print(f"  - {tool['name']}: {tool['description']}")

    # Run the agent
    # This is where all the magic happens
    # The agent will loop, use tools, and refine the response
    final_message = agent_loop(user_message, available_tools)

    print(f"\n" + "="*70)
    print("AGENT COMPLETED SUCCESSFULLY")
    print("="*70)
    print(f"\nFinal professional message:")
    print(f"{final_message}")


# ============================================================================
# KEY CONCEPTS EXPLAINED
# ============================================================================

"""
WHY THIS PATTERN IS POWERFUL:

1. AUTONOMY
   The agent decides what to do. It doesn't follow a script.
   It analyzes the problem and chooses tools intelligently.

2. ITERATION
   Tools can return new information. The agent uses this to make
   better decisions. Loop enables continuous improvement.

3. FLEXIBILITY
   If circumstances change or new information appears, the agent
   adapts its approach. It doesn't get stuck in a predetermined path.

4. TRANSPARENCY
   The conversation history shows exactly how the agent thought
   through the problem. You can see every decision and tool call.

5. EXTENSIBILITY
   Want to add a new capability? Just add a new tool. The agent
   will learn to use it automatically through the tool descriptions.

WHAT HAPPENS IN EACH ITERATION:

Iteration 1:
  - Claude sees: Original user message
  - Claude thinks: "I need more context about tone"
  - Claude decides: Use analyze_tone tool
  - Result: Tone analysis

Iteration 2:
  - Claude sees: Original message + tone analysis
  - Claude thinks: "Good, now I understand the tone to use"
  - Claude thinks: "Should I structure the message? Let me organize it"
  - Claude decides: Use structure_organizer tool
  - Result: Structure suggestions

Iteration 3:
  - Claude sees: Original message + tone + structure
  - Claude thinks: "I have all the info. Let me write the final message"
  - Claude decides: No more tools needed
  - Claude returns: Final professional message

THE CONVERSATION HISTORY:

Throughout the loop, the conversation grows:

[1] User: "Hey, so like, we crushed Q1..."
[2] Assistant: "I'll analyze tone" [uses tool]
[3] User: "Tool result: Tone analysis..."
[4] Assistant: "I'll organize structure" [uses tool]
[5] User: "Tool result: Structure suggestions..."
[6] Assistant: "Here's your professional message..."

Claude can see ALL of this when making decisions.
Each response is informed by everything that came before.
This is the power of the reasoning loop.
"""


if __name__ == "__main__":
    main()
