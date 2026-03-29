---
description: Template function that connects to SQL databases, executes parameterized SELECT queries, and returns results as structured data (list of dicts) for use in document generation.
id: sql-data-source
layer: core
package: mdcomp.database
status: stable
summary: Database query integration for templates
title: SQL Data Source
type: concept
---

A template function that executes SQL queries and returns results as structured data.

## Responsibilities

- Connect to SQL databases using connection URLs
- Execute parameterized SELECT queries
- Return results as list of dicts (column names as keys)
- Handle connection errors gracefully
- Enforce read-only access

## Integration Points

- Injected into Jinja2 environment as `sql()` global function
- Connection string provided via context, env var, or CLI
- Follows same error handling patterns as `shell()`
