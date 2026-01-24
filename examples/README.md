# MDComp Examples

This directory contains complete examples demonstrating MDComp's capabilities.

## Examples

### 1. Invoice Generation (`invoice/`)

Generate professional invoices from timesheet data with hourly rates.

```bash
cd invoice
mdcomp render templates/invoice.md.j2 -c context/acme-january.yaml
```

**Features demonstrated:**
- Hourly rate calculations with Jinja2 math
- Reusable company header and payment terms
- Multi-language support (EN/NL payment terms)
- VAT calculation

---

### 2. IT Architecture Document (`architecture/`)

Compose comprehensive architecture documents from modular snippets.

```bash
cd architecture
mdcomp render templates/architecture-doc.md.j2 -c context/project.yaml
```

**Features demonstrated:**
- Querying files by frontmatter (`status=accepted`)
- Multiple snippet categories (ADRs, requirements, legal, components, threats)
- Dynamic document assembly
- Auto-generated table of contents references

**Snippet types included:**
- Architecture Decision Records (ADRs)
- Functional & Non-functional Requirements
- GDPR & ISO 27001 compliance documentation
- Infrastructure & application architecture
- STRIDE threat model & risk register

---

### 3. Table of Contents (`toc/`)

Generate a table of contents from markdown headers.

```bash
cd toc
mdcomp render templates/document.md.j2
```

**Features demonstrated:**
- The `headers` filter to extract headers from content
- Two-pass pattern: capture body, generate TOC, output body
- Anchor link generation with `slugify`
- Nested indentation based on header level

---

### 4. System Status Report (`system-report/`)

Generate system reports using shell commands - no API keys required.

```bash
cd system-report
mdcomp render templates/system-report.md.j2 -c context/report.yaml
```

**Features demonstrated:**
- Shell command execution (`shell()` function)
- Conditional sections based on context
- Threshold-based warnings (disk usage)
- Tool version detection
- Dynamic data from system commands

---

## Quick Start

```bash
# Run any example from the mdcomp root directory
cd /path/to/mdcomp

# Invoice
uv run mdcomp render examples/invoice/templates/invoice.md.j2 \
  -c examples/invoice/context/acme-january.yaml

# Architecture document
uv run mdcomp render examples/architecture/templates/architecture-doc.md.j2 \
  -c examples/architecture/context/project.yaml

# Table of contents
uv run mdcomp render examples/toc/templates/document.md.j2

# System report
uv run mdcomp render examples/system-report/templates/system-report.md.j2 \
  -c examples/system-report/context/report.yaml
```

## Converting to PDF

All examples can be converted to PDF using pandoc:

```bash
mdcomp render templates/invoice.md.j2 -c context/acme-january.yaml | \
  pandoc -o invoice.pdf

# With table of contents for longer documents
mdcomp render templates/architecture-doc.md.j2 -c context/project.yaml | \
  pandoc --toc --toc-depth=2 -o architecture.pdf
```

## Creating Your Own Examples

1. Create a directory structure:
   ```
   my-example/
   ├── templates/      # Jinja2 templates (.md.j2)
   ├── snippets/       # Reusable content blocks (.md with frontmatter)
   ├── context/        # YAML/JSON data files
   └── output/         # Generated documents
   ```

2. Add frontmatter to snippets for querying:
   ```yaml
   ---
   title: My Snippet
   tags: [important, category-a]
   status: active
   ---
   Content here...
   ```

3. Use in templates:
   ```jinja
   {% for doc in query("snippets/", status="active") %}
   ## {{ doc.meta.title }}
   {{ doc.content }}
   {% endfor %}
   ```
