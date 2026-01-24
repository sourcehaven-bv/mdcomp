# Issue 010: Improve test coverage

## Summary
Increase test coverage from 87% to 95%+ by adding tests for uncovered code paths.

## Current Behavior
Coverage: 87% with gaps in:
- `__main__.py` (0% - 3 lines)
- `cli.py` (80% - error handling, YAML output)
- `context.py` (90% - edge cases)
- `filters.py` (93% - error paths)
- `query.py` (88% - edge cases)
- `render.py` (94% - error paths)

## Expected Behavior
95%+ coverage with tests for:
1. `__main__.py` entry point
2. CLI error handling paths (template not found, directory not found)
3. YAML output format in `list` command
4. Context loading edge cases
5. Filter error handling

## Missing Test Cases

### `__main__.py`
```python
def test_main_entry():
    """Test the __main__ entry point."""
    # Can be tested via subprocess or by importing
```

### `cli.py`
- Test `--format yaml` in list command (lines 134-137)
- Test when no files match filter (lines 141-142)
- Test meta command error handling (lines 192-194)

### `query.py`
- Test files with invalid frontmatter
- Test empty directories
- Test comparison operators edge cases

## Priority
Medium - Important for reliability

## Labels
testing, quality
