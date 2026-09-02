from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_research_proposal_focus import (
    ResearchProposalFocusController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _extension() -> SimpleNamespace:
    app = _app()
    workspace = QWidget()
    layout = QVBoxLayout(workspace)
    proposal_list = QListWidget(workspace)
    proposal_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    accept = QPushButton("Accept", workspace)
    separate = QPushButton("Keep separate", workspace)
    reject = QPushButton("Reject", workspace)
    other = QLineEdit(workspace)
    for widget in (proposal_list, accept, separate, reject, other):
        layout.addWidget(widget)
    workspace.show()
    app.processEvents()
    return SimpleNamespace(
        workspace=workspace,
        proposal_list=proposal_list,
        accept_button=accept,
        accept_separate_button=separate,
        reject_button=reject,
        process=QProcess(workspace),
        _operation="",
        _selected_proposal_id="abcdef12-3456",
        other=other,
    )


def test_successful_decision_waits_for_refresh_before_restoring_focus() -> None:
    extension = _extension()
    controller = ResearchProposalFocusController(extension)  # type: ignore[arg-type]
    extension._operation = "accept"
    extension.accept_button.setFocus()

    controller._decision_clicked(extension.accept_button)
    controller._process_finished(0, QProcess.ExitStatus.NormalExit)

    assert controller._phase == "waiting-refresh"
    controller._process_started()
    assert controller._phase == "refresh-running"
    controller._process_finished(0, QProcess.ExitStatus.NormalExit)

    assert extension.workspace.property("pathenaProposalFocusOutcome") == (
        "proposal-list-restored"
    )
    assert extension.proposal_list.hasFocus()


def test_newer_usable_focus_wins_after_refresh() -> None:
    extension = _extension()
    controller = ResearchProposalFocusController(extension)  # type: ignore[arg-type]
    extension._operation = "reject"
    extension.reject_button.setFocus()
    controller._decision_clicked(extension.reject_button)
    controller._process_finished(0, QProcess.ExitStatus.NormalExit)
    controller._process_started()
    extension.other.setFocus()

    controller._process_finished(0, QProcess.ExitStatus.NormalExit)

    assert extension.workspace.property("pathenaProposalFocusOutcome") == (
        "preserved-newer-focus"
    )
    assert extension.other.hasFocus()


def test_failed_decision_returns_focus_to_proposal_list() -> None:
    extension = _extension()
    controller = ResearchProposalFocusController(extension)  # type: ignore[arg-type]
    extension._operation = "accept"
    extension.accept_button.setFocus()
    controller._decision_clicked(extension.accept_button)

    controller._process_finished(1, QProcess.ExitStatus.NormalExit)

    assert extension.workspace.property("pathenaProposalFocusReason") == "decision-error"
    assert extension.proposal_list.hasFocus()


def test_missing_followup_refresh_has_bounded_focus_fallback() -> None:
    extension = _extension()
    controller = ResearchProposalFocusController(extension)  # type: ignore[arg-type]
    extension._operation = "reject"
    extension.reject_button.setFocus()
    controller._decision_clicked(extension.reject_button)
    controller._process_finished(0, QProcess.ExitStatus.NormalExit)

    controller._restore_if_refresh_did_not_start()

    assert extension.workspace.property("pathenaProposalFocusReason") == (
        "refresh-not-started"
    )
    assert extension.proposal_list.hasFocus()
