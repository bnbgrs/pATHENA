from __future__ import annotations

import os
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_OPENGL", "software")

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


def _prepare_application() -> QApplication:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(["pathena-fontsafe-visual-capture"])

    font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = (
        "segoeui.ttf",
        "segoeuib.ttf",
        "seguisb.ttf",
        "seguisym.ttf",
        "arial.ttf",
        "arialbd.ttf",
        "georgia.ttf",
        "georgiab.ttf",
        "times.ttf",
        "timesbd.ttf",
        "consola.ttf",
        "consolab.ttf",
    )
    for filename in candidates:
        path = font_dir / filename
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))

    families = set(QFontDatabase.families())
    content = (
        "Segoe UI"
        if "Segoe UI" in families
        else ("Arial" if "Arial" in families else app.font().family())
    )
    display = (
        "Georgia"
        if "Georgia" in families
        else ("Times New Roman" if "Times New Roman" in families else content)
    )
    mono = "Consolas" if "Consolas" in families else content

    from athena.desktop.pathena_theme import PATHENA_STYLESHEET

    stylesheet = PATHENA_STYLESHEET
    stylesheet = stylesheet.replace(
        '"Segoe UI Variable", "Segoe UI", sans-serif', f'"{content}"'
    )
    stylesheet = stylesheet.replace(
        '"Georgia", "Times New Roman", serif', f'"{display}"'
    )
    stylesheet = stylesheet.replace(
        '"Cascadia Mono", "Consolas", monospace', f'"{mono}"'
    )
    app.setApplicationName("ATHENA")
    app.setOrganizationName("ATHENA")
    app.setApplicationDisplayName("pATHENA")
    app.setFont(QFont(content, 10))
    app.setStyleSheet(stylesheet)
    print(
        f"font-safe capture families: content={content!r}, "
        f"display={display!r}, mono={mono!r}"
    )
    return app


def _screenshot_directory(argv: Sequence[str]) -> Path | None:
    try:
        index = argv.index("--screenshot-directory")
    except ValueError:
        return None
    if index + 1 >= len(argv):
        return None
    return Path(argv[index + 1]).resolve()


def _write_capture_failure(argv: Sequence[str], exc: Exception) -> None:
    directory = _screenshot_directory(argv)
    if directory is None:
        return
    directory.mkdir(parents=True, exist_ok=True)
    report = directory / "capture-wrapper-error.txt"
    report.write_text(
        f"{type(exc).__name__}: {exc}\n\n{traceback.format_exc()}",
        encoding="utf-8",
    )


def main() -> int:
    _prepare_application()
    from scripts.render_pathena_ui_snapshot import main as render_main

    argv = sys.argv[1:]
    try:
        return render_main(argv)
    except Exception as exc:
        _write_capture_failure(argv, exc)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
