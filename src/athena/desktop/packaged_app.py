"""Windows packaged entry point for the pATHENA desktop preview build.

The normal desktop supervisor launches the Core through ``python -m``.  A
PyInstaller executable is not a general Python interpreter, so packaged builds
launch the sibling ``pATHENA-Core.exe`` instead.  This module is intentionally
packaging-only and leaves the normal development runtime unchanged.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

import athena.desktop.supervisor as supervisor_module
from athena.desktop.supervisor import CoreProcessLaunchSpec


def _packaged_core_process_launch_spec(
    *,
    executable: str | None = None,
    base_executable: str | None = None,
    platform: str | None = None,
) -> CoreProcessLaunchSpec:
    del executable, base_executable, platform
    core_executable = Path(sys.executable).resolve().with_name("pATHENA-Core.exe")
    if not core_executable.is_file():
        raise RuntimeError(
            "pATHENA-Core.exe is missing. Keep pATHENA.exe and pATHENA-Core.exe "
            "in the same folder."
        )
    return CoreProcessLaunchSpec(program=str(core_executable), arguments=())


def main(argv: Sequence[str] | None = None) -> int:
    supervisor_module.core_process_launch_spec = _packaged_core_process_launch_spec

    from athena.desktop.app import main as desktop_main

    return desktop_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
