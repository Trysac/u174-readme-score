"""Line-based parser and checker evaluation for readme_score."""

from __future__ import annotations

import posixpath
import re
from collections.abc import Callable
from typing import TYPE_CHECKING, Literal

from readme_score.errors import ReadmeError

if TYPE_CHECKING:
    from readme_score import Report

_INSTALL_RE = re.compile(r"(?i)\b(install|installation|getting started|setup)\b")
_USAGE_RE = re.compile(r"(?i)\b(usage|examples?|quick ?start)\b")
_LICENSE_RE = re.compile(r"(?i)\blicen[cs]e\b")
_PLACEHOLDER_RE = re.compile(r"(?i)\b(lorem ipsum|coming soon|todo|fixme|tbd)\b")
_LINK_IMAGE_RE = re.compile(r"(!?)(\[[^\]]*\])\(([^)\s]+)(?:\s+[^)]*)?\)")
_IMAGE_ONLY_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)")
_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def grade(score: int) -> Literal["A", "B", "C", "D", "F"]:
    """Return letter grade for a given numerical score.

    Args:
        score: Integer score from 0 to 100.

    Returns:
        Literal['A', 'B', 'C', 'D', 'F']
    """
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _is_fence_delimiter(line: str) -> tuple[bool, str, int, str]:
    stripped = line.strip()
    if not stripped:
        return False, "", 0, ""
    char = stripped[0]
    if char not in ("`", "~"):
        return False, "", 0, ""
    run_len = 0
    for c in stripped:
        if c == char:
            run_len += 1
        else:
            break
    if run_len < 3:
        return False, "", 0, ""
    info = stripped[run_len:].strip()
    return True, char, run_len, info


def score_readme(
    text: str,
    *,
    exists: Callable[[str], bool] | None = None,
    max_bytes: int = 1_048_576,
) -> Report:
    """Score a README string against the ten standard checks.

    Args:
        text: README Markdown text content.
        exists: Optional predicate checking existence of a relative target path.
        max_bytes: Maximum allowed UTF-8 byte length (default 1 MiB).

    Returns:
        Report with final score, letter grade, and individual check results.

    Raises:
        ReadmeError: If input length exceeds max_bytes.
    """
    from readme_score import CheckResult, Report

    raw_bytes = text.encode("utf-8")
    if len(raw_bytes) > max_bytes:
        raise ReadmeError(
            "input_too_large", f"Input exceeds maximum allowed size of {max_bytes} bytes"
        )

    lines = text.splitlines()

    in_fence = False
    fence_char = ""
    fence_length = 0

    has_language_fence = False
    outside_lines: list[tuple[int, str]] = []  # 1-indexed (line_number, text)

    for idx, line in enumerate(lines, start=1):
        is_fence, f_char, f_len, info = _is_fence_delimiter(line)
        if not in_fence:
            if is_fence:
                in_fence = True
                fence_char = f_char
                fence_length = f_len
                if info:
                    has_language_fence = True
            else:
                outside_lines.append((idx, line))
        else:
            if is_fence and f_char == fence_char and f_len >= fence_length:
                in_fence = False
                fence_char = ""
                fence_length = 0

    # R01: Title (weight 10)
    # The first non-empty line outside fences is a level-1 heading ('# ')
    first_non_empty_idx: int | None = None
    r01_pass = False
    for i, (_, line_content) in enumerate(outside_lines):
        if line_content.strip():
            first_non_empty_idx = i
            break

    if first_non_empty_idx is not None:
        first_line = outside_lines[first_non_empty_idx][1]
        if first_line.startswith("# "):
            r01_pass = True

    # R02: Summary (weight 10)
    # A non-heading, non-empty line outside fences appears within the 10 lines after the title
    # (or within the first 10 lines when there is no title)
    r02_pass = False
    if r01_pass and first_non_empty_idx is not None:
        window_start = first_non_empty_idx + 1
        window = outside_lines[window_start : window_start + 10]
    else:
        window = outside_lines[:10]

    for _, line_content in window:
        stripped = line_content.strip()
        if stripped:
            is_heading = any(stripped.startswith("#" * k + " ") for k in range(1, 7))
            if not is_heading:
                r02_pass = True
                break

    # Headings outside fences for R03, R04, R06
    headings: list[str] = []
    for _, line_content in outside_lines:
        stripped = line_content.strip()
        for k in range(1, 7):
            prefix = "#" * k + " "
            if stripped.startswith(prefix):
                headings.append(stripped[k + 1 :].strip())
                break

    # R03: Install (weight 15)
    r03_pass = any(_INSTALL_RE.search(h) is not None for h in headings)

    # R04: Usage (weight 15)
    r04_pass = any(_USAGE_RE.search(h) is not None for h in headings)

    # R05: Code language (weight 10)
    r05_pass = has_language_fence

    # R06: License (weight 10)
    r06_pass = any(_LICENSE_RE.search(h) is not None for h in headings)

    # R07: No placeholders (weight 10)
    r07_pass = True
    r07_detail: str | None = None
    for line_num, line_content in outside_lines:
        m = _PLACEHOLDER_RE.search(line_content)
        if m:
            r07_pass = False
            r07_detail = f"line {line_num}: {m.group(1)}"
            break

    # R08: Relative links (weight 10)
    r08_status: Literal["pass", "fail", "skipped"]
    r08_detail: str | None = None
    if exists is None:
        r08_status = "skipped"
    else:
        r08_status = "pass"
        for _, line_content in outside_lines:
            for m in _LINK_IMAGE_RE.finditer(line_content):
                target = m.group(3).strip()
                if not target:
                    continue
                if _SCHEME_RE.match(target) or target.startswith(("#", "/")):
                    continue
                clean_target = target.split("#", 1)[0].split("?", 1)[0]
                if not clean_target:
                    continue
                normalized = posixpath.normpath(clean_target)
                if normalized == ".." or normalized.startswith("../"):
                    r08_status = "fail"
                    r08_detail = f"{target}: escapes root"
                    break
                if not exists(normalized):
                    r08_status = "fail"
                    r08_detail = target
                    break
            if r08_status == "fail":
                break

    # R09: Length (weight 5)
    # At least 150 words outside fences (words are \S+ runs)
    total_words = sum(len(line_content.split()) for _, line_content in outside_lines)
    r09_pass = total_words >= 150

    # R10: Image alt (weight 5)
    r10_pass = True
    for _, line_content in outside_lines:
        for m in _IMAGE_ONLY_RE.finditer(line_content):
            alt = m.group(1).strip()
            if not alt:
                r10_pass = False
                break
        if not r10_pass:
            break

    results = (
        CheckResult("R01", "title", 10, "pass" if r01_pass else "fail"),
        CheckResult("R02", "summary", 10, "pass" if r02_pass else "fail"),
        CheckResult("R03", "install", 15, "pass" if r03_pass else "fail"),
        CheckResult("R04", "usage", 15, "pass" if r04_pass else "fail"),
        CheckResult("R05", "code_language", 10, "pass" if r05_pass else "fail"),
        CheckResult("R06", "license", 10, "pass" if r06_pass else "fail"),
        CheckResult("R07", "no_placeholders", 10, "pass" if r07_pass else "fail", r07_detail),
        CheckResult("R08", "relative_links", 10, r08_status, r08_detail),
        CheckResult("R09", "length", 5, "pass" if r09_pass else "fail"),
        CheckResult("R10", "image_alt", 5, "pass" if r10_pass else "fail"),
    )

    passed_weight = sum(r.weight for r in results if r.status == "pass")
    applicable_weight = sum(r.weight for r in results if r.status != "skipped")

    score = round(100 * passed_weight / applicable_weight) if applicable_weight > 0 else 0
    return Report(score=score, grade=grade(score), checks=results)
