from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase

from athena.desktop import app as desktop_app

_ORIGINAL_CREATE_APPLICATION = desktop_app.create_application


def _create_application_fontsafe(argv: list[str] | None = None):
    app = _ORIGINAL_CREATE_APPLICATION(argv)
    font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = (
        "segoeui.ttf",
        "segoeuib.ttf",
        "seguisb.ttf",
        "segoeuil.ttf",
        "seguisym.ttf",
        "georgia.ttf",
        "georgiab.ttf",
        "times.ttf",
        "timesbd.ttf",
        "consola.ttf",
        "consolab.ttf",
        "arial.ttf",
        "arialbd.ttf",
    )
    loaded: list[str] = []
    for filename in candidates:
        path = font_dir / filename
        if not path.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id >= 0:
            loaded.extend(QFontDatabase.applicationFontFamilies(font_id))

    available = set(QFontDatabase.families())
    content = "Segoe UI" if "Segoe UI" in available else ("Arial" if "Arial" in available else app.font().family())
    display = "Georgia" if "Georgia" in available else ("Times New Roman" if "Times New Roman" in available else content)
    mono = "Consolas" if "Consolas" in available else content

    css = app.styleSheet()
    replacements = {
        '"Segoe UI Variable", "Segoe UI", sans-serif': f'"{content}"',
        '"Georgia", "Times New Roman", serif': f'"{display}"',
        '"Cascadia Mono", "Consolas", monospace': f'"{mono}"',
    }
    for old, new in replacements.items():
        css = css.replace(old, new)
    app.setStyleSheet("")
    app.setFont(QFont(content, 10))
    app.setStyleSheet(css)
    print("font families loaded:", sorted(set(loaded)))
    print("resolved fonts:", content, display, mono)
    return app


def main() -> int:
    desktop_app.create_application = _create_application_fontsafe
    runtime_root = Path(os.environ["RUNNER_TEMP"]) / "pathena-current-runtime"
    screenshot_root = Path.cwd() / "artifacts" / "current-ui"
    sys.argv = [
        "render_pathena_ui_snapshot.py",
        "--runtime-root",
        str(runtime_root),
        "--screenshot-directory",
        str(screenshot_root),
        "--initial-delay-seconds",
        "7",
    ]
    try:
        runpy.run_path("scripts/render_pathena_ui_snapshot.py", run_name="__main__")
    finally:
        desktop_app.create_application = _ORIGINAL_CREATE_APPLICATION
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
