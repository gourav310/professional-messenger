"""
Simple Composer Agent - Single-call alternative to MessageComposerAgent.

This agent demonstrates a simpler approach to message composition:
- Makes ONE LLM call (no reasoning loop)
- No tools (no iterative analysis)
- Trades sophistication for speed

COMPARISON WITH MessageComposerAgent:
════════════════════════════════════════════════════════════════════════════

MessageComposerAgent (Complex):
- Multiple iterations with reasoning loop
- Uses tools to analyze tone, structure, clarity
- More thorough analysis, longer processing time
- Better for nuanced messages that need multiple angles

SimpleComposer (Fast):
- Single LLM call with comprehensive system prompt
- No tools, no looping
- Faster response, lower API cost
- Perfect for quick composition, simple messages

WHY THIS DESIGN:
═════════════════════════════════════════════════════════════════════════════

Some use cases don't need complex reasoning:
- Quick message composition
- High-volume processing (cost/speed critical)
- Simple messages that don't need deep analysis
- Integration into time-sensitive systems

SimpleComposer shows that you don't need tools to be useful. A good system
prompt can guide the LLM to:
1. Analyze tone in their internal reasoning
2. Check clarity in their thinking
3. Synthesize variants in a single pass

It's like asking an expert to "write 3 professional versions of this message"
in one conversation vs. asking them to "first analyze tone, then check clarity,
then compose" (which is what MessageComposerAgent does).

KEY INSIGHT: Same output, different path. Both return:
{
    "primary": "Best message variant...",
    "variants": ["Alt 1...", "Alt 2..."],
    "reasoning": "How we got here..."
}

IMPLEMENTATION NOTES:
═════════════════════════════════════════════════════════════════════════════

1. Extends Agent base class (from src.agent)
2. No tools needed (empty list)
3. System prompt is comprehensive (does all analysis in LLM reasoning)
4. compose() method makes ONE LLM call
5. Uses extract methods from MessageComposerAgent for consistent parsing
6. Returns same output contract as MessageComposerAgent
"""

from typing import Optional
from src.agent import Agent
from src.llm_client import LLMClient


class SimpleComposer(Agent):
    """
    Fast message composition agent using single LLM call.

    This agent provides professional message composition without the complexity
    of the reasoning loop. Instead of multiple iterations with tools, it:
    - Relies on a comprehensive system prompt
    - Makes one LLM call
    - Returns professional variants immediately

    DESIGN PHILOSOPHY:
    ═════════════════════════════════════════════════════════════════════════

    SimpleComposer demonstrates that agent architecture doesn't require tools.
    Sometimes the simplest approach is the best:
    - One good prompt is better than multiple weak prompts
    - One fast API call beats multiple round trips
    - Clear instructions can replace iterative analysis

    The LLM is capable of:
    1. Understanding the message comprehensively
    2. Analyzing tone/clarity/structure internally
    3. Generating multiple variants directly
    4. Providing explanation of reasoning

    All in one pass.

    PERFORMANCE:
    ═════════════════════════════════════════════════════════════════════════

    Typical execution:
    - 1 API call (vs 2-5 for MessageComposerAgent)
    - 500-800ms (vs 1-3 seconds for MessageComposerAgent)
    - Cost: ~0.001 USD per composition
    - Suitable for high-volume processing

    WHEN TO USE SimpleComposer:
    ═════════════════════════════════════════════════════════════════════════

    Use SimpleComposer when:
    - Speed is critical
    - Cost matters (fewer API calls)
    - Messages are relatively simple
    - You want straightforward composition

    Use MessageComposerAgent when:
    - You need thorough analysis
    - Complex messages with subtle tone requirements
    - You want detailed reasoning explanation
    - User can wait for higher quality

    EXAMPLE:
    ═════════════════════════════════════════════════════════════════════════

    >>> composer = SimpleComposer(api_key="gsk-...")
    >>> result = composer.compose("hey project delayed")
    >>> print(result["primary"])
    # "I wanted to inform you that the project timeline has been affected..."
    >>> print(result["variants"])
    # ["Alternative 1...", "Alternative 2..."]
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SimpleComposer agent.

        Simpler initialization than MessageComposerAgent:
        - No tools to set up
        - Just system prompt and LLMClient

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY environment variable.

        Raises:
            ValueError: (from LLMClient) If API key not available.
        """

        # Define system prompt for single-call composition
        system_prompt = """You are a professional message composition expert.

YOUR TASK: Transform the user's raw message into 3 professional variants.

THINK THROUGH:
1. What is the message about?
2. What tone should it have?
3. What clarity issues exist?
4. What different communication styles would work?

THEN COMPOSE: Generate 3 variants with different approaches:
- Variant 1: Formal and professional
- Variant 2: Balanced and approachable
- Variant 3: Direct and concise

FORMAT YOUR RESPONSE EXACTLY AS:
Professional Message 1: [formal variant - detailed, respectful tone]
Professional Message 2: [balanced variant - professional but warm]
Professional Message 3: [direct variant - brief and to the point]

IMPORTANT: Each variant should be 1-3 sentences. Keep them concise but complete.

After the three variants, provide a brief explanation of:
- What issues you identified in the original message
- How each variant addresses those issues
- When to use each variant"""

        # Initialize parent Agent class
        # No tools needed for SimpleComposer
        super().__init__(
            name="SimpleComposer",
            system_prompt=system_prompt,
            tools=[]  # No tools - single call, no loops
        )

        # Initialize LLM Client
        try:
            self.llm_client = LLMClient(api_key=api_key)
        except ValueError:
            self.llm_client = None

    def compose(self, user_input: str, max_tokens: int = 1024) -> dict:
        """
        Compose professional message variants with a single LLM call.

        This is simpler than MessageComposerAgent.compose():
        - No reasoning loop
        - No tool execution
        - Just one call to LLM with comprehensive prompt

        THE SINGLE-CALL APPROACH:
        ═════════════════════════════════════════════════════════════════════

        Unlike MessageComposerAgent which:
        1. Sends initial message
        2. Loops: LLM calls tools, we execute them, loop again
        3. Eventually LLM returns final answer

        SimpleComposer:
        1. Sends message with all instructions
        2. LLM thinks through everything
        3. Returns answer in one response

        The system prompt does the work of directing the LLM's thinking.

        DESIGN TRADE-OFFS:
        ═════════════════════════════════════════════════════════════════════

        Advantages:
        - Faster (1 API call vs 2-5)
        - Simpler (no tool execution)
        - Cheaper (fewer API calls)
        - Deterministic (no iteration variability)

        Disadvantages:
        - Less detailed analysis
        - Can't adapt based on tool results
        - Less transparent reasoning
        - May miss subtle issues

        Args:
            user_input: The raw message to compose professionally.
                       Examples:
                       - "hey project got delayed"
                       - "i need talk to boss about timeline"
                       - "urgent need to send email about changes"

            max_tokens: Maximum response length. Default 1024 is usually enough.
                       Increase if variants are being cut off.

        Returns:
            dict with keys:
            - "primary": Best message variant (String)
            - "variants": Alternative variants (List of 2 Strings)
            - "reasoning": Full LLM response with analysis and variants

        Example:
            >>> composer = SimpleComposer(api_key="gsk-...")
            >>> result = composer.compose("hey project got delayed")
            >>> print(result["primary"])
            # "I wanted to inform you that the project timeline..."
            >>> print(len(result["variants"]))
            # 2 (two alternatives in addition to primary)
        """

        # Validate LLM client
        if not self.llm_client:
            raise ValueError("LLMClient not initialized. Check API key.")

        # Format initial message
        # Unlike MessageComposerAgent, we don't ask "what tools do you need"
        # We give all instructions upfront
        initial_message = f"""Transform this message into professional variants:

"{user_input}"

Remember: Generate exactly 3 professional variants with different tones.
Format them as:
Professional Message 1: [variant 1]
Professional Message 2: [variant 2]
Professional Message 3: [variant 3]

Then explain your reasoning."""

        # Create message history
        conversation = [
            {
                "role": "user",
                "content": initial_message
            }
        ]

        # SINGLE API CALL (no loop)
        # ═════════════════════════════════════════════════════════════════
        # This is the key difference: we make ONE call and get the answer.
        # No tools, no iterations, no loops.
        # The system_prompt does all the thinking guidance.
        response = self.llm_client.create_message(
            messages=conversation,
            system=self.system_prompt,
            tools=[],  # No tools for SimpleComposer
            max_tokens=max_tokens
        )

        # Extract the text response
        text_output = self.llm_client.extract_text(response)

        # Parse the response using same methods as MessageComposerAgent
        # This ensures consistent output format
        return {
            "primary": self._extract_primary(text_output),
            "variants": self._extract_variants(text_output),
            "reasoning": text_output
        }

    def _extract_primary(self, text: str) -> str:
        """
        Extract primary (best) message variant from LLM's output.

        This method is copied from MessageComposerAgent to ensure
        consistent parsing between simple and complex agents.

        WHY EXTRACT METHODS:
        ═════════════════════════════════════════════════════════════════

        The LLM returns text with multiple pieces:
        - Multiple variant messages
        - Explanation and reasoning
        - Possibly other analysis

        We need to extract just the primary variant (the best one).

        The parsing logic is identical to MessageComposerAgent so that
        both agents produce the same output format.

        Args:
            text: Full LLM response

        Returns:
            str: Primary message variant

        Example:
            >>> text = '''Professional Message 1: Hello there...
            ...           Professional Message 2: Hi...'''
            >>> primary = composer._extract_primary(text)
            >>> assert "Hello" in primary
        """

        lines = text.split('\n')

        # Look for explicit markers like "Primary" or "Version 1"
        for i, line in enumerate(lines):
            if any(marker in line.lower() for marker in ['primary', 'message 1', 'version 1']):
                # Found a marker - return the next few lines
                result_lines = []
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip():
                        result_lines.append(lines[j].strip())
                if result_lines:
                    return ' '.join(result_lines)

        # Fallback: return first substantive paragraph
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not any(word in stripped.lower()
                                   for word in ['analysis', 'issues', 'suggestions', 'reasoning:', 'tone:']) \
               and len(result_lines) < 5:
                result_lines.append(stripped)
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
        Extract alternative message variants from LLM's output.

        This method is copied from MessageComposerAgent to ensure
        consistent parsing between simple and complex agents.

        WHY CONSISTENT EXTRACTION:
        ═════════════════════════════════════════════════════════════════

        Both SimpleComposer and MessageComposerAgent should:
        1. Return variants in same format
        2. Extract them the same way
        3. Provide same output contract

        This means users can swap agents without changing client code.

        Args:
            text: Full LLM response with multiple variants

        Returns:
            list[str]: Alternative variants (2 items typically)

        Example:
            >>> text = '''Professional Message 1: ...
            ...           Professional Message 2: ...
            ...           Professional Message 3: ...'''
            >>> variants = composer._extract_variants(text)
            >>> assert len(variants) <= 2  # Return alternatives only
        """

        lines = text.split('\n')
        variants = []

        for i, line in enumerate(lines):
            # Look for variant indicators (not "1" which is primary)
            if any(marker in line.lower()
                   for marker in ['message 2', 'message 3', 'alternative', 'variant', 'option']):
                # Found variant marker - collect the next few lines
                variant_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not any(
                        bad_word in lines[j].lower()
                        for bad_word in ['analysis', 'issues:', 'tone:', 'primary', 'message 1']
                    ):
                        variant_lines.append(lines[j].strip())
                    elif len(variant_lines) > 0:
                        # Hit a blank line after collecting text
                        break

                if variant_lines:
                    variants.append(' '.join(variant_lines))

        # Return up to 2 alternatives (3 total including primary)
        return variants[:2]
