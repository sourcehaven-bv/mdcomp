"""Custom Jinja2 filters for mdcomp."""

import json
import re
import subprocess
from datetime import datetime
from typing import Any

import yaml


def from_json(value: str) -> dict | list | None:
    """Parse JSON string to Python object. Returns None for empty strings."""
    if not value or not value.strip():
        return None
    return json.loads(value)


def from_yaml(value: str) -> dict | list | None:
    """Parse YAML string to Python object. Returns None for empty strings."""
    return yaml.safe_load(value)


def to_json(value: dict | list, indent: int | None = None) -> str:
    """Serialize Python object to JSON string."""
    return json.dumps(value, indent=indent, default=str)


def to_yaml(value: dict | list) -> str:
    """Serialize Python object to YAML string."""
    return yaml.dump(value, default_flow_style=False)


def slugify(value: Any) -> str:
    """Convert string to URL-friendly slug. Non-string inputs are converted to string first."""
    if not isinstance(value, str):
        value = str(value)
    value = value.lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[-\s]+", "-", value)
    return value.strip("-")


def shift_headers(value: str, levels: int = 1) -> str:
    """
    Shift markdown header levels by a specified amount.

    Uses mistletoe to properly parse markdown AST, modify header levels,
    and render back to markdown.

    Examples:
        {{ content("snippet.md") | shift_headers(2) }}
        # Title -> ### Title
        ## Subtitle -> #### Subtitle

        {{ content("snippet.md") | shift_headers(-1) }}
        ### Title -> ## Title
    """
    if levels == 0:
        return value

    from typing import Any

    from mistletoe import Document
    from mistletoe.block_token import Heading
    from mistletoe.markdown_renderer import MarkdownRenderer

    def shift_heading_levels(token: Any, levels: int) -> None:
        """Recursively shift heading levels in the AST."""
        if isinstance(token, Heading):
            new_level = token.level + levels
            # Clamp between 1 and 6
            token.level = max(1, min(6, new_level))
        if hasattr(token, "children") and token.children:
            for child in token.children:
                shift_heading_levels(child, levels)

    with MarkdownRenderer() as renderer:
        doc = Document(value)
        shift_heading_levels(doc, levels)
        return renderer.render(doc)


def date_format(value: str | datetime, fmt: str = "%Y-%m-%d") -> str:
    """Format date string or datetime object."""
    if isinstance(value, str):
        # Try common date formats
        parsed: datetime | None = None
        for parse_fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                parsed = datetime.strptime(value, parse_fmt)
                break
            except ValueError:
                continue
        if parsed is None:
            return value  # Return as-is if parsing fails
        return parsed.strftime(fmt)
    return value.strftime(fmt)


def headers(
    value: str,
    min_level: int = 1,
    max_level: int = 6,
) -> list[dict[str, int | str]]:
    """
    Extract headers from markdown content.

    Returns a list of dicts with 'level' (int) and 'title' (str) keys.
    Use with the slugify filter to generate anchor links.

    Examples:
        {% for h in body | headers %}
        {{ "  " * (h.level - 2) }}- [{{ h.title }}](#{{ h.title | slugify }})
        {% endfor %}

        {# Filter to only h2 and h3 #}
        {% for h in body | headers(min_level=2, max_level=3) %}
        ...
        {% endfor %}
    """
    from mistletoe import Document
    from mistletoe.block_token import Heading
    from mistletoe.span_token import RawText

    def extract_text(token: Any) -> str:
        """Extract plain text from a token and its children."""
        if isinstance(token, RawText):
            return token.content
        if hasattr(token, "children") and token.children:
            return "".join(extract_text(child) for child in token.children)
        return ""

    def collect_headers(token: Any, result: list[dict[str, int | str]]) -> None:
        """Recursively collect headers from the AST."""
        if isinstance(token, Heading) and min_level <= token.level <= max_level:
            title = extract_text(token).strip()
            result.append({"level": token.level, "title": title})
        if hasattr(token, "children") and token.children:
            for child in token.children:
                collect_headers(child, result)

    doc = Document(value)
    result: list[dict[str, int | str]] = []
    collect_headers(doc, result)
    return result


def pipe(value: str, command: str) -> str:
    """
    Pipe value through a shell command.

    The value is passed to the command's stdin, and stdout is returned.

    Examples:
        {{ content("doc.md") | pipe("pandoc -f markdown -t latex") }}
        {{ data | to_json | pipe("jq '.items[]'") }}
        {{ text | pipe("sort | uniq") }}
    """
    result = subprocess.run(
        command,
        shell=True,
        input=value,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Pipe command failed: {command}\nStderr: {result.stderr}")
    return result.stdout


# Registry of all custom filters
FILTERS = {
    "from_json": from_json,
    "from_yaml": from_yaml,
    "to_json": to_json,
    "to_yaml": to_yaml,
    "slugify": slugify,
    "date_format": date_format,
    "shift_headers": shift_headers,
    "headers": headers,
    "pipe": pipe,
}
