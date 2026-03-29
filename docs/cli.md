# CLI Reference

## Commands

### mdcomp render

Render a Jinja2 template with context variables.

```bash
mdcomp render <template> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `template` | Path to the template file (required) |

**Options:**

| Option | Description |
|--------|-------------|
| `-c, --context <file>` | YAML or JSON file with template variables |
| `--context-stdin` | Read context as JSON from stdin |
| `--var <key=value>` | Set or override a variable (repeatable) |
| `-o, --output <file>` | Output file (default: stdout) |
| `--strict` | Fail on undefined variables |
| `--content-base <dir>` | Base directory for content lookups (default: cwd) |
| `--db-url <url>` | Database connection URL for `sql()` function |

**Examples:**

```bash
# Basic rendering
mdcomp render template.md.j2 -c context.yaml

# Save to file
mdcomp render template.md.j2 -c context.yaml -o output.md

# Override variables
mdcomp render template.md.j2 -c context.yaml --var name="Test" --var debug=true

# Read context from stdin
echo '{"name": "Test"}' | mdcomp render template.md.j2 --context-stdin

# Pipe to pandoc
mdcomp render template.md.j2 -c context.yaml | pandoc -o output.pdf

# Set content base for content lookups
mdcomp render templates/doc.md.j2 -c context.yaml --content-base ./content

# Query a database (requires: pip install mdcomp[sql])
mdcomp render report.md.j2 --db-url "sqlite:///data.db"
```

### mdcomp list

List markdown files with their frontmatter metadata.

```bash
mdcomp list <directory> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `directory` | Directory to search (required) |

**Options:**

| Option | Description |
|--------|-------------|
| `-f, --format <fmt>` | Output format: `table`, `json`, `yaml` (default: table) |
| `--filter <expr>` | Filter by `field=value` (repeatable) |
| `-s, --sort <field>` | Sort by frontmatter field |
| `-r, --reverse` | Reverse sort order |

**Examples:**

```bash
# List all markdown files
mdcomp list snippets/

# Filter by status
mdcomp list posts/ --filter status=published

# Multiple filters
mdcomp list tasks/ --filter status=open --filter priority=high

# Sort by date
mdcomp list posts/ --sort date --reverse

# Output as JSON
mdcomp list snippets/ --format json

# Output as YAML
mdcomp list snippets/ --format yaml
```

### mdcomp watch

Watch files and re-render template on changes.

```bash
mdcomp watch <template> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `template` | Path to the template file (required) |

**Options:**

| Option | Description |
|--------|-------------|
| `-c, --context <file>` | YAML or JSON file with template variables |
| `--var <key=value>` | Set or override a variable (repeatable) |
| `-o, --output <file>` | Output file (required for watch) |
| `--watch <path>` | Additional paths to watch (repeatable) |
| `--content-base <dir>` | Base directory for content lookups (default: cwd) |
| `--db-url <url>` | Database connection URL for `sql()` function |

**Note:** Requires the `watchfiles` package. Install with `pip install mdcomp[watch]`.

**Examples:**

```bash
# Watch template and context, re-render to output
mdcomp watch template.md.j2 -c context.yaml -o output.md

# Watch additional directories (e.g., snippets)
mdcomp watch template.md.j2 -c context.yaml -o output.md --watch snippets/
```

### mdcomp meta

Show frontmatter metadata of a single markdown file.

```bash
mdcomp meta <file> [options]
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `file` | Markdown file to inspect (required) |

**Options:**

| Option | Description |
|--------|-------------|
| `-f, --format <fmt>` | Output format: `yaml`, `json` (default: yaml) |

**Examples:**

```bash
# Show metadata as YAML
mdcomp meta snippets/header.md

# Show metadata as JSON
mdcomp meta snippets/header.md --format json
```

## Variable Priority

When the same variable is defined in multiple sources, later sources override earlier ones:

1. **Environment variables** (lowest priority)
   ```bash
   export MDCOMP_VAR_name="From Environment"
   ```

2. **Context file**
   ```bash
   mdcomp render template.md.j2 -c context.yaml
   ```

3. **Template frontmatter**
   ```jinja
   ---
   name: Default Name
   ---
   ```

4. **CLI --var overrides** (highest priority)
   ```bash
   mdcomp render template.md.j2 --var name="Override"
   ```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MDCOMP_VAR_<name>` | Set template variable `<name>` |

Environment variable values are parsed as JSON if possible, otherwise treated as strings:

```bash
# String value
export MDCOMP_VAR_name="John"

# Number (parsed as JSON)
export MDCOMP_VAR_count="42"

# Object (parsed as JSON)
export MDCOMP_VAR_config='{"debug": true, "level": 3}'

# Array (parsed as JSON)
export MDCOMP_VAR_items='["one", "two", "three"]'
```

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (file not found, template error, etc.) |

## Shell Integration

### With pandoc

```bash
# PDF via LaTeX
mdcomp render doc.md.j2 -c ctx.yaml | pandoc -o doc.pdf

# PDF via WeasyPrint
mdcomp render doc.md.j2 -c ctx.yaml | pandoc --pdf-engine=weasyprint -o doc.pdf

# Word document
mdcomp render doc.md.j2 -c ctx.yaml | pandoc -o doc.docx

# HTML
mdcomp render doc.md.j2 -c ctx.yaml | pandoc -s -o doc.html
```

### With LaTeX

```bash
# Render LaTeX template
mdcomp render doc.tex.j2 -c ctx.yaml -o doc.tex

# Compile to PDF
pdflatex doc.tex
```

### With Make

```makefile
%.md: templates/%.md.j2 context/%.yaml
	mdcomp render $< -c $(word 2,$^) -o $@

%.pdf: %.md
	pandoc $< -o $@
```

### With just

```just
render-invoice:
    mdcomp render templates/invoice.md.j2 \
        -c context/invoice.yaml \
        -o output/invoice.md

render-pdf: render-invoice
    pandoc output/invoice.md -o output/invoice.pdf
```

### Watching for changes

```bash
# Using built-in watch command (recommended)
mdcomp watch template.md.j2 -c context.yaml -o output.md

# Using entr
find . -name '*.md' -o -name '*.j2' -o -name '*.yaml' | \
  entr -r mdcomp render template.md.j2 -c context.yaml -o output.md

# Using watchexec
watchexec -e md,j2,yaml -- mdcomp render template.md.j2 -c context.yaml
```
