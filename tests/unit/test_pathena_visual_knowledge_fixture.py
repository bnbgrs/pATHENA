from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QApplication, QSplitter, QWidget

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from scripts.render_pathena_ui_snapshot_sequential import (
    _REFERENCE_KNOWLEDGE_DRAFTS,
    _REFERENCE_KNOWLEDGE_IDENTITIES,
    _seed_reference_knowledge,
    _select_reference_knowledge,
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
        assert len(workspace.findChildren(QSplitter, "canonicalMemorySplit")) == 3
        assert len(workspace.findChildren(QWidget, "canonicalMemoryListPane")) == 3
        assert len(workspace.findChildren(QWidget, "canonicalMemoryDetailPane")) == 3
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

        listed_ids = tuple(
            str(
                workspace.knowledge_list.item(index).data(
                    Qt.ItemDataRole.UserRole
                )
            )
            for index in range(workspace.knowledge_list.count())
        )
        assert set(listed_ids) == set(first_ids)
        assert listed_ids == first_ids
        assert first_ids[0] == _REFERENCE_KNOWLEDGE_IDENTITIES[
            _REFERENCE_KNOWLEDGE_DRAFTS[0][1]
        ][0]

        evidence = _select_reference_knowledge(
            app=app,
            knowledge_list=workspace.knowledge_list,
            knowledge_details=workspace.knowledge_details,
            expected_ids=first_ids,
        )

        assert evidence["selected_knowledge_id"] == first_ids[0]
        assert evidence["selected_knowledge_key"] == _REFERENCE_KNOWLEDGE_DRAFTS[0][1]
        assert evidence["selected_knowledge_state"] == "ready"
        detail_text = workspace.knowledge_details.toPlainText()
        assert _REFERENCE_KNOWLEDGE_DRAFTS[0][1] in detail_text
        assert _REFERENCE_KNOWLEDGE_DRAFTS[0][2] in detail_text
        assert "PERSISTED DETAIL UNAVAILABLE" not in detail_text
        assert "PROVENANCE" in detail_text
    finally:
        _stop_workspace_processes(workspace)
        workspace.close()
        workspace.deleteLater()
        app.processEvents()
