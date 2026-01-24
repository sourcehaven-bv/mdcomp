"""Query markdown files by frontmatter metadata."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter


@dataclass
class Document:
    """A markdown document with metadata and content."""

    path: Path
    meta: dict
    content: str

    @classmethod
    def load(cls, path: Path) -> "Document":
        """Load a document from a file path."""
        post = frontmatter.load(path)
        return cls(path=path, meta=post.metadata, content=post.content)


def match_value(actual: Any, expected: Any, operator: str = "eq") -> bool:
    """Check if actual value matches expected value with given operator."""
    if actual is None:
        return False

    if operator == "eq":
        return actual == expected
    elif operator == "contains":
        if isinstance(actual, (list, tuple)):
            return expected in actual
        if isinstance(actual, str):
            return expected in actual
        return False
    elif operator == "startswith":
        return isinstance(actual, str) and actual.startswith(expected)
    elif operator == "endswith":
        return isinstance(actual, str) and actual.endswith(expected)
    elif operator == "gt":
        return actual > expected
    elif operator == "gte":
        return actual >= expected
    elif operator == "lt":
        return actual < expected
    elif operator == "lte":
        return actual <= expected
    else:
        return actual == expected


def parse_filter_key(key: str) -> tuple[str, str]:
    """Parse a filter key into field name and operator."""
    operators = ["__contains", "__startswith", "__endswith", "__gt", "__gte", "__lt", "__lte"]
    for op in operators:
        if key.endswith(op):
            return key[: -len(op)], op[2:]  # Remove __ prefix
    return key, "eq"


def matches_filters(doc: Document, filters: dict) -> bool:
    """Check if a document matches all given filters."""
    for key, expected in filters.items():
        field, operator = parse_filter_key(key)
        actual = doc.meta.get(field)
        if not match_value(actual, expected, operator):
            return False
    return True


def query_files(directory: str | Path, **filters: Any) -> list[Document]:
    """
    Query markdown files in a directory by frontmatter fields.

    Examples:
        query_files("snippets/", status="published")
        query_files("docs/", tags__contains="api")
        query_files("posts/", date__gte="2024-01-01")
    """
    directory = Path(directory)
    if not directory.exists():
        return []

    results = []
    for path in directory.rglob("*.md"):
        try:
            doc = Document.load(path)
            if matches_filters(doc, filters):
                results.append(doc)
        except Exception:
            # Skip files that can't be parsed
            continue

    return results


def glob_files(pattern: str, base_dir: str | Path = ".") -> list[Path]:
    """Return list of files matching a glob pattern."""
    base = Path(base_dir)
    return sorted(base.glob(pattern))
