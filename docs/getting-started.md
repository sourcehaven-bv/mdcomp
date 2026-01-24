# Getting Started

## Installation

### Using pip

```bash
pip install mdcomp
```

### Using uv

```bash
uv add mdcomp
```

### From source

```bash
git clone https://github.com/sourcehaven-bv/mdcomp.git
cd mdcomp
pip install -e .
```

## Project Structure

A typical MDComp project looks like this:

```
project/
├── templates/          # Jinja2 templates (.md.j2)
│   └── invoice.md.j2
├── snippets/           # Reusable markdown snippets
│   ├── header.md
│   └── footer.md
├── context/            # Data files (YAML/JSON)
│   └── client.yaml
└── output/             # Generated documents
```

## Your First Template

### 1. Create a template

Create `templates/hello.md.j2`:

```jinja
# Hello, {{ name }}!

Today is {{ date }}.

{% if items %}
## Your Items

{% for item in items %}
- {{ item }}
{% endfor %}
{% endif %}
```

### 2. Create a context file

Create `context/demo.yaml`:

```yaml
name: World
date: 2024-01-15
items:
  - First item
  - Second item
  - Third item
```

### 3. Render the document

```bash
mdcomp render templates/hello.md.j2 -c context/demo.yaml
```

Output:
```markdown
# Hello, World!

Today is 2024-01-15.

## Your Items

- First item
- Second item
- Third item
```

## Including Snippets

### 1. Create a snippet

Create `snippets/signature.md`:

```markdown
---
author: Jane Doe
---
Best regards,
**{{ author | default("The Team") }}**
```

### 2. Use it in a template

```jinja
# Document Title

Main content here...

{% include "snippets/signature.md" %}
```

The `{% include %}` tag processes the snippet as Jinja2, so variables are rendered.

## Outputting to Files

### Save to a file

```bash
mdcomp render template.md.j2 -c context.yaml -o output/document.md
```

### Pipe to pandoc for PDF

```bash
mdcomp render template.md.j2 -c context.yaml | pandoc -o output/document.pdf
```

### Generate LaTeX then PDF

```bash
# Using a .tex.j2 template
mdcomp render template.tex.j2 -c context.yaml -o output/document.tex
pdflatex output/document.tex
```

## Variable Sources

Variables can come from multiple sources (in order of priority, lowest to highest):

### 1. Environment variables

```bash
export MDCOMP_VAR_name="Environment Name"
mdcomp render template.md.j2
```

### 2. Context file

```bash
mdcomp render template.md.j2 -c context.yaml
```

### 3. CLI overrides

```bash
mdcomp render template.md.j2 -c context.yaml --var name="CLI Override"
```

The `--var` option always wins, allowing you to override any value.

## Next Steps

- Learn about [template features](templates.md) like queries and shell commands
- Explore [built-in filters](filters.md) for transforming content
- See [real-world recipes](recipes.md) for common patterns
- Check the [CLI reference](cli.md) for all options
