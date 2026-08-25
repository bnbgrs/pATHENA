"""Temporary screenshot harness for the current pATHENA Qt UI.

This script is intentionally presentation-only: it instantiates the current desktop
shell without starting Core, Scheduler, workers, or model generation.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_OPENGL", "software")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from athena.api.client import CoreApiClient
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.canonical_memory_extensions import install_canonical_memory_extensions
from athena.desktop.command_palette import install_command_palette
from athena.desktop.files_workspace import install_files_workspace
from athena.desktop.jobs_workspace import install_jobs_workspace
from athena.desktop.knowledge_acceptance import install_knowledge_acceptance
from athena.desktop.knowledge_workspace import install_knowledge_workspace
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_quiet_workspace import apply_quiet_workspace_refinement
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


OUT = Path(os.environ.get("PATHENA_SCREENSHOT_DIR", "screenshots-current"))
OUT.mkdir(parents=True, exist_ok=True)


def _flush(app: QApplication) -> None:
    for _ in range(6):
        app.processEvents()
        QCoreApplication.sendPostedEvents()


def _save(window: PathenaMainWindow, app: QApplication, name: str) -> None:
    _flush(app)
    image = window.grab()
    path = OUT / f"{name}.png"
    if not image.save(str(path), "PNG"):
        raise RuntimeError(f"Could not save {path}")
    print(f"saved {path} {image.width()}x{image.height()}")


def main() -> int:
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        app = QApplication(sys.argv)
    app.setApplicationName("pATHENA Screenshot Capture")
    app.setOrganizationName("pATHENA")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(PATHENA_STYLESHEET)

    client = CoreApiClient.from_environment()
    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)

    installed: list[object] = []

    knowledge_workspace = install_knowledge_workspace(window, controller)
    installed.append(knowledge_workspace)
    knowledge_acceptance = install_knowledge_acceptance(knowledge_workspace, controller)
    installed.append(knowledge_acceptance)
    apply_knowledge_acceptance_presentation(knowledge_acceptance)
    installed.append(install_canonical_memory_extensions(knowledge_workspace))

    research_workspace = install_research_workspace(window)
    installed.append(research_workspace)
    research_results_extension = install_research_results_extension(research_workspace)
    installed.append(research_results_extension)
    apply_research_result_presentation(research_results_extension)
    if hasattr(research_results_extension, "refresh_timer"):
        research_results_extension.refresh_timer.stop()

    installed.append(install_jobs_workspace(window, None))
    installed.append(install_files_workspace(window))
    system_workspace = install_system_workspace(window, controller)
    installed.append(system_workspace)
    installed.append(install_system_backup(window, system_workspace))

    apply_shell_density(window)
    apply_workspace_presentation(window)
    apply_quiet_workspace_refinement(window)
    command_palette = install_command_palette(window)
    installed.append(command_palette)

    if hasattr(window, "refresh_timer"):
        window.refresh_timer.stop()

    window.resize(1480, 900)
    window.show()
    _flush(app)

    page_names = ["chat", "knowledge", "research", "jobs", "files", "system", "settings"]
    for index, name in enumerate(page_names):
        window.navigation.setCurrentRow(index)
        _flush(app)
        _save(window, app, f"01-page-{index+1:02d}-{name}")

    # Settings variants: capture the actual widgets in several realistic states.
    window.navigation.setCurrentRow(6)
    _flush(app)

    window.context_spin.setValue(32768)
    window.max_output_spin.setValue(4096)
    window.temperature_spin.setValue(0.20)
    window.thinking_checkbox.setChecked(False)
    _save(window, app, "02-settings-balanced-direct")

    window.context_spin.setValue(65536)
    window.max_output_spin.setValue(8192)
    window.temperature_spin.setValue(0.70)
    window.thinking_checkbox.setChecked(True)
    _save(window, app, "03-settings-reasoning-medium")

    window.context_spin.setValue(131072)
    window.max_output_spin.setValue(16384)
    window.temperature_spin.setValue(1.00)
    window.thinking_checkbox.setChecked(True)
    _save(window, app, "04-settings-long-context")

    # Return to Chat and capture progressive disclosure / command palette where available.
    window.navigation.setCurrentRow(0)
    _flush(app)
    details = getattr(window, "details_button", None)
    if details is not None:
        details.setVisible(True)
        details.setChecked(True)
        _save(window, app, "05-chat-details-open")
        details.setChecked(False)

    # Open the real command palette via its public-ish installed widget/action path when possible.
    opened = False
    for method_name in ("show_palette", "open", "show"):
        method = getattr(command_palette, method_name, None)
        if callable(method):
            try:
                method()
                opened = True
                break
            except TypeError:
                pass
    if opened:
        _save(window, app, "06-command-palette")

    manifest = {
        "branch": "agent/pathena",
        "source_commit": "fbbf44dc8c8175499528f07be079061b644d1604",
        "capture_branch": "capture/current-ui-20260825",
        "pages": page_names,
        "note": "UI instantiated without Core/Scheduler/workers; screenshots are real Qt renders from current source.",
        "files": sorted(path.name for path in OUT.glob("*.png")),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    window.close()
    for obj in reversed(installed):
        delete_later = getattr(obj, "deleteLater", None)
        if callable(delete_later):
            delete_later()
    _flush(app)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
