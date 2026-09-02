"""Accessible ownership context for background desktop operations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from weakref import ref

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLabel, QListWidget, QWidget

from athena.desktop.files_workspace import FilesWorkspace
from athena.desktop.jobs_workspace import JobsWorkspace
from athena.desktop.research_results_extension import ResearchResultsExtension
from athena.desktop.system_backup import BackupWorkspace


@dataclass(frozen=True)
class _Target:
    status: QLabel
    details: QWidget
    selection: QListWidget
    selected_id: Callable[[], str | None]
    noun: str


class BackgroundCompletionAccessibility(QObject):
    """Keep accessible status copy aligned with visual operation ownership."""

    def __init__(self, targets: tuple[_Target, ...]) -> None:
        parent = targets[0].status if targets else None
        super().__init__(parent)
        self._targets = targets
        for target in targets:
            self._observe_status_text(target)
            target.selection.currentItemChanged.connect(
                lambda _current, _previous, current=target: self._sync_target(current)
            )
            self._sync_target(target)

    def _observe_status_text(self, target: _Target) -> None:
        """Refresh accessibility copy after QLabel.setText without assuming a Qt signal.

        QLabel intentionally exposes no ``textChanged`` signal.  The desktop status widgets
        are plain QLabel instances, so observing a non-existent signal crashes the native
        shell during construction.  Wrap the instance method instead: callers keep the
        normal QLabel API and accessibility state is synchronized immediately after a
        successful text update.
        """

        original_set_text = target.status.setText
        controller_ref = ref(self)

        def set_text(text: str, *, current: _Target = target) -> None:
            original_set_text(text)
            controller = controller_ref()
            if controller is not None:
                controller._sync_target(current)

        target.status.setText = set_text  # type: ignore[method-assign]

    @staticmethod
    def _label(identifier: str | None) -> str:
        if not identifier:
            return "none"
        if len(identifier) >= 8:
            return identifier[:8].upper()
        return identifier.upper()

    def _sync_target(self, target: _Target) -> None:
        status_text = target.status.text().strip()
        owner_value = target.details.property("pathenaBackgroundOperationOwner")
        owner = str(owner_value).strip() if owner_value else ""
        selected = target.selected_id()

        if owner and owner != selected:
            owner_label = self._label(owner)
            selected_label = self._label(selected)
            selection_copy = (
                f"Current selection remains {selected_label}."
                if selected
                else "No current selection is active."
            )
            description = (
                f"Background {target.noun} operation belongs to {owner_label}. "
                f"{selection_copy} {status_text}"
            ).strip()
            target.status.setAccessibleName(f"{target.noun.capitalize()} background status")
            target.status.setAccessibleDescription(description)
            target.status.setProperty("pathenaBackgroundAccessibleOwner", owner)
            target.status.setProperty("pathenaBackgroundAccessibleAnnouncement", description)
            return

        target.status.setAccessibleName(f"{target.noun.capitalize()} status")
        target.status.setAccessibleDescription(status_text)
        target.status.setProperty("pathenaBackgroundAccessibleOwner", "")
        target.status.setProperty("pathenaBackgroundAccessibleAnnouncement", status_text)


def install_background_completion_accessibility(
    files: FilesWorkspace,
    jobs: JobsWorkspace,
    backup: BackupWorkspace,
    research_results: ResearchResultsExtension,
) -> BackgroundCompletionAccessibility:
    """Install ownership-aware accessible status copy for shared detail panes."""
    targets = (
        _Target(
            status=files.status,
            details=files.details,
            selection=files.sources,
            selected_id=lambda: files._selected_source_id,
            noun="Source",
        ),
        _Target(
            status=jobs.status,
            details=jobs.details,
            selection=jobs.jobs,
            selected_id=lambda: jobs._selected_job_id,
            noun="job",
        ),
        _Target(
            status=backup.status,
            details=backup.details,
            selection=backup.snapshots,
            selected_id=lambda: backup._selected_snapshot_id,
            noun="backup",
        ),
        _Target(
            status=research_results.proposal_status,
            details=research_results.workspace.details,
            selection=research_results.workspace.jobs,
            selected_id=research_results._selected_job_id,
            noun="Research",
        ),
    )
    return BackgroundCompletionAccessibility(targets)
