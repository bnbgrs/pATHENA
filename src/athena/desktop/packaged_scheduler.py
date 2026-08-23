"""PyInstaller launcher for the packaged pATHENA scheduler executable."""

from __future__ import annotations

import sys

from athena.__main__ import main


def _normalize_argv() -> None:
    """Accept the supervisor's normal ``python -m athena`` argument prefix."""
    arguments = sys.argv[1:]
    if arguments[:2] == ["-m", "athena"]:
        sys.argv = [sys.argv[0], *arguments[2:]]


if __name__ == "__main__":
    _normalize_argv()
    raise SystemExit(main())
