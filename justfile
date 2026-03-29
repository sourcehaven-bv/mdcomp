# mdcomp justfile - run `just` to see available commands

# List available commands
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --dev

# Install pre-commit hooks
hooks:
    uv run pre-commit install

# Run tests
test *args:
    uv run pytest {{args}}

# Run tests with coverage
test-cov:
    uv run pytest --cov=src/mdcomp --cov-report=term-missing

# Lint code
lint:
    uv run ruff check src tests

# Format code
fmt:
    uv run ruff format src tests
    uv run ruff check --fix src tests

# Check formatting without changes
fmt-check:
    uv run ruff format --check src tests

# Type check
typecheck:
    uv run mypy src

# Find dead code
deadcode:
    uv run vulture src vulture_allowlist.py

# Check for duplicate code
dupes:
    uv run pylint src --output-format=colorized

# Run all checks (before commit)
check: fmt-check lint typecheck deadcode dupes test

# Build package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist build *.egg-info .pytest_cache .ruff_cache .mypy_cache __pycache__
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# --- Examples ---

# Render invoice example (markdown)
example-invoice:
    uv run mdcomp render examples/invoice/templates/invoice.md.j2 \
        -c examples/invoice/context/acme-january.yaml \
        --snippets examples/invoice/snippets

# Render invoice example (LaTeX + PDF, requires pandoc and pdflatex)
example-invoice-latex:
    cd examples/invoice && uv run mdcomp render templates/invoice.tex.j2 \
        -c context/acme-january.yaml \
        --snippets snippets \
        -o output/invoice-acme-january.tex
    cd examples/invoice/output && pdflatex -interaction=nonstopmode invoice-acme-january.tex

# Render architecture document example
example-arch:
    uv run mdcomp render examples/architecture/templates/architecture-doc.md.j2 \
        -c examples/architecture/context/project.yaml \
        --snippets examples/architecture/snippets

# Render system report example
example-system:
    uv run mdcomp render examples/system-report/templates/system-report.md.j2 \
        -c examples/system-report/context/report.yaml \
        --snippets examples/system-report/snippets

# Render all examples
examples: example-invoice example-invoice-latex example-arch example-system

# --- Development ---

# Run mdcomp CLI
run *args:
    uv run mdcomp {{args}}

# Show help
help:
    uv run mdcomp --help
