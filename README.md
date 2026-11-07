# readme-score

[![PyPI version](https://img.shields.io/pypi/v/trysac-readme-score)](https://pypi.org/project/trysac-readme-score/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-readme-score)](LICENSE)
[![CI](https://github.com/Trysac/u174-readme-score/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u174-readme-score/actions/workflows/ci.yml)

Score a README on ten documented checks: title, summary, install and usage sections, tagged code blocks, license, placeholders, relative links, length and image alt text

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-readme-score
# or
uv add trysac-readme-score
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import readme_score

# normalize() trims surrounding whitespace and lower-cases the text.
print(readme_score.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    readme_score.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
