"""Temporary screenshot harness for the current pATHENA Qt UI.

The current desktop shell is really instantiated and rendered by Qt. Core,
Scheduler, workers and model generation are deliberately not started. A broken
nonvisual accessibility hook is isolated so it cannot prevent static UI capture.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_OPENGL", "software")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication

from athena.api.client import CoreApiClient
from athena.desktop import app as desktop_app
from athena.desktop.api_controller import DesktopApiController
from athena.desktop.pathena_window import PathenaMainWindow

OUT = Path(os.environ.get("PATHENA_SCREENSHOT_DIR", "screenshots-current"))
OUT.mkdir(parents=True, exist_ok=True)
SKIPPED_HOOKS: list[str] = []


def _flush(app: QApplication) -> None:
    for _ in range(10):
        app.processEvents()
        QCoreApplication.sendPostedEvents()


def _save(window: PathenaMainWindow, app: QApplication, name: str) -> None:
    _flush(app)
    image = window.grab()
    path = OUT / f"{name}.png"
    if not image.save(str(path), "PNG"):
        raise RuntimeError(f"Could not save {path}")
    print(f"saved {path} {image.width()}x{image.height()}")


def _delete_later(obj: object) -> None:
    method = getattr(obj, "deleteLater", None)
    if callable(method):
        method()


def _optional_hook(label: str, factory):
    try:
        return factory()
    except Exception as exc:
        SKIPPED_HOOKS.append(f"{label}: {type(exc).__name__}: {exc}")
        print(f"SKIPPED HOOK {label}: {type(exc).__name__}: {exc}")
        return None


def _register_windows_fonts(app: QApplication) -> None:
    """Make native Windows fonts explicit for Qt's headless/offscreen plugin."""
    windows_dir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    font_dir = windows_dir / "Fonts"
    candidates = [
        "segoeui.ttf",
        "segoeuib.ttf",
        "seguisb.ttf",
        "segoeuil.ttf",
        "arial.ttf",
        "arialbd.ttf",
        "consola.ttf",
        "consolab.ttf",
    ]
    loaded_families: list[str] = []
    for filename in candidates:
        path = font_dir / filename
        if not path.exists():
            print(f"font missing: {path}")
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        families = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
        loaded_families.extend(families)
        print(f"font load: {filename} id={font_id} families={list(families)}")
    if "Segoe UI" in QFontDatabase.families() or "Segoe UI" in loaded_families:
        app.setFont(QFont("Segoe UI", 10))
    elif "Arial" in QFontDatabase.families() or "Arial" in loaded_families:
        app.setFont(QFont("Arial", 10))
        app.setStyleSheet(app.styleSheet().replace('"Segoe UI", "Inter", sans-serif', '"Arial", sans-serif'))
    print(f"capture font family: {app.font().family()}")


def main() -> int:
    app = desktop_app.create_application(["pATHENA-screenshot-capture"])
    _register_windows_fonts(app)
    client = CoreApiClient.from_environment()
    controller = DesktopApiController(client)
    window = PathenaMainWindow(api_controller=controller)
    installed: list[object] = []

    knowledge_workspace = desktop_app.install_knowledge_workspace(window, controller)
    installed.append(knowledge_workspace)
    installed.append(desktop_app.install_knowledge_selection_continuity(knowledge_workspace))
    installed.append(desktop_app.install_knowledge_detail_ownership(knowledge_workspace))
    installed.append(desktop_app.install_knowledge_tab_refresh_handoff(knowledge_workspace))
    knowledge_acceptance = desktop_app.install_knowledge_acceptance(knowledge_workspace, controller)
    installed.append(knowledge_acceptance)
    desktop_app.apply_knowledge_acceptance_presentation(knowledge_acceptance)
    canonical_memory_extensions = desktop_app.install_canonical_memory_extensions(knowledge_workspace)
    installed.append(canonical_memory_extensions)

    research_workspace = desktop_app.install_research_workspace(window)
    installed.append(research_workspace)
    research_results_extension = desktop_app.install_research_results_extension(research_workspace)
    installed.append(research_results_extension)
    desktop_app.apply_research_result_presentation(research_results_extension)
    installed.append(desktop_app.install_research_proposal_density(research_results_extension))
    installed.append(desktop_app.install_research_proposal_focus(research_results_extension))
    research_results_extension.refresh_timer.stop()

    jobs_workspace = desktop_app.install_jobs_workspace(window, None)
    installed.append(jobs_workspace)
    files_workspace = desktop_app.install_files_workspace(window)
    installed.append(files_workspace)
    system_workspace = desktop_app.install_system_workspace(window, controller)
    installed.append(system_workspace)
    system_backup = desktop_app.install_system_backup(window, system_workspace)
    installed.append(system_backup)
    installed.append(desktop_app.install_backup_target_context(system_backup.backup))
    installed.append(desktop_app.install_backup_details_provenance(system_backup.backup))

    desktop_app.apply_shell_density(window)
    desktop_app.apply_workspace_presentation(window)
    desktop_app.install_navigation_context_accessibility(window)
    command_palette = desktop_app.install_command_palette(window)
    installed.append(command_palette)
    transient_dialog_shortcuts = desktop_app.install_transient_dialog_shortcut_continuity(command_palette)
    installed.append(transient_dialog_shortcuts)
    command_palette_truth = desktop_app.install_command_palette_truth(command_palette)
    installed.append(command_palette_truth)
    installed.append(
        desktop_app.install_empty_search_comprehension(
            window, command_palette, command_palette_truth, canonical_memory_extensions
        )
    )
    installed.append(desktop_app.install_dialog_focus_return(window))
    installed.append(desktop_app.install_jobs_experience(jobs_workspace))
    installed.append(desktop_app.install_startup_experience(window))
    desktop_app.apply_complete_ui_refinements(window)
    desktop_app.apply_ui_refinements_6101_6200(window)
    desktop_app.apply_result_scope_clarity(window)
    installed.append(desktop_app.apply_detail_provenance(window))
    installed.append(desktop_app.apply_quiet_success_decay(window))
    installed.append(desktop_app.install_chat_scroll_stability(window))
    desktop_app.apply_inspector_scanability(window)
    installed.append(desktop_app.install_backup_action_context(window))
    installed.append(desktop_app.install_backup_action_truth(system_backup.backup))
    installed.append(desktop_app.install_message_action_accessibility(window))
    installed.append(desktop_app.install_message_action_tab_order(window))
    installed.append(desktop_app.install_message_action_quiet(window))
    installed.append(desktop_app.install_interaction_refinement(window))
    installed.append(desktop_app.install_layout_refinement(window))
    installed.append(desktop_app.install_progressive_workspace_refinement(window))
    installed.append(desktop_app.install_research_readability(window, research_results_extension))
    installed.append(desktop_app.install_research_experience(research_workspace, research_results_extension))
    installed.append(desktop_app.install_research_proposal_clarity(research_results_extension))
    installed.append(desktop_app.install_research_knowledge_transition(window, research_results_extension))

    optional = _optional_hook(
        "background_completion_accessibility",
        lambda: desktop_app.install_background_completion_accessibility(
            files_workspace, jobs_workspace, system_backup.backup, research_results_extension
        ),
    )
    if optional is not None:
        installed.append(optional)
    optional = _optional_hook(
        "selection_disappearance_handoff",
        lambda: desktop_app.install_selection_disappearance_handoff(
            files_workspace,
            jobs_workspace,
            research_workspace,
            system_backup.backup,
            research_results_extension,
        ),
    )
    if optional is not None:
        installed.append(optional)
    _optional_hook(
        "primary_input_accessibility",
        lambda: desktop_app.install_primary_input_accessibility(
            window,
            chat_prompt=window.prompt_input,
            knowledge_filter=knowledge_workspace.search_input,
            research_query=research_workspace.query_input,
            research_filter=research_results_extension.job_filter,
        ),
    )

    if hasattr(window, "refresh_timer"):
        window.refresh_timer.stop()
    if hasattr(research_results_extension, "refresh_timer"):
        research_results_extension.refresh_timer.stop()

    window.resize(1480, 900)
    window.show()
    _flush(app)

    page_names = ["chat", "knowledge", "research", "jobs", "files", "system", "settings"]
    for index, name in enumerate(page_names):
        window.navigation.setCurrentRow(index)
        _save(window, app, f"01-page-{index+1:02d}-{name}")

    window.navigation.setCurrentRow(6)
    _flush(app)
    settings_states = [
        ("02-settings-default-offline", None, None, None, None),
        ("03-settings-compact-direct", 16384, 2048, 0.10, False),
        ("04-settings-balanced-direct", 32768, 4096, 0.20, False),
        ("05-settings-reasoning-medium", 65536, 8192, 0.70, True),
        ("06-settings-long-context", 131072, 16384, 1.00, True),
        ("07-settings-low-temperature-reasoning", 65536, 4096, 0.00, True),
    ]
    for name, context, output, temperature, thinking in settings_states:
        if context is not None:
            window.context_spin.setValue(context)
        if output is not None:
            window.max_output_spin.setValue(output)
        if temperature is not None:
            window.temperature_spin.setValue(temperature)
        if thinking is not None:
            window.thinking_checkbox.setChecked(thinking)
        _save(window, app, name)

    window.navigation.setCurrentRow(0)
    _flush(app)
    details = getattr(window, "details_button", None)
    if details is not None:
        details.setVisible(True)
        details.setChecked(True)
        _save(window, app, "08-chat-details-open")
        details.setChecked(False)

    palette_opened = False
    for candidate in (command_palette, getattr(command_palette, "palette", None)):
        if candidate is None:
            continue
        for method_name in ("show_palette", "open_palette", "open", "show"):
            method = getattr(candidate, method_name, None)
            if callable(method):
                try:
                    method()
                    palette_opened = True
                    break
                except TypeError:
                    continue
        if palette_opened:
            break
    if palette_opened:
        _save(window, app, "09-command-palette")

    manifest = {
        "source_branch": "agent/pathena",
        "source_commit": "fbbf44dc8c8175499528f07be079061b644d1604",
        "capture_branch": "capture/current-ui-run-20260825",
        "platform": "Windows GitHub Actions / Qt offscreen software renderer",
        "background_processes_started": False,
        "capture_font": app.font().family(),
        "skipped_hooks": SKIPPED_HOOKS,
        "pages": page_names,
        "note": "Real current Qt UI render; Core/Scheduler/workers intentionally not started.",
        "files": sorted(path.name for path in OUT.glob("*.png")),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    window.close()
    for obj in reversed(installed):
        _delete_later(obj)
    _flush(app)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
