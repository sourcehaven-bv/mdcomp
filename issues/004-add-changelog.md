# Issue 004: Add CHANGELOG.md

## Summary
Add a CHANGELOG.md file to track releases and changes following the Keep a Changelog format.

## Current Behavior
No changelog exists. Users have no way to see what changed between versions.

## Expected Behavior
A `CHANGELOG.md` file at the project root documenting all notable changes, following semantic versioning and the Keep a Changelog format.

## Implementation
Create `CHANGELOG.md` with:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - YYYY-MM-DD

### Added
- Initial release
- `render` command for template rendering
- `list` command for querying markdown files
- `meta` command for inspecting frontmatter
- Jinja2 template support with custom filters
- Shell integration via `shell()` and `pipe`
- Variable layering (environment, files, CLI)
- Documentation and examples
```

## Priority
Medium - Standard practice for versioned software

## Labels
documentation, release-management
