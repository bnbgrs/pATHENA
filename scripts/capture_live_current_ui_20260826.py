from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_OPENGL", "software")

from PySide6.QtCore import QCoreApplication, QTimer
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication, QMainWindow

from athena.desktop import app as desktop_app

SOURCE_SHA = "5b1438e585b1e6d758132e1d5df3adad68a49adf"
OUT = Path(os.environ.get("PATHENA_SCREENSHOT_DIR", "screenshots-current-live"))
OUT.mkdir(parents=True, exist_ok=True)


def _register_windows_fonts(app: QApplication) -> None:
    font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = [
        "segoeui.ttf", "segoeuib.ttf", "seguisb.ttf", "segoeuil.ttf",
        "georgia.ttf", "georgiab.ttf", "times.ttf", "timesbd.ttf",
        "consola.ttf", "consolab.ttf", "arial.ttf", "arialbd.ttf",
    ]
    loaded: list[str] = []
    for filename in candidates:
        path = font_dir / filename
        if not path.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id >= 0:
            loaded.extend(QFontDatabase.applicationFontFamilies(font_id))
    app.setFont(QFont("Segoe UI", 10))
    current = app.styleSheet()
    app.setStyleSheet("")
    app.setStyleSheet(current)
    print("registered font families:", sorted(set(loaded)))
    print("application font:", app.font().family())


def _flush(app: QApplication) -> None:
    for _ in range(12):
        app.processEvents()
        QCoreApplication.sendPostedEvents()


def _find_main_window(app: QApplication) -> QMainWindow:
    windows = [w for w in app.topLevelWidgets() if isinstance(w, QMainWindow) and w.isVisible()]
    if len(windows) != 1:
        raise RuntimeError(f"Expected one visible QMainWindow, found {len(windows)}")
    return windows[0]


def _capture_all(app: QApplication) -> None:
    window = _find_main_window(app)
    window.resize(1480, 900)
    _flush(app)
    navigation = getattr(window, "navigation")
    pages = getattr(window, "pages")
    logical_names = ["chat", "knowledge", "research", "jobs", "files", "system", "settings"]
    captures = []
    for row, name in enumerate(logical_names):
        navigation.setCurrentRow(row)
        _flush(app)
        path = OUT / f"{row + 1:02d}-{name}.png"
        image = window.grab()
        if not image.save(str(path), "PNG"):
            raise RuntimeError(f"Could not save {path}")
        captures.append({"file": path.name, "row": row, "page_index": pages.currentIndex(), "width": image.width(), "height": image.height()})
        print("saved", path, image.width(), image.height())
    manifest = {
        "source_branch": "bot/pathena-candidate",
        "source_commit": SOURCE_SHA,
        "capture_branch": "capture/current-ui-20260826-1737",
        "platform": "Windows GitHub Actions / Qt offscreen software renderer",
        "real_application_main": True,
        "font_registration": True,
        "application_font": app.font().family(),
        "captures": captures,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    app.quit()


def main() -> int:
    app = desktop_app.create_application(["pathena-current-live-capture"])
    _register_windows_fonts(app)
    QTimer.singleShot(12000, lambda: _capture_all(app))
    return desktop_app.main(["pathena-current-live-capture"])


if __name__ == "__main__":
    raise SystemExit(main())

# Trigger push after workflow exists on this isolated branch.
