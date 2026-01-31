"""Command-line interface for mdcomp."""

import traceback
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mdcomp import __version__
from mdcomp.context import load_context
from mdcomp.errors import MdcompError
from mdcomp.query import Document, query_files
from mdcomp.render import render_template


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"mdcomp {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="mdcomp",
    help="Compose documents from Markdown snippets and templates.",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)

# Module-level state for global options
_state: dict[str, bool] = {"verbose": False}


def _handle_error(e: Exception) -> None:
    """Print a user-friendly error message, with optional traceback."""
    if isinstance(e, MdcompError):
        err_console.print(f"[red]Error:[/red] {e}")
    else:
        err_console.print(f"[red]Unexpected error:[/red] {e}")
    if _state["verbose"]:
        err_console.print(f"\n[dim]{traceback.format_exc()}[/dim]")


@app.command()
def render(
    template: Annotated[Path, typer.Argument(help="Path to the template file")],
    context: Annotated[
        Path | None,
        typer.Option("-c", "--context", help="YAML or JSON context file"),
    ] = None,
    context_stdin: Annotated[
        bool,
        typer.Option("--context-stdin", help="Read context as JSON from stdin"),
    ] = False,
    var: Annotated[
        list[str] | None,
        typer.Option("--var", help="Set variable as key=value (repeatable)"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("-o", "--output", help="Output file (default: stdout)"),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail on undefined variables"),
    ] = False,
    content_base: Annotated[
        Path | None,
        typer.Option(
            "--content-base",
            help="Base directory for content lookups (default: cwd)",
        ),
    ] = None,
) -> None:
    """Render a template with context variables."""
    if not template.exists():
        err_console.print(f"[red]Error:[/red] Template not found: {template}")
        raise typer.Exit(1)

    try:
        # Load context from various sources
        ctx = load_context(
            context_file=context,
            context_stdin=context_stdin,
            var_overrides=var,
        )

        # Render the template
        result = render_template(
            template_path=template,
            context=ctx,
            strict=strict,
            content_base=content_base,
        )

        # Output result
        if output:
            output.write_text(result)
            err_console.print(f"[green]Written to:[/green] {output}")
        else:
            print(result)

    except Exception as e:
        _handle_error(e)
        raise typer.Exit(1) from None


@app.command("list")
def list_files(
    directory: Annotated[Path, typer.Argument(help="Directory to search")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: table, json, yaml"),
    ] = "table",
    filter: Annotated[
        list[str] | None,
        typer.Option("--filter", help="Filter by field=value (repeatable)"),
    ] = None,
    sort: Annotated[
        str | None,
        typer.Option("--sort", "-s", help="Sort by frontmatter field"),
    ] = None,
    reverse: Annotated[
        bool,
        typer.Option("--reverse", "-r", help="Reverse sort order"),
    ] = False,
) -> None:
    """List markdown files with their frontmatter metadata."""
    if not directory.exists():
        err_console.print(f"[red]Error:[/red] Directory not found: {directory}")
        raise typer.Exit(1)

    # Parse filters
    filters = {}
    if filter:
        for f in filter:
            if "=" in f:
                key, _, value = f.partition("=")
                filters[key] = value

    # Query files
    docs = query_files(directory, **filters)

    # Sort if requested
    if sort:
        docs.sort(key=lambda d: d.meta.get(sort, ""), reverse=reverse)
    elif reverse:
        docs.reverse()

    # Output in requested format
    if format == "json":
        import json

        output = [{"path": str(d.path), "meta": d.meta} for d in docs]
        print(json.dumps(output, indent=2, default=str))
    elif format == "yaml":
        import yaml

        output = [{"path": str(d.path), "meta": d.meta} for d in docs]
        print(yaml.dump(output, default_flow_style=False))
    else:
        # Table format
        if not docs:
            console.print("[dim]No matching files found.[/dim]")
            return

        # Collect all unique keys from frontmatter
        all_keys: set[str] = set()
        for doc in docs:
            all_keys.update(doc.meta.keys())
        keys = sorted(all_keys)[:5]  # Limit to 5 columns

        table = Table(show_header=True)
        table.add_column("Path", style="cyan")
        for key in keys:
            table.add_column(key.title())

        for doc in docs:
            row = [str(doc.path.relative_to(directory))]
            for key in keys:
                value = doc.meta.get(key, "")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row.append(str(value)[:50])  # Truncate long values
            table.add_row(*row)

        console.print(table)


@app.command()
def meta(
    file: Annotated[Path, typer.Argument(help="Markdown file to inspect")],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: yaml, json"),
    ] = "yaml",
) -> None:
    """Show frontmatter metadata of a markdown file."""
    if not file.exists():
        err_console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        doc = Document.load(file)

        if format == "json":
            import json

            print(json.dumps(doc.meta, indent=2, default=str))
        else:
            import yaml

            print(yaml.dump(doc.meta, default_flow_style=False))

    except Exception as e:
        _handle_error(e)
        raise typer.Exit(1) from None


@app.command()
def watch(
    template: Annotated[Path, typer.Argument(help="Path to the template file")],
    context: Annotated[
        Path | None,
        typer.Option("-c", "--context", help="YAML or JSON context file"),
    ] = None,
    var: Annotated[
        list[str] | None,
        typer.Option("--var", help="Set variable as key=value (repeatable)"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("-o", "--output", help="Output file (required for watch)"),
    ] = None,
    watch_paths: Annotated[
        list[Path] | None,
        typer.Option("--watch", help="Additional paths to watch (repeatable)"),
    ] = None,
    content_base: Annotated[
        Path | None,
        typer.Option(
            "--content-base",
            help="Base directory for content lookups (default: cwd)",
        ),
    ] = None,
) -> None:
    """Watch files and re-render on changes."""
    try:
        from watchfiles import watch as watchfiles_watch
    except ImportError:
        err_console.print(
            "[red]Error:[/red] watchfiles not installed. "
            "Install with: [cyan]pip install mdcomp[watch][/cyan]"
        )
        raise typer.Exit(1) from None

    if not template.exists():
        err_console.print(f"[red]Error:[/red] Template not found: {template}")
        raise typer.Exit(1)

    if not output:
        err_console.print("[red]Error:[/red] --output is required for watch mode")
        raise typer.Exit(1)

    from datetime import datetime

    def do_render() -> bool:
        """Render the template, return True on success."""
        try:
            ctx = load_context(
                context_file=context,
                context_stdin=False,
                var_overrides=var,
            )
            result = render_template(
                template_path=template,
                context=ctx,
                content_base=content_base,
            )
            output.write_text(result)
            return True
        except Exception as e:
            _handle_error(e)
            return False

    # Collect paths to watch
    paths_to_watch: set[Path] = {template.parent.resolve()}
    if context:
        paths_to_watch.add(context.parent.resolve())
    if watch_paths:
        for p in watch_paths:
            if p.exists():
                paths_to_watch.add(p.resolve())
            else:
                err_console.print(f"[yellow]Warning:[/yellow] Watch path not found: {p}")

    # Initial render
    timestamp = datetime.now().strftime("%H:%M:%S")
    if do_render():
        console.print(f"[dim][{timestamp}][/dim] Rendered {template.name} → {output}")

    console.print("\n[bold]Watching for changes...[/bold] (Ctrl+C to stop)")
    console.print(f"[dim]Paths: {', '.join(str(p) for p in paths_to_watch)}[/dim]\n")

    try:
        for changes in watchfiles_watch(*paths_to_watch):
            timestamp = datetime.now().strftime("%H:%M:%S")
            for _change_type, changed_path in changes:
                console.print(f"[dim][{timestamp}][/dim] Changed: {Path(changed_path).name}")
            if do_render():
                console.print(f"[dim][{timestamp}][/dim] Rendered {template.name} → {output}")
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped watching.[/dim]")


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show full error tracebacks for debugging.",
        ),
    ] = False,
) -> None:
    """MDComp - Compose documents from Markdown snippets and templates."""
    _state["verbose"] = verbose


if __name__ == "__main__":
    app()
