---
id: PLAN-ZBZP
status: done
title: 'Planning: SQL Data Source'
type: planning-checklist
---

## Understanding

- [x] Clarify requirements
  - Use SQLAlchemy Core (not ORM) for database abstraction - similar to JDBC
  - Support MySQL, PostgreSQL, SQLite via same connection URL format
  - Raw queries only, no ORM
- [x] Define scope (in/out)
  - **In scope**: `sql()` function, single connection, parameterized queries, read-only
  - **Out of scope**: ORM, multiple connections, write operations, NoSQL
- [x] Write acceptance criteria
  1. `sql(query, params)` function available in templates
  2. Returns list of dicts (column names as keys)
  3. Connection via `MDCOMP_DB_URL` env var, `db_url` context, or `--db-url` CLI flag
  4. Parameterized queries to prevent SQL injection
  5. Clear error messages for connection/query failures
  6. Works with MySQL, PostgreSQL, SQLite

## Approach

- [x] Research codebase
  - `render.py:create_environment()` - injects global functions into Jinja2
  - `errors.py` - custom exception hierarchy (add `DatabaseError`)
  - `context.py` - loads variables from env/file/CLI
  - `cli.py` - defines CLI options
- [x] Document technical approach
  1. Add `sqlalchemy` as optional dependency (`pip install mdcomp[sql]`)
  2. Add `DatabaseError` to `errors.py`
  3. Create `src/mdcomp/database.py` with connection handling and `run_sql()` function
  4. Add `--db-url` CLI option and `MDCOMP_DB_URL` env var support
  5. Inject `sql()` function in `create_environment()` when db_url is provided
- [x] List files to modify
  - `pyproject.toml` - add sqlalchemy optional dependency
  - `src/mdcomp/errors.py` - add DatabaseError
  - `src/mdcomp/database.py` - NEW: connection and query logic
  - `src/mdcomp/render.py` - inject sql() into environment
  - `src/mdcomp/cli.py` - add --db-url option
  - `src/mdcomp/context.py` - support MDCOMP_DB_URL
  - `tests/test_database.py` - NEW: database tests
  - `docs/templates.md` - document sql() function
- [x] Consider alternatives
  - **Direct driver (mysql-connector)**: Simpler but MySQL-only
  - **SQLAlchemy Core**: Chosen - multi-DB support with same interface
  - **asyncio version**: Overkill for CLI tool, rejected

## Test Plan

- [x] Define test scenarios
  1. Basic SELECT query returns list of dicts
  2. Parameterized queries work correctly
  3. Empty result returns empty list
  4. Connection errors give clear message
  5. Query errors give clear message
  6. Works in Jinja2 template context
- [x] List edge cases
  - NULL values in results
  - Special characters in data
  - Large result sets
  - Unicode column names
  - No db_url configured (sql() should error clearly)
- [x] Integration test approach
  - Use SQLite in-memory for fast tests
  - Test full render pipeline with sql() in template

## Risk Assessment

- [x] Identify risks
  1. **Dependency bloat**: SQLAlchemy adds overhead
  2. **SQL injection**: Users might concatenate strings
  3. **Credentials exposure**: db_url in context files
  4. **Performance**: Large result sets in memory
- [x] Document mitigations
  1. Make SQLAlchemy optional (`mdcomp[sql]`)
  2. Document parameterized queries prominently, use text() binding
  3. Recommend env var over context files for credentials
  4. Document that this is for reporting, not ETL
