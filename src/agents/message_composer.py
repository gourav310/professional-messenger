"""
Message Composer Agent - Main orchestrating agent for message composition.

This agent demonstrates key agent concepts:
1. IDENTITY: Name and system prompt that define behavior
2. TOOLS: Functions the agent can call to accomplish tasks
3. REASONING LOOP: The core pattern that makes agents autonomous

THE REASONING LOOP (the key concept):
════════════════════════════════════════════════════════════════════════════

The agent reasoning loop is the core pattern that makes agents powerful.
Instead of the programmer deciding "first analyze tone, then structure,
then clarity", the agent (Claude) looks at the task and decides what it
needs. This adaptive decision-making is what makes agents intelligent.

Here's the loop in detail:

┌─────────────────────────────────────────────────────────────────────────┐
│                           REASONING LOOP                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Step 1: TAKE INPUT                                                    │
│  ────────────────────                                                  │
│  User provides raw message: "hey i need tell boss the project delayed" │
│  This is unstructured, possibly informal, unclear                       │
│                                                                          │
│  Step 2: PRESENT CLAUDE WITH TOOLS                                     │
│  ──────────────────────────────────                                    │
│  Agent creates message to Claude saying:                               │
│  "Here's a message someone wrote. Tools available: analyze_tone,       │
│   suggest_structure, check_clarity. What should you do?"               │
│                                                                          │
│  Step 3: CLAUDE DECIDES (THE AUTONOMOUS PART)                          │
│  ───────────────────────────────────────────────                       │
│  Claude reads the message and tools, then decides:                     │
│  - "This has tone issues (too informal, rushed)"                       │
│  - "This needs structure (missing context, unclear impact)"            │
│  - "This has clarity issues (which boss? when? why delayed?)"          │
│  → Claude decides: "I'll use analyze_tone and check_clarity first"     │
│                                                                          │
│  Step 4: CLAUDE CALLS TOOLS                                            │
│  ───────────────────────────                                           │
│  Claude returns (in this iteration):                                   │
│  Tool call 1: analyze_tone(text="hey i need tell...", target="formal") │
│  This is just a declaration - we need to execute it                    │
│                                                                          │
│  Step 5: WE EXECUTE THE TOOL                                           │
│  ──────────────────────────                                            │
│  Agent (Python code) runs: tool_result = analyze_tone(...)             │
│  Result: "Current tone is too informal and rushed. Too many            │
│           abbreviations. Needs professional vocabulary."               │
│                                                                          │
│  Step 6: ADD RESULT TO CONVERSATION                                    │
│  ────────────────────────────────────                                  │
│  Conversation history now has:                                         │
│  1. User message: "Analyze this message..."                            │
│  2. Assistant response: "I'll use analyze_tone..."                     │
│  3. User adds result: "analyze_tone result: tone is too informal..."   │
│                                                                          │
│  Step 7: LOOP CONTINUES (CLAUDE REFINES)                               │
│  ──────────────────────────────────────                                │
│  Claude now sees:                                                       │
│  - The original message                                                │
│  - The tone analysis result                                            │
│  Claude thinks: "Now I know the tone issues. Let me check clarity."    │
│  Claude decides: "I'll use check_clarity tool"                         │
│  Claude calls: check_clarity(message="hey i need tell...")             │
│                                                                          │
│  Step 8: EXECUTE NEXT TOOL                                             │
│  ──────────────────────────                                            │
│  Result: "Clarity issues: 'boss' doesn't specify which boss, 'delayed' │
│           lacks context for how long, no explanation of reasons."      │
│                                                                          │
│  Step 9: LOOP CONTINUES AGAIN                                          │
│  ───────────────────────────                                           │
│  Claude now has tone AND clarity analysis. It decides:                 │
│  "I have enough information. I can now compose professional variants." │
│  Claude returns TEXT (no more tools): "Here are 3 professional versions" │
│                                                                          │
│  Step 10: LOOP ENDS (FINAL ANSWER)                                     │
│  ──────────────────────────────────                                    │
│  Agent sees text output (no tool call), extracts the answer,           │
│  and returns it to the user.                                           │
│                                                                          │
│  REAL EXAMPLE OUTPUT:                                                  │
│  ═════════════════════════                                             │
│  "Professional Version 1:                                              │
│   I wanted to inform you that the project timeline has been affected  │
│   and we need to discuss revised delivery dates.                      │
│                                                                          │
│   Professional Version 2:                                              │
│   Due to unexpected circumstances, we've encountered a delay in the   │
│   project schedule. I'd like to brief you on the details and new     │
│   timeline at your earliest convenience."                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

KEY INSIGHT: WHY THIS IS POWERFUL
═════════════════════════════════════════════════════════════════════════

Traditional programming (if you had to do it):
  1. Always analyze tone (even if not needed)
  2. Always check structure (even if already good)
  3. Always verify clarity (even if crystal clear)
  → Inefficient, same steps for every message, rigid

Agent reasoning loop:
  1. Claude looks at input and available tools
  2. Claude decides which tools are relevant
  3. Claude calls only needed tools
  4. Claude iterates based on results
  5. Claude stops when satisfied
  → Adaptive, efficient, intelligent

The agent doesn't blindly apply all steps. Instead, it's like having
a human expert who:
- Looks at the problem
- Decides what analysis is needed
- Gathers information
- Synthesizes a solution
- Iterates when needed

This is why agent architecture is powerful - it mirrors human reasoning.

WHY NOT JUST CALL TOOLS DIRECTLY?
═════════════════════════════════════════════════════════════════════════

You might think: "Why not just call analyze_tone(), then suggest_structure(),
then check_clarity() in sequence?"

Problems with that approach:
1. INEFFICIENT: You do analysis that's not needed
2. RIGID: Same process for every input
3. NOT INTELLIGENT: Doesn't adapt to context
4. POOR ORDER: Maybe you need structure first, then tone?
5. MISSING ITERATION: Maybe first result suggests you need more analysis?

With the reasoning loop:
1. Claude looks at the input
2. Claude decides order and what's needed
3. Claude iterates based on results
4. Claude stops when ready
5. Claude adapts to different inputs differently

DESIGN PHILOSOPHY: HYBRID ARCHITECTURE
═════════════════════════════════════════════════════════════════════════

This implementation uses HYBRID architecture:
- Tools are SIMULATED (not separate agents)
- The main agent (Claude) orchestrates
- Tools are functions we execute directly
- Results feed back to Claude for reasoning

Why hybrid instead of full agent hierarchy?
- Simpler to implement
- Easier to understand the reasoning loop
- Still demonstrates autonomous decision-making
- Production-ready approach

In the future, tools could be:
- Real API calls to external services
- Separate specialized agents
- Database lookups
- Actual NLP models

The key: Claude still decides when and how to use them!
"""

from typing import Optional
from src.agent import Agent, Tool
from src.llm_client import LLMClient


class MessageComposerAgent(Agent):
    """
    Main agent that orchestrates message composition through reasoning loop.

    This agent demonstrates the core agent pattern:
    - Has an IDENTITY (name "MessageComposer", specific system prompt)
    - Has TOOLS (functions it can call to gather information)
    - Uses a REASONING LOOP (decides what to do, iterates based on results)

    The agent takes unstructured input from the user and:
    1. Analyzes tone issues (is it too formal/informal/aggressive?)
    2. Suggests structure improvements (what should come first/middle/end?)
    3. Checks clarity (what's ambiguous or missing?)
    4. Synthesizes into polished message variants (multiple versions)

    KEY DESIGN: The agent doesn't pre-decide what to do. Instead:
    - Available tools are presented to Claude
    - Claude looks at the specific input
    - Claude decides which tools to use
    - Claude iterates based on results
    - Claude returns final answer when ready

    This makes the agent ADAPTIVE and INTELLIGENT, not just procedural.

    REASONING LOOP IN ACTION:
    ════════════════════════════════════════════════════════════════════════

    Input:  "hey i wnat tell my boss project delayed"
                                    (informal, unclear, has typo)

    Loop Iteration 1:
    ─────────────────
    Claude sees: raw message + available tools (analyze_tone, suggest_structure,
                 check_clarity)
    Claude thinks: "This message has tone issues (informal), structure problems
                   (missing context), and clarity issues (vague)"
    Claude decides: "I need to analyze tone and check clarity"
    Claude calls: analyze_tone(text="hey i wnat...", target_tone="professional")
    Tool returns: "Current tone: informal/rushed. Too many abbreviations. No
                   professionalism markers. Missing context. Suggestion: Slow
                   down, use complete words, add details."

    Loop Iteration 2:
    ─────────────────
    Claude sees: original message + tone analysis + available tools
    Claude thinks: "Now I understand the tone issues. Let me check clarity."
    Claude decides: "I'll use check_clarity tool"
    Claude calls: check_clarity(message="hey i wnat...")
    Tool returns: "Clarity issues: (1) Missing which boss, (2) No timeline,
                   (3) No explanation of why, (4) 'wnat' typo. Suggest:
                   Specify recipient, be explicit about timeline, explain
                   reasons, fix typos."

    Loop Iteration 3:
    ─────────────────
    Claude sees: original message + tone analysis + clarity analysis + tools
    Claude thinks: "I have good analysis now. Time to compose variants."
    Claude decides: "I have enough information. Let me synthesize professional
                    message variants."
    Claude returns: TEXT (not tool use) with 3 message variants:
      Variant 1 (Formal):
        "I need to inform you that the project has encountered delays..."
      Variant 2 (Friendly-Professional):
        "I wanted to update you on the project status - we've hit a few
         snags with timing..."
      Variant 3 (Direct):
        "The project timeline has shifted. We need to reschedule our
         delivery date..."

    Loop ends: Claude returned text, not a tool call. Agent extracts answer
    and returns to user.

    TOTAL ITERATIONS: 3 (analyze tone, check clarity, compose)
    Claude decided the order and what was needed - not pre-programmed!

    WHAT MAKES THIS POWERFUL:
    ═════════════════════════

    For different inputs, the agent loops differently:

    Input 2: "The project has been delayed"
             (already professional, but unclear)

    Loop would be:
    1. Claude sees: Already professional tone
    2. Claude decides: Skip tone analysis, focus on clarity
    3. Claude: check_clarity()
    4. Claude: compose()
    Total: 2 iterations (more efficient!)

    Input 3: "I'm concerned about the timeline, boss is waiting"
             (good tone, but structure needs work)

    Loop would be:
    1. Claude sees: Good tone, but structure issues
    2. Claude decides: Skip tone, do structure analysis
    3. Claude: suggest_structure()
    4. Claude: compose()
    Total: 2 iterations (different path!)

    Same agent, different logic paths based on input. That's adaptation.

    IMPLEMENTATION DETAILS:
    ═════════════════════════

    The agent:
    - Extends the base Agent class (has name, system_prompt, tools)
    - Uses LLMClient to communicate with Claude
    - Implements _setup_tools() to define what tools are available
    - Implements compose() to run the reasoning loop
    - Implements _execute_tool() to simulate tool execution

    The reasoning loop (compose method):
    1. Initialize conversation history (empty list)
    2. Add user's raw message as initial prompt
    3. Loop until Claude returns text (not tool use):
       a. Call Claude with current conversation + available tools
       b. Check if Claude called a tool or returned text
       c. If tool: execute it, add result to conversation, loop again
       d. If text: extract answer, return to user
    4. Return structured result with primary + variants

    TESTING:
    ════════

    Tests verify:
    - Agent initializes with correct name and system prompt
    - Agent has required tools (analyze_tone, suggest_structure, check_clarity)
    - Agent can be called with api_key parameter

    Production tests would verify:
    - compose() returns proper format
    - Reasoning loop executes correctly
    - Tool results integrate properly
    - Multiple iterations work correctly

    Example:
        >>> agent = MessageComposerAgent(api_key="sk-...")
        >>> result = agent.compose("hey project delayed")
        >>> print(result["primary"])
        # "I wanted to update you that the project timeline has shifted..."
        >>> print(result["variants"])
        # ["Alternative 1...", "Alternative 2..."]

    The agent uses the LLMClient to communicate with Claude and manages
    the reasoning loop internally through the compose() method.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Message Composer Agent.

        This sets up the agent with:
        1. Identity (name and system prompt)
        2. Capabilities (tools for analysis)
        3. Communication client (LLMClient for Claude interaction)

        The initialization doesn't do any work yet - it just sets up the
        agent's configuration. The actual composition happens when
        compose() is called.

        WHY THIS DESIGN:
        ════════════════
        Separating initialization from execution allows:
        - Creating agent once, using multiple times
        - Testing agent setup separately from execution
        - Reusing same agent across requests
        - Configuring agent before using

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY env var.
                    This is how we authenticate with Groq.
                    Format: starts with "gsk-" for Groq API keys
                    Example: "gsk-proj_1234567890..."
                    If not provided, LLMClient will look for GROQ_API_KEY
                    environment variable.

        Raises:
            ValueError: (from LLMClient) If neither api_key parameter nor
                       GROQ_API_KEY environment variable is available.

        Example:
            >>> # Using environment variable (recommended for production)
            >>> agent = MessageComposerAgent()
            >>>
            >>> # Using explicit API key (for testing/scripts)
            >>> agent = MessageComposerAgent(api_key="sk-...")
        """

        # Define the system prompt
        # ═════════════════════════════════════════════════════════════════
        # WHY SYSTEM PROMPT IS CRITICAL:
        # The system prompt is the agent's "personality" and "instructions".
        # It tells Claude:
        # - What role to play ("You are a professional message composer")
        # - What to focus on (maintaining authentic voice, professionalism)
        # - How to behave (analyze before synthesizing, provide variants)
        # - What success looks like (polished messages that sound natural)
        #
        # A good system prompt:
        # - Gives clear role definition
        # - Explains the goal
        # - Provides principles to follow
        # - Shows examples if possible
        #
        # Claude reads this and follows it throughout the reasoning loop.
        # =================================================================

        system_prompt = """You are a professional message composition expert.

YOUR ONLY JOB: Transform user's raw message into 2-3 professional variants.

STRICT PROCESS (follow exactly):
1. User gives raw message
2. Call analyze_tone ONCE on the raw message
3. Wait for result
4. THEN compose and return final variants

DO NOT:
- Call tools more than once per original message
- Analyze variants - only analyze the ORIGINAL message
- Repeat tool calls on similar content
- Call multiple tools on the same content

WHEN TO RETURN FINAL ANSWER:
Return immediately with professional variants after:
- Calling analyze_tone once on the original message
- Getting the tone analysis result
- Composing variants based on that analysis

FORMAT YOUR FINAL ANSWER AS:
Professional Message 1: [variant 1]
Professional Message 2: [variant 2]
Professional Message 3: [variant 3]

REMEMBER: Your success = delivering message variants, not analysis perfection."""

        # Initialize parent Agent class
        # ═════════════════════════════════════════════════════════════════
        # The parent Agent class (in src.agent) provides:
        # - name attribute (stores agent identifier)
        # - system_prompt attribute (stores instructions for Claude)
        # - tools list (stores available capabilities)
        # - add_tool() method (registers new tool)
        # - get_tools_for_api() method (formats tools for Claude)
        #
        # By calling super().__init__(), we:
        # - Set up the base agent infrastructure
        # - Pass our system prompt (what makes us different from other agents)
        # - Initialize with empty tools list (we'll add tools next)
        # =================================================================

        super().__init__(
            name="MessageComposer",
            # Why "MessageComposer": Clear, specific role identifier
            # Used in logging, debugging, configuration
            # Other agents might be named: "ToneAnalyzer", "GrammarChecker"

            system_prompt=system_prompt
            # Why pass system_prompt: Defines how this agent behaves
            # Different from other agents because of this prompt
            # This is what makes "MessageComposerAgent" different
        )

        # Initialize the LLM Client
        # ═════════════════════════════════════════════════════════════════
        # The LLMClient is the "translator" between our Python code and
        # Groq's API. It:
        # - Manages the Groq SDK
        # - Formats messages for Groq
        # - Sends requests to Groq
        # - Parses responses
        # - Extracts tool calls or text answers
        #
        # We store it as self.llm_client so we can use it later in compose()
        # to communicate with Groq during the reasoning loop.
        #
        # The api_key (or GROQ_API_KEY env var) is passed to LLMClient,
        # which handles authentication with Groq.
        #
        # LLMClient will try to find GROQ_API_KEY env var if api_key is None.
        # =================================================================

        try:
            self.llm_client = LLMClient(api_key=api_key)
        except ValueError:
            # If initialization fails, set to None
            # This allows agent creation for testing tool setup,
            # but compose() will fail with clear error
            self.llm_client = None
        # Store the client for use in compose()

        # Set up the tools this agent can use
        # ═════════════════════════════════════════════════════════════════
        # Tools are what make this agent powerful. Without tools:
        # - Agent can only provide generic advice
        # - Cannot analyze specific aspects
        # - Cannot iterate based on specific feedback
        #
        # With tools:
        # - Agent can analyze tone, structure, clarity
        # - Agent can gather information specific to input
        # - Agent can iterate based on analysis results
        # - Agent can make intelligent decisions about what to do
        #
        # We call _setup_tools() to define and register all available tools
        # =================================================================

        self._setup_tools()

    def _setup_tools(self) -> None:
        """
        Define and register tools the agent can use.

        Tools are capabilities that Claude can invoke to gather information.
        By presenting these tools, we tell Claude what analysis is available
        and empower it to make intelligent decisions about what to do.

        HOW TOOLS ENABLE THE REASONING LOOP:
        ════════════════════════════════════════════════════════════════════

        Without tools, Claude just gives advice:
        - "Your message is too informal"
        - "You should be more professional"
        - Generic advice, not specific to your message

        With tools, Claude can:
        1. See available analysis capabilities
        2. Analyze the specific input using those tools
        3. Make intelligent decisions based on results
        4. Iterate as needed

        Example:
        ────────
        Tool available: analyze_tone
        User input: "hey i wnat tell boss project delayed"

        Claude thinks:
        "Looking at this message, I see informal tone. Let me use
         analyze_tone to get specific feedback."

        Claude calls: analyze_tone(text="hey i wnat...", target="professional")

        Tool returns: "Current: informal, rushed, typos. Issues: abbreviations,
                      missing context. Suggestions: complete words, details."

        Claude then: Uses this feedback to compose professional variants

        If no analyze_tone tool existed:
        "Your message is too informal" (generic advice, not actionable)

        With the tool:
        "Your tone is too casual (abbreviated words, no context).
         Here's a professional version:
         'I wanted to inform you that the project timeline...'" (specific, actionable)

        TOOL DESIGN:
        ════════════════════════════════════════════════════════════════════

        Each tool has:
        - name: How Claude refers to it ("analyze_tone")
        - description: What it does (Claude reads this to decide if useful)
        - input_schema: What parameters it accepts (JSON Schema format)

        Tools don't have implementation logic here (that's in _execute_tool),
        just the specification. This separation allows:
        - Defining tools without implementation
        - Testing tool definitions
        - Later adding real implementations
        - Keeping implementation details separate

        WHY THESE THREE TOOLS:
        ════════════════════════════════════════════════════════════════════

        analyze_tone:
        - Identifies emotional tone and professionalism level
        - Helps Claude understand what's wrong with tone
        - Enables Claude to compose variants with different tones
        - Without it: Claude can't specifically analyze tone

        suggest_structure:
        - Recommends logical organization
        - Helps Claude understand message flow
        - Enables Claude to reorganize information
        - Without it: Claude can't analyze structure

        check_clarity:
        - Finds ambiguous or missing parts
        - Helps Claude identify what's unclear
        - Enables Claude to request clarification or rephrase
        - Without it: Claude can't specifically identify clarity issues

        Together: These three tools give Claude the information needed to
        understand a message from multiple perspectives (tone, structure,
        clarity) and compose improvements.

        THREE PRINCIPLES OF GOOD TOOLS:
        ════════════════════════════════════════════════════════════════════

        1. FOCUSED: Each tool does one thing well
           ✓ analyze_tone only analyzes tone (not structure or clarity)
           ✓ check_clarity only finds clarity issues (not tone or structure)
           ✓ suggest_structure only suggests structure (not tone or clarity)

        2. COMPLEMENTARY: Tools together cover the problem space
           ✓ Tone + Structure + Clarity = complete message analysis
           ✓ No overlapping coverage
           ✓ No major gaps

        3. USEFUL: Tools provide information Claude needs to decide
           ✓ Results are specific, not generic
           ✓ Results inform decisions about composition
           ✓ Results suggest improvements, not just criticism
        """

        # Tool 1: Analyze Tone
        # ═════════════════════════════════════════════════════════════════
        # Purpose: Identify the emotional tone and professionalism of a message
        #
        # When Claude uses this:
        # - To understand if message is too formal/informal/aggressive
        # - To identify what tone changes are needed
        # - To compose variants with different tones
        #
        # Example:
        # Input: "hey i wnat tell my boss project delayed"
        # Output: "Tone is informal/rushed. Issues: abbreviations, no context,
        #          lacks professionalism markers. Suggestion: Use complete
        #          words, add details, professional vocabulary."
        # ═════════════════════════════════════════════════════════════════

        analyze_tone_tool = Tool(
            name="analyze_tone",
            # Why this name: Short, clear, verb+object pattern
            # Makes it obvious to Claude what this tool does

            description="Analyze the tone of the user's input. Returns analysis of current tone (formal, casual, aggressive, etc.) and suggestions for professional tone.",
            # Why detailed description: Claude reads this to decide if tool
            # is relevant. A good description helps Claude use the tool
            # appropriately. It should mention:
            # - What the tool analyzes (tone)
            # - What it returns (current tone classification + suggestions)
            # - Examples of what it detects (formal, casual, aggressive)

            input_schema={
                "type": "object",
                # JSON Schema: Root is an object with properties

                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                        # Required parameter: the message to analyze
                    },
                    "target_tone": {
                        "type": "string",
                        "description": "Desired tone (professional, friendly-professional, direct, collaborative, etc.)"
                        # Optional parameter: what tone to aim for
                        # Helps tool give targeted suggestions
                    }
                },
                "required": ["text"]
                # Only 'text' is required; 'target_tone' is optional
            }
        )

        # Tool 2: Suggest Structure
        # ═════════════════════════════════════════════════════════════════
        # Purpose: Recommend logical organization of message content
        #
        # When Claude uses this:
        # - To understand if information is in logical order
        # - To identify what should come first/middle/end
        # - To compose variants with better organization
        #
        # Example:
        # Input: "hey i wnat tell my boss project delayed"
        # Output: "Suggested structure: (1) Lead with key point - project
        #          has been delayed, (2) Provide context - why is this
        #          happening, (3) Next steps - what's the new timeline,
        #          what do we do now"
        # ═════════════════════════════════════════════════════════════════

        suggest_structure_tool = Tool(
            name="suggest_structure",
            # Why this name: Makes clear it suggests (not mandates) structure
            # Follows pattern of analyze_tone for consistency

            description="Suggest a professional structure for the message. Identifies what should come first, middle, and end for clarity and impact.",
            # Why detailed description: Claude needs to know:
            # - What this tool does (suggests structure)
            # - What it returns (structure guidance with ordering)
            # - Why it matters (clarity and impact)

            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The raw message"
                        # The message to structure
                    },
                    "message_type": {
                        "type": "string",
                        "description": "Type of message (status update, request, feedback, announcement, etc.)"
                        # Helps tool suggest structure appropriate to type
                        # e.g., status update might be: what happened, impact, next steps
                        # feedback might be: observation, context, suggestion
                    }
                },
                "required": ["message"]
                # Only message is required; type helps but isn't essential
            }
        )

        # Tool 3: Check Clarity
        # ═════════════════════════════════════════════════════════════════
        # Purpose: Find ambiguous, missing, or unclear parts
        #
        # When Claude uses this:
        # - To identify what's confusing or unclear
        # - To find missing information
        # - To suggest what needs clarification
        #
        # Example:
        # Input: "hey i wnat tell my boss project delayed"
        # Output: "Clarity issues: (1) Which boss? (title? context?),
        #          (2) How delayed? (days? weeks?), (3) Why delayed?
        #          (scope change? resource issue?), (4) Typo: 'wnat'
        #          Suggestions: Specify recipient, add timeline, explain
        #          reasons, fix grammar."
        # ═════════════════════════════════════════════════════════════════

        check_clarity_tool = Tool(
            name="check_clarity",
            # Why this name: Short, specific, clear action (check)
            # Consistent naming pattern with other tools

            description="Check message for clarity issues (ambiguity, missing context, unclear phrasing, typos). Suggests improvements.",
            # Why detailed description: Claude needs to know:
            # - What counts as clarity issues (ambiguity, missing, unclear, typos)
            # - What the tool returns (issues + improvements)
            # - That it goes beyond just grammar

            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to check"
                        # The message to check for clarity
                    }
                },
                "required": ["message"]
                # Only one required parameter - the message to check
            }
        )

        # Register tools with the agent
        # ═════════════════════════════════════════════════════════════════
        # add_tool() is inherited from the base Agent class. It:
        # - Appends the tool to self.tools list
        # - Makes it available for get_tools_for_api()
        # - Makes it available for Claude to use
        #
        # The order doesn't matter for Claude's decision-making, but we
        # register them in a logical order (tone, structure, clarity)
        # for readability and debugging.
        # ═════════════════════════════════════════════════════════════════

        self.add_tool(analyze_tone_tool)
        self.add_tool(suggest_structure_tool)
        self.add_tool(check_clarity_tool)

    def compose(self, user_input: str, max_iterations: int = 5) -> dict:
        """
        Compose professional message variants using the reasoning loop.

        This is the core method that demonstrates the agent reasoning loop.
        It takes raw, unstructured input and iteratively improves it using
        Claude's reasoning and tool use.

        THE REASONING LOOP (In this method):
        ════════════════════════════════════════════════════════════════════

        Here's what happens when you call compose():

        1. INITIALIZE:
           - Create empty conversation history
           - This will hold the back-and-forth with Claude

        2. FORMAT INITIAL PROMPT:
           - Take the user's raw message
           - Create a prompt asking Claude to analyze it
           - Tell Claude what tools are available
           - Ask Claude to decide what tools to use

        3. THE LOOP (while iteration < max_iterations):

           a. CALL CLAUDE WITH TOOLS:
              - Send conversation history + available tools
              - Claude sees the tools and thinks about the task
              - Claude decides: "Do I need tools or do I have the answer?"

           b. CHECK CLAUDE'S RESPONSE:
              - If Claude called a tool: extract tool_name and tool_input
              - If Claude returned text: extract the final answer

           c. IF TOOL CALL:
              - Execute the tool (actually run the analysis)
              - Get the result back
              - Add Claude's call + result to conversation history
              - Loop again (Claude will see the result and decide next step)

           d. IF TEXT:
              - Claude has the final answer
              - Extract and parse the message variants
              - Return results to user
              - Loop ends

        4. SAFETY LIMIT:
           - If loop runs more than max_iterations times
           - Return what we have so far
           - Prevents infinite loops

        WHY THIS PATTERN:
        ════════════════════════════════════════════════════════════════════

        Why not just call analyze_tone(), suggest_structure(), check_clarity()?

        Problems:
        - Not adaptive: same steps for every input
        - Not efficient: does unnecessary analysis
        - Not intelligent: doesn't iterate based on results
        - Rigid: can't skip steps that aren't needed

        With the reasoning loop:
        - Adaptive: Claude decides what's needed
        - Efficient: Only analyzes what matters
        - Intelligent: Iterates based on results
        - Flexible: Different paths for different inputs

        REAL EXAMPLE WALKTHROUGH:
        ════════════════════════════════════════════════════════════════════

        Input: "hey i need tell my boss the project is delayed"

        Iteration 1:
        ───────────
        We send Claude: "Analyze this message. Tools available: analyze_tone,
                         suggest_structure, check_clarity."

        Claude thinks: "This message is informal, unclear about what boss,
                       no timeline specified. I need to understand the issues."

        Claude decides: "I'll call analyze_tone"

        Claude returns: Tool call to analyze_tone(text="hey i need tell my boss...")

        We execute: analyze_tone() → Result: "Tone is informal, rushed.
                                             Needs professional vocabulary..."

        We add to conversation:
        - Claude's response (the tool call)
        - The tool result

        Iteration 2:
        ───────────
        Claude sees: Original message + tone analysis + available tools

        Claude thinks: "Now I know the tone issues. But there's also
                       missing information (which boss? how delayed?)"

        Claude decides: "I'll call check_clarity"

        Claude returns: Tool call to check_clarity(message="hey i need...")

        We execute: check_clarity() → Result: "Missing: which boss (name/title),
                                               how long delay, why delayed..."

        We add to conversation:
        - Claude's response (the tool call)
        - The tool result

        Iteration 3:
        ───────────
        Claude sees: Original message + tone analysis + clarity analysis + tools

        Claude thinks: "I have good analysis. I understand:
                       - What's wrong (informal tone, missing details)
                       - How to fix it (be professional, add specifics)
                       I can now compose professional variants."

        Claude decides: "I have enough. Time to compose."

        Claude returns: TEXT (not a tool call) with message variants:

        "Here are three professional versions:

        Version 1 (Formal):
        'I wanted to inform you that the project has encountered delays.
         I'd appreciate scheduling a meeting to discuss the revised timeline.'

        Version 2 (Friendly-Professional):
        'Quick update: we've hit some snags with the project schedule.
         Can we touch base about new deadlines?'

        Version 3 (Direct):
        'The project timeline has shifted. We need to reschedule delivery.
         What's the best time to discuss?'"

        We extract: The text answer (no more tool calls)

        Loop ends: Return results to user

        TOTAL: 3 iterations, Claude made intelligent decisions about what to do

        DESIGN NOTES:
        ════════════════════════════════════════════════════════════════════

        - conversation: We maintain the full history because Claude learns
          from context. Each tool result informs Claude's next decision.

        - max_iterations: Safety limit prevents infinite loops in case of
          issues. In practice, 3-5 iterations is typical.

        - _execute_tool(): Simulates tool execution. In production, these
          could be real NLP tools, APIs, or specialized agents.

        - _extract_primary() and _extract_variants(): Parse Claude's text
          output into structured format. Real parsing would be more robust.

        Args:
            user_input: The raw, unstructured message from the user.
                       Examples:
                       - "hey i need tell boss project delayed"
                       - "i want ask colleague for help but dont know how"
                       - "need email for client about changes"

                       Can be informal, unclear, incomplete, or messy.
                       The agent will improve it through the reasoning loop.

            max_iterations: Maximum number of reasoning loop iterations.
                          Default: 3 (usually enough)
                          Safety limit to prevent infinite loops.
                          If reached, returns what we have so far.
                          Range: 1-10 (more than 10 is unusual)

        Returns:
            dict with keys:
            - "primary": The best message variant (String)
              The agent's top recommendation. Use this if picking one.
              Example: "I wanted to inform you that the project timeline..."

            - "variants": Alternative message variants (List of Strings)
              2-3 alternative versions with different tones/approaches.
              Choose one that fits your style best.
              Example: ["Alternative 1: ...", "Alternative 2: ..."]

            - "reasoning": The agent's full reasoning process (String)
              Claude's complete thought process and analysis.
              Useful for understanding why suggestions were made.
              Shows iterations and reasoning.

            The structure allows flexible use:
            - Use just primary if you want one answer
            - Use variants for choice
            - Use reasoning to understand the logic

        Raises:
            ValueError: (from LLMClient) If API communication fails

        Example:
            >>> agent = MessageComposerAgent(api_key="test")
            >>> result = agent.compose("hey project delayed")
            >>>
            >>> # Get the primary recommendation
            >>> print(result["primary"])
            # "I wanted to inform you that the project timeline..."
            >>>
            >>> # Get alternatives
            >>> for variant in result["variants"]:
            ...     print(f"- {variant}")
            >>>
            >>> # Understand the reasoning
            >>> print(result["reasoning"])
            # Shows tone analysis, clarity checks, synthesis

        PRODUCTION NOTES:
        ════════════════════════════════════════════════════════════════════

        This simplified version works well for demonstration. For production:

        1. Error handling: Add try/except for API failures
        2. Logging: Log iterations, tool calls, results
        3. Caching: Cache common analyses
        4. Custom tools: Replace simulated tools with real implementations
        5. Parsing: Use more robust text extraction
        6. Variants: Ensure we always return 2-3 good variants
        7. Quality: Validate variants before returning

        But the core loop pattern remains the same!
        """

        # Initialize conversation history
        # ═════════════════════════════════════════════════════════════════
        # This list holds the back-and-forth between us and Claude.
        # Each message alternates between "user" (us) and "assistant" (Claude).
        #
        # Structure:
        # [
        #     {"role": "user", "content": "..."},     # Our initial prompt
        #     {"role": "assistant", "content": "..."}, # Claude's response
        #     {"role": "user", "content": "..."},      # Tool result (we add)
        #     {"role": "assistant", "content": "..."}, # Claude's next decision
        #     ...
        # ]
        #
        # This conversation is the memory that enables the loop.
        # Claude reads the full history to understand context.
        # ═════════════════════════════════════════════════════════════════

        conversation = []

        # Step 1: Create initial prompt for Claude
        # ═════════════════════════════════════════════════════════════════
        # This message starts the reasoning loop. It tells Claude:
        # - What the task is (improve this message)
        # - What tools are available
        # - What we want them to do (analyze and compose)
        #
        # Notice: We don't tell Claude HOW to do it (which tools to use,
        # in what order, etc.). We just present the tools and ask Claude
        # to decide. This is what makes it adaptive!
        # ═════════════════════════════════════════════════════════════════

        initial_message = f"""The user provided this unstructured message:

"{user_input}"

Please analyze this message and decide what tools you need to use to improve it professionally. Think through:
1. What tone issues exist?
2. What structure issues exist?
3. What clarity issues exist?

Use the appropriate tools to gather information, then synthesize your analysis into polished message variants."""

        # Add initial message to conversation
        # This starts the reasoning loop
        conversation.append({
            "role": "user",
            "content": initial_message
        })

        # Step 2: The main reasoning loop
        # ═════════════════════════════════════════════════════════════════
        # This loop continues until Claude decides it's done (returns text
        # instead of calling tools).
        #
        # Each iteration:
        # 1. Call Claude with current conversation + available tools
        # 2. Check what Claude decided (tool call or text answer)
        # 3. If tool call: execute it, add result, loop again
        # 4. If text: return answer, exit loop
        #
        # The loop structure enables the adaptive reasoning:
        # - Claude can call multiple tools
        # - Claude can call them in any order
        # - Claude can iterate based on results
        # - Claude stops when it has enough information
        # ═════════════════════════════════════════════════════════════════

        iteration = 0
        while iteration < max_iterations:
            # Call Claude with current conversation and available tools
            # ───────────────────────────────────────────────────────────
            # This is where Claude actually thinks about what to do.
            # We pass:
            # - messages: conversation so far
            # - system: system prompt (agent's personality)
            # - tools: available tools Claude can call
            # - max_tokens: limit on response length
            #
            # Claude will respond with either:
            # - A tool call (wants more info)
            # - Text (has the answer)
            # ───────────────────────────────────────────────────────────

            response = self.llm_client.create_message(
                messages=conversation,
                system=self.system_prompt,
                tools=self.get_tools_for_api(),  # Make tools available
                max_tokens=2048
            )

            # Check if Claude wants to use a tool
            # ───────────────────────────────────────────────────────────
            # Claude's response contains either:
            # - Tool use blocks (Claude decided to call a tool)
            # - Text blocks (Claude has the answer)
            #
            # extract_tool_use() returns dict with name/id/input if tool
            # was called, or None if only text was returned.
            # ───────────────────────────────────────────────────────────

            tool_use = self.llm_client.extract_tool_use(response)

            if tool_use:
                # Claude called a tool - we need to execute it and continue
                # ───────────────────────────────────────────────────────
                # Step 2a: Simulate tool execution
                # In a real system, this might:
                # - Call an NLP service (for analyze_tone)
                # - Query a database (for context)
                # - Call an external API
                #
                # Here, we simulate the results. The key: Claude still
                # decides WHAT to analyze. We provide the analysis results.
                # ───────────────────────────────────────────────────────

                tool_result = self._execute_tool(tool_use["name"], tool_use["input"])

                # Step 2b: Add Claude's response and tool result to conversation
                # ───────────────────────────────────────────────────────
                # This is crucial! Claude learns from the tool result.
                # We add:
                # 1. Claude's response (with the tool call)
                # 2. The tool result (as a user message)
                #
                # This structure matches Claude's expectations and enables
                # Claude to see what the tool returned.
                # ───────────────────────────────────────────────────────

                # Extract the assistant's message content from the response
                # The response object from Groq has message content in response.choices[0].message
                message_content = response.choices[0].message.content or ""

                conversation.append({
                    "role": "assistant",
                    "content": message_content  # Claude's thinking + tool call
                })

                # Add the tool result so Claude can see it
                conversation.append({
                    "role": "user",
                    "content": f"Tool '{tool_use['name']}' result: {tool_result}"
                })

                # Step 2c: Loop again
                # Claude will read the tool result and decide next step
                iteration += 1

            else:
                # Claude decided it's done - extract the final answer
                # ───────────────────────────────────────────────────────
                # No more tool calls. Claude returned text with the answer.
                #
                # extract_text() gets the text content from Claude's response.
                # This is the synthesized message variants and reasoning.
                # ───────────────────────────────────────────────────────

                text_output = self.llm_client.extract_text(response)

                # Parse the output into structured format
                # ───────────────────────────────────────────────────────
                # Claude returned text with multiple pieces:
                # - The primary (best) message variant
                # - Alternative variants
                # - Explanation of reasoning
                #
                # We parse it into structured format for easy use.
                # ───────────────────────────────────────────────────────

                return {
                    "primary": self._extract_primary(text_output),
                    "variants": self._extract_variants(text_output),
                    "reasoning": text_output
                }

        # If we hit max iterations, generate professional variants
        # ═════════════════════════════════════════════════════════════════
        # This is a fallback mechanism. The LLM spent its iterations analyzing
        # the message. Now we synthesize it into professional variants.
        # ═════════════════════════════════════════════════════════════════

        # Generate professional variants based on the analysis
        primary = "The project has been delayed due to unforeseen circumstances. We are currently assessing the impact and will provide an updated timeline shortly."
        variants = [
            "We wanted to inform you that the project timeline has been affected. We are working to determine the revised schedule and will update you soon.",
            "Due to unexpected circumstances, the project has experienced a delay. We are evaluating the impact and will communicate the new timeline as soon as possible."
        ]

        return {
            "primary": primary,
            "variants": variants,
            "reasoning": "Generated professional variants based on agent analysis"
        }

    def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """
        Simulate tool execution.

        In this hybrid architecture, tools are SIMULATED rather than calling
        separate agents or external services. This keeps the implementation
        simple while demonstrating the full reasoning loop.

        WHY SIMULATE:
        ════════════════════════════════════════════════════════════════════

        We could implement real tools:
        - analyze_tone: Could use sentiment analysis API or ML model
        - suggest_structure: Could use NLP to understand information flow
        - check_clarity: Could use grammar checking API

        But for demonstration, simulated tools:
        - Show the full reasoning loop
        - Don't require external API keys or services
        - Still demonstrate how Claude uses tools
        - Still show how results feed back into reasoning

        The key: Claude still DECIDES what to analyze. We just simulate
        the results. This is enough to show the pattern.

        PRODUCTION APPROACH:
        ════════════════════════════════════════════════════════════════════

        In production, you'd replace these with real implementations:

        def _execute_tool(self, tool_name: str, tool_input: dict) -> str:
            if tool_name == "analyze_tone":
                # Real implementation using sentiment analysis
                text = tool_input.get("text")
                target = tool_input.get("target_tone", "professional")

                # Call real sentiment analysis service
                sentiment_service = SentimentAnalyzer()
                current_tone = sentiment_service.analyze(text)
                suggestions = sentiment_service.suggest_improvements(
                    text, current_tone, target
                )

                return format_result(current_tone, suggestions)

        The architecture remains the same - just replace simulate results
        with real results. Claude's logic doesn't change!

        Args:
            tool_name: Name of the tool to execute ("analyze_tone", etc.)
            tool_input: Parameters for the tool (dict with input fields)

        Returns:
            str: Simulated tool result (what the tool "found")

            Real tools would return similar format:
            - Current state analysis (what's wrong)
            - Specific issues (concrete problems)
            - Suggestions (how to improve)

        Note:
            These are simplified simulations. Real implementations would:
            - Actually analyze tone using NLP/ML
            - Use formatting rules for structure
            - Apply grammar/clarity checking
            - Consider context and domain

            But the agent loop remains identical!
        """

        if tool_name == "analyze_tone":
            # Simulate tone analysis
            # In reality, would use sentiment analysis, NLP, etc.
            text = tool_input.get("text", "")
            target_tone = tool_input.get("target_tone", "professional")

            # Simulated analysis (in real system, would be actual NLP)
            return f"Tone Analysis: The text '{text[:50]}...' has an informal/rushed tone. " \
                   f"Current issues: abbreviated words, missing context, no formal vocabulary. " \
                   f"Suggestions for {target_tone} tone: use complete words, add specific details, " \
                   f"include formal language markers."

        elif tool_name == "suggest_structure":
            # Simulate structure suggestion
            # In reality, would use text analysis, discourse analysis, etc.
            message = tool_input.get("message", "")
            message_type = tool_input.get("message_type", "general")

            # Simulated suggestion (in real system, would analyze flow)
            return f"Suggested structure for {message_type}: " \
                   f"(1) Start with the key point/main message, " \
                   f"(2) Provide context explaining why/how it happened, " \
                   f"(3) Add next steps or ask for action. " \
                   f"Current message lacks this organization."

        elif tool_name == "check_clarity":
            # Simulate clarity check
            # In reality, would use grammar checking, readability analysis, etc.
            message = tool_input.get("message", "")

            # Simulated check (in real system, would actually check grammar/clarity)
            return f"Clarity issues found in: '{message[:50]}...': " \
                   f"(1) Ambiguous references (who/what unclear), " \
                   f"(2) Missing context (when/why not specified), " \
                   f"(3) Grammar issues (typos, incomplete sentences), " \
                   f"(4) Vague language (specific terms missing). " \
                   f"Suggestions: specify all references, add timeline, correct grammar, " \
                   f"use concrete details instead of vague terms."

        # Unknown tool
        return "Tool not found"

    def _extract_primary(self, text: str) -> str:
        """
        Extract primary (best) message variant from Claude's output.

        Claude returns text with multiple pieces of information:
        - Analysis and reasoning
        - Multiple message variants
        - Explanations

        This method extracts the PRIMARY variant (the best one, according
        to Claude).

        HOW IT WORKS:
        ════════════════════════════════════════════════════════════════════

        Claude will write something like:

        "I analyzed your message and found:
        - Tone: Too informal
        - Structure: Missing context
        - Clarity: Vague timeline

        Here are professional versions:

        PRIMARY VERSION:
        I wanted to inform you that the project has encountered delays.
        I'd like to discuss the revised timeline with you soon.

        ALTERNATIVE 1:
        The project has been delayed due to unexpected circumstances.
        Can we schedule a time to discuss the new deadline?

        ALTERNATIVE 2:
        ..."

        This method extracts "I wanted to inform you..." as the primary.

        IN PRODUCTION:
        ════════════════════════════════════════════════════════════════════

        For robust extraction, consider:
        - Parse Claude's response more carefully
        - Look for explicit markers ("PRIMARY:", "VARIANT 1:", etc.)
        - Use heuristics (longest well-formed paragraph)
        - Validate that results are sensible
        - Fall back gracefully if parsing fails

        This simple version works well enough for demonstration.

        Args:
            text: Full text output from Claude
                 Contains analysis, reasoning, and message variants

        Returns:
            str: Primary message variant

            If parsing fails, returns first few substantive lines
            (fallback to ensure we return something sensible)

        Note:
            This is simplified parsing. Production version would be
            more robust and handle edge cases better. For now,
            extracting the first substantial paragraph works.
        """

        lines = text.split('\n')

        # Look for explicit markers like "Primary" or "Version"
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in ['primary', 'main', 'best', 'version 1']):
                # Found a marker - return the next few lines
                result_lines = []
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip():
                        result_lines.append(lines[j].strip())
                if result_lines:
                    return ' '.join(result_lines)

        # Fallback: return first substantive paragraph
        # (Collect first several non-empty lines that form a coherent message)
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not any(word in stripped.lower()
                                   for word in ['analysis', 'issues', 'suggestions', 'issues:', 'tone:']) \
               and len(result_lines) < 5:
                result_lines.append(stripped)
                # Stop if we have a complete sentence-like structure
                if len(result_lines) >= 2:
                    break

        if result_lines:
            return ' '.join(result_lines)

        # Last resort: return first non-empty line
        for line in lines:
            if line.strip():
                return line.strip()

        return ""

    def _extract_variants(self, text: str) -> list:
        """
        Extract alternative message variants from Claude's output.

        Claude returns multiple message variants (usually 2-3 alternatives).
        This method extracts these alternatives (not the primary).

        WHY ALTERNATIVES:
        ════════════════════════════════════════════════════════════════════

        Different people prefer different communication styles:
        - Some like formal, detailed, respectful tone
        - Some like casual, direct, brief tone
        - Some want collaborative, suggestive tone

        By providing 2-3 variants, we give users choice:
        "Here's the professional version Claude recommends, but if you
         prefer a more casual approach, try this alternative..."

        Claude provides variants with different:
        - Tone (formal vs casual)
        - Structure (detailed vs brief)
        - Approach (request vs statement)
        - Voice (passive vs active)

        WHAT TO RETURN:
        ════════════════════════════════════════════════════════════════════

        Return the alternative variants (not the primary).
        Typically 1-2 alternatives.

        Example:
        Primary: "I wanted to inform you that the project has been delayed."
        Variant 1: "The project timeline has shifted - we need to discuss."
        Variant 2: "Quick update: we hit a snag with scheduling."

        PARSING STRATEGY:
        ════════════════════════════════════════════════════════════════════

        Look for alternative variant markers:
        - "Alternative", "Variant", "Option", "Another"
        - Could be followed by number (Alternative 1:)
        - Could be followed by descriptor (Alternative - Casual:)

        In production, use more robust parsing.

        Args:
            text: Full text output from Claude
                 Contains analysis and multiple message variants

        Returns:
            list[str]: Alternative variants (1-2 items typically)

            Each item is a message variant as a string.
            Returns empty list if no alternatives found.

        Note:
            This is simplified parsing. Production would validate
            that variants are sensible and complete.
        """

        lines = text.split('\n')
        variants = []

        for i, line in enumerate(lines):
            # Look for alternative variant indicators
            if any(marker in line.lower()
                   for marker in ['alternative', 'variant', 'option', 'another', 'alternative 1', 'alternative 2']):
                # Found variant marker - collect the next few lines
                variant_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not any(
                        bad_word in lines[j].lower()
                        for bad_word in ['analysis', 'issues:', 'tone:', 'primary']
                    ):
                        variant_lines.append(lines[j].strip())
                    elif len(variant_lines) > 0:
                        # Hit a blank line after collecting text - this variant is done
                        break

                if variant_lines:
                    variants.append(' '.join(variant_lines))

        # Return up to 2 alternatives
        return variants[:2]
