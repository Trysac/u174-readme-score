# Project record

## Objective

To provide an automated, transparent quality score for software READMEs, specifically ensuring that essential documentation sections are present and functional.

## Scope

- Parsing and scoring of README Markdown files based on ten specific heuristics (title presence, summary, install section, usage section, language tagging in code blocks, license presence, placeholder detection, relative link resolution, word count, and image alt text).
- Exposing functionality via a Python library and a CLI interface.

## Out-of-scope

- Markdown syntax linting or style enforcement.
- Spelling or grammar checking.
- External URL validation.
- Reference-style link parsing.
- HTML block parsing.
- Configurable scoring weights.

## Factory run u174 (measured from API usage)

| Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|
| generation | gemini-3.8-flash | yes | 4432 | 9918 | 0 | 0 | 0.0203 |
| fix-1 | gemini-3.8-flash | no | 14758 | 225 | 0 | 16843 | 0.0132 |
| fix-2 | gemini-3.8-flash | no | 79438 | 2370 | 0 | 436671 | 0.1012 |
| fix-3 | gemini-3.8-flash | no | 62489 | 942 | 0 | 362426 | 0.0776 |
| audit | gemini-3.1-flash-lite | no | 90158 | 677 | 0 | 479113 | 0.0355 |
| docs | gemini-3.1-flash-lite | no | 179856 | 1641 | 0 | 0 | 0.0474 |

Total: $0.2952. Prices: Anthropic list prices.
