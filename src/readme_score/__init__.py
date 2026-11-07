"""README scoring utility evaluating completeness, readability, and structural health."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

from readme_score.checker import grade, score_readme
from readme_score.errors import ReadmeError

__all__ = [
    "CheckResult",
    "ReadmeError",
    "Report",
    "__version__",
    "grade",
    "score_readme",
]

__version__ = "0.1.0"

logging.getLogger(__name__).addHandler(logging.NullHandler())


@dataclass(frozen=True)
class CheckResult:
    """Result of a single README check.

    Attributes:
        id: Unique check identifier (e.g., 'R01').
        name: Human-readable check name.
        weight: Numerical weight allocated towards the total score.
        status: Outcome status ('pass', 'fail', or 'skipped').
        detail: Context or diagnostic failure message, if applicable.
    """

    id: str
    name: str
    weight: int
    status: Literal["pass", "fail", "skipped"]
    detail: str | None = None


@dataclass(frozen=True)
class Report:
    """Evaluation report summarizing all README checks.

    Attributes:
        score: Overall score from 0 to 100.
        grade: Letter grade ('A', 'B', 'C', 'D', 'F').
        checks: Sequence of individual check results.
    """

    score: int
    grade: Literal["A", "B", "C", "D", "F"]
    checks: tuple[CheckResult, ...]
