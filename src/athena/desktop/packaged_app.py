"""Frozen Windows entry point that safely multiplexes pATHENA child processes.

A PyInstaller build changes ``sys.executable`` from Python to ``pATHENA.exe``. The
normal desktop intentionally starts its Core, scheduler, and short-lived JOBS helper
through ``sys.executable -m ...``. Without a dispatcher those child launches recurse
back into the desktop entry point. This module recognizes only the module invocations
that pATHENA itself owns and fails closed for every other ``-m`` request.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum


class PackagedTarget(StrEnum):
    DESKTOP = "desktop"
    CORE = "core"
    ATHENA_CLI = "athena-cli"
    JOBS_CLI = "jobs-cli"


class PackagedInvocationError(ValueError):
    """Raised when a frozen executable receives an unsupported module dispatch."""


@dataclass(frozen=True, slots=True)
class PackagedInvocation:
    target: PackagedTarget
    arguments: tuple[str, ...]


_MODULE_TARGETS = {
    "athena.api.process": PackagedTarget.CORE,
    "athena": PackagedTarget.ATHENA_CLI,
    "athena.desktop.jobs_cli": PackagedTarget.JOBS_CLI,
}


def route_packaged_argv(argv: Sequence[str]) -> PackagedInvocation:
    """Resolve one frozen invocation without ever falling through an unknown ``-m``."""
    arguments = tuple(argv)
    if not arguments or arguments[0] != "-m":
        return PackagedInvocation(PackagedTarget.DESKTOP, arguments)
    if len(arguments) < 2 or not arguments[1].strip():
        raise PackagedInvocationError("Packaged module invocation is missing a module name.")

    module = arguments[1]
    target = _MODULE_TARGETS.get(module)
    if target is None:
        raise PackagedInvocationError(
            f"Packaged pATHENA refuses unsupported module dispatch: {module!r}."
        )
    return PackagedInvocation(target, arguments[2:])


def dispatch(argv: Sequence[str] | None = None) -> int:
    """Dispatch the desktop or one explicitly supported internal process role."""
    raw_arguments = tuple(sys.argv[1:] if argv is None else argv)
    try:
        invocation = route_packaged_argv(raw_arguments)
    except PackagedInvocationError as exc:
        print(f"pATHENA packaged runtime error: {exc}", file=sys.stderr)
        return 2

    if invocation.target is PackagedTarget.CORE:
        from athena.api.process import main as core_main

        return core_main(invocation.arguments)

    if invocation.target is PackagedTarget.ATHENA_CLI:
        from athena.__main__ import main as athena_main

        return athena_main(invocation.arguments)

    if invocation.target is PackagedTarget.JOBS_CLI:
        from athena.desktop.jobs_cli import main as jobs_main

        return jobs_main(invocation.arguments)

    from athena.desktop.app import main as desktop_main

    # QApplication expects argv[0] to remain the executable identity.
    return desktop_main((sys.argv[0], *invocation.arguments))


def main(argv: Sequence[str] | None = None) -> int:
    return dispatch(argv)


if __name__ == "__main__":
    raise SystemExit(main())
