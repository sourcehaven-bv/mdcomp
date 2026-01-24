# Issue 003: Add PyPI metadata to pyproject.toml

## Summary
The `pyproject.toml` is missing metadata fields required for proper PyPI publishing and discoverability.

## Current Behavior
Missing: `authors`, `keywords`, `classifiers`, `project.urls`

## Expected Behavior
Complete metadata for PyPI listing including:
- Author information
- Keywords for search
- Classifiers for categorization
- URLs for homepage, documentation, repository

## Implementation
Add the following to `pyproject.toml`:

```toml
[project]
# ... existing fields ...
authors = [
    { name = "Author Name", email = "email@example.com" }
]
keywords = ["markdown", "jinja2", "templates", "documents", "cli", "composition"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Documentation",
    "Topic :: Text Processing :: Markup :: Markdown",
    "Typing :: Typed",
]

[project.urls]
Homepage = "https://github.com/username/mdcomp"
Documentation = "https://github.com/username/mdcomp#readme"
Repository = "https://github.com/username/mdcomp"
Changelog = "https://github.com/username/mdcomp/blob/main/CHANGELOG.md"
Issues = "https://github.com/username/mdcomp/issues"
```

## Priority
Medium - Required for PyPI publishing

## Labels
enhancement, packaging, pypi
