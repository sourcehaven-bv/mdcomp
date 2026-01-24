# Contributing to MDComp

Thank you for your interest in contributing to MDComp! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- [just](https://just.systems/) command runner (optional but recommended)

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/sourcehaven-bv/mdcomp.git
   cd mdcomp
   ```

2. Install dependencies:
   ```bash
   uv sync --dev
   ```

3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

4. Verify your setup:
   ```bash
   just check
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
just test

# Run tests with coverage
just test-cov

# Run specific test file
just test tests/test_cli.py

# Run specific test
just test -k test_render_template
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Run all checks (recommended before committing)
just check

# Individual checks:
just lint        # Ruff linting
just fmt         # Format code with Ruff
just typecheck   # MyPy type checking
just deadcode    # Vulture dead code detection
just dupes       # Pylint duplicate code detection
```

### Code Style

- Code is formatted with [Ruff](https://docs.astral.sh/ruff/)
- Line length: 100 characters
- Type hints are required for all functions
- Docstrings for public functions and modules

The pre-commit hooks will automatically format your code and check for issues.

## Making Changes

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring

### Commit Messages

Write clear, concise commit messages:

- Use imperative mood ("Add feature" not "Added feature")
- First line: 50 characters or less
- Body: Wrap at 72 characters
- Reference issues when applicable

Example:
```
Add shell timeout option to prevent hanging

The shell() function now accepts an optional timeout parameter
to prevent templates from hanging on long-running commands.

Resolves #42
```

### Pull Request Process

1. Create a feature branch from `develop`
2. Make your changes with tests
3. Ensure all checks pass: `just check`
4. Update documentation if needed
5. Update CHANGELOG.md under `[Unreleased]`
6. Submit a pull request to `develop`

## Project Structure

```
mdcomp/
├── src/mdcomp/      # Source code
│   ├── cli.py       # CLI commands
│   ├── render.py    # Template rendering
│   ├── query.py     # File querying
│   ├── filters.py   # Jinja2 filters
│   └── context.py   # Context loading
├── tests/           # Test suite
├── docs/            # Documentation
├── examples/        # Example projects
└── issues/          # Issue tracking
```

## Adding Features

### New CLI Commands

1. Add command function in `src/mdcomp/cli.py`
2. Use Typer decorators and type hints
3. Add tests in `tests/test_cli.py`
4. Document in `docs/cli.md`

### New Jinja2 Filters

1. Add filter function in `src/mdcomp/filters.py`
2. Register in `src/mdcomp/render.py`
3. Add tests in `tests/test_filters.py`
4. Document in `docs/filters.md`

### New Global Functions

1. Add function in `src/mdcomp/render.py`
2. Register in `create_environment()`
3. Add tests in `tests/test_render.py`
4. Document in `docs/templates.md`

## Questions?

Feel free to open an issue for questions or discussion.
