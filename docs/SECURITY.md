# Security notes

## Threat model

`trysac-readme-score` is a pure Python library designed to process text strings.

### Defended

- **Denial of Service (DoS)**: The library enforces an explicit `max_bytes` limit (default 1 MiB) on the input text. If the input exceeds this, `ReadmeError` is raised immediately before significant processing occurs.
- **Path Traversal**: When validating relative links, the CLI and library resolve paths against the base directory. It strictly checks that the resolved target remains within the base directory. If a link attempts to escape the root directory, it is flagged as a failure (`escapes root`).

### Not defended

- **Hostile Input**: The library does not sanitize or sanitize HTML/Markdown for rendering. It is intended for analysis, not for display to a browser. Callers are responsible for sanitizing output if they intend to render the README content.
