# IT Architecture Document Example

Compose comprehensive architecture documents from modular snippets covering ADRs, requirements, compliance, infrastructure, and threat modelling.

## Structure

```
architecture/
├── templates/
│   └── architecture-doc.md.j2    # Main document template
├── snippets/
│   ├── adrs/                     # Architecture Decision Records
│   │   ├── adr-001-database.md
│   │   ├── adr-002-auth.md
│   │   └── adr-003-encryption.md
│   ├── requirements/             # Functional & non-functional
│   │   ├── req-functional.md
│   │   └── req-nonfunctional.md
│   ├── legal/                    # Compliance documentation
│   │   ├── gdpr.md
│   │   └── iso27001.md
│   ├── components/               # System architecture
│   │   ├── infrastructure.md
│   │   └── application.md
│   └── threats/                  # Security analysis
│       ├── threat-model.md
│       └── risk-register.md
├── context/
│   └── project.yaml              # Document metadata
└── output/
    └── architecture-doc.md
```

## Usage

```bash
# Generate architecture document
mdcomp render templates/architecture-doc.md.j2 \
  -c context/project.yaml \
  --snippets snippets \
  -o output/architecture-doc.md

# Convert to PDF (for stakeholders)
mdcomp render templates/architecture-doc.md.j2 \
  -c context/project.yaml \
  --snippets snippets | \
  pandoc --toc --toc-depth=2 -o output/architecture-doc.pdf

# Generate with different ADR filter
mdcomp render templates/architecture-doc.md.j2 \
  -c context/project.yaml \
  --snippets snippets \
  --var adr_status=proposed
```

## Key Features

### Header Level Shifting

Snippets are written as standalone documents with H2 headers (`## Section`). When included in the main document, `shift_headers` adjusts them to fit the hierarchy:

```jinja
## Architecture Decisions

{% for adr in query("snippets/adrs/", status=adr_status) %}
### {{ adr.meta.id }}: {{ adr.meta.title }}

{# ADR has ## Context, ## Decision - shift to #### to nest under ### #}
{{ adr.content | shift_headers(2) }}
{% endfor %}

## System Components

{# Snippet has ## Cloud Architecture - shift to ### to nest under ## #}
{{ content("snippets/components/infrastructure.md") | shift_headers(1) }}
```

### Dynamic ADR Inclusion

The template queries ADRs by status:

```jinja
{% for adr in query("snippets/adrs/", status=adr_status) %}
```

This allows generating documents with only accepted, proposed, or all ADRs.

### Frontmatter-Driven Organization

Each snippet has metadata for filtering and organization:

```yaml
---
id: ADR-001
title: Use PostgreSQL as Primary Database
status: accepted
tags: [database, infrastructure, critical]
---
```

### Modular Compliance Sections

Add new compliance frameworks by creating snippets in `snippets/legal/`:

```bash
# Add SOC 2 compliance
touch snippets/legal/soc2.md
# Then reference in template:
# {{ content("snippets/legal/soc2.md") }}
```

## Customization

### Add a new ADR

1. Create `snippets/adrs/adr-004-messaging.md`
2. Include proper frontmatter with `status: accepted`
3. Regenerate document - it's automatically included

### Different document types

Create specialized templates:

- `templates/security-review.md.j2` - Focus on threats and compliance
- `templates/executive-summary.md.j2` - High-level overview only
- `templates/audit-report.md.j2` - Compliance-focused for auditors

### Query by tags

```jinja
{# Include only critical decisions #}
{% for adr in query("snippets/adrs/", tags__contains="critical") %}
```
