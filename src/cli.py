"""
Command-line interface for Professional Messenger.

This module provides a CLI for users to compose professional messages from
unstructured thoughts. It demonstrates CLI patterns using Click framework.

The CLI handles:
- User input (from arguments or stdin)
- Calling the MessageComposerAgent
- Formatting output nicely
- Clipboard integration (macOS)
- Configuration management

WHY CLICK FRAMEWORK:
═══════════════════════════════════════════════════════════════════════════

Click is a Python library for building command-line interfaces. It makes
CLI development easy by handling:

1. ARGUMENT PARSING:
   Without Click: sys.argv parsing is error-prone
   With Click: @click.argument() declares arguments clearly

2. TYPE CONVERSION:
   Without Click: Manual string → type conversion, validation
   With Click: Automatic type checking and conversion

3. HELP TEXT:
   Without Click: Manually format help messages
   With Click: Generates beautiful --help automatically

4. GROUPS & SUBCOMMANDS:
   Without Click: Manual routing logic
   With Click: @click.group() and @click.command() organize commands

5. OPTIONS & FLAGS:
   Without Click: Manual flag parsing
   With Click: @click.option() for flags, --help text, defaults

EXAMPLE CLICK PATTERNS:
═══════════════════════════════════════════════════════════════════════════

@click.group()
def app():
    '''Top-level CLI group (like 'pm' command).'''
    pass

@app.command()  # Registers 'compose' subcommand
@click.argument('text', required=False)  # Positional argument
@click.option('--show-variants', is_flag=True, help='...')  # Flag option
def compose(text, show_variants):
    '''Compose a message.'''
    pass

When user runs:
  pm compose "hello world" --show-variants

Click handles:
- Parsing "hello world" as text argument
- Parsing --show-variants as a flag
- Calling compose(text="hello world", show_variants=True)
- Generating help from docstrings

TESTING CLI:
═══════════════════════════════════════════════════════════════════════════

The CliRunner simulates CLI invocation without real system calls:

  from click.testing import CliRunner
  runner = CliRunner()
  result = runner.invoke(app, ['compose', '--help'])
  assert result.exit_code == 0

This allows testing:
- Command structure
- Argument parsing
- Error handling
- Help output
- Exit codes

Without actually running commands on the system!

Architecture of this module:
════════════════════════════════════════════════════════════════════════════

1. @click.group() app()
   Top-level CLI group. Provides main entry point and documentation.

2. @app.command() compose()
   Subcommand for composing messages.
   - Takes user input (from argument or stdin)
   - Loads configuration
   - Calls MessageComposerAgent
   - Formats and displays results
   - Copies to clipboard if requested

3. @app.command() config()
   Subcommand for managing configuration.
   - Creates config.yaml from example
   - Shows current configuration
   - Guides user to customize

4. _copy_to_clipboard()
   Helper function for clipboard integration.
   - Platform-specific (macOS uses pbcopy)
   - Wrapped in try/except for graceful failure
"""

import os
import sys
import click
from pathlib import Path
from src.config import Config
from src.agents.message_composer import MessageComposerAgent


@click.group()
def app():
    """
    Professional Messenger - Compose professional messages from unstructured thoughts.

    This is the main CLI entry point. It provides commands for composing messages
    and managing configuration.

    WHAT PROFESSIONAL MESSENGER DOES:
    ═════════════════════════════════════════════════════════════════════════

    You write: "hey boss the project got delayed we need new timeline"

    Professional Messenger transforms it to:
    ✓ "I wanted to inform you that the project has encountered delays.
       I'd like to discuss the revised timeline with you soon."

    The tool:
    1. Analyzes your raw message (tone, clarity, structure)
    2. Identifies issues (too informal, unclear, missing context)
    3. Generates professional alternatives
    4. Copies the best one to your clipboard

    KEY FEATURES:
    ═════════════════════════════════════════════════════════════════════════

    - TONE CORRECTION: Transforms casual/informal to professional
    - STRUCTURE IMPROVEMENT: Organizes thoughts logically
    - CLARITY ENHANCEMENT: Specifies vague parts, fixes grammar
    - VARIANTS: Shows 2-3 options so you can choose
    - CLIPBOARD: Automatically copies result to clipboard
    - CONFIGURATION: Customize voice rules and preferences

    AVAILABLE COMMANDS:
    ═════════════════════════════════════════════════════════════════════════

    pm compose "your message here"
      Compose a professional message
      Options: --show-variants, --clipboard, --config

    pm config
      Initialize or view configuration

    pm --help
      Show this help message

    USAGE EXAMPLES:
    ═════════════════════════════════════════════════════════════════════════

    1. Compose from command line:
       pm compose "hey i wnat tell my boss project delayed"

    2. Compose interactively (paste multiple lines):
       pm compose

    3. See all variants:
       pm compose "text" --show-variants

    4. Don't copy to clipboard:
       pm compose "text" --clipboard=false

    5. Use custom configuration:
       pm compose "text" --config ./work-config.yaml

    6. Initialize configuration:
       pm config

    WORKFLOW:
    ═════════════════════════════════════════════════════════════════════════

    First time:
    1. pm config                    # Creates config.yaml
    2. Edit config.yaml             # Customize voice rules
    3. export CLAUDE_API_KEY="..."  # Set API key
    4. pm compose "your message"    # Use the tool!

    Daily use:
    1. pm compose "your thought"
    2. Select which variant you like
    3. Use it in your email/chat

    TIPS:
    ═════════════════════════════════════════════════════════════════════════

    - More context → Better results
      "need help" → "I'm working on the data analysis for Q2 and hit a
                     blocker with the API integration - would appreciate
                     your input"

    - Be honest about tone
      Want casual? The agent respects your style, just polishes it
      Want formal? Specify in config.yaml voice_rules

    - Use variants to learn
      Compare the options to understand what makes a message better
      See what the agent changed and why

    This CLI demonstrates how to:
    - Build command-line tools with Click
    - Integrate with a Python agent
    - Handle user input flexibly
    - Display results nicely
    - Manage configuration
    """
    pass


@app.command()
@click.argument('text', required=False)
@click.option('--show-variants', is_flag=True, help='Show all message variants')
@click.option('--clipboard', is_flag=True, default=True, help='Copy best variant to clipboard')
@click.option('--config', help='Path to custom config.yaml file')
def compose(text, show_variants, clipboard, config):
    """
    Compose a professional message from unstructured thoughts.

    This command transforms raw, unstructured input into polished professional
    messages using the MessageComposerAgent.

    HOW IT WORKS:
    ═════════════════════════════════════════════════════════════════════════

    1. Takes your unstructured input
    2. Sends it to Claude via MessageComposerAgent
    3. Claude analyzes tone, structure, clarity
    4. Returns 2-3 professional variants
    5. Copies the best one to your clipboard

    THE REASONING LOOP:
    ═════════════════════════════════════════════════════════════════════════

    The MessageComposerAgent uses a "reasoning loop":

    Your input:
      "hey i need tell boss the project got delayed"

    Agent's decision-making:
      "This has tone issues (too informal)
       This has clarity issues (which boss? when?)
       Let me analyze these..."

      Claude calls: analyze_tone(text="...")
      Claude calls: check_clarity(message="...")
      Claude synthesizes: "Here are professional versions..."

    Output: Multiple polished options

    USAGE EXAMPLES:
    ═════════════════════════════════════════════════════════════════════════

    1. Compose from command line argument:
       pm compose "hey i wnat tell my boss project delayed"

       Pros: Quick, for short messages
       Cons: Can be hard to read long text in terminal

    2. Compose from interactive input (stdin):
       pm compose

       (then paste your message, Ctrl+D to finish)

       Pros: Good for longer messages
       Cons: Requires copying text first

    3. Show all variants:
       pm compose "text" --show-variants

       Shows primary + all alternatives for comparison

    4. Use custom configuration:
       pm compose "text" --config ./my-config.yaml

       Useful for different communication styles
       Work config vs personal email config

    5. Don't copy to clipboard:
       pm compose "text" --clipboard=false

       Useful for scripting or when clipboard isn't available

    INTERACTIVE MODE DETAILS:
    ═════════════════════════════════════════════════════════════════════════

    If you don't provide text argument, the tool prompts for input:

      pm compose

      📝 Enter your unstructured thoughts (press Ctrl+D when done):

    Then you can:
    - Paste your message
    - Press Enter for new lines
    - Press Ctrl+D when done (Ctrl+Z on Windows)

    This is useful for:
    - Multi-line messages
    - Complex thoughts
    - When you want to carefully compose your input

    CLIPBOARD INTEGRATION:
    ═════════════════════════════════════════════════════════════════════════

    After composing, the tool automatically copies the best message to
    your clipboard. Then you can:
    - Cmd+V (macOS) or Ctrl+V (other) to paste into email/chat
    - Manually copy if clipboard fails

    Clipboard is tried on best-effort basis:
    - Works on macOS (uses pbcopy)
    - May work on other systems (depends on available commands)
    - Always tells you if it copied

    CONFIGURATION:
    ═════════════════════════════════════════════════════════════════════════

    The --config option lets you use different configs:

      pm compose "text" --config ./work-config.yaml
      pm compose "text" --config ./personal-config.yaml

    This allows:
    - Different voice rules for different contexts
    - Different model settings
    - Different output preferences

    ERRORS AND TROUBLESHOOTING:
    ═════════════════════════════════════════════════════════════════════════

    "No input provided" error:
    - Make sure you provided text as argument or pasted it interactively
    - pm compose "your message" should work

    "CLAUDE_API_KEY not set" error:
    - Set your API key: export GROQ_API_KEY="gsk-..."
    - Get key from: https://console.groq.com

    "Error during composition" error:
    - Check your API key is valid
    - Check your internet connection
    - Check Groq API is available

    Args:
        text (str, optional): Your unstructured message.

            Optional because:
            - Can be provided as argument: pm compose "text"
            - Or from stdin: pm compose (then paste)

            If not provided, you're prompted for interactive input.

            Examples:
            - "hey i wnat tell my boss project delayed"
            - "need ask colleague for help with code review"
            - "want email client about project changes"

        show_variants (bool): Show all message variants instead of just primary.

            Default: False (only show the best one)
            Use --show-variants to see alternatives

            Why helpful:
            - Choose which variant best matches your style
            - Compare and learn what makes messages better
            - See formal vs casual vs direct versions

        clipboard (bool): Copy best variant to clipboard.

            Default: True (automatic copy)
            Use --clipboard=false to disable

            Why helpful:
            - Quick paste into email/chat
            - Works best on macOS, best-effort on others
            - Gracefully fails if not available

        config (str, optional): Path to custom config.yaml file.

            Default: ./config.yaml
            Use --config=/path/to/custom.yaml to override

            Why helpful:
            - Use different settings for different contexts
            - Different voice rules for work vs personal
            - Test different configurations

    The function handles:
    - Configuration loading with error handling
    - Interactive input from stdin
    - Input validation
    - Agent invocation
    - Result formatting and display
    - Clipboard integration with graceful fallback
    """

    # Load configuration
    # ═════════════════════════════════════════════════════════════════════════
    # Configuration contains:
    # - API settings (model, tokens)
    # - Voice rules (tone, formality)
    # - Output settings (variants count, clipboard behavior)
    # - Example messages (for training agent)
    #
    # Loading can fail if:
    # - config.yaml has YAML syntax errors
    # - File permissions prevent reading
    # - But we handle these gracefully
    # ═════════════════════════════════════════════════════════════════════════

    try:
        config_obj = Config(config_path=config)
    except Exception as e:
        # Configuration loading failed - show error and exit
        # Error could be YAML parsing, file I/O, etc.
        click.echo(f"❌ Error loading config: {e}")
        # Return instead of raising - cleaner error for CLI user
        return

    # If no text provided, prompt for input
    # ═════════════════════════════════════════════════════════════════════════
    # Users can provide text in three ways:
    # 1. As argument: pm compose "text"
    # 2. From stdin: pm compose < file.txt
    # 3. Interactively: pm compose (then paste, Ctrl+D)
    #
    # If no text argument provided, we prompt for interactive input.
    # This allows composing longer or more complex messages.
    # ═════════════════════════════════════════════════════════════════════════

    if not text:
        # Show prompt to user
        click.echo("📝 Enter your unstructured thoughts (press Ctrl+D when done):")
        try:
            # Read from stdin until EOF
            # User pastes their message, presses Ctrl+D to finish
            text = sys.stdin.read()
        except EOFError:
            # User pressed Ctrl+D (EOF) - that's fine, continue with what we have
            pass

    # Validate input
    # ═════════════════════════════════════════════════════════════════════════
    # After reading (from argument or stdin), check if we have anything to work with
    # Whitespace-only input is treated as empty (text.strip() removes spaces/newlines)
    # ═════════════════════════════════════════════════════════════════════════

    if not text.strip():
        # No content provided - can't compose without input
        click.echo("❌ No input provided")
        # Return exits the command gracefully
        return

    # Show progress indicator
    # ═════════════════════════════════════════════════════════════════════════
    # Composing can take a few seconds (API call, reasoning loop)
    # Show a spinner/indicator so user knows something is happening
    # ═════════════════════════════════════════════════════════════════════════

    click.echo("🤖 Composing message...")

    # Get API key
    # ═════════════════════════════════════════════════════════════════════════
    # MessageComposerAgent needs API key to authenticate with Claude
    # We look for CLAUDE_API_KEY environment variable
    #
    # Environment variable is standard practice:
    # - Never hardcode secrets in code
    # - User sets: export CLAUDE_API_KEY="sk-..."
    # - Code reads: os.getenv("CLAUDE_API_KEY")
    # - Can be set in .bashrc, .zshrc, .env files
    # ═════════════════════════════════════════════════════════════════════════

    api_key = os.getenv("CLAUDE_API_KEY")

    if not api_key:
        # API key not set - show helpful error message
        click.echo("❌ Error: CLAUDE_API_KEY not set")
        click.echo("   Set it: export CLAUDE_API_KEY=your-key-here")
        # Return exits the command
        return

    # Create agent and compose
    # ═════════════════════════════════════════════════════════════════════════
    # MessageComposerAgent handles:
    # 1. Tool setup (analyze_tone, suggest_structure, check_clarity)
    # 2. Reasoning loop (Claude decides what analysis needed)
    # 3. Result synthesis (multiple professional variants)
    #
    # The compose() method runs the full reasoning loop:
    # - Sends input to Claude
    # - Claude calls tools as needed
    # - Tools return analysis
    # - Claude synthesizes results
    # - Returns primary + variants
    # ═════════════════════════════════════════════════════════════════════════

    try:
        # Create agent with API key
        agent = MessageComposerAgent(api_key=api_key)

        # Run composition - this is the main work
        result = agent.compose(text)
    except Exception as e:
        # Composition failed - could be API error, network, etc.
        click.echo(f"❌ Error during composition: {e}")
        # Return exits the command
        return

    # Display results
    # ═════════════════════════════════════════════════════════════════════════
    # Format and show the primary message and variants
    # Make output clear and easy to read
    # ═════════════════════════════════════════════════════════════════════════

    # Show primary message
    # The "best" version according to Claude
    click.echo("\n✨ Composed Message:\n")
    click.echo(f"   {result['primary']}\n")

    # Show variants if requested
    # ═════════════════════════════════════════════════════════════════════════
    # user can see alternatives and choose which fits their style best
    # --show-variants flag enables this
    # ═════════════════════════════════════════════════════════════════════════

    if show_variants and result['variants']:
        # User wants to see alternatives
        click.echo("📋 Alternative versions:\n")
        # Show each variant numbered for clarity
        for i, var in enumerate(result['variants'], 1):
            click.echo(f"   Option {i}: {var}\n")

    # Copy to clipboard if requested
    # ═════════════════════════════════════════════════════════════════════════
    # By default (clipboard=True), copy best variant to clipboard
    # User can paste with Cmd+V or Ctrl+V
    #
    # If clipboard is not available (system, permissions, etc.),
    # we fail gracefully - message was already shown, clipboard is bonus
    # ═════════════════════════════════════════════════════════════════════════

    if clipboard:
        try:
            # Attempt to copy to clipboard
            _copy_to_clipboard(result['primary'])
            # Success - show confirmation
            click.echo("✅ Copied to clipboard!")
        except Exception:
            # Clipboard not available - graceful failure
            # Message was already shown, so user can still see/use it
            click.echo("ℹ️  (Clipboard copy not available on this system)")


@app.command()
def config():
    """
    Manage configuration.

    This command helps set up your configuration file (config.yaml).
    It defines your voice rules and communication preferences.

    WHAT CONFIGURATION DOES:
    ═════════════════════════════════════════════════════════════════════════

    config.yaml stores your preferences:
    - Voice rules (how you want messages to sound)
    - API settings (which model to use)
    - Output settings (how many variants, clipboard behavior)
    - Example messages (your personal style examples)

    WHY CONFIGURATION:
    ═════════════════════════════════════════════════════════════════════════

    Without config: Tool uses built-in defaults
    With config: Tool adapts to YOUR style and preferences

    Examples:
    - Professional work tone: formal, detailed
    - Casual friends: friendly, brief
    - Mixed audience: balanced, moderate formality

    CONFIGURATION STRUCTURE:
    ═════════════════════════════════════════════════════════════════════════

    config.yaml is a YAML file with sections:

    api:
      model: claude-3-5-haiku-20241022  # Which Claude model
      max_tokens: 2048                   # Token limit

    voice_rules:
      tone: professional                 # professional, casual, friendly
      formality: medium                  # low, medium, high
      avoid_words: []                    # Words to never use
      key_phrases: []                    # Phrases that are "you"

    output:
      num_variants: 2                    # How many alternatives
      include_explanations: true         # Show reasoning
      copy_to_clipboard: true            # Auto-copy

    examples:                            # Your personal examples
      good_message_1: "I wanted to..."
      good_message_2: "Quick update..."

    HOW TO CUSTOMIZE:
    ═════════════════════════════════════════════════════════════════════════

    1. Run: pm config
       → Creates config.yaml from template

    2. Edit config.yaml in your editor
       nano config.yaml
       vim config.yaml
       open config.yaml (macOS)

    3. Edit the sections that matter to you:

       For TONE, change to one of:
       - "professional" (business, formal)
       - "casual" (friendly, relaxed)
       - "direct" (to the point, brief)
       - "collaborative" (suggest, ask for input)

       For FORMALITY, change to:
       - "low" (very casual, lots of contractions)
       - "medium" (normal professional)
       - "high" (very formal, lots of "please", "would appreciate")

       For NUM_VARIANTS, set to:
       - 1 (just show the best)
       - 2 (best + one alternative) - recommended
       - 3 (best + two alternatives)

    4. Add your own examples in the EXAMPLES section:

       examples:
         work_update: "I wanted to update you that..."
         casual_request: "Hey, would you be able to..."
         formal_email: "I am writing to inform you..."

       Then Claude uses these as style references!

    5. Save and run: pm compose "text"
       Now it uses YOUR configuration

    CONFIGURATION EXAMPLES:
    ═════════════════════════════════════════════════════════════════════════

    WORK CONFIGURATION (professional.yaml):
    ────────────────────────────────────────
    voice_rules:
      tone: professional
      formality: high
      avoid_words: [hey, gonna, wanna, cool]
      key_phrases: [I wanted to inform you, At your earliest convenience]

    output:
      num_variants: 2
      copy_to_clipboard: true

    PERSONAL CONFIGURATION (personal.yaml):
    ────────────────────────────────────────
    voice_rules:
      tone: casual
      formality: low
      avoid_words: [shall, moreover]
      key_phrases: [Hey, Let me know, Would you mind]

    output:
      num_variants: 1
      copy_to_clipboard: true

    USAGE:
    ═════════════════════════════════════════════════════════════════════════

    1. Initialize configuration:
       pm config
       → Creates config.yaml

    2. Edit your preferences:
       nano config.yaml

    3. Use with different configs:
       pm compose "text" --config work.yaml
       pm compose "text" --config personal.yaml

    4. View your current config:
       cat config.yaml

    TIPS:
    ═════════════════════════════════════════════════════════════════════════

    - Start with defaults and customize gradually
    - Try different tone/formality combinations
    - Add examples of messages YOU like as reference
    - Create separate configs for different contexts
    - The agent learns from your examples!

    NEXT STEPS:
    ═════════════════════════════════════════════════════════════════════════

    1. pm config                    # Create config.yaml
    2. nano config.yaml             # Edit to customize
    3. pm compose "text"            # Use your config!
    """

    # Determine where config should be created
    # ═════════════════════════════════════════════════════════════════════════
    # By default, look for config.yaml in current directory
    # This is where user runs 'pm config' from
    # ═════════════════════════════════════════════════════════════════════════

    config_path = Path("config.yaml")

    if not config_path.exists():
        # Config doesn't exist - try to create from example
        # ═════════════════════════════════════════════════════════════════════
        # We look for config.yaml.example in the package
        # This is the template users copy from
        # ═════════════════════════════════════════════════════════════════════

        # Find the example config in the package
        # Path(__file__).parent gives us src/ directory
        # .parent.parent gives us project root
        # Actually, easier way: look relative to cli.py
        example_path = Path(__file__).parent.parent / "config.yaml.example"

        if example_path.exists():
            # Found example - copy it to config.yaml
            with open(example_path) as f:
                content = f.read()

            with open(config_path, 'w') as f:
                f.write(content)

            # Show confirmation and instructions
            click.echo(f"✅ Created {config_path} from example")
            click.echo("📝 Edit this file to set your voice rules and preferences")
            click.echo(f"\n   nano {config_path}")
            click.echo(f"   or open it in your editor")
        else:
            # Example not found - show error
            # This shouldn't happen in a properly installed package
            click.echo("❌ config.yaml.example not found")
            click.echo("   Please create config.yaml manually or reinstall the package")
    else:
        # Config already exists
        click.echo(f"✅ Config already exists at {config_path}")
        click.echo("📝 Edit this file to change your settings")
        click.echo(f"\n   nano {config_path}")


def _copy_to_clipboard(text: str) -> None:
    """
    Copy text to system clipboard.

    This is a platform-specific function. Different operating systems have
    different ways to access the clipboard:
    - macOS: pbcopy command
    - Linux: xclip or xsel commands
    - Windows: clip command

    This implementation supports macOS. Other systems will fail gracefully.

    WHY PLATFORM-SPECIFIC:
    ═════════════════════════════════════════════════════════════════════════

    Operating systems don't expose clipboard through standard Python.
    Instead, we call system commands:
    - pbcopy: macOS command to copy from stdin to clipboard
    - xclip/xsel: Linux commands for clipboard
    - clip: Windows command for clipboard

    By calling external commands, we avoid:
    - Large dependencies (PyQT, wxPython for GUI clipboard)
    - Platform-specific libraries
    - Permission issues

    GRACEFUL FAILURE:
    ═════════════════════════════════════════════════════════════════════════

    Clipboard is a convenience feature. If it fails:
    - Message was already displayed
    - User can still see the output
    - User can manually copy if needed
    - No errors stop the program

    This is why we catch exceptions in compose() and show info message
    instead of error.

    HOW IT WORKS:
    ═════════════════════════════════════════════════════════════════════════

    1. Open pbcopy subprocess
       subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
       This starts a pbcopy process ready to receive input

    2. Send text to it
       process.communicate(text.encode('utf-8'))
       This sends the text as bytes to pbcopy

    3. Wait for completion
       communicate() waits for the process to finish
       Returns (stdout, stderr)

    4. Done
       Text is now on clipboard, ready to paste

    PRODUCTION IMPROVEMENTS:
    ═════════════════════════════════════════════════════════════════════════

    For a more robust version, consider:

    def _copy_to_clipboard(text: str) -> None:
        '''Copy text to clipboard, with fallback support.'''
        import platform
        import subprocess

        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            elif system == "Linux":
                # Try xclip first, then xsel
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'],
                                              stdin=subprocess.PIPE)
                except FileNotFoundError:
                    process = subprocess.Popen(['xsel', '--clipboard', '--input'],
                                              stdin=subprocess.PIPE)
            elif system == "Windows":
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
            else:
                raise NotImplementedError(f"Clipboard not supported on {system}")

            process.communicate(text.encode('utf-8'))
        except Exception:
            raise

    Args:
        text (str): Text to copy to clipboard.

            Must be a string. Will be encoded as UTF-8 bytes
            for transmission to pbcopy.

    Raises:
        Exception: If clipboard command fails.

            Raised for:
            - pbcopy not found
            - Process exits with error
            - Permission denied
            - Other subprocess issues

            Caught in compose() and handled gracefully.

    Implementation Details:
    ═════════════════════════════════════════════════════════════════════════

    Uses subprocess.Popen and communicate() for:
    - Cleaner than shell=True (security)
    - Better than os.system() (error handling)
    - Wait for completion (communicate blocks until done)
    - Get output if needed (though we don't use it)

    Why subprocess.PIPE for stdin:
    - Allows us to send data directly
    - Avoids need for temp files
    - Efficient for small amounts of data

    Why text.encode('utf-8'):
    - subprocess expects bytes, not strings
    - UTF-8 handles all Unicode characters
    - Standard encoding for text interchange

    Why catch and re-raise:
    - Allows compose() to catch and handle gracefully
    - Don't want to crash the whole command
    - But do want to report error if needed

    Example:
        >>> _copy_to_clipboard("Hello, world!")
        >>> # Text now on clipboard, can be pasted
        >>>
        >>> # If fails:
        >>> _copy_to_clipboard("text")  # Raises Exception
        >>> # Caught in compose() and shown as info message
    """
    try:
        # Open pbcopy process on macOS
        # stdin=subprocess.PIPE allows us to send data to it
        import subprocess
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)

        # Send the text to pbcopy
        # communicate() sends data and waits for process to finish
        # text.encode('utf-8') converts string to bytes that subprocess expects
        process.communicate(text.encode('utf-8'))
    except Exception as e:
        # Re-raise for caller to handle
        # Caller (compose) will catch and show graceful message
        raise e


if __name__ == '__main__':
    # Entry point when script is run directly
    # python3 src/cli.py compose "text"
    # But normally called as: pm compose "text"
    # (after installation via setup.py entry_points)
    app()
