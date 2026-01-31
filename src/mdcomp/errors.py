"""Custom exception hierarchy for mdcomp."""

from __future__ import annotations


class MdcompError(Exception):
    """Base exception for all mdcomp errors.

    All user-facing errors should be subclasses of this. The CLI layer
    catches MdcompError to produce clean, friendly error messages instead
    of raw Python tracebacks.
    """


class TemplateError(MdcompError):
    """Error during template rendering."""


class TemplateSyntaxError(TemplateError):
    """Invalid Jinja2 template syntax."""


class UndefinedVariableError(TemplateError):
    """Reference to an undefined variable in strict mode."""


class ContextError(MdcompError):
    """Error loading or parsing context data."""


class ContextParseError(ContextError):
    """Error parsing a context file (JSON, YAML) or stdin input."""


class ContentNotFoundError(MdcompError):
    """A file referenced in a template could not be found."""


class ShellError(MdcompError):
    """A shell command (shell() or pipe()) failed."""
