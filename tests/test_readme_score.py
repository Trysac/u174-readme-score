"""Behavior tests for the public API of readme_score."""

from __future__ import annotations

import pytest

import readme_score


def test_normalize_trims_and_lowercases() -> None:
    assert readme_score.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        readme_score.normalize(value)


def test_version_is_semver() -> None:
    parts = readme_score.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
