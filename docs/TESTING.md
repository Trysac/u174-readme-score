# Testing

## Coverage

Tests are located in `tests/test_readme_score.py` and mirror the public API and internal logic modules.

- **`score_readme` Logic**: Exercises all ten quality checks (R01-R10). Tests include empty strings, strings that fail every check, and strings that pass every check.
- **Relative Link Resolution**: Verifies that links to missing files fail, while links to existing files (injected via the `exists` predicate) pass. Validates that paths escaping the root directory are caught.
- **Error Handling**: Verifies that input exceeding `MAX_FILE_BYTES` raises the appropriate `ReadmeError`.
- **CLI**: Verifies exit codes (0 for success, 1 for score below min, 2 for errors) and formatted output (text or json).
- **Scoring**: Validates the numerical scoring calculation and letter grade mappings.
