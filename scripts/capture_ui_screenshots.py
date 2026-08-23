"""Capture eight real Qt screenshots from the current pATHENA desktop code.

This is CI-only validation tooling. It does not replace or mock application widgets:
the same QApplication, PathenaMainWindow, workspace installers, supervisors and
stylesheet used by the desktop entry point are instantiated offscreen.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter, QPixmap

from athena.api.client import CoreApiClient
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.app import create_application
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
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.scheduler_supervisor import DesktopJobSchedulerSupervisor
from athena.desktop.supervisor import DesktopCoreSupervisor
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


def _pump(app: object, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.04)
    app.processEvents()


def _save_window(window: PathenaMainWindow, output: Path, filename: str) -> None:
    pixmap = window.grab()
    target = output / filename
    if not pixmap.save(str(target), "PNG"):
        raise RuntimeError(f"Unable to save screenshot: {target}")


def _save_with_overlay(
    window: PathenaMainWindow,
    overlay: object,
    output: Path,
    filename: str,
) -> None:
    base = window.grab()
    overlay_pixmap = overlay.grab()
    composite = QPixmap(base.size())
    composite.fill()
    painter = QPainter(composite)
    painter.drawPixmap(QPoint(0, 0), base)
    x = max(0, (base.width() - overlay_pixmap.width()) // 2)
    y = max(38, (base.height() - overlay_pixmap.height()) // 3)
    painter.drawPixmap(QPoint(x, y), overlay_pixmap)
    painter.end()
    target = output / filename
    if not composite.save(str(target), "PNG"):
        raise RuntimeError(f"Unable to save screenshot: {target}")


def _import_real_sample_source(sample: Path) -> None:
    sample.write_text(
        "pATHENA screenshot validation source.\n"
        "This temporary local source exists only inside the CI runtime and is used "
        "to exercise the real Source capture and retrieval-readiness workflow.\n",
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, "-m", "athena.desktop.sources_cli", "import", str(sample)],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    print("SOURCE IMPORT EXIT", completed.returncode)
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)


def main() -> int:
    output = Path(os.environ.get("PATHENA_SCREENSHOT_DIR", "ui-screenshots")).resolve()
    output.mkdir(parents=True, exist_ok=True)

    app = create_application(["pATHENA-screenshot-capture"])
    client = CoreApiClient.from_environment()
    supervisor = DesktopCoreSupervisor(client=client, parent=app)
    scheduler_supervisor = DesktopJobSchedulerSupervisor(parent=app)
    supervisor.ensure_running()
    scheduler_supervisor.ensure_running()

    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)
    knowledge_workspace = install_knowledge_workspace(window, controller)
    knowledge_acceptance = install_knowledge_acceptance(knowledge_workspace, controller)
    apply_knowledge_acceptance_presentation(knowledge_acceptance)
    canonical_memory_extensions = install_canonical_memory_extensions(knowledge_workspace)
    research_workspace = install_research_workspace(window)
    research_results_extension = install_research_results_extension(research_workspace)
    apply_research_result_presentation(research_results_extension)
    research_results_extension.refresh_timer.stop()
    jobs_workspace = install_jobs_workspace(window, scheduler_supervisor)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    system_backup = install_system_backup(window, system_workspace)
    apply_shell_density(window)
    apply_workspace_presentation(window)
    apply_quiet_workspace_refinement(window)
    command_palette = install_command_palette(window)

    window.show()
    _pump(app, 0.35)

    # 01: genuine first visible frame after the same application construction path.
    window.navigation.setCurrentRow(0)
    _pump(app, 0.15)
    _save_window(window, output, "01-start-chat.png")

    # Allow the real Core/scheduler supervision and initial workspace refreshes to settle.
    controller.refresh()
    _pump(app, 4.0)

    # 02: real command palette rendered over the live chat shell.
    command_palette.open()
    _pump(app, 0.25)
    _save_with_overlay(window, command_palette.dialog, output, "02-command-palette.png")
    command_palette.dialog.hide()

    # 03: canonical Knowledge browser with its real list/detail split and tabs.
    window.navigation.setCurrentRow(1)
    knowledge_workspace.refresh_knowledge()
    _pump(app, 1.2)
    _save_window(window, output, "03-knowledge-details.png")

    # 04: exercise the real durable research enqueue path, then show its detail split.
    window.navigation.setCurrentRow(2)
    research_workspace.query_input.setText(
        "How does pATHENA preserve evidence and provenance across local knowledge?"
    )
    research_workspace.enqueue()
    _pump(app, 2.2)
    _save_window(window, output, "04-research-job-details.png")

    # 05: the research enqueue above creates canonical durable work visible in Jobs.
    window.navigation.setCurrentRow(3)
    jobs_workspace.refresh()
    _pump(app, 1.6)
    _save_window(window, output, "05-jobs-details.png")

    # 06: import a real temporary text source through the canonical CLI, then render Files.
    sample = output / "capture-source.txt"
    _import_real_sample_source(sample)
    window.navigation.setCurrentRow(4)
    files_workspace.refresh()
    _pump(app, 1.8)
    _save_window(window, output, "06-files-source-details.png")

    # 07: live Core/provider/model/chat metrics from the real controller snapshot.
    window.navigation.setCurrentRow(5)
    controller.refresh()
    _pump(app, 1.0)
    _save_window(window, output, "07-system-runtime-details.png")

    # 08: actual per-model inference controls from the pATHENA Settings workspace.
    window.navigation.setCurrentRow(6)
    _pump(app, 0.35)
    _save_window(window, output, "08-settings-details.png")

    window.close()
    scheduler_supervisor.stop()
    supervisor.stop()
    _pump(app, 0.25)

    canonical_memory_extensions.deleteLater()
    knowledge_acceptance.deleteLater()
    knowledge_workspace.deleteLater()
    research_results_extension.deleteLater()
    research_workspace.deleteLater()
    jobs_workspace.deleteLater()
    files_workspace.deleteLater()
    system_backup.deleteLater()
    system_workspace.deleteLater()
    command_palette.deleteLater()

    print(f"Captured 8 screenshots in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
