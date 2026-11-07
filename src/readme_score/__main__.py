"""CLI entry point for readme_score."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from readme_score.checker import score_readme
from readme_score.errors import ReadmeError

MAX_FILE_BYTES = 1_048_576


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for scoring a README file.

    Args:
        argv: Argument list or None to use sys.argv[1:].

    Returns:
        Exit code: 0 on success >= min score, 1 on score < min, 2 on usage or IO errors.
    """
    parser = argparse.ArgumentParser(
        prog="readme-score",
        description="Score a README file against standard quality checks.",
    )
    parser.add_argument("path", help="Path to the README file")
    parser.add_argument(
        "--min", dest="min_score", type=int, default=0, help="Minimum passing score"
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json)",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code != 0 else 0

    target_path = Path(args.path)
    if not target_path.is_file():
        sys.stderr.write(f"Error: File '{args.path}' not found.\n")
        return 2

    try:
        file_size = target_path.stat().st_size
        if file_size > MAX_FILE_BYTES:
            sys.stderr.write(
                f"Error: File '{args.path}' exceeds maximum size of {MAX_FILE_BYTES} bytes.\n"
            )
            return 2
        text = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as err:
        sys.stderr.write(f"Error reading file '{args.path}': {err}\n")
        return 2

    base_dir = target_path.resolve().parent

    def file_exists(rel_target: str) -> bool:
        try:
            resolved = (base_dir / rel_target).resolve()
            # Ensure resolved path is inside or identical to base_dir
            try:
                resolved.relative_to(base_dir)
            except ValueError:
                return False
            return resolved.exists()
        except OSError:
            return False

    try:
        report = score_readme(text, exists=file_exists, max_bytes=MAX_FILE_BYTES)
    except ReadmeError as err:
        sys.stderr.write(f"Error: {err}\n")
        return 2

    if args.output_format == "json":
        payload: dict[str, Any] = {
            "score": report.score,
            "grade": report.grade,
            "checks": [
                {
                    "id": c.id,
                    "name": c.name,
                    "weight": c.weight,
                    "status": c.status,
                    "detail": c.detail,
                }
                for c in report.checks
            ],
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(f"{report.score} {report.grade}\n")
        for c in report.checks:
            if c.status != "pass":
                detail_str = f": {c.detail}" if c.detail else ""
                sys.stdout.write(f"{c.id} {c.status} {c.name}{detail_str}\n")

    return 0 if report.score >= args.min_score else 1


if __name__ == "__main__":
    sys.exit(main())
