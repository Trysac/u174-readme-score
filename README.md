# readme-score

[![CI](https://github.com/Trysac/u174-readme-score/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u174-readme-score/actions)

Score a README on ten documented checks: title, summary, install and usage sections, tagged code blocks, license, placeholders, relative links, length and image alt text.

## Problem

Open source READMEs often lack installation steps, usage examples, or license notes. Generic Markdown linters focus on syntax formatting; `readme-score` assesses whether the README provides the information a user actually needs to get started.

## Installation

```bash
pip install trysac-readme-score
```

## Usage

```python
from readme_score import score_readme

markdown = "# Project Name\n\nA useful tool.\n\n## Installation\npip install foo"
report = score_readme(markdown)
print(f"Score: {report.score} ({report.grade})")
for check in report.checks:
    if check.status != "pass":
        print(f"Check {check.id} failed: {check.detail}")
```

## API, Limits and Options

- `score_readme(text, exists=None, max_bytes=1_048_576)`: Analyzes the string and returns a `Report` object.
- `grade(score)`: Returns a letter grade ('A' through 'F').
- Limits: Input is limited to `1_048_576` bytes. Input exceeding this raises `ReadmeError('input_too_large')`.
- Options: The `exists` callable can be injected to validate relative links.

## Why not generic linters?

Generic linters (like `markdownlint`) check syntax and style formatting. `readme-score` verifies that the document contains essential content sections (Installation, Usage, License) and has valid relative linking.

See [Security Notes](docs/SECURITY.md).
