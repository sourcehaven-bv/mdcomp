# Filters

Filters transform values in templates. Use them with the pipe syntax: `{{ value | filter }}`.

MDComp includes all [standard Jinja2 filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters) plus these custom filters.

## Data Format Filters

### from_json

Parse a JSON string into a Python object:

```jinja
{% set data = '{"name": "test", "value": 42}' | from_json %}
Name: {{ data.name }}
Value: {{ data.value }}

{# Commonly used with shell() #}
{% set issues = shell("gh issue list --json title,number") | from_json %}
```

### from_yaml

Parse a YAML string into a Python object:

```jinja
{% set data = "name: test\nvalue: 42" | from_yaml %}
Name: {{ data.name }}
```

### to_json

Serialize an object to JSON:

```jinja
{{ data | to_json }}

{# With indentation #}
{{ data | to_json(indent=2) }}
```

### to_yaml

Serialize an object to YAML:

```jinja
{{ data | to_yaml }}
```

## Text Filters

### slugify

Convert a string to a URL-friendly slug:

```jinja
{{ "Hello World!" | slugify }}
{# Output: hello-world #}

{{ "My Document Title" | slugify }}
{# Output: my-document-title #}
```

### date_format

Format a date string:

```jinja
{{ "2024-01-15" | date_format("%d/%m/%Y") }}
{# Output: 15/01/2024 #}

{{ "2024-01-15" | date_format("%B %d, %Y") }}
{# Output: January 15, 2024 #}

{# Default format is %Y-%m-%d #}
{{ date | date_format }}
```

Supported input formats:
- `%Y-%m-%d` (2024-01-15)
- `%Y-%m-%dT%H:%M:%S` (2024-01-15T10:30:00)
- `%d/%m/%Y` (15/01/2024)
- `%m/%d/%Y` (01/15/2024)

## Markdown Filters

### shift_headers

Shift markdown header levels up or down:

```jinja
{# Shift headers down (add levels) #}
{{ content("doc.md") | shift_headers(2) }}
{# # Title becomes ### Title #}
{# ## Section becomes #### Section #}

{# Shift headers up (remove levels) #}
{{ content("nested.md") | shift_headers(-1) }}
{# ### Title becomes ## Title #}
```

Header levels are clamped between 1 and 6.

This is essential when including standalone documents that have their own H1 headings into a larger document where they should appear as subsections.

### headers

Extract headers from markdown content, returning a list of dictionaries with `level` and `title` keys. Useful for generating tables of contents.

```jinja
{% set body %}
## Introduction
Content here...
### Subsection
More content...
## Conclusion
{% endset %}

{# Generate a table of contents #}
{% for h in body | headers(min_level=2) %}
{{ "  " * (h.level - 2) }}- [{{ h.title }}](#{{ h.title | slugify }})
{% endfor %}

{{ body }}
```

Output:
```markdown
- [Introduction](#introduction)
  - [Subsection](#subsection)
- [Conclusion](#conclusion)

## Introduction
...
```

**Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_level` | 1 | Minimum header level to include |
| `max_level` | 6 | Maximum header level to include |

**Examples:**

```jinja
{# All headers #}
{% for h in content | headers %}

{# Only h2 and h3 #}
{% for h in content | headers(min_level=2, max_level=3) %}

{# Only top-level sections (h2) #}
{% for h in content | headers(min_level=2, max_level=2) %}
```

Each header dict contains:
- `level` (int): The header level (1-6)
- `title` (str): The header text (with formatting removed)

**Note:** Since the TOC needs to reference headers that appear later in the document, you must capture the body content in a `{% set %}` block first, then generate the TOC, then output the body. See the `examples/toc/` directory for a complete example.

**Example:**

Your snippet `adr-001.md`:
```markdown
# Use PostgreSQL for Data Storage

## Context
We need a database...

## Decision
We will use PostgreSQL...
```

Your template:
```jinja
# Architecture Document

## Architecture Decision Records

{% for adr in query("adrs/", type="adr") %}
{{ content(adr.path) | shift_headers(2) }}
{% endfor %}
```

Output:
```markdown
# Architecture Document

## Architecture Decision Records

### Use PostgreSQL for Data Storage

#### Context
We need a database...

#### Decision
We will use PostgreSQL...
```

## Shell Filter

### pipe

Pipe content through a shell command. The content is sent to stdin, and stdout is returned.

```jinja
{# Convert markdown to LaTeX #}
{{ content("doc.md") | pipe("pandoc -f markdown -t latex") }}

{# Convert markdown to HTML #}
{{ content("doc.md") | pipe("pandoc -f markdown -t html") }}

{# Process JSON with jq #}
{{ data | to_json | pipe("jq '.items[]'") }}

{# Sort lines #}
{{ text | pipe("sort | uniq") }}

{# Chain with other filters #}
{{ content("doc.md") | shift_headers(1) | pipe("pandoc -t latex") }}
```

**For snippets with Jinja variables**, capture with `{% set %}` first:

```jinja
{# Wrong: variables won't be rendered #}
{{ content("snippets/terms.md") | pipe("pandoc -t latex") }}

{# Correct: include first to render variables, then pipe #}
{% set terms %}{% include "snippets/terms.md" %}{% endset %}
{{ terms | pipe("pandoc -t latex") }}
```

The difference:
- `content()` returns raw file text, Jinja syntax is not processed
- `{% include %}` processes the file through Jinja, rendering variables

## Common Jinja2 Filters

These are built into Jinja2 and commonly used:

| Filter | Description | Example |
|--------|-------------|---------|
| `default(value)` | Provide default if undefined | `{{ x \| default("N/A") }}` |
| `join(sep)` | Join list items | `{{ items \| join(", ") }}` |
| `length` | Get length | `{{ items \| length }}` |
| `first` / `last` | First/last item | `{{ items \| first }}` |
| `sort` | Sort a list | `{{ items \| sort }}` |
| `reverse` | Reverse a list | `{{ items \| reverse }}` |
| `sum` | Sum numbers | `{{ items \| sum }}` |
| `sum(attribute)` | Sum by attribute | `{{ items \| sum(attribute='amount') }}` |
| `map(attribute)` | Extract attribute | `{{ items \| map(attribute='name') }}` |
| `select` / `reject` | Filter items | `{{ items \| selectattr('active') }}` |
| `truncate(n)` | Truncate string | `{{ text \| truncate(100) }}` |
| `upper` / `lower` | Change case | `{{ text \| upper }}` |
| `replace(old, new)` | Replace text | `{{ text \| replace("_", "-") }}` |
| `round(n)` | Round number | `{{ price \| round(2) }}` |
| `int` / `float` | Convert type | `{{ "42" \| int }}` |

## Filter Chaining

Filters can be chained:

```jinja
{# Get total, round to 2 decimals, format as string #}
{{ items | sum(attribute='amount') | round(2) }}

{# Sort by date, get first 5, extract titles #}
{% for doc in query("posts/") | sort(attribute='meta.date') | reverse %}
{% if loop.index <= 5 %}
- {{ doc.meta.title }}
{% endif %}
{% endfor %}

{# Read, shift headers, convert to LaTeX #}
{{ content("section.md") | shift_headers(1) | pipe("pandoc -t latex") }}
```
