"""PyInstaller entry point for the pATHENA Windows test executable.

This file is packaging-only. The frozen executable doubles as the desktop shell
and as the child-process roles already launched by the desktop supervisors.
"""

from __future__ import annotations

import multiprocessing
import os
import sys
from collections.abc import Sequence
from importlib.metadata import version

_BUILD_SOURCE_SHA = "e639ed59cc449738c74bf550503282f7f2df9d4b"
_EXPECTED_PYPDF_VERSION = "6.12.2"


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


def _run_import_smoke() -> int:
    """Prove frozen distribution metadata and deep application imports are present."""
    installed_pypdf = version("pypdf")
    if installed_pypdf != _EXPECTED_PYPDF_VERSION:
        raise RuntimeError(
            "Frozen pypdf metadata mismatch: "
            f"expected {_EXPECTED_PYPDF_VERSION}, got {installed_pypdf}."
        )

    from athena.core.application import AthenaApplication
    from athena.source.pdf_representation_service import SourcePdfRepresentationService

    if AthenaApplication is None or SourcePdfRepresentationService is None:
        raise RuntimeError("Frozen pATHENA application imports are incomplete.")
    return 0


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
    if arguments == ["--pathena-import-smoke"]:
        return _run_import_smoke()
    if arguments == ["--pathena-desktop-smoke"]:
        return _run_desktop_smoke()

    from athena.desktop.app import main as desktop_main

    return desktop_main(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
