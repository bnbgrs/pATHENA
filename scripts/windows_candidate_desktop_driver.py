"""Controlled native-Windows source launch for SHA-bound acceptance diagnostics."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Sequence
from pathlib import Path


def _safe_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or "screen"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--screenshot-directory", type=Path, required=True)
    parser.add_argument("--initial-delay-seconds", type=int, default=7)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if os.name != "nt":
        raise RuntimeError("This diagnostic is valid only on native Windows.")
    if args.initial_delay_seconds < 5:
        raise ValueError("The desktop needs at least five seconds before capture.")

    runtime_root = args.runtime_root.resolve()
    screenshot_directory = args.screenshot_directory.resolve()
    runtime_root.mkdir(parents=True, exist_ok=True)
    screenshot_directory.mkdir(parents=True, exist_ok=True)
    os.environ["ATHENA_LOCAL_ROOT"] = str(runtime_root)
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QMainWindow

    from athena.desktop.app import create_application
    from athena.desktop.app import main as desktop_main

    app = create_application(["pathena-windows-candidate-acceptance"])
    captures: list[dict[str, object]] = []
    errors: list[str] = []
    started = time.monotonic()

    def find_window() -> QMainWindow:
        windows = [
            widget
            for widget in app.topLevelWidgets()
            if isinstance(widget, QMainWindow) and widget.isVisible()
        ]
        if len(windows) != 1:
            raise RuntimeError(
                f"Expected exactly one visible main window, found {len(windows)}."
            )
        return windows[0]

    def capture_row(row: int) -> None:
        try:
            window = find_window()
            navigation = getattr(window, "navigation", None)
            pages = getattr(window, "pages", None)
            if navigation is None or pages is None:
                raise RuntimeError("Desktop navigation contract is unavailable.")
            if navigation.count() != 7 or pages.count() != 7:
                raise RuntimeError(
                    "Legacy candidate must expose its seven real navigation pages "
                    f"for this probe; found {navigation.count()} nav items and "
                    f"{pages.count()} pages."
                )
            navigation.setCurrentRow(row)
            app.processEvents()
            label = navigation.item(row).text()
            output = screenshot_directory / f"{row + 1:02d}-{_safe_name(label)}.png"
            if not window.grab().save(str(output), "PNG"):
                raise RuntimeError(f"Qt failed to save {output.name}.")
            captures.append(
                {
                    "row": row,
                    "label": label,
                    "page_index": pages.currentIndex(),
                    "file": output.name,
                    "width": window.width(),
                    "height": window.height(),
                }
            )
        except Exception as exc:  # noqa: BLE001 - callback must preserve evidence
            errors.append(f"row {row}: {type(exc).__name__}: {exc}")

    interval_ms = 500
    first_capture_ms = args.initial_delay_seconds * 1_000
    for row in range(7):
        QTimer.singleShot(
            first_capture_ms + row * interval_ms,
            lambda selected_row=row: capture_row(selected_row),
        )
    QTimer.singleShot(first_capture_ms + 7 * interval_ms + 500, app.quit)

    exit_code = desktop_main(["pathena-windows-candidate-acceptance"])
    duration_seconds = time.monotonic() - started
    manifest = {
        "candidate_sha": os.environ.get("CANDIDATE_SHA", ""),
        "platform": sys.platform,
        "status": "PASS" if not errors and len(captures) == 7 else "FAIL",
        "duration_seconds": round(duration_seconds, 3),
        "captures": captures,
        "errors": errors,
        "target_coverage": {
            "captured_legacy_pages": [
                "Chat",
                "Knowledge",
                "Research",
                "Jobs",
                "Files",
                "System",
                "Settings",
            ],
            "not_implemented_as_target_screens": [
                "ComfyUI",
                "Help",
                "interactive PALLAS",
                "standalone search/command palette reference state",
            ],
        },
    }
    (screenshot_directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    if exit_code != 0:
        raise RuntimeError(f"Desktop returned exit code {exit_code}.")
    if errors or len(captures) != 7:
        raise RuntimeError(
            "Desktop capture failed: " + "; ".join(errors or ["capture count mismatch"])
        )
    if duration_seconds < args.initial_delay_seconds:
        raise RuntimeError("Desktop exited before the controlled capture window.")

    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
