# Issue 006: Add pre-commit hooks configuration

## Summary
Add a `.pre-commit-config.yaml` to automatically run linting and formatting checks before commits.

## Current Behavior
Developers must manually run `just check` before committing. Easy to forget and push unformatted code.

## Expected Behavior
Pre-commit hooks automatically run ruff format, ruff check, and mypy before each commit, preventing bad code from being committed.

## Implementation
Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies:
          - types-pyyaml
        args: [--config-file=pyproject.toml]
        pass_filenames: false
        entry: mypy src
```

Add to dev dependencies:
```toml
"pre-commit>=3.0",
```

Add just command:
```just
# Install pre-commit hooks
hooks:
    uv run pre-commit install
```

## Priority
Medium - Improves code quality workflow

## Labels
enhancement, developer-experience, tooling
