"""Run ATHENA's local quality gate.

This script intentionally mirrors the checks used by GitHub Actions so a
developer can reproduce CI failures locally before pushing a commit.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    command: tuple[str, ...]


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ATHENA quality gate.")
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="run every check and report all failures instead of stopping at the first failure",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    checks = (
        Check(
            name="Specification validator",
            command=(sys.executable, "scripts/validate_spec.py"),
        ),
        Check(
            name="Ruff",
            command=(
                sys.executable,
                "-m",
                "ruff",
                "check",
                "src",
                "tests",
                "scripts",
            ),
        ),
        Check(
            name="mypy",
            command=(sys.executable, "-m", "mypy", "src/athena"),
        ),
        Check(
            name="pytest",
            command=(sys.executable, "-m", "pytest"),
        ),
    )

    print("ATHENA QUALITY GATE")
    print("=" * 60)

    failures: list[tuple[str, int]] = []
    for check in checks:
        print(f"\n[RUN] {check.name}")
        print(" ".join(check.command))

        completed = subprocess.run(
            check.command,
            check=False,
        )

        if completed.returncode != 0:
            print(
                f"\n[FAIL] {check.name} returned {completed.returncode}.",
                file=sys.stderr,
            )
            failures.append((check.name, completed.returncode))
            if not args.keep_going:
                return completed.returncode
            continue

        print(f"[PASS] {check.name}")

    print("\n" + "=" * 60)
    if failures:
        print("ATHENA QUALITY GATE: FAIL", file=sys.stderr)
        for name, returncode in failures:
            print(f"- {name}: exit {returncode}", file=sys.stderr)
        return failures[0][1]

    print("ATHENA QUALITY GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
