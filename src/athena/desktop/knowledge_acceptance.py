"""Explicit desktop acceptance controller for reviewed Knowledge proposals."""

from __future__ import annotations

import sys

from PySide6.QtCore import QObject, QProcess, Slot
from PySide6.QtWidgets import QBoxLayout, QPushButton, QVBoxLayout, QWidget

from athena.api.contracts import KnowledgeReviewResponse
from athena.desktop.api_controller import DesktopApiController


class KnowledgeAcceptanceController(QObject):
    """Commit only the exact preflight the user has reviewed in this session."""

    def __init__(
        self,
        *,
        workspace: QWidget,
        controller: DesktopApiController | None,
        claims_panel: QWidget | None = None,
    ) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.controller = controller
        self.claims_panel = claims_panel
        self.processing_run_id: str | None = None
        self.preflight_digest: str | None = None
        self._buffer = ""

        self.button = QPushButton("ACCEPT REVIEW")
        self.button.setObjectName("newChatButton")
        self.button.setToolTip(
            "Atomically commit exactly the reviewed Knowledge and Claim proposals"
        )
        self.button.setEnabled(False)
        self.button.clicked.connect(self.accept)
        self._insert_button()

        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._drain_output)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._process_error)

        if controller is not None:
            controller.knowledge_review_ready.connect(self.apply_review)

    def _insert_button(self) -> None:
        root = self.workspace.layout()
        if not isinstance(root, QVBoxLayout) or root.count() < 1:
            raise RuntimeError("Knowledge workspace header is unavailable")
        header_item = root.itemAt(0)
        header = None if header_item is None else header_item.layout()
        if not isinstance(header, QBoxLayout):
            raise RuntimeError("Knowledge workspace header layout is unavailable")
        header.addWidget(self.button)

    @Slot(object)
    def apply_review(self, payload: object) -> None:
        if not isinstance(payload, KnowledgeReviewResponse):
            return
        if payload.ready_to_accept and payload.preflight_digest:
            self.processing_run_id = payload.processing_run_id
            self.preflight_digest = payload.preflight_digest
            self.button.setEnabled(not self._busy())
            self.button.setToolTip(
                "Commit this exact reviewed preflight to canonical Knowledge / Claims"
            )
            return
        self.processing_run_id = None
        self.preflight_digest = None
        self.button.setEnabled(False)

    @Slot()
    def accept(self) -> None:
        if self._busy():
            return
        run_id = self.processing_run_id
        digest = self.preflight_digest
        if run_id is None or digest is None:
            return

        self._buffer = ""
        self.button.setEnabled(False)
        state = getattr(self.workspace, "state", None)
        if state is not None:
            state.setText("ACCEPTING / ATOMIC COMMIT")
        summary = getattr(self.workspace, "summary", None)
        if summary is not None:
            summary.setText(
                "Revalidating the reviewed canonical deduplication plan before commit …"
            )
        self.process.start(
            sys.executable,
            [
                "-m",
                "athena.desktop.knowledge_cli",
                "accept",
                run_id,
                digest,
            ],
        )

    def _busy(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning

    @Slot()
    def _drain_output(self) -> None:
        chunk = bytes(self.process.readAllStandardOutput().data()).decode(
            "utf-8", errors="replace"
        )
        if chunk:
            self._buffer += chunk

    @Slot(int, QProcess.ExitStatus)
    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._drain_output()
        state = getattr(self.workspace, "state", None)
        summary = getattr(self.workspace, "summary", None)

        if exit_code != 0:
            if state is not None:
                state.setText("ACCEPTANCE FAILED / REVIEW AGAIN")
            if summary is not None:
                detail = self._buffer.strip() or f"Knowledge acceptance failed (exit {exit_code})."
                summary.setText(detail)
            # The displayed preflight may now be stale. Never re-enable the same ticket.
            self.processing_run_id = None
            self.preflight_digest = None
            self.button.setEnabled(False)
            return

        if state is not None:
            state.setText("ACCEPTED / CANONICAL")
        if summary is not None:
            lines = [line for line in self._buffer.splitlines() if line.strip()]
            counts = " · ".join(lines[1:7]) if len(lines) > 1 else "Canonical commit completed."
            summary.setText(counts)

        self.processing_run_id = None
        self.preflight_digest = None
        self.button.setEnabled(False)

        refresh_knowledge = getattr(self.workspace, "refresh_knowledge", None)
        if callable(refresh_knowledge):
            refresh_knowledge()
        if self.claims_panel is not None:
            refresh_claims = getattr(self.claims_panel, "refresh_claims", None)
            if callable(refresh_claims):
                refresh_claims()
        if self.controller is not None:
            self.controller.refresh()

    @Slot(QProcess.ProcessError)
    def _process_error(self, error: QProcess.ProcessError) -> None:
        if error != QProcess.ProcessError.FailedToStart:
            return
        state = getattr(self.workspace, "state", None)
        summary = getattr(self.workspace, "summary", None)
        if state is not None:
            state.setText("ACCEPTANCE FAILED / PROCESS")
        if summary is not None:
            summary.setText("Unable to start the local canonical Knowledge acceptance command.")
        self.processing_run_id = None
        self.preflight_digest = None
        self.button.setEnabled(False)


def install_knowledge_acceptance(
    workspace: QWidget,
    controller: DesktopApiController | None,
    claims_panel: QWidget | None = None,
) -> KnowledgeAcceptanceController:
    """Attach explicit acceptance to the existing Knowledge workspace header."""
    return KnowledgeAcceptanceController(
        workspace=workspace,
        controller=controller,
        claims_panel=claims_panel,
    )
