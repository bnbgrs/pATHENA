"""Focus continuity for Research proposal decision and refresh cycles."""

from __future__ import annotations

from PySide6.QtCore import QObject, QProcess, QTimer, Qt
from PySide6.QtWidgets import QApplication, QListWidget, QPushButton, QWidget

from athena.desktop.research_results_extension import ResearchResultsExtension


class ResearchProposalFocusController(QObject):
    """Return decision focus to proposals unless newer user focus should win."""

    def __init__(self, extension: ResearchResultsExtension) -> None:
        super().__init__(extension.workspace)
        self.extension = extension
        self._phase = "idle"
        self._source: QPushButton | None = None
        self._selected_id = ""

        for button in (
            extension.accept_button,
            extension.accept_separate_button,
            extension.reject_button,
        ):
            button.clicked.connect(
                lambda _checked=False, source=button: self._decision_clicked(source)
            )

        extension.process.started.connect(self._process_started)
        extension.process.finished.connect(self._process_finished)
        extension.process.errorOccurred.connect(self._process_error)
        extension.proposal_list.setProperty("pathenaProposalDecisionFocusTarget", True)

    def _decision_clicked(self, source: QPushButton) -> None:
        operation = getattr(self.extension, "_operation", "")
        if operation not in {"accept", "reject"}:
            return
        self._phase = "decision-running"
        self._source = source
        selected = getattr(self.extension, "_selected_proposal_id", None)
        self._selected_id = selected if isinstance(selected, str) else ""
        self.extension.workspace.setProperty(
            "pathenaProposalFocusDecision",
            self._selected_id,
        )

    def _process_started(self) -> None:
        if self._phase == "waiting-refresh":
            self._phase = "refresh-running"
            self.extension.workspace.setProperty(
                "pathenaProposalFocusPhase",
                "refresh-running",
            )

    def _process_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        if self._phase == "decision-running":
            if exit_code == 0:
                self._phase = "waiting-refresh"
                self.extension.workspace.setProperty(
                    "pathenaProposalFocusPhase",
                    "waiting-refresh",
                )
                QTimer.singleShot(350, self._restore_if_refresh_did_not_start)
            else:
                self._restore_or_preserve("decision-error")
            return

        if self._phase == "refresh-running":
            self._restore_or_preserve(
                "refresh-complete" if exit_code == 0 else "refresh-error"
            )

    def _process_error(self, _error: QProcess.ProcessError) -> None:
        if self._phase in {"decision-running", "refresh-running"}:
            self._restore_or_preserve("process-error")

    def _restore_if_refresh_did_not_start(self) -> None:
        if self._phase == "waiting-refresh":
            self._restore_or_preserve("refresh-not-started")

    def _restore_or_preserve(self, reason: str) -> None:
        proposal_list = self.extension.proposal_list
        focused = QApplication.focusWidget()
        if self._newer_focus_should_win(focused, proposal_list):
            outcome = "preserved-newer-focus"
        elif self._focusable(proposal_list):
            proposal_list.setFocus(Qt.FocusReason.OtherFocusReason)
            proposal_list.setProperty("pathenaProposalDecisionFocusRestored", True)
            outcome = "proposal-list-restored"
        else:
            outcome = "proposal-list-unavailable"

        self.extension.workspace.setProperty("pathenaProposalFocusOutcome", outcome)
        self.extension.workspace.setProperty("pathenaProposalFocusReason", reason)
        self.extension.workspace.setProperty(
            "pathenaProposalFocusSelectedIdentity",
            self._selected_id,
        )
        self._phase = "idle"
        self._source = None
        self._selected_id = ""

    def _newer_focus_should_win(
        self,
        focused: QWidget | None,
        proposal_list: QListWidget,
    ) -> bool:
        if focused is None or focused is self._source or focused is proposal_list:
            return False
        return self._focusable(focused)

    @staticmethod
    def _focusable(widget: QWidget) -> bool:
        return (
            widget.isEnabled()
            and widget.isVisibleTo(widget.window())
            and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
        )


def install_research_proposal_focus(
    extension: ResearchResultsExtension,
) -> ResearchProposalFocusController:
    """Install focus continuity for existing Research proposal decisions."""
    controller = ResearchProposalFocusController(extension)
    extension.workspace.setProperty("pathenaResearchProposalFocusController", controller)
    return controller
