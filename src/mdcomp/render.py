"""Jinja2 rendering environment with custom functions."""

import subprocess
from pathlib import Path
from typing import Any

import frontmatter
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from mdcomp.filters import FILTERS
from mdcomp.query import glob_files, query_files


def create_environment(
    template_dir: Path | None = None,
    content_base: Path | None = None,
    strict: bool = False,
    context: dict | None = None,
) -> Environment:
    """Create a Jinja2 environment with custom functions and filters.

    Args:
        template_dir: Directory containing the template (for Jinja2 includes)
        content_base: Base directory for content functions (defaults to cwd)
        strict: If True, fail on undefined variables
        context: Context dict for render_content function
    """
    # Base directory for content lookups (defaults to cwd)
    resolved_content_base = (content_base or Path()).resolve()

    # Resolved template directory (for template_dir variable)
    resolved_template_dir = template_dir.resolve() if template_dir else Path().resolve()

    # Context for render_content function
    render_context = context if context else {}

    # Search paths for Jinja2 includes (template dir first, then cwd)
    search_paths = []
    if template_dir:
        search_paths.append(str(template_dir))
    search_paths.append(".")  # Current directory as fallback

    env_kwargs: dict[str, Any] = {
        "loader": FileSystemLoader(search_paths),
        "autoescape": False,  # No escaping for Markdown/LaTeX output
        "trim_blocks": True,
        "lstrip_blocks": True,
    }
    if strict:
        env_kwargs["undefined"] = StrictUndefined

    env = Environment(**env_kwargs)

    # Add custom filters
    env.filters.update(FILTERS)

    # Create path-resolving wrapper for content functions
    def resolve_content_path(path: str | Path, base: str | Path | None = None) -> Path:
        """Resolve a path relative to content base or explicit base."""
        p = Path(path)
        if p.is_absolute():
            return p
        if base is not None:
            effective_base = Path(base).resolve()
        else:
            effective_base = resolved_content_base
        return effective_base / p

    def read_file(path: str | Path, base: str | Path | None = None) -> str:
        """Read and return file contents as a string.

        Args:
            path: Path to file (absolute or relative to content base)
            base: Optional base directory override
        """
        return resolve_content_path(path, base).read_text()

    def get_content(path: str | Path, base: str | Path | None = None) -> str:
        """Get the content of a markdown file without frontmatter.

        Args:
            path: Path to file (absolute or relative to content base)
            base: Optional base directory override
        """
        post = frontmatter.load(resolve_content_path(path, base))
        return post.content

    def get_render_content(path: str | Path, base: str | Path | None = None) -> str:
        """Get the content of a markdown file without frontmatter, rendered as a template.

        Args:
            path: Path to file (absolute or relative to content base)
            base: Optional base directory override
        """
        post = frontmatter.load(resolve_content_path(path, base))
        # Render the content as a Jinja2 template using the current context
        template = env.from_string(post.content)
        return template.render(**render_context)

    def get_frontmatter(path: str | Path, base: str | Path | None = None) -> dict:
        """Get the frontmatter of a markdown file as a dictionary.

        Args:
            path: Path to file (absolute or relative to content base)
            base: Optional base directory override
        """
        post = frontmatter.load(resolve_content_path(path, base))
        return post.metadata

    def glob_wrapper(pattern: str, base: str | Path | None = None) -> list[Path]:
        """Find files matching a glob pattern.

        Args:
            pattern: Glob pattern to match
            base: Base directory for search (defaults to content base)
        """
        if base is not None:
            search_dir = Path(base).resolve() if not Path(base).is_absolute() else Path(base)
        else:
            search_dir = resolved_content_base
        return glob_files(pattern, search_dir)

    def query_wrapper(
        directory: str | Path, base: str | Path | None = None, **filters: Any
    ) -> list[Any]:
        """Query markdown files by frontmatter filters.

        Args:
            directory: Directory to search
            base: Optional base directory override
            **filters: Frontmatter field filters
        """
        return query_files(resolve_content_path(directory, base), **filters)

    # Add global functions
    env.globals["read"] = read_file
    env.globals["content"] = get_content
    env.globals["render_content"] = get_render_content
    env.globals["frontmatter"] = get_frontmatter
    env.globals["meta"] = get_frontmatter  # Alias
    env.globals["glob"] = glob_wrapper
    env.globals["query"] = query_wrapper
    env.globals["shell"] = run_shell

    # Add path variables for use in templates
    env.globals["template_dir"] = resolved_template_dir
    env.globals["cwd"] = Path().resolve()

    return env


def run_shell(command: str) -> str:
    """Execute a shell command and return its stdout."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}\nStderr: {result.stderr}")
    return result.stdout


def render_template(
    template_path: Path,
    context: dict,
    strict: bool = False,
    content_base: Path | None = None,
) -> str:
    """
    Render a Jinja2 template with the given context.

    Args:
        template_path: Path to the template file
        context: Dictionary of variables to pass to the template
        strict: If True, fail on undefined variables
        content_base: Base directory for content functions (overrides frontmatter)

    Returns:
        Rendered template as a string
    """
    template_dir = template_path.parent.resolve()

    # Load and parse template frontmatter for defaults
    template_content = template_path.read_text()
    if template_content.startswith("---"):
        post = frontmatter.loads(template_content)
        # Template frontmatter provides defaults (lower priority than context)
        merged_context = {**post.metadata, **context}
        template_body = post.content
        template_metadata = post.metadata
    else:
        merged_context = context
        template_body = template_content
        template_metadata = {}

    # Determine content base: CLI flag > frontmatter > cwd (default)
    effective_content_base = content_base
    if effective_content_base is None and "content_base" in template_metadata:
        # Resolve frontmatter content_base relative to template directory
        fm_content_base = Path(template_metadata["content_base"])
        if fm_content_base.is_absolute():
            effective_content_base = fm_content_base
        else:
            effective_content_base = template_dir / fm_content_base

    # Create environment with merged context for render_content() function
    env = create_environment(
        template_dir=template_dir,
        content_base=effective_content_base,
        strict=strict,
        context=merged_context,
    )

    # Create template from string (since we may have stripped frontmatter)
    template = env.from_string(template_body)

    return template.render(**merged_context)


def render_string(template_string: str, context: dict, base_dir: Path | None = None) -> str:
    """
    Render a Jinja2 template string with the given context.

    Args:
        template_string: Template content as a string
        context: Dictionary of variables to pass to the template
        base_dir: Optional base directory for file operations

    Returns:
        Rendered template as a string
    """
    env = create_environment(template_dir=base_dir)
    template = env.from_string(template_string)
    return template.render(**context)
