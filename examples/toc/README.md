# Table of Contents Example

Generate a table of contents from markdown headers using the `headers` filter.

## Structure

```
toc/
├── templates/
│   └── document.md.j2   # Template with TOC generation
└── output/
    └── document.md      # Generated output
```

## Usage

```bash
mdcomp render templates/document.md.j2 -o output/document.md
```

## How It Works

The `headers` filter extracts headers from markdown content:

```jinja
{% set body %}
## Introduction
Content...
### Subsection
More content...
## Conclusion
{% endset %}

## Table of Contents

{% for h in body | headers(min_level=2) %}
{{ "  " * (h.level - 2) }}- [{{ h.title }}](#{{ h.title | slugify }})
{% endfor %}

{{ body }}
```

**Key points:**

1. Capture the document body in a `{% set %}` block first
2. Use `headers(min_level=2)` to skip the document title (h1)
3. Calculate indentation with `"  " * (h.level - 2)`
4. Generate anchor links with the `slugify` filter
5. Output the body after the TOC

## Variations

### Only Top-Level Sections

```jinja
{% for h in body | headers(min_level=2, max_level=2) %}
- [{{ h.title }}](#{{ h.title | slugify }})
{% endfor %}
```

### Numbered List

```jinja
{% for h in body | headers(min_level=2, max_level=2) %}
{{ loop.index }}. [{{ h.title }}](#{{ h.title | slugify }})
{% endfor %}
```

### HTML Output

```jinja
<nav class="toc">
  <ul>
{% for h in body | headers(min_level=2) %}
    <li class="toc-level-{{ h.level }}">
      <a href="#{{ h.title | slugify }}">{{ h.title }}</a>
    </li>
{% endfor %}
  </ul>
</nav>
```
