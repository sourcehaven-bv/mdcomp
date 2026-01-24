"""Context/variable management with layered resolution."""

import json
import os
import sys
from pathlib import Path

import yaml


def load_yaml_or_json(path: Path) -> dict:
    """Load a YAML or JSON file."""
    content = path.read_text()
    if path.suffix == ".json":
        return json.loads(content)
    return yaml.safe_load(content) or {}


def parse_var(var_string: str) -> tuple[str, str]:
    """Parse a key=value string into a tuple."""
    if "=" not in var_string:
        raise ValueError(f"Invalid variable format: {var_string}. Expected key=value")
    key, _, value = var_string.partition("=")
    return key.strip(), value


def load_context(
    context_file: Path | None = None,
    context_stdin: bool = False,
    var_overrides: list[str] | None = None,
    env_prefix: str = "MDCOMP_VAR_",
) -> dict:
    """
    Load context with layered resolution.

    Priority (lowest to highest):
    1. Environment variables (prefixed with env_prefix)
    2. Context file (YAML or JSON)
    3. CLI --var overrides
    """
    context: dict = {}

    # Layer 1: Environment variables
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            var_name = key[len(env_prefix) :]
            # Try to parse as JSON for complex values
            try:
                context[var_name] = json.loads(value)
            except json.JSONDecodeError:
                context[var_name] = value

    # Layer 2: Context file
    if context_file and context_file.exists():
        file_context = load_yaml_or_json(context_file)
        context.update(file_context)

    # Layer 2b: Context from stdin
    if context_stdin:
        stdin_data = sys.stdin.read()
        if stdin_data.strip():
            stdin_context = json.loads(stdin_data)
            context.update(stdin_context)

    # Layer 3: CLI overrides
    if var_overrides:
        for var_string in var_overrides:
            key, value = parse_var(var_string)
            # Try to parse as JSON for complex values
            try:
                context[key] = json.loads(value)
            except json.JSONDecodeError:
                context[key] = value

    return context
