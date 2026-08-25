"""Windowed entry point for the supported pATHENA Windows package.

The desktop executable is deliberately separate from ``pATHENA-Worker.exe``. Before
constructing the real desktop, a frozen build redirects ``sys.executable`` to that
sibling worker so every existing ``sys.executable -m ...`` child launch reaches the
strict internal dispatcher rather than recursively opening another desktop window.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class PackagedTarget(StrEnum):
    DESKTOP = "desktop"
    CORE = "core"
    ATHENA_CLI = "athena-cli"
    JOBS_CLI = "jobs-cli"
    HARDWARE_ACCEPTANCE = "hardware-acceptance"


class PackagedInvocationError(ValueError):
    """Raised when a packaged executable receives an unsupported module dispatch."""


@dataclass(frozen=True, slots=True)
class PackagedInvocation:
    target: PackagedTarget
    arguments: tuple[str, ...]


_MODULE_TARGETS = {
    "athena.api.process": PackagedTarget.CORE,
    "athena": PackagedTarget.ATHENA_CLI,
    "athena.desktop.jobs_cli": PackagedTarget.JOBS_CLI,
    "athena.hardware_acceptance": PackagedTarget.HARDWARE_ACCEPTANCE,
}

_WORKER_NAME = "pATHENA-Worker.exe"
_PACKAGED_DESKTOP_ENV = "PATHENA_PACKAGED_DESKTOP_EXECUTABLE"


def route_packaged_argv(argv: Sequence[str]) -> PackagedInvocation:
    """Resolve a desktop/internal invocation and fail closed for unknown modules."""
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


def packaged_worker_path(executable: str) -> Path:
    """Return the required sibling worker without depending on the current directory."""
    return Path(executable).resolve(strict=False).with_name(_WORKER_NAME)


def prepare_frozen_desktop_runtime(
    *,
    executable: str | None = None,
    frozen: bool | None = None,
) -> Path | None:
    """Bind child launches to the sibling worker or fail before opening the desktop."""
    runtime_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
    if not runtime_frozen:
        return None

    desktop_executable = str(Path(executable or sys.executable).resolve(strict=False))
    worker = packaged_worker_path(desktop_executable)
    if not worker.is_file():
        raise PackagedInvocationError(
            f"Supported Windows package is incomplete: missing {worker.name}."
        )

    os.environ[_PACKAGED_DESKTOP_ENV] = desktop_executable
    sys.executable = str(worker)
    return worker


def dispatch(argv: Sequence[str] | None = None) -> int:
    """Start only the desktop; internal module roles belong to the worker executable."""
    raw_arguments = tuple(sys.argv[1:] if argv is None else argv)
    try:
        invocation = route_packaged_argv(raw_arguments)
        if invocation.target is not PackagedTarget.DESKTOP:
            raise PackagedInvocationError(
                "Internal module dispatch is allowed only through pATHENA-Worker.exe."
            )
        prepare_frozen_desktop_runtime()
    except PackagedInvocationError:
        # ``--windowed`` builds intentionally have no reliable stderr stream.
        return 2

    from athena.desktop.app import main as desktop_main

    # QApplication expects argv[0] to remain the user-facing desktop identity.
    return desktop_main((sys.argv[0], *invocation.arguments))


def main(argv: Sequence[str] | None = None) -> int:
    return dispatch(argv)


if __name__ == "__main__":
    raise SystemExit(main())
