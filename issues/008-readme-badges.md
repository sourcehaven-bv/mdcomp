# Issue 008: Add README badges

## Summary
Add status badges to the README for CI status, test coverage, PyPI version, and Python version support.

## Current Behavior
README has no badges showing project status at a glance.

## Expected Behavior
README includes badges for:
- CI build status
- Test coverage percentage
- PyPI version
- Python version support
- License

## Implementation
Add badges section after the title in `README.md`:

```markdown
# mdcomp

[![CI](https://github.com/username/mdcomp/actions/workflows/ci.yml/badge.svg)](https://github.com/username/mdcomp/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/username/mdcomp/branch/main/graph/badge.svg)](https://codecov.io/gh/username/mdcomp)
[![PyPI](https://img.shields.io/pypi/v/mdcomp.svg)](https://pypi.org/project/mdcomp/)
[![Python](https://img.shields.io/pypi/pyversions/mdcomp.svg)](https://pypi.org/project/mdcomp/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A CLI tool for composing documents from Markdown snippets and Jinja2 templates.
```

Note: Badge URLs will need to be updated with the actual repository username once CI is set up.

## Priority
Low - Visual improvement for project presentation

## Labels
documentation, enhancement
