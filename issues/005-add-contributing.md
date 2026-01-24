# Issue 005: Add CONTRIBUTING.md

## Summary
Add a CONTRIBUTING.md file to guide potential contributors on how to contribute to the project.

## Current Behavior
No contribution guidelines exist. Contributors don't know the process for submitting changes.

## Expected Behavior
A `CONTRIBUTING.md` file explaining:
- How to set up the development environment
- How to run tests and linting
- Code style guidelines
- Pull request process

## Implementation
Create `CONTRIBUTING.md` covering:
1. Development setup with uv
2. Running tests (`just test`)
3. Running all checks (`just check`)
4. Code style (enforced by ruff)
5. Commit message guidelines
6. PR process

## Priority
Medium - Important for open source projects

## Labels
documentation, community
