---
id: IMPL-Z7S1
status: done
title: 'Implementation: SQL Data Source'
type: implementation-checklist
---

## Development

- [x] Add sqlalchemy optional dependency to pyproject.toml
- [x] Add DatabaseError to errors.py
- [x] Create database.py with run_sql() function
- [x] Add --db-url CLI option
- [x] Inject sql() into render.py environment
- [x] Write unit tests
- [x] Write integration tests

## Verification

- [x] All tests pass (162 passed)
- [x] Manual test with SQLite - verified sql() queries database correctly
- [x] Error handling verified - clear message when db_url not provided
