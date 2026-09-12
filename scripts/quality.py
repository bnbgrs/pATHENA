"""Run ATHENA's local canonical quality gate.

The command plan mirrors the primary Python quality job in GitHub Actions:
validate the dependency lock, then run the specification validator, Ruff,
mypy, and pytest through the locked project environment with development
and desktop extras enabled.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UV_RUN_PREFIX = ("uv", "run", "--locked", "--extra", "dev", "--extra", "desktop")


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    command: tuple[str, ...]


def build_checks() -> tuple[Check, ...]:
    return (
        Check(name="Dependency lock", command=("uv", "lock", "--check")),
        Check(
            name="Specification validator",
            command=(*UV_RUN_PREFIX, "python", "scripts/validate_spec.py"),
        ),
        Check(
            name="Ruff",
            command=(*UV_RUN_PREFIX, "python", "-m", "ruff", "check", "src", "tests", "scripts"),
        ),
        Check(
            name="mypy",
            command=(*UV_RUN_PREFIX, "python", "-m", "mypy", "src/athena"),
        ),
        Check(
            name="pytest",
            command=(*UV_RUN_PREFIX, "python", "-m", "pytest"),
        ),
    )


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ATHENA canonical local quality gate.")
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="run every check and report all failures instead of stopping at the first failure",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the exact locked command plan without executing it",
    )
    return parser.parse_args(argv)


def _quality_environment() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    return env


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    checks = build_checks()

    print("ATHENA QUALITY GATE")
    print("=" * 60)
    print(f"Repository root: {REPO_ROOT}")

    if args.dry_run:
        print("\n[DRY RUN] Locked command plan")
        for check in checks:
            print(f"- {check.name}: {shlex.join(check.command)}")
        return 0

    env = _quality_environment()
    failures: list[tuple[str, int]] = []

    for check in checks:
        print(f"\n[RUN] {check.name}")
        print(shlex.join(check.command))

        try:
            completed = subprocess.run(
                check.command,
                check=False,
                cwd=REPO_ROOT,
                env=env,
            )
        except FileNotFoundError as exc:
            print(
                f"\n[FAIL] {check.name} could not start: {exc}. "
                "Install the repository-pinned uv resolver first.",
                file=sys.stderr,
            )
            return 127

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
