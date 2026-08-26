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

OUT = Path(os.environ.get("PATHENA_SCREENSHOT_DIR", "screenshots-current-live"))
OUT.mkdir(parents=True, exist_ok=True)
PRODUCT_SHA = os.environ.get("PATHENA_PRODUCT_SHA", "unknown")
FONT_REPORT: dict[str, object] = {}


def _flush(app: QApplication, rounds: int = 12) -> None:
    for _ in range(rounds):
        app.processEvents()
        QCoreApplication.sendPostedEvents()


def _register_fonts_and_normalize_qss(app: QApplication) -> None:
    windows_dir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    font_dir = windows_dir / "Fonts"
    candidates = [
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
    ]
    loaded: dict[str, list[str]] = {}
    for filename in candidates:
        path = font_dir / filename
        if not path.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        families = list(QFontDatabase.applicationFontFamilies(font_id)) if font_id >= 0 else []
        loaded[filename] = families

    families = set(QFontDatabase.families())
    content = "Segoe UI" if "Segoe UI" in families else ("Arial" if "Arial" in families else app.font().family())
    display = "Georgia" if "Georgia" in families else ("Times New Roman" if "Times New Roman" in families else content)
    mono = "Consolas" if "Consolas" in families else content

    css = app.styleSheet()
    replacements = {
        '"Segoe UI Variable", "Segoe UI", sans-serif': f'"{content}"',
        '"Georgia", "Times New Roman", serif': f'"{display}"',
        '"Cascadia Mono", "Consolas", monospace': f'"{mono}"',
    }
    for old, new in replacements.items():
        css = css.replace(old, new)
    app.setStyleSheet(css)
    app.setFont(QFont(content, 10))

    FONT_REPORT.update(
        {
            "font_dir": str(font_dir),
            "loaded": loaded,
            "content_family": content,
            "display_family": display,
            "mono_family": mono,
        }
    )


def _largest_main_window(app: QApplication) -> QMainWindow:
    windows = [
        widget
        for widget in app.topLevelWidgets()
        if isinstance(widget, QMainWindow) and widget.isVisible()
    ]
    if not windows:
        raise RuntimeError("No visible pATHENA QMainWindow found")
    return max(windows, key=lambda window: window.width() * window.height())


def main() -> int:
    app = desktop_app.create_application(["pATHENA-live-current-capture"])
    _register_fonts_and_normalize_qss(app)
    capture_error: list[str] = []

    def capture() -> None:
        try:
            window = _largest_main_window(app)
            window.resize(1480, 900)
            window.show()
            _flush(app)

            navigation = getattr(window, "navigation", None)
            pages = getattr(window, "pages", None)
            if navigation is None or pages is None:
                raise RuntimeError("Current pATHENA navigation contract unavailable")

            names = ["chat", "knowledge", "research", "jobs", "files", "system", "settings"]
            files: list[str] = []
            for index, name in enumerate(names):
                if index >= navigation.count():
                    break
                navigation.setCurrentRow(index)
                _flush(app)
                path = OUT / f"{index + 1:02d}-{name}.png"
                image = window.grab()
                if not image.save(str(path), "PNG"):
                    raise RuntimeError(f"Could not save {path}")
                files.append(path.name)

            manifest = {
                "product_sha": PRODUCT_SHA,
                "capture_branch": os.environ.get("GITHUB_REF_NAME", "local"),
                "platform": os.name,
                "qt_platform": os.environ.get("QT_QPA_PLATFORM"),
                "real_program_started": True,
                "mockup": False,
                "window_size": [window.width(), window.height()],
                "navigation_count": navigation.count(),
                "page_count": pages.count(),
                "font_report": FONT_REPORT,
                "files": files,
                "capture_errors": capture_error,
            }
            (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            capture_error.append(f"{type(exc).__name__}: {exc}")
            (OUT / "capture-error.txt").write_text("\n".join(capture_error), encoding="utf-8")
        finally:
            app.quit()

    def timeout() -> None:
        capture_error.append("TimeoutError: pATHENA did not become capturable within 35 seconds")
        (OUT / "capture-error.txt").write_text("\n".join(capture_error), encoding="utf-8")
        app.quit()

    QTimer.singleShot(12_000, capture)
    QTimer.singleShot(35_000, timeout)
    return desktop_app.main(["pATHENA-live-current-capture"])


if __name__ == "__main__":
    raise SystemExit(main())
