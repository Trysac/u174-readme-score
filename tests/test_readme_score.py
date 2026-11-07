"""Comprehensive tests for readme_score."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from readme_score import ReadmeError, grade, score_readme
from readme_score.__main__ import main


def test_empty_readme_with_and_without_exists() -> None:
    # score_readme('', exists=lambda p: True) passes exactly R07, R08 and R10 for score 25 and grade 'F'
    rep_with_exists = score_readme("", exists=lambda p: True)
    assert rep_with_exists.score == 25
    assert rep_with_exists.grade == "F"
    passed = [c.id for c in rep_with_exists.checks if c.status == "pass"]
    assert passed == ["R07", "R08", "R10"]

    # score_readme('') without exists skips R08 and scores 17 (round(100 * 15 / 90))
    rep_no_exists = score_readme("")
    assert rep_no_exists.score == 17
    assert rep_no_exists.grade == "F"
    r08 = next(c for c in rep_no_exists.checks if c.id == "R08")
    assert r08.status == "skipped"


def test_title_and_summary_checks() -> None:
    # '# Title\n\nA tool that does one thing.\n' passes R01 and R02
    sample1 = "# Title\n\nA tool that does one thing.\n"
    rep1 = score_readme(sample1)
    c_map1 = {c.id: c.status for c in rep1.checks}
    assert c_map1["R01"] == "pass"
    assert c_map1["R02"] == "pass"

    # '## Title\n' as the first line fails R01
    sample2 = "## Title\n"
    rep2 = score_readme(sample2)
    c_map2 = {c.id: c.status for c in rep2.checks}
    assert c_map2["R01"] == "fail"

    # a '# Title' line inside a fenced code block is ignored
    sample3 = "```\n# Title\n```\n## Subtitle\n"
    rep3 = score_readme(sample3)
    c_map3 = {c.id: c.status for c in rep3.checks}
    assert c_map3["R01"] == "fail"


def test_installation_and_usage_headings() -> None:
    # Headings '## Installation' and '## Getting Started' pass R03
    rep_inst1 = score_readme("## Installation\n")
    assert next(c for c in rep_inst1.checks if c.id == "R03").status == "pass"

    rep_inst2 = score_readme("## Getting Started\n")
    assert next(c for c in rep_inst2.checks if c.id == "R03").status == "pass"

    # '## Usage' and '## Quick start' pass R04
    rep_use1 = score_readme("## Usage\n")
    assert next(c for c in rep_use1.checks if c.id == "R04").status == "pass"

    rep_use2 = score_readme("## Quick start\n")
    assert next(c for c in rep_use2.checks if c.id == "R04").status == "pass"

    # the same headings inside a fenced block pass nothing
    fenced_headings = "```\n## Installation\n## Usage\n```\n"
    rep_fenced = score_readme(fenced_headings)
    assert next(c for c in rep_fenced.checks if c.id == "R03").status == "fail"
    assert next(c for c in rep_fenced.checks if c.id == "R04").status == "fail"


def test_code_language_and_license() -> None:
    # A block opened with '```python' or '~~~js' passes R05 and one opened with a bare '```' does not
    rep_py = score_readme("```python\nprint(1)\n```\n")
    assert next(c for c in rep_py.checks if c.id == "R05").status == "pass"

    rep_js = score_readme("~~~js\nconsole.log(1);\n~~~\n")
    assert next(c for c in rep_js.checks if c.id == "R05").status == "pass"

    rep_bare = score_readme("```\ncode\n```\n")
    assert next(c for c in rep_bare.checks if c.id == "R05").status == "fail"

    # '## License' passes R06
    rep_lic = score_readme("## License\nMIT\n")
    assert next(c for c in rep_lic.checks if c.id == "R06").status == "pass"

    rep_lic_uk = score_readme("# Licence\nMIT\n")
    assert next(c for c in rep_lic_uk.checks if c.id == "R06").status == "pass"


def test_placeholders() -> None:
    # The text 'lorem ipsum' on line 3 outside code fails R07 with detail 'line 3: lorem ipsum'
    text_ph = "Line 1\nLine 2\nHere is lorem ipsum content\n"
    rep = score_readme(text_ph)
    r07 = next(c for c in rep.checks if c.id == "R07")
    assert r07.status == "fail"
    assert r07.detail == "line 3: lorem ipsum"

    # and the same text inside a fenced block does not
    text_ph_fenced = "```\nline 2\nlorem ipsum\n```\n"
    rep2 = score_readme(text_ph_fenced)
    r07_2 = next(c for c in rep2.checks if c.id == "R07")
    assert r07_2.status == "pass"
    assert r07_2.detail is None


def test_relative_links() -> None:
    # With exists=lambda p: p == 'docs/x.md', '[a](docs/x.md)' and '[c](docs/x.md#sec)' pass R08,
    # '[b](missing.md)' fails with detail 'missing.md',
    # links starting with 'https://', 'mailto:' or '#' are not checked,
    # and '[d](../out.md)' fails with detail '../out.md: escapes root'
    def ex(p: str) -> bool:
        return p == "docs/x.md"

    text_ok = "Check [a](docs/x.md) and [c](docs/x.md#sec) and [ext](https://example.com) and [mail](mailto:test@example.com) and [anchor](#sec)"
    rep_ok = score_readme(text_ok, exists=ex)
    r08_ok = next(c for c in rep_ok.checks if c.id == "R08")
    assert r08_ok.status == "pass"

    text_missing = "Check [b](missing.md)"
    rep_missing = score_readme(text_missing, exists=ex)
    r08_missing = next(c for c in rep_missing.checks if c.id == "R08")
    assert r08_missing.status == "fail"
    assert r08_missing.detail == "missing.md"

    text_escape = "Check [d](../out.md)"
    rep_escape = score_readme(text_escape, exists=ex)
    r08_escape = next(c for c in rep_escape.checks if c.id == "R08")
    assert r08_escape.status == "fail"
    assert r08_escape.detail == "../out.md: escapes root"


def test_image_alt_and_grade() -> None:
    # '![](logo.png)' fails R10 and '![Logo](logo.png)' passes
    rep_no_alt = score_readme("![](logo.png)")
    assert next(c for c in rep_no_alt.checks if c.id == "R10").status == "fail"

    rep_with_alt = score_readme("![Logo](logo.png)")
    assert next(c for c in rep_with_alt.checks if c.id == "R10").status == "pass"

    # grade(90) == 'A', grade(89) == 'B', grade(75) == 'B', grade(74) == 'C',
    # grade(60) == 'C', grade(59) == 'D', grade(40) == 'D' and grade(39) == 'F'
    assert grade(90) == "A"
    assert grade(89) == "B"
    assert grade(75) == "B"
    assert grade(74) == "C"
    assert grade(60) == "C"
    assert grade(59) == "D"
    assert grade(40) == "D"
    assert grade(39) == "F"


def test_length_check_and_full_readme() -> None:
    content = [
        "# Great Project",
        "",
        "A clean utility for scoring documentation quality.",
        "",
        "## Installation",
        "",
        "Run pip install.",
        "",
        "## Usage",
        "",
        "```python",
        "import readme_score",
        "print(readme_score.__version__)",
        "```",
        "",
        "## License",
        "",
        "MIT License",
    ] + [f"Word{i}" for i in range(160)]
    full_text = "\n".join(content)
    rep = score_readme(full_text, exists=lambda p: True)
    assert rep.score == 100
    assert rep.grade == "A"
    assert all(c.status == "pass" for c in rep.checks)


def test_input_too_large() -> None:
    with pytest.raises(ReadmeError) as exc_info:
        score_readme("a" * 50, max_bytes=20)
    assert exc_info.value.code == "input_too_large"


def test_cli_acceptance(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # main(['README.md', '--min', '75']) returns 1 below 75 and 0 at or above it
    readme_file = tmp_path / "README.md"
    readme_file.write_text("# Low score README\n", encoding="utf-8")

    exit_code = main([str(readme_file), "--min", "75"])
    assert exit_code == 1
    out, _ = capsys.readouterr()
    assert "fail" in out

    # High score readme
    high_score_content = (
        "# Title\n\nSummary line.\n\n## Installation\nSetup.\n\n"
        "## Quick start\nExample.\n\n```python\nfoo()\n```\n\n## License\nMIT\n\n"
        + " ".join([f"w{i}" for i in range(160)])
    )
    readme_file.write_text(high_score_content, encoding="utf-8")
    assert main([str(readme_file), "--min", "75"]) == 0
    out, _ = capsys.readouterr()
    assert "100 A" in out

    # '--format json' prints an object with keys 'score', 'grade' and 'checks'
    assert main([str(readme_file), "--format", "json"]) == 0
    json_out, _ = capsys.readouterr()
    data = json.loads(json_out)
    assert "score" in data
    assert "grade" in data
    assert "checks" in data
    assert data["score"] == 100
    assert data["grade"] == "A"

    # missing file returns 2
    missing_path = tmp_path / "non_existent.md"
    assert main([str(missing_path)]) == 2
    _, err = capsys.readouterr()
    assert "not found" in err

    # file over 1_048_576 bytes returns 2
    huge_file = tmp_path / "huge.md"
    huge_file.write_bytes(b"x" * (1_048_576 + 10))
    assert main([str(huge_file)]) == 2
    _, err_huge = capsys.readouterr()
    assert "exceeds maximum size" in err_huge


def test_cli_argument_parsing_errors(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert main(["--unknown"]) == 2


def test_adversarial_and_boundary_checks(tmp_path: Path) -> None:
    # Fenced blocks with varying backtick/tilde lengths and nesting
    text_fence_nesting = "````markdown\n```python\ncode\n```\n````\n# Heading\nSummary\n"
    rep = score_readme(text_fence_nesting)
    # The outer fence has language 'markdown', so R05 passes
    assert next(c for c in rep.checks if c.id == "R05").status == "pass"
    # The '# Heading' outside fence passes R01
    assert next(c for c in rep.checks if c.id == "R01").status == "pass"

    # Escaping root relative links with ../../etc
    esc_doc = tmp_path / "escape.md"
    esc_doc.write_text("[doc](../../secret.txt)\n", encoding="utf-8")
    ret = main([str(esc_doc), "--min", "50"])
    assert ret == 1

    # R07 adversarial token neighbors: 'todone', 'autodo', 'fixment'
    safe_text = "# Title\n\nThis is todone and prefixcoming soonish.\n"
    rep_safe = score_readme(safe_text)
    assert next(c for c in rep_safe.checks if c.id == "R07").status == "pass"

    # R08 absolute paths or anchors: /root/path, #fragment
    link_text = "[root](/abs/path) and [anchor](#heading)"
    rep_link = score_readme(link_text, exists=lambda p: False)
    assert next(c for c in rep_link.checks if c.id == "R08").status == "pass"

    # Relative link with query and fragment query parameter
    rep_query = score_readme("[doc](docs/x.md?query=1#hash)", exists=lambda p: p == "docs/x.md")
    assert next(c for c in rep_query.checks if c.id == "R08").status == "pass"

    # ReadmeError with long message truncation
    err_long = ReadmeError("input_too_large", "x" * 250)
    assert len(str(err_long)) == 200
    assert str(err_long).endswith("...")
