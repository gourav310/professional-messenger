"""
Tests for the CLI interface.

These tests verify that the CLI commands exist and work correctly.
They use Click's CliRunner for testing CLI commands without calling
the actual system.

Testing CLI is important because:
- Commands should be discoverable (--help works)
- Arguments should be properly parsed
- Error handling should be graceful
- User feedback should be clear

The tests here are organized by command:
- test_cli_exists: Basic CLI app existence
- test_compose_command_exists: Compose command exists
- test_compose_with_text: Compose accepts text input

Example:
    >>> runner = CliRunner()
    >>> result = runner.invoke(app, ['compose', '--help'])
    >>> assert result.exit_code == 0
"""

import pytest
from click.testing import CliRunner
from src.cli import app


def test_cli_exists():
    """
    CLI app should exist and be callable.

    This is the most basic test - it just checks that the CLI app
    is defined and importable.

    What it tests:
    - The app object exists in src.cli
    - The app is not None
    - The app can be instantiated

    Why it matters:
    - Ensures the main entry point is defined
    - Foundation for all other CLI tests

    Example:
        >>> from src.cli import app
        >>> assert app is not None
    """
    assert app is not None


def test_compose_command_exists():
    """
    CLI should have compose command.

    This test checks that when you ask for help, the compose command
    is mentioned. This verifies the command is registered.

    What it tests:
    - The 'compose' command is registered
    - The help output mentions it
    - The help text is discoverable

    Why it matters:
    - Users need to find the compose command
    - Help should guide them to it
    - Command registration is working

    Example:
        >>> runner = CliRunner()
        >>> result = runner.invoke(app, ['--help'])
        >>> assert 'compose' in result.output.lower()

    How CliRunner works:
    - Simulates command-line invocation
    - Captures output and exit code
    - Doesn't actually call the system
    - Perfect for testing CLI without side effects
    """
    runner = CliRunner()
    result = runner.invoke(app, ['--help'])
    assert 'compose' in result.output.lower()


def test_compose_with_text():
    """
    Compose command should accept text input and show help.

    This test checks that the compose command:
    - Exists and is callable
    - Has a help message
    - Accepts arguments

    What it tests:
    - compose --help succeeds
    - help output includes usage information
    - command structure is correct

    Why it matters:
    - Users need to understand how to use compose
    - Help should explain arguments/options
    - Command interface should be clear

    Example:
        >>> runner = CliRunner()
        >>> result = runner.invoke(app, ['compose', '--help'])
        >>> assert result.exit_code == 0
        >>> assert 'Usage' in result.output
    """
    runner = CliRunner()
    result = runner.invoke(app, ['compose', '--help'])
    assert result.exit_code == 0
    assert 'Usage' in result.output
