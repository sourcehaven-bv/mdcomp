---
description: Add a sql() function to templates that executes queries against MySQL/PostgreSQL/SQLite and returns results as a list of dictionaries for iteration in Jinja2 templates.
id: FEAT-HS50
priority: medium
status: implemented
summary: Execute SQL queries against databases from within templates
title: SQL Data Source
type: feature
---

Allow templates to query SQL databases (MySQL, PostgreSQL, SQLite) as a data source for document generation.

## User Value

- Generate reports from live database data
- Create documentation that reflects current system state
- Build dashboards and status pages with real data

## Capabilities

- `sql()` function available in templates
- Parameterized queries to prevent SQL injection
- Results returned as list of dictionaries
- Read-only operations only (SELECT)
- Connection via URL string (standard database URL format)
