# Templates

MDComp uses [Jinja2](https://jinja.palletsprojects.com/) for templating with additional functions for document composition.

## Basics

### Variables

```jinja
Hello, {{ name }}!
The date is {{ date }}.
```

### Conditionals

```jinja
{% if client.vat_number %}
VAT: {{ client.vat_number }}
{% endif %}

{% if status == "draft" %}
**DRAFT - NOT FOR DISTRIBUTION**
{% elif status == "review" %}
**UNDER REVIEW**
{% endif %}
```

### Loops

```jinja
{% for item in items %}
- {{ item.name }}: {{ item.value }}
{% endfor %}

{# With loop index #}
{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}
```

### Comments

```jinja
{# This is a comment and won't appear in output #}
```

## Template Defaults

Templates can define default values in frontmatter:

```jinja
---
payment_days: 30
currency: EUR
vat_rate: 21
---
# Invoice

Payment due in {{ payment_days }} days.
Currency: {{ currency }}
```

These defaults are overridden by context files and CLI `--var` options.

## Including Files

### Basic include

The `{% include %}` tag includes and processes a file as Jinja2:

```jinja
{% include "snippets/header.md" %}

Main content...

{% include "snippets/footer.md" %}
```

Variables from your context are available in included files.

### Dynamic includes

```jinja
{# Include based on a variable #}
{% include "snippets/footer-" + language + ".md" %}

{# Include with ignore if missing #}
{% include "snippets/optional.md" ignore missing %}
```

### Include with variable capture

To process an include and then pipe it through a filter:

```jinja
{% set terms %}{% include "snippets/payment-terms.md" %}{% endset %}
{{ terms | pipe("pandoc -f markdown -t latex") }}
```

## Path Resolution

MDComp has two path resolution mechanisms:

| Function Type | Default Base | Description |
|---------------|--------------|-------------|
| `{% include %}` | template directory → cwd | Jinja2 native includes |
| `content()`, `read()`, etc. | **cwd** | Content lookup functions |

### Content functions default to cwd

All content functions resolve paths relative to the **current working directory**:

```jinja
{# Resolves from cwd #}
{{ content("snippets/intro.md") }}
{{ read("data/config.json") }}
{% for doc in query("content/posts/") %}...{% endfor %}
```

This makes templates portable — paths match what you see in your terminal.

### Overriding the base directory

#### Per-call with `base=`

```jinja
{# Resolve relative to template directory #}
{{ content("../snippets/header.md", base=template_dir) }}

{# Resolve relative to a specific path #}
{{ content("header.md", base="/var/shared/snippets") }}
```

#### In template frontmatter

Set `content_base` to change the default for all content functions in a template:

```jinja
---
title: My Document
content_base: .
---
{# Now paths resolve relative to template directory #}
{{ content("../snippets/header.md") }}
```

The `content_base` path is resolved relative to the template directory, so `.` means "template directory".

#### Via CLI flag

```bash
mdcomp render template.md.j2 --content-base ./content
```

The CLI flag overrides frontmatter settings.

### Built-in path variables

Two variables are available in all templates:

| Variable | Value |
|----------|-------|
| `template_dir` | Absolute path to the template's directory |
| `cwd` | Absolute path to the current working directory |

```jinja
{# Use template_dir for template-relative paths #}
{{ content("header.md", base=template_dir) }}

{# Reference paths explicitly #}
Template location: {{ template_dir }}
Running from: {{ cwd }}
```

### Resolution priority

For content functions, the base directory is determined by (highest priority first):

1. **`base=` parameter** in the function call
2. **`--content-base` CLI flag**
3. **`content_base` in template frontmatter**
4. **cwd** (default)

### Template includes vs content functions

`{% include %}` and `content()` behave differently:

```jinja
{# Jinja2 include: searches template_dir first, then cwd #}
{% include "snippets/header.md" %}

{# content(): resolves from cwd (or configured base) #}
{{ content("snippets/header.md") }}
```

Use `{% include %}` for template partials that need Jinja2 processing.
Use `content()` for markdown snippets that should be included verbatim.

## Reading Files

### read()

Read a file's raw contents without Jinja processing:

```jinja
{# Include code example verbatim #}
```python
{{ read("examples/code.py") }}
```

{# Read from absolute path #}
{{ read("/etc/hostname") }}
```

### content()

Read a markdown file's content, excluding frontmatter:

```jinja
{{ content("snippets/intro.md") }}
```

This is useful when you want the content but not the YAML frontmatter.

### frontmatter() / meta()

Read a file's frontmatter metadata as a dictionary:

```jinja
{% set info = frontmatter("snippets/project.md") %}
Project: {{ info.title }}
Version: {{ info.version }}
Status: {{ info.status }}
```

`meta()` is an alias for `frontmatter()`.

## Querying Files

### glob()

Find files matching a pattern:

```jinja
{% for file in glob("reports/*.md") %}
- {{ file }}
{% endfor %}

{# Recursive glob #}
{% for file in glob("**/*.md") %}
- {{ file }}
{% endfor %}
```

### query()

Find markdown files by frontmatter metadata:

```jinja
{# Simple equality filter #}
{% for doc in query("snippets/", status="published") %}
### {{ doc.meta.title }}
{{ doc.content }}
{% endfor %}

{# Multiple filters #}
{% for doc in query("posts/", status="published", category="tech") %}
- [{{ doc.meta.title }}]({{ doc.path }})
{% endfor %}
```

Each result has:
- `doc.path` - Path to the file
- `doc.meta` - Frontmatter as a dictionary
- `doc.content` - File content without frontmatter

### Query Operators

| Operator | Example | Description |
|----------|---------|-------------|
| (none) | `status="draft"` | Exact equality |
| `__contains` | `tags__contains="api"` | List contains value, or string contains substring |
| `__startswith` | `title__startswith="Q1"` | String starts with |
| `__endswith` | `name__endswith=".md"` | String ends with |
| `__gt` | `priority__gt=5` | Greater than |
| `__gte` | `date__gte="2024-01-01"` | Greater than or equal |
| `__lt` | `amount__lt=1000` | Less than |
| `__lte` | `score__lte=100` | Less than or equal |

Example with operators:

```jinja
{# Find high-priority items from 2024 #}
{% for doc in query("tasks/", priority__gte=8, date__gte="2024-01-01") %}
- {{ doc.meta.title }} (Priority: {{ doc.meta.priority }})
{% endfor %}

{# Find items tagged with "urgent" #}
{% for doc in query("tickets/", tags__contains="urgent") %}
- {{ doc.meta.title }}
{% endfor %}
```

## Shell Commands

### shell()

Execute a command and return its stdout:

```jinja
{# Simple command #}
Current directory: {{ shell("pwd") }}

{# Get git info #}
Commit: {{ shell("git rev-parse --short HEAD") }}
Branch: {{ shell("git branch --show-current") }}

{# Parse JSON output #}
{% set issues = shell("gh issue list --json title,number --limit 5") | from_json %}
{% for issue in issues %}
- #{{ issue.number }}: {{ issue.title }}
{% endfor %}
```

## Combining Features

### Architecture document example

```jinja
# {{ project.name }} Architecture

**Version:** {{ version }}
**Date:** {{ date }}

## Overview

{% include "snippets/overview.md" %}

## Components

{% for doc in query("snippets/components/", type="component") | sort(attribute='meta.order') %}
### {{ doc.meta.title }}

{{ doc.content | shift_headers(1) }}

{% endfor %}

## Architecture Decision Records

{% for doc in query("snippets/adrs/", type="adr") | sort(attribute='meta.id') %}
### {{ doc.meta.id }}: {{ doc.meta.title }}

**Status:** {{ doc.meta.status }}
**Date:** {{ doc.meta.date }}

{{ doc.content | shift_headers(1) }}

---
{% endfor %}

## Appendix

{% include "snippets/appendix.md" %}
```

This template:
1. Uses variables from context (`project.name`, `version`, `date`)
2. Includes static snippets (`overview.md`, `appendix.md`)
3. Queries components and ADRs by frontmatter type
4. Sorts results by metadata fields
5. Shifts header levels to fit document hierarchy
