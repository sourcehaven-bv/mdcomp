# Issue 001: Add --version flag to CLI

## Summary
The CLI is missing a `--version` flag, which is a standard expectation for command-line tools.

## Current Behavior
Running `mdcomp --version` results in an error or unrecognized option.

## Expected Behavior
Running `mdcomp --version` should display the package version (e.g., `mdcomp 0.1.0`).

## Implementation
Use Typer's built-in version callback:

```python
from mdcomp import __version__

def version_callback(value: bool) -> None:
    if value:
        print(f"mdcomp {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-V", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    ...
```

## Priority
High - Expected by all CLI users

## Labels
enhancement, cli, quick-win
