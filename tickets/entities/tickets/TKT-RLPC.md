---
effort: m
id: TKT-RLPC
kind: enhancement
priority: medium
status: done
title: Add SQL data source for template queries
type: ticket
---

Enable mdcomp templates to execute SQL queries against MySQL (and potentially other SQL databases) as a data source for document generation.

## Motivation

Currently, mdcomp templates can access data from:
- Context files (YAML/JSON)
- Environment variables
- CLI arguments
- File system queries (markdown with frontmatter)
- Shell commands

For many documentation and reporting use cases, data lives in SQL databases. While users can work around this using shell commands (`shell("mysql -e 'SELECT ...' | jq")`), a native SQL integration would provide:
- Better ergonomics with parameterized queries
- Proper result formatting as lists of dicts
- Secure credential handling
- Connection pooling for multiple queries
- Clear error messages for database issues

## Proposed Solution

Add a `sql()` function available in templates:

```jinja
{% for user in sql("SELECT name, email FROM users WHERE status = %s", ["active"]) %}
- {{ user.name }}: {{ user.email }}
{% endfor %}
```

With database connection configured via:
- Context variable (`db_url` or similar)
- Environment variable (`MDCOMP_DB_URL`)
- CLI flag (`--db-url`)

## Out of Scope

- ORM/model support (this is for raw SQL queries)
- Schema migrations
- Write operations (INSERT/UPDATE/DELETE) - read-only by design
- NoSQL databases (separate feature)
