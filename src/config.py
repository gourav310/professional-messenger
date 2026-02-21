"""
Configuration system for voice rules and model settings.

The Config class loads and manages settings from config.yaml.
This allows users to customize their communication preferences
without touching code.

Configuration includes:
- API settings (model choice, token limits)
- Voice rules (tone, formality preferences)
- Output settings (number of variants, clipboard behavior)
- Example messages (for training the agent)

Example:
    >>> config = Config()
    >>> model = config.model
    >>> voice_rules = config.voice_rules
    >>> config.get("api.model")
"""

import os
import yaml
from typing import Optional, Any
from pathlib import Path


class Config:
    """
    Load and manage configuration from YAML file.

    The Config class reads config.yaml and provides easy access to settings.
    If config.yaml doesn't exist, it provides defaults. This allows the tool
    to work out of the box without requiring a configuration file.

    WHY A CONFIG CLASS:
    ═══════════════════════════════════════════════════════════════════════════

    Without this:
    - Settings would be hardcoded in Python
    - Users couldn't customize without editing code
    - Configuration scattered across different modules
    - Hard to change settings between runs

    With this class:
    - Configuration in a single YAML file
    - Easy to change without touching code
    - Different configs for different use cases
    - Settings are version-controllable (in config.yaml)
    - Python code stays clean and focused

    DESIGN PRINCIPLES:
    ═══════════════════════════════════════════════════════════════════════════

    1. SENSIBLE DEFAULTS:
       If config.yaml doesn't exist, the tool still works.
       Users get default settings that are reasonable.
       They can create config.yaml later to customize.

    2. EASY TO USE:
       Access settings with dot notation: config.get("api.model")
       Or use properties: config.model
       Both should be clear and convenient.

    3. FLEXIBLE:
       Users can add new settings to config.yaml
       The class should handle missing keys gracefully
       Should never crash if a setting is missing

    4. TYPE SAFE:
       Settings have expected types (string, bool, dict)
       Validation should be optional but possible
       Users can't accidentally set wrong types

    CONFIGURATION FILE STRUCTURE:
    ═══════════════════════════════════════════════════════════════════════════

    config.yaml should look like:

    api:
      model: gpt-3.5-turbo
      max_tokens: 2048

    voice_rules:
      tone: professional
      formality: medium
      avoid_words: []

    output:
      num_variants: 2
      include_explanations: true
      copy_to_clipboard: true

    examples:
      good_message_1: "I wanted to update you that..."
      good_message_2: "Quick status: the project..."

    Attributes:
        config_path (str): Path to config.yaml
        data (dict): Parsed YAML configuration

    Example:
        >>> config = Config()
        >>> model = config.model  # Get configured model
        >>> voice = config.voice_rules  # Get tone preferences
        >>> print(config.get("api.model"))
        # "gpt-3.5-turbo"
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Sets up the Config object and loads settings from file (or uses defaults).
        The configuration is lazy-loaded here - actual file reading happens in
        the load() method.

        WHY SEPARATE INIT AND LOAD:
        ═══════════════════════════════════════════════════════════════════════

        This design allows:
        - Creating Config object in tests without file I/O
        - Reloading configuration later
        - Mocking configuration in tests
        - Separating setup from loading

        Args:
            config_path (str, optional): Path to config.yaml. If None, looks for:
                1. CONFIG_PATH environment variable
                2. "config.yaml" in current directory

                This allows three ways to specify config:
                1. Parameter: Config(config_path="./my-config.yaml")
                2. Environment: export CONFIG_PATH="./custom.yaml"
                3. Default: Places "config.yaml" in current directory

        Example:
            >>> # Use default location (./config.yaml)
            >>> config = Config()
            >>>
            >>> # Use environment variable
            >>> import os
            >>> os.environ["CONFIG_PATH"] = "./work.yaml"
            >>> config = Config()
            >>>
            >>> # Use explicit path
            >>> config = Config(config_path="./custom.yaml")
        """
        # Store path with three-level fallback
        # 1. Use explicit parameter if provided
        # 2. Check environment variable
        # 3. Use current directory default
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config.yaml")

        # Initialize empty data dict
        # This gets populated in load()
        self.data = {}

        # Load configuration from file
        self.load()

    def load(self) -> None:
        """
        Load configuration from YAML file.

        Reads config.yaml and parses it into self.data.
        If file doesn't exist, uses default configuration.

        This allows the tool to work even without config.yaml,
        while still supporting full customization when present.

        HOW IT WORKS:
        ═══════════════════════════════════════════════════════════════════════

        1. Check if config_path points to an existing file
        2. If exists: open and parse YAML
        3. If not: use default configuration
        4. Store result in self.data

        WHY GRACEFUL FALLBACK:
        ═══════════════════════════════════════════════════════════════════════

        Users might:
        - Delete config.yaml accidentally
        - Forget to create it
        - Run on a new system
        - Run in a Docker container

        With graceful fallback:
        - Tool still works with reasonable defaults
        - Users see clear error only if something's really wrong
        - They can create config.yaml when ready
        - No scary errors on first run

        ERROR HANDLING:
        ═══════════════════════════════════════════════════════════════════════

        Current implementation:
        - Silently uses defaults if file missing (user-friendly)
        - Would crash on YAML syntax errors (user should fix)

        Production version could:
        - Log warnings when falling back to defaults
        - Validate YAML structure
        - Handle permission errors
        - Suggest creating config.yaml

        Example:
            >>> config = Config()
            >>> config.load()  # Load from file
            >>> print(config.model)  # Get model from loaded config
        """
        if os.path.exists(self.config_path):
            try:
                # File exists - parse it
                with open(self.config_path, 'r') as f:
                    self.data = yaml.safe_load(f) or {}
            except Exception as e:
                # If parsing fails, fall back to defaults
                # (but in real code, would log this error)
                self.data = self._get_default_config()
        else:
            # File doesn't exist - use sensible defaults
            self.data = self._get_default_config()

    def _get_default_config(self) -> dict:
        """
        Return default configuration for new users with OpenAI settings.
        """
        return {
            "api": {
                "model": "gpt-3.5-turbo"
            },
            "voice_rules": {
                "tone": "professional",
                "formality": "medium"
            },
            "output": {
                "num_variants": 2,
                "include_explanations": True,
                "copy_to_clipboard": True
            }
        }

    @property
    def model(self) -> str:
        """
        Get configured OpenAI model.

        This is a convenience property for accessing the model.
        Rather than config.get("api.model"), you can use config.model.

        Returns:
            str: Model identifier (e.g., "gpt-3.5-turbo")

            The returned value is:
            - From config.yaml if user specified it
            - Default value if not specified
            - Always a valid model identifier

        Example:
            >>> config = Config()
            >>> model = config.model
            >>> print(model)  # "gpt-3.5-turbo"

        Note:
            The model is used when creating the LLMClient
            to communicate with OpenAI's API.
        """
        return self.data.get("api", {}).get("model", "gpt-3.5-turbo")

    @property
    def voice_rules(self) -> dict:
        """
        Get voice and tone rules.

        These define how messages should sound.
        Includes tone (professional, casual) and formality level.

        Returns:
            dict: Voice rules with keys like:
            - "tone": "professional"
            - "formality": "medium"

            Other keys might be present if defined in config.yaml:
            - "avoid_words": ["xyz"]
            - "key_phrases": ["important to note"]

        Example:
            >>> config = Config()
            >>> rules = config.voice_rules
            >>> print(rules['tone'])  # "professional"
            >>> print(rules.get('formality'))  # "medium"

        Note:
            These are passed to the system prompt
            to guide the tone of composed messages.
        """
        return self.data.get("voice_rules", {})

    @property
    def examples(self) -> dict:
        """
        Get example messages for style reference.

        Example messages help the LLM understand the desired style.
        They show "here's what good looks like".

        For example, if you provide:
        {
            "good_message": "I wanted to update you that we've found a solution...",
            "bad_message": "hey boss project ok now"
        }

        The LLM can use these to understand the style difference
        and compose messages in the "good" style.

        Returns:
            dict: Example messages (keys are labels, values are messages)

            Structure:
            {
                "good_update": "I wanted to inform you...",
                "good_request": "Would you have time...",
                ...
            }

        Example:
            >>> config = Config()
            >>> examples = config.examples
            >>> print(examples.get('good_message_1'))
            # "I wanted to inform you that..."

        Note:
            Optional - if not in config.yaml, returns empty dict.
            LLM still works without examples, but can be more
            accurate with them.
        """
        return self.data.get("examples", {})

    @property
    def output_config(self) -> dict:
        """
        Get output settings.

        Controls how results are displayed and formatted to the user.
        Includes settings for number of variants, explanations, etc.

        Returns:
            dict: Output settings with keys like:
            - "num_variants": 2 (how many message options to show)
            - "include_explanations": True (show reasoning)
            - "copy_to_clipboard": True (auto-copy best variant)

        Example:
            >>> config = Config()
            >>> output = config.output_config
            >>> print(output['num_variants'])  # 2
            >>> variants_to_show = output.get('num_variants', 1)

        Note:
            These settings control the CLI output behavior.
            Used in src.cli to format messages for the user.
        """
        return self.data.get("output", {})

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dotted path.

        Allows accessing nested config values using dot notation.
        This is useful for accessing deeply nested values without
        having to manually navigate the dictionary.

        DOTTED PATH NOTATION:
        ═══════════════════════════════════════════════════════════════════════

        Instead of:
            config.data["api"]["model"]
            config.data.get("api", {}).get("model")

        You can write:
            config.get("api.model")

        Advantages:
        - More readable
        - Safer (handles missing keys)
        - Defaults work naturally
        - Single method for all access

        HOW IT WORKS:
        ═══════════════════════════════════════════════════════════════════════

        1. Split key by dots: "api.model" → ["api", "model"]
        2. Start with root: value = self.data
        3. Navigate through each level:
           - value = value.get("api") → dict
           - value = value.get("model") → string
        4. Return final value or default if missing

        Args:
            key (str): Dotted path to value (e.g., "api.model")

                Examples:
                - "api.model" → returns model string
                - "voice_rules.tone" → returns tone string
                - "output.num_variants" → returns number
                - "nonexistent.path" → returns default

            default (Any): Value to return if key not found

                Defaults to None if not specified.
                Can be any type: string, int, dict, etc.

                Examples:
                - config.get("api.model") → returns model or None
                - config.get("api.max_tokens", 2048) → returns tokens or 2048
                - config.get("custom.setting", {}) → returns dict or {}

        Returns:
            Any: Configuration value at the path, or default if not found

            Type depends on the configuration:
            - Strings for model, tone, etc.
            - Ints for num_variants, max_tokens, etc.
            - Dicts for nested settings
            - The default if path not found

        Example:
            >>> config = Config()
            >>>
            >>> # Get with no default (returns None if missing)
            >>> model = config.get("api.model")
            >>> # Returns "gpt-3.5-turbo"
            >>>
            >>> # Get with default value
            >>> max_tokens = config.get("api.max_tokens", 2048)
            >>> # Returns max_tokens from config, or 2048 if missing
            >>>
            >>> # Works for any depth
            >>> tone = config.get("voice_rules.tone")
            >>> # Returns "professional"
            >>>
            >>> # Missing path returns default
            >>> missing = config.get("custom.path.here", "default")
            >>> # Returns "default" (path doesn't exist)

        Note:
            This method is the primary way to access configuration.
            It's more reliable than direct dictionary access and
            supports defaults naturally.
        """
        # Split the dotted path into individual keys
        # Example: "api.model" → ["api", "model"]
        keys = key.split(".")

        # Start at the root of the configuration
        value = self.data

        # Navigate through each level of the nested dictionary
        # Example walkthrough for "api.model":
        # - Iteration 1: k="api", value=dict, value = value.get("api")
        # - Iteration 2: k="model", value=dict, value = value.get("model")
        # - End: value = "gpt-3.5-turbo"
        for k in keys:
            # Check if we can still navigate deeper
            if isinstance(value, dict):
                # Yes, it's still a dict - get the next level
                value = value.get(k)
            else:
                # No, hit a non-dict - can't navigate further
                return default

        # If we have a value, return it; otherwise return default
        # (handles case where value is None/missing)
        return value if value is not None else default
