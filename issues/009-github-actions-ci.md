# Issue 009: Add GitHub Actions CI workflow

## Summary
Add a GitHub Actions workflow for continuous integration to automatically run tests and checks on every push and pull request.

## Current Behavior
No CI pipeline exists. Tests and linting are only run manually by developers.

## Expected Behavior
GitHub Actions automatically runs on push/PR:
- Linting (ruff)
- Type checking (mypy)
- Tests with coverage (pytest)
- Matrix testing across Python 3.10-3.13

## Implementation
Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run ruff check src tests
      - run: uv run ruff format --check src tests
      - run: uv run mypy src

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: uv sync --dev
      - run: uv run pytest --cov=mdcomp --cov-report=xml
      - uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.13'
```

## Priority
High - Essential for any published package

## Labels
enhancement, ci-cd, infrastructure
