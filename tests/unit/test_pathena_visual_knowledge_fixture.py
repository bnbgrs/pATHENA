from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QSplitter,
    QWidget,
)

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_detail_provenance_6300 import apply_detail_provenance
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


def test_visual_knowledge_capture_waits_for_current_detail_provenance() -> None:
    app = _app()
    knowledge_list = QListWidget()
    knowledge_details = QPlainTextEdit()
    reference_id = _REFERENCE_KNOWLEDGE_IDENTITIES[
        _REFERENCE_KNOWLEDGE_DRAFTS[0][1]
    ][0]
    item = QListWidgetItem(_REFERENCE_KNOWLEDGE_DRAFTS[0][1])
    item.setData(Qt.ItemDataRole.UserRole, reference_id)
    knowledge_list.addItem(item)
    knowledge_list.setCurrentItem(item)
    knowledge_details.setPlainText(
        "\n".join(
            (
                _REFERENCE_KNOWLEDGE_DRAFTS[0][1],
                _REFERENCE_KNOWLEDGE_DRAFTS[0][2],
            )
        )
    )
    knowledge_details.setProperty("pathenaKnowledgeEntityId", reference_id)
    knowledge_details.setProperty("pathenaKnowledgeReviewState", "ready")
    knowledge_details.setProperty("pathenaDetailContentIdentity", "")
    knowledge_details.setProperty("pathenaDetailProvenanceMode", "empty")

    def settle_provenance() -> None:
        knowledge_details.setProperty("pathenaDetailContentIdentity", reference_id)
        knowledge_details.setProperty("pathenaDetailProvenanceMode", "current")

    QTimer.singleShot(100, settle_provenance)
    evidence = _select_reference_knowledge(
        app=app,
        knowledge_list=knowledge_list,
        knowledge_details=knowledge_details,
        expected_ids=(reference_id,),
        timeout_seconds=1.0,
    )

    assert evidence["selected_knowledge_provenance"] == "current"


def test_visual_knowledge_capture_settles_detail_at_canonical_scroll_position() -> None:
    app = _app()
    knowledge_list = QListWidget()
    knowledge_details = QPlainTextEdit()
    knowledge_details.resize(240, 100)
    knowledge_details.show()
    reference_id = _REFERENCE_KNOWLEDGE_IDENTITIES[
        _REFERENCE_KNOWLEDGE_DRAFTS[0][1]
    ][0]
    item = QListWidgetItem(_REFERENCE_KNOWLEDGE_DRAFTS[0][1])
    item.setData(Qt.ItemDataRole.UserRole, reference_id)
    knowledge_list.addItem(item)
    knowledge_list.setCurrentItem(item)
    knowledge_details.setPlainText(
        "\n".join(
            (
                _REFERENCE_KNOWLEDGE_DRAFTS[0][1],
                _REFERENCE_KNOWLEDGE_DRAFTS[0][2],
                *(f"provenance line {index}" for index in range(20)),
            )
        )
    )
    knowledge_details.setProperty("pathenaKnowledgeEntityId", reference_id)
    knowledge_details.setProperty("pathenaKnowledgeReviewState", "ready")
    knowledge_details.setProperty("pathenaDetailContentIdentity", reference_id)
    knowledge_details.setProperty("pathenaDetailProvenanceMode", "current")
    app.processEvents()
    detail_scroll = knowledge_details.verticalScrollBar()
    assert detail_scroll.maximum() > 0
    detail_scroll.setValue(0)

    _select_reference_knowledge(
        app=app,
        knowledge_list=knowledge_list,
        knowledge_details=knowledge_details,
        expected_ids=(reference_id,),
        timeout_seconds=1.0,
    )

    assert detail_scroll.value() == detail_scroll.maximum()
    knowledge_details.close()


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
    provenance_controller = apply_detail_provenance(workspace)
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
        assert evidence["selected_knowledge_provenance"] == "current"
        assert (
            workspace.knowledge_details.property("pathenaDetailContentIdentity")
            == first_ids[0]
        )
        detail_text = workspace.knowledge_details.toPlainText()
        assert _REFERENCE_KNOWLEDGE_DRAFTS[0][1] in detail_text
        assert _REFERENCE_KNOWLEDGE_DRAFTS[0][2] in detail_text
        assert "PERSISTED DETAIL UNAVAILABLE" not in detail_text
        assert "PROVENANCE" in detail_text
    finally:
        provenance_controller._timer.stop()
        _stop_workspace_processes(workspace)
        workspace.close()
        workspace.deleteLater()
        app.processEvents()
