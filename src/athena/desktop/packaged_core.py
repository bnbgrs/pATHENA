"""PyInstaller launcher for the packaged pATHENA Core executable."""

from __future__ import annotations

import sys

from athena.api.process import main


def _normalize_argv() -> None:
    """Accept the supervisor's normal ``python -m`` argument prefix."""
    arguments = sys.argv[1:]
    if arguments[:2] == ["-m", "athena.api.process"]:
        sys.argv = [sys.argv[0], *arguments[2:]]


if __name__ == "__main__":
    _normalize_argv()
    raise SystemExit(main())
