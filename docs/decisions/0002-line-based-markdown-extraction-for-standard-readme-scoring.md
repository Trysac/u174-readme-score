# Line-based Markdown extraction for standard README scoring

Status: accepted (generated, pending human review)

## Context

README evaluation requires differentiating content outside and inside fenced code blocks and identifying ATX headings, inline links, image alt texts, and placeholder keywords. Introducing external heavy Markdown AST parsers would add runtime dependencies and potential parsing overhead.

## Decision

Implement a pure Python line-based fence parser handling arbitrary backtick and tilde delimiters, filtering content outside fences before running targeted regular expression checks and relative path validation.

## Consequences

Zero runtime dependencies, fast deterministic execution, strict compliance with the ten acceptance checks, and bounded memory consumption.
