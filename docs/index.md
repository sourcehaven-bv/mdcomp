# MDComp Documentation

**MDComp** is a command-line tool for composing documents from Markdown snippets and Jinja2 templates.

## What is MDComp?

MDComp lets you build complex documents by combining:

- **Markdown snippets** - Reusable content blocks with frontmatter metadata
- **Jinja2 templates** - Logic, loops, conditionals, and includes
- **External data** - YAML/JSON context files, shell command output
- **Pipeline integration** - Works with pandoc, LaTeX, and other tools

Use cases include invoices, reports, proposals, architecture documents, compliance reports, and any document that combines boilerplate with dynamic content.

## Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](getting-started.md) | Installation and your first template |
| [Templates](templates.md) | Template syntax, includes, and queries |
| [Filters](filters.md) | Built-in filters for transforming content |
| [CLI Reference](cli.md) | Command-line options and usage |
| [Recipes](recipes.md) | Real-world examples and patterns |

## Quick Example

**Template** (`invoice.md.j2`):
```jinja
# Invoice {{ invoice_number }}

**To:** {{ client.name }}
**Date:** {{ date }}

| Service | Amount |
|---------|--------|
{% for item in services %}
| {{ item.name }} | {{ currency }} {{ item.amount }} |
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
  - name: Development
    amount: 3000
```

**Render**:
```bash
mdcomp render invoice.md.j2 -c context.yaml
```
