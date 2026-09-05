"""PyInstaller entry point for the pATHENA Windows test executable.

This file is packaging-only. The frozen executable doubles as the desktop shell
and as the two child-process roles already launched by the desktop supervisors.
"""

from __future__ import annotations

import multiprocessing
import os
import sys
from collections.abc import Sequence

_BUILD_SOURCE_SHA = "415debaae20fd84cd12fa0613dc063dc48dd134f"


def _run_core(arguments: Sequence[str]) -> int:
    from athena.api.process import main as core_main

    return core_main(arguments)


def _run_cli(arguments: Sequence[str]) -> int:
    from athena.__main__ import main as cli_main

    return cli_main(arguments)


def _run_desktop_smoke() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import QTimer

    from athena.desktop.app import create_application

    app = create_application([sys.argv[0]])
    QTimer.singleShot(150, app.quit)
    return app.exec()


def main() -> int:
    multiprocessing.freeze_support()
    arguments = sys.argv[1:]

    if arguments[:2] == ["-m", "athena.api.process"]:
        return _run_core(arguments[2:])
    if arguments[:2] == ["-m", "athena"]:
        return _run_cli(arguments[2:])
    if arguments == ["--pathena-build-info"]:
        print(f"pATHENA Windows test build from {_BUILD_SOURCE_SHA}")
        return 0
    if arguments == ["--pathena-desktop-smoke"]:
        return _run_desktop_smoke()

    from athena.desktop.app import main as desktop_main

    return desktop_main(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
