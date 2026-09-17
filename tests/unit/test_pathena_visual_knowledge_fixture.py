from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from scripts.render_pathena_ui_snapshot_sequential import (
    _REFERENCE_KNOWLEDGE_DRAFTS,
    _seed_reference_knowledge,
)

_FRESH_PROCESS_ENV = "PATHENA_VISUAL_KNOWLEDGE_FRESH_PROCESS"


def _app() -> QApplication:
    app = QApplication.instance()
    if isinstance(app, QApplication):
        return app
    return QApplication([])


def _wait_until(app: QApplication, predicate: object, *, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        app.processEvents()
        if callable(predicate) and predicate():
            return
        time.sleep(0.02)
    raise AssertionError("Timed out waiting for repository-backed Knowledge UI state.")


def _stop_workspace_processes(workspace: KnowledgeWorkspace) -> None:
    workspace._knowledge_refresh_timer.stop()
    for process in (workspace._knowledge_process, workspace._obsidian_process):
        if process.state() == QProcess.ProcessState.NotRunning:
            continue
        process.kill()
        process.waitForFinished(2_000)


def test_visual_knowledge_fixture_is_idempotent_and_renders_real_detail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if os.environ.get(_FRESH_PROCESS_ENV) != "1":
        child_environment = os.environ.copy()
        child_environment[_FRESH_PROCESS_ENV] = "1"
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(Path(__file__).resolve())],
            cwd=Path(__file__).resolve().parents[2],
            env=child_environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        return

    runtime_root = tmp_path / "isolated-visual-runtime"
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(runtime_root))

    first_ids = _seed_reference_knowledge(runtime_root)
    second_ids = _seed_reference_knowledge(runtime_root)

    assert second_ids == first_ids
    assert len(first_ids) == len(_REFERENCE_KNOWLEDGE_DRAFTS)
    assert len(set(first_ids)) == len(first_ids)

    app = _app()
    workspace = KnowledgeWorkspace(QWidget(), None)
    try:
        _wait_until(
            app,
            lambda: (
                workspace.knowledge_list.count() == len(first_ids)
                and workspace.knowledge_details.property(
                    "pathenaKnowledgeReviewState"
                )
                == "ready"
            ),
            timeout_seconds=10.0,
        )

        listed_ids = {
            str(
                workspace.knowledge_list.item(index).data(
                    Qt.ItemDataRole.UserRole
                )
            )
            for index in range(workspace.knowledge_list.count())
        }
        assert listed_ids == set(first_ids)
        assert str(
            workspace.knowledge_details.property("pathenaKnowledgeEntityId")
        ) in set(first_ids)
        assert "PERSISTED DETAIL UNAVAILABLE" not in (
            workspace.knowledge_details.toPlainText()
        )
        assert "PROVENANCE" in workspace.knowledge_details.toPlainText()
    finally:
        _stop_workspace_processes(workspace)
        workspace.close()
        workspace.deleteLater()
        app.processEvents()
