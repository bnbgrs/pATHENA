"""Quiet density and decision-scope summary for Research promotion proposals."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout

from athena.desktop.research_results_extension import ResearchResultsExtension


class ResearchProposalDensityController(QObject):
    """Summarize proposal state without reordering or changing promotion semantics."""

    def __init__(self, extension: ResearchResultsExtension) -> None:
        super().__init__(extension.workspace)
        self.extension = extension
        self.summary = self._install_summary()
        self._configure_list()
        extension.proposal_list.currentItemChanged.connect(self.schedule_sync)
        extension.process.finished.connect(self.schedule_sync)
        self.sync()

    def _install_summary(self) -> QLabel:
        panel = self.extension.workspace.findChild(QLabel, "researchProposalScope")
        if panel is not None:
            return panel

        label = QLabel(self.extension.workspace)
        label.setObjectName("researchProposalScope")
        label.setProperty("role", "dim")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAccessibleName("Research proposal decision scope")

        parent = self.extension.proposal_list.parentWidget()
        layout = parent.layout() if parent is not None else None
        if isinstance(layout, QVBoxLayout):
            index = layout.indexOf(self.extension.proposal_status)
            layout.insertWidget(index + 1 if index >= 0 else 0, label)
        return label

    def _configure_list(self) -> None:
        proposal_list = self.extension.proposal_list
        proposal_list.setSpacing(2)
        proposal_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        proposal_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        proposal_list.setAccessibleName("Research promotion proposals")
        proposal_list.setAccessibleDescription(
            "Evidence-backed proposals remain in deterministic ordinal order. "
            "Select a row to inspect its decision state and available actions."
        )
        proposal_list.setProperty("pathenaProposalOrderPreserved", True)
        proposal_list.setProperty("pathenaProposalEvidenceInTooltip", True)

    def schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        proposal_list = self.extension.proposal_list
        total = proposal_list.count()
        pending = 0
        resolved = 0
        for row in range(total):
            item = proposal_list.item(row)
            state = str(item.data(Qt.ItemDataRole.UserRole + 1) or "unknown")
            proposal_type = str(item.data(Qt.ItemDataRole.UserRole + 2) or "proposal")
            if state == "pending":
                pending += 1
            else:
                resolved += 1
            item.setData(
                Qt.ItemDataRole.AccessibleTextRole,
                f"{proposal_type.replace('_', ' ')} proposal, {state}. {item.text()}",
            )

        selected = self._selected_summary()
        if total == 0:
            text = "No promotion proposals loaded"
        else:
            text = (
                f"{total} proposals · {pending} pending · {resolved} resolved"
                f" · {selected}"
            )
        self.summary.setText(text)
        self.summary.setAccessibleDescription(text)
        self.summary.setProperty("pathenaProposalTotal", total)
        self.summary.setProperty("pathenaProposalPending", pending)
        self.summary.setProperty("pathenaProposalResolved", resolved)
        self.summary.setProperty("pathenaProposalSelected", selected)

    def _selected_summary(self) -> str:
        item = self.extension.proposal_list.currentItem()
        if item is None:
            return "none selected"
        proposal_id = item.data(Qt.ItemDataRole.UserRole)
        state = str(item.data(Qt.ItemDataRole.UserRole + 1) or "unknown")
        proposal_type = str(item.data(Qt.ItemDataRole.UserRole + 2) or "proposal")
        identity = (
            str(proposal_id)[:8].upper()
            if isinstance(proposal_id, str) and proposal_id
            else "selected"
        )
        evidence = self._evidence_from_tooltip(item.toolTip())
        suffix = f" · {evidence}" if evidence else ""
        return f"{proposal_type.replace('_', ' ')} / {state} / {identity}{suffix}"

    @staticmethod
    def _evidence_from_tooltip(tooltip: str) -> str:
        for line in tooltip.splitlines():
            if line.startswith("evidence="):
                return line.replace("evidence=", "evidence ", 1)
        return ""


def install_research_proposal_density(
    extension: ResearchResultsExtension,
) -> ResearchProposalDensityController:
    """Install quiet proposal scope and evidence scanability."""
    controller = ResearchProposalDensityController(extension)
    extension.workspace.setProperty("pathenaResearchProposalDensityController", controller)
    return controller
