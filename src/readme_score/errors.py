"""Typed errors for readme_score."""

from __future__ import annotations

from typing import Literal

ErrorCode = Literal["input_too_large"]


class ReadmeError(Exception):
    """Base exception raised for readme scoring errors.

    Attributes:
        code: Stable machine-readable error code.
        message: Human-readable error description.
    """

    def __init__(self, code: ErrorCode, message: str | None = None) -> None:
        self.code: ErrorCode = code
        msg = message or f"Readme scoring error: {code}"
        if len(msg) > 200:
            msg = msg[:197] + "..."
        super().__init__(msg)
