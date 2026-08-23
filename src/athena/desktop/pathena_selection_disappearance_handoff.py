"""Accessibility and dependent-view handoff for selections removed by refresh."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject, QTimer
from PySide6.QtWidgets import QListWidget, QPlainTextEdit

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.research_workspace import ResearchWorkspace
from athena.desktop.system_backup import BackupWorkspace


@dataclass(frozen=True)
class _SelectionTarget:
    selection: QListWidget
    details: QPlainTextEdit


class SelectionDisappearanceHandoff(QObject):
    """Keep keyboard/accessibility context truthful after a selected row vanishes."""

    def __init__(
        self,
        targets: tuple[_SelectionTarget, ...],
        research_results: ResearchResultsExtension,
    ) -> None:
        super().__init__(research_results.workspace)
        self._targets = targets
        self._base_descriptions = {
            target.selection: target.selection.accessibleDescription() for target in targets
        }
        self._research_results = research_results

        for target in targets:
            target.selection.installEventFilter(self)
            target.selection.currentItemChanged.connect(
                lambda _current, _previous, current=target: self._sync_target(current)
            )
            self._sync_target(target)

        research_results.workspace._process.finished.connect(self._schedule_research_sync)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QListWidget) and isinstance(
            event, QDynamicPropertyChangeEvent
        ):
            if bytes(event.propertyName()) == b"pathenaSelectionDisappeared":
                target = next(
                    (item for item in self._targets if item.selection is watched),
                    None,
                )
                if target is not None:
                    QTimer.singleShot(0, lambda current=target: self._sync_target(current))
        return super().eventFilter(watched, event)

    def _sync_target(self, target: _SelectionTarget) -> None:
        missing_value = target.selection.property("pathenaSelectionDisappeared")
        missing = str(missing_value).strip() if missing_value else ""
        if missing:
            message = target.details.toPlainText().strip()
            if not message:
                message = (
                    "The previously selected item is no longer present after refresh. "
                    "Select another item to continue."
                )
            target.selection.setAccessibleDescription(message)
            target.selection.setProperty("pathenaSelectionHandoffAnnouncement", message)
            target.selection.setProperty(
                "pathenaSelectionFocusRetained",
                target.selection.hasFocus(),
            )
            return

        base = self._base_descriptions.get(target.selection, "")
        target.selection.setAccessibleDescription(base)
        target.selection.setProperty("pathenaSelectionHandoffAnnouncement", "")
        target.selection.setProperty("pathenaSelectionFocusRetained", False)

    def _schedule_research_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self._sync_research_results)

    def _sync_research_results(self) -> None:
        extension = self._research_results
        workspace = extension.workspace
        missing_value = workspace.jobs.property("pathenaSelectionDisappeared")
        missing = str(missing_value).strip() if missing_value else ""
        if not missing or workspace._selected_job_id is not None:
            return

        extension._selected_proposal_id = None
        extension.proposal_list.clear()
        extension._sync_proposal_actions()
        label = missing[:8].upper()
        message = (
            f"Research run {label} is no longer listed after refresh. "
            "No ResearchResult proposal is selected; choose another run to continue."
        )
        extension.proposal_status.setText(message)
        extension.proposal_status.setAccessibleDescription(message)
        extension.proposal_status.setProperty("pathenaSelectionDisappeared", missing)


def install_selection_disappearance_handoff(
    files: FilesWorkspace,
    jobs: JobsWorkspace,
    research: ResearchWorkspace,
    backup: BackupWorkspace,
    research_results: ResearchResultsExtension,
) -> SelectionDisappearanceHandoff:
    """Install selection-removal handoff across dynamic desktop list/detail views."""
    targets = (
        _SelectionTarget(files.sources, files.details),
        _SelectionTarget(jobs.jobs, jobs.details),
        _SelectionTarget(research.jobs, research.details),
        _SelectionTarget(backup.snapshots, backup.details),
    )
    return SelectionDisappearanceHandoff(targets, research_results)
