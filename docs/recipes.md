# Recipes

Real-world patterns and examples for common use cases.

## Invoices

### Project structure

```
invoices/
├── templates/
│   ├── invoice.md.j2      # Markdown invoice
│   └── invoice.tex.j2     # LaTeX invoice (for PDF)
├── snippets/
│   ├── company-header.md
│   ├── payment-terms.md
│   └── payment-terms-nl.md
├── context/
│   ├── acme-january.yaml
│   └── globex-february.yaml
└── output/
```

### Markdown template

`templates/invoice.md.j2`:
```jinja
---
payment_days: 30
currency: EUR
vat_rate: 21
---
{{ content("snippets/company-header.md") }}

---

# INVOICE

| | |
|----------------|----------------------------------------|
| **Invoice #:** | {{ invoice_number }} |
| **Date:** | {{ date }} |
| **Due Date:** | {{ due_date }} |
{% if reference %}| **Reference:** | {{ reference }} |{% endif %}

---

## Bill To

**{{ client.name }}**
{% if client.contact %}Attn: {{ client.contact }}{% endif %}

{{ client.address }}
{% if client.vat_number %}VAT: {{ client.vat_number }}{% endif %}

---

## Services Rendered
{% if project %}
**Project:** {{ project }}
{% endif %}

| Date | Hours | Description |
|------|------:|-------------|
{% for entry in timesheet %}
| {{ entry.date }} | {{ entry.hours }} | {{ entry.description }} |
{% endfor %}

---

## Summary

{% set total_hours = timesheet | sum(attribute='hours') %}
{% set subtotal = total_hours * hourly_rate %}
{% set vat_amount = (subtotal * vat_rate / 100) | round(2) %}
{% set total = subtotal + vat_amount %}

| | |
|---------------------|-------------------:|
| **Hourly Rate:** | {{ currency }} {{ "%.2f" | format(hourly_rate) }} |
| **Total Hours:** | {{ total_hours }} |
| **Subtotal:** | {{ currency }} {{ "%.2f" | format(subtotal) }} |
| **VAT ({{ vat_rate }}%):** | {{ currency }} {{ "%.2f" | format(vat_amount) }} |
| **Total Due:** | **{{ currency }} {{ "%.2f" | format(total) }}** |

---

{% include "snippets/payment-terms.md" %}
```

### Context file

`context/acme-january.yaml`:
```yaml
invoice_number: INV-2024-003
date: 2024-01-24
due_date: 2024-02-23

client:
  name: Acme Corporation
  contact: John Smith
  address: |
    456 Enterprise Avenue
    1017 RT Amsterdam
    Netherlands
  vat_number: NL987654321B01

hourly_rate: 150
project: Cloud Migration Phase 2
reference: PO-2024-0042

timesheet:
  - date: 2024-01-06
    hours: 8
    description: Architecture review and documentation
  - date: 2024-01-07
    hours: 6
    description: Security assessment meeting
  - date: 2024-01-13
    hours: 8
    description: Implementation of authentication module
```

### Generate

```bash
# Markdown
mdcomp render templates/invoice.md.j2 \
  -c context/acme-january.yaml \
  -o output/invoice-acme-january.md

# PDF via pandoc
mdcomp render templates/invoice.md.j2 \
  -c context/acme-january.yaml | \
  pandoc -o output/invoice-acme-january.pdf
```

## LaTeX PDF Generation

For professional PDFs, use a LaTeX template with the `pipe` filter.

### LaTeX template

`templates/invoice.tex.j2`:
```jinja
---
payment_days: 30
currency: EUR
vat_rate: 21
---
\documentclass[11pt,a4paper]{article}
\usepackage[margin=2.5cm]{geometry}
\usepackage{booktabs}
\usepackage{longtable}

% Required for pandoc output
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}

\begin{document}

% Company header (markdown converted to LaTeX)
{{ content("snippets/company-header.md") | pipe("pandoc -f markdown -t latex") }}

\section*{INVOICE}

\begin{tabular}{@{}ll@{}}
\textbf{Invoice \#:} & {{ invoice_number }} \\
\textbf{Date:} & {{ date }} \\
\textbf{Due Date:} & {{ due_date }} \\
\end{tabular}

\section*{Services}

\begin{longtable}{@{}llp{8cm}@{}}
\toprule
\textbf{Date} & \textbf{Hours} & \textbf{Description} \\
\midrule
{% for entry in timesheet %}
{{ entry.date }} & {{ entry.hours }} & {{ entry.description }} \\
{% endfor %}
\bottomrule
\end{longtable}

{% set total_hours = timesheet | sum(attribute='hours') %}
{% set subtotal = total_hours * hourly_rate %}
{% set vat_amount = (subtotal * vat_rate / 100) | round(2) %}
{% set total = subtotal + vat_amount %}

\textbf{Total: {{ currency }} {{ "%.2f" | format(total) }}}

% Payment terms (with variables, so use include+capture)
{% set terms %}{% include "snippets/payment-terms.md" %}{% endset %}
{{ terms | pipe("pandoc -f markdown -t latex") }}

\end{document}
```

### Generate PDF

```bash
# Render LaTeX
mdcomp render templates/invoice.tex.j2 \
  -c context/acme-january.yaml \
  -o output/invoice.tex

# Compile to PDF
pdflatex -output-directory=output output/invoice.tex
```

## Architecture Documents

Compose architecture documentation from modular ADRs, component docs, and requirements.

### Project structure

```
architecture/
├── templates/
│   └── architecture-doc.md.j2
├── snippets/
│   ├── adrs/
│   │   ├── adr-001-database.md
│   │   ├── adr-002-auth.md
│   │   └── adr-003-encryption.md
│   ├── components/
│   │   ├── api.md
│   │   └── frontend.md
│   └── requirements/
│       ├── functional.md
│       └── nonfunctional.md
├── context/
│   └── project.yaml
└── output/
```

### ADR snippet format

`snippets/adrs/adr-001-database.md`:
```markdown
---
type: adr
id: ADR-001
title: Use PostgreSQL for Primary Data Storage
status: accepted
date: 2024-01-10
---
# Use PostgreSQL for Primary Data Storage

## Context

We need a reliable database for storing application data...

## Decision

We will use PostgreSQL 15+ as our primary database.

## Consequences

- Positive: ACID compliance, strong ecosystem
- Negative: Requires PostgreSQL expertise on the team
```

### Architecture template

`templates/architecture-doc.md.j2`:
```jinja
# {{ project.name }} - Architecture Document

**Version:** {{ version }}
**Date:** {{ date }}
**Status:** {{ status }}

## Executive Summary

{{ project.description }}

## System Components

{% for doc in query("snippets/components/", type="component") | sort(attribute='meta.order') %}
### {{ doc.meta.title }}

{{ doc.content | shift_headers(1) }}

{% endfor %}

## Architecture Decision Records

{% for doc in query("snippets/adrs/", type="adr") | sort(attribute='meta.id') %}
### {{ doc.meta.id }}: {{ doc.meta.title }}

| | |
|---|---|
| **Status** | {{ doc.meta.status }} |
| **Date** | {{ doc.meta.date }} |

{{ doc.content | shift_headers(1) }}

---
{% endfor %}

## Requirements

### Functional Requirements

{{ content("snippets/requirements/functional.md") | shift_headers(1) }}

### Non-Functional Requirements

{{ content("snippets/requirements/nonfunctional.md") | shift_headers(1) }}
```

## Multi-language Snippets

Use frontmatter to select language-specific content.

### Snippet with language metadata

`snippets/payment-terms-en.md`:
```markdown
---
type: legal
lang: en
---
## Payment Terms

Payment is due within {{ payment_days | default(30) }} days.
```

`snippets/payment-terms-nl.md`:
```markdown
---
type: legal
lang: nl
---
## Betalingsvoorwaarden

Betaling dient binnen {{ payment_days | default(30) }} dagen te geschieden.
```

### Template with language selection

```jinja
{% set lang = language | default("en") %}
{% for doc in query("snippets/", type="legal", lang=lang) %}
{{ doc.content }}
{% endfor %}
```

Or directly include:

```jinja
{% include "snippets/payment-terms-" + language + ".md" %}
```

## Dynamic Content from APIs

### GitHub issues

```jinja
# Sprint Report

## Open Issues

{% set issues = shell("gh issue list --state open --json number,title,labels --limit 20") | from_json %}

{% for issue in issues %}
- [#{{ issue.number }}](https://github.com/org/repo/issues/{{ issue.number }}): {{ issue.title }}
  {% if issue.labels %}*{{ issue.labels | map(attribute='name') | join(', ') }}*{% endif %}
{% endfor %}
```

### Git information

```jinja
# Release Notes

**Version:** {{ version }}
**Commit:** {{ shell("git rev-parse --short HEAD") | trim }}
**Branch:** {{ shell("git branch --show-current") | trim }}
**Date:** {{ shell("date +%Y-%m-%d") | trim }}

## Changes since last release

{{ shell("git log --oneline v" + previous_version + "..HEAD") }}
```

### System information

```jinja
# System Report

**Generated:** {{ shell("date") | trim }}
**Hostname:** {{ shell("hostname") | trim }}
**Uptime:** {{ shell("uptime") | trim }}

## Disk Usage

```
{{ shell("df -h") }}
```

## Memory

```
{{ shell("free -h 2>/dev/null || vm_stat") }}
```
```

## Batch Processing

### Makefile for multiple invoices

```makefile
CONTEXTS := $(wildcard context/invoices/*.yaml)
OUTPUTS := $(patsubst context/invoices/%.yaml,output/%.pdf,$(CONTEXTS))

all: $(OUTPUTS)

output/%.pdf: context/invoices/%.yaml templates/invoice.md.j2
	mdcomp render templates/invoice.md.j2 -c $< | \
	pandoc -o $@

clean:
	rm -f output/*.pdf

.PHONY: all clean
```

### Shell script for batch rendering

```bash
#!/bin/bash
for context in context/invoices/*.yaml; do
    name=$(basename "$context" .yaml)
    echo "Rendering $name..."
    mdcomp render templates/invoice.md.j2 \
        -c "$context" \
        -o "output/${name}.md"
done
```

### justfile for development

```just
# Render single invoice
invoice client:
    mdcomp render templates/invoice.md.j2 \
        -c context/invoices/{{client}}.yaml

# Render all invoices
invoices:
    for f in context/invoices/*.yaml; do \
        name=$(basename "$f" .yaml); \
        just invoice "$name" > "output/${name}.md"; \
    done

# Watch and re-render on changes
watch client:
    mdcomp watch templates/invoice.md.j2 \
        -c context/invoices/{{client}}.yaml \
        -o output/{{client}}.md
```

## Conditional Content

### Based on document type

```jinja
{% if document_type == "internal" %}
**INTERNAL USE ONLY - CONFIDENTIAL**
{% elif document_type == "draft" %}
**DRAFT - NOT FOR DISTRIBUTION**
{% endif %}

# {{ title }}

Main content...

{% if document_type == "internal" %}
## Internal Notes

{{ content("snippets/internal-notes.md") }}
{% endif %}
```

### Based on audience

```jinja
# API Documentation

{% if audience == "developer" %}
## Authentication

Use Bearer tokens for all requests:

```bash
curl -H "Authorization: Bearer $TOKEN" https://api.example.com/v1/users
```
{% endif %}

{% if audience in ["developer", "admin"] %}
## Rate Limits

| Tier | Requests/minute |
|------|-----------------|
| Free | 60 |
| Pro | 600 |
{% endif %}
```

## Error Handling

### Default values

```jinja
{# Provide defaults for missing values #}
**Author:** {{ author | default("Unknown") }}
**Date:** {{ date | default("N/A") }}
**Version:** {{ version | default(1) }}

{# Default for complex objects #}
{% for item in items | default([]) %}
- {{ item }}
{% endfor %}
```

### Conditional includes

```jinja
{# Only include if file exists #}
{% include "snippets/optional-section.md" ignore missing %}

{# Check before including #}
{% if include_appendix %}
{% include "snippets/appendix.md" %}
{% endif %}
```
