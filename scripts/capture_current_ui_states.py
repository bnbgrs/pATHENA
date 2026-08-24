from __future__ import annotations

import os
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
from athena.desktop.pathena_interaction_refinement import install_interaction_refinement
from athena.desktop.pathena_jobs_experience_2800 import install_jobs_experience
from athena.desktop.pathena_knowledge_acceptance_presentation import (
    apply_knowledge_acceptance_presentation,
)
from athena.desktop.pathena_layout_refinement_2200 import install_layout_refinement
from athena.desktop.pathena_progressive_workspace_2300 import (
    install_progressive_workspace_refinement,
)
from athena.desktop.pathena_research_experience_2500 import install_research_experience
from athena.desktop.pathena_research_knowledge_transition_2700 import (
    install_research_knowledge_transition,
)
from athena.desktop.pathena_research_proposal_clarity_2600 import (
    install_research_proposal_clarity,
)
from athena.desktop.pathena_research_readability_2400 import install_research_readability
from athena.desktop.pathena_research_result_presentation import (
    apply_research_result_presentation,
)
from athena.desktop.pathena_shell_density import apply_shell_density
from athena.desktop.pathena_startup_experience_2900 import install_startup_experience
from athena.desktop.pathena_ui_refinement_integrity import apply_complete_ui_refinements
from athena.desktop.pathena_window import PathenaMainWindow
from athena.desktop.pathena_workspace_presentation import apply_workspace_presentation
from athena.desktop.research_results_extension import install_research_results_extension
from athena.desktop.research_workspace import install_research_workspace
from athena.desktop.system_backup import install_system_backup
from athena.desktop.system_workspace import install_system_workspace


def _pump(app: object, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.04)
    app.processEvents()


def _save(window: PathenaMainWindow, output: Path, filename: str) -> None:
    target = output / filename
    pixmap = window.grab()
    if not pixmap.save(str(target), "PNG"):
        raise RuntimeError(f"Unable to save screenshot: {target}")
    print(target.resolve())


def _save_with_overlay(
    window: PathenaMainWindow,
    overlay: object,
    output: Path,
    filename: str,
) -> None:
    base = window.grab()
    popup = overlay.grab()
    composite = QPixmap(base.size())
    composite.fill()
    painter = QPainter(composite)
    painter.drawPixmap(QPoint(0, 0), base)
    x = max(0, (base.width() - popup.width()) // 2)
    y = max(36, (base.height() - popup.height()) // 3)
    painter.drawPixmap(QPoint(x, y), popup)
    painter.end()
    target = output / filename
    if not composite.save(str(target), "PNG"):
        raise RuntimeError(f"Unable to save screenshot: {target}")
    print(target.resolve())


def build_window() -> tuple[PathenaMainWindow, object]:
    client = CoreApiClient.from_environment()
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

    jobs_workspace = install_jobs_workspace(window, None)
    files_workspace = install_files_workspace(window)
    system_workspace = install_system_workspace(window, controller)
    system_backup = install_system_backup(window, system_workspace)

    apply_shell_density(window)
    apply_workspace_presentation(window)
    command_palette = install_command_palette(window)

    jobs_experience = install_jobs_experience(jobs_workspace)
    startup_experience = install_startup_experience(window)
    apply_complete_ui_refinements(window)
    interaction_refinement = install_interaction_refinement(window)
    layout_refinement = install_layout_refinement(window)
    progressive_workspace = install_progressive_workspace_refinement(window)
    research_readability = install_research_readability(
        window, research_results_extension
    )
    research_experience = install_research_experience(
        research_workspace, research_results_extension
    )
    research_proposal_clarity = install_research_proposal_clarity(
        research_results_extension
    )
    research_transition = install_research_knowledge_transition(
        window, research_results_extension
    )

    window._capture_refs = (  # type: ignore[attr-defined]
        controller,
        knowledge_workspace,
        knowledge_acceptance,
        canonical_memory_extensions,
        research_workspace,
        research_results_extension,
        jobs_workspace,
        jobs_experience,
        startup_experience,
        files_workspace,
        system_workspace,
        system_backup,
        command_palette,
        interaction_refinement,
        layout_refinement,
        progressive_workspace,
        research_readability,
        research_experience,
        research_proposal_clarity,
        research_transition,
    )
    return window, command_palette


def main() -> int:
    output = Path(
        os.environ.get("PATHENA_UI_CAPTURE_DIR", "artifacts/current-ui-states")
    ).resolve()
    output.mkdir(parents=True, exist_ok=True)

    app = create_application(["pathena-current-ui-capture"])
    window, command_palette = build_window()
    window.resize(1480, 900)
    window.show()
    _pump(app, 1.0)

    # These are direct grabs of the actual current Qt widget tree. No mock UI is used.
    window.navigation.setCurrentRow(0)
    _pump(app, 0.35)
    _save(window, output, "01-chat-start.png")

    command_palette.open()
    _pump(app, 0.25)
    _save_with_overlay(
        window,
        command_palette.dialog,
        output,
        "02-command-palette.png",
    )
    command_palette.dialog.hide()

    states = (
        (1, "03-knowledge.png"),
        (2, "04-research.png"),
        (3, "05-jobs.png"),
        (4, "06-files.png"),
        (5, "07-system.png"),
        (6, "08-settings.png"),
    )
    for row, filename in states:
        window.navigation.setCurrentRow(row)
        _pump(app, 0.55)
        _save(window, output, filename)

    window.close()
    _pump(app, 0.2)

    files = sorted(output.glob("*.png"))
    if len(files) != 8:
        raise RuntimeError(f"Expected 8 screenshots, found {len(files)}")
    print(f"Captured {len(files)} current code-based pATHENA screenshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
