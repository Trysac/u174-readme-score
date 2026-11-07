# Architecture

## Overview

`readme-score` evaluates Markdown content using line-based parsing rather than a full Abstract Syntax Tree (AST), ensuring zero dependencies on the Python Standard Library.

## Components

- **`checker.py`**: Contains the core logic for line-by-line parsing. It identifies fenced code blocks to isolate "outside" text from code content, and uses regexes to identify headings and content requirements.
- **`__main__.py`**: CLI interface wrapper that handles file I/O, `max_bytes` limits, and user-provided arguments.
- **`errors.py`**: Defines specific, typed exceptions like `ReadmeError` for API consistency.
