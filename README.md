# MDComp

[![CI](https://github.com/sourcehaven-bv/mdcomp/actions/workflows/ci.yml/badge.svg)](https://github.com/sourcehaven-bv/mdcomp/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/mdcomp.svg)](https://pypi.org/project/mdcomp/)
[![Python](https://img.shields.io/pypi/pyversions/mdcomp.svg)](https://pypi.org/project/mdcomp/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A CLI tool for composing documents from Markdown snippets and Jinja2 templates.

## Features

- **Jinja2 templates** with loops, conditionals, and includes
- **Snippet queries** to find and filter markdown files by frontmatter
- **Shell integration** via `shell()` function and `pipe` filter
- **Multi-format output** to Markdown, LaTeX, HTML, PDF (via pandoc)
- **Variable layering** from environment, files, and CLI

## Installation

### From PyPI

```bash
# As a CLI tool (recommended)
uv tool install mdcomp
pipx install mdcomp

# As a project dependency
uv add mdcomp
pip install mdcomp
```

### From GitHub

```bash
# Latest from main branch
uv tool install git+https://github.com/sourcehaven-bv/mdcomp

# Specific version tag
uv tool install git+https://github.com/sourcehaven-bv/mdcomp@v1.0.0
```

## Quick Start

**Template** (`invoice.md.j2`):
```jinja
# Invoice {{ invoice_number }}

**To:** {{ client.name }}
**Date:** {{ date }}

{% for item in services %}
- {{ item.name }}: {{ currency }} {{ item.amount }}
{% endfor %}

**Total: {{ currency }} {{ services | sum(attribute='amount') }}**
```

**Context** (`context.yaml`):
```yaml
invoice_number: INV-2024-001
date: 2024-01-15
currency: EUR
client:
  name: Acme Corp
services:
  - name: Consulting
    amount: 1500
```

**Render:**
```bash
# To stdout
mdcomp render invoice.md.j2 -c context.yaml

# To file
mdcomp render invoice.md.j2 -c context.yaml -o invoice.md

# To PDF via pandoc
mdcomp render invoice.md.j2 -c context.yaml | pandoc -o invoice.pdf
```

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and first steps |
| [Templates](docs/templates.md) | Template syntax, includes, queries |
| [Filters](docs/filters.md) | Built-in filters (`pipe`, `shift_headers`, etc.) |
| [CLI Reference](docs/cli.md) | All commands and options |
| [Recipes](docs/recipes.md) | Real-world examples and patterns |

## Examples

The `examples/` directory contains complete working examples:

- **invoice/** - Professional invoices with markdown and LaTeX templates
- **architecture/** - Architecture documents with ADRs and component docs
- **system-report/** - Dynamic system reports with shell commands

Run examples with:

```bash
just example-invoice          # Markdown invoice
just example-invoice-latex    # LaTeX invoice with PDF
just example-arch             # Architecture document
just examples                 # All examples
```

## License

MIT
