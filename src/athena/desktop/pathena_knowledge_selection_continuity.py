"""Selection-identity continuity for canonical Knowledge list refreshes."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPlainTextEdit

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state


class KnowledgeSelectionContinuity(QObject):
    """Prevent a vanished canonical identity from silently selecting row zero."""

    def __init__(self, workspace: KnowledgeWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._original: Callable[..., None] = workspace._restore_or_select_first
        workspace._restore_or_select_first = self._restore_or_select_first
        for widget in (
            workspace.knowledge_list,
            workspace.claim_list,
            workspace.review_list,
        ):
            widget.currentItemChanged.connect(
                lambda current, _previous, source=widget: (
                    self._clear_disappearance_on_new_selection(source, current)
                )
            )

    def _restore_or_select_first(
        self,
        widget: QListWidget,
        selected: QListWidgetItem | None,
        *,
        empty_callback: object,
    ) -> None:
        previous_id, details, noun = self._selection_context(widget)
        widget.setProperty("pathenaSelectionDisappeared", "")
        details.setProperty("pathenaSelectionDisappeared", "")

        if selected is not None or widget.count() == 0 or previous_id is None:
            self._original(widget, selected, empty_callback=empty_callback)
            return

        self._clear_selection_state(widget)
        widget.setCurrentRow(-1)
        label = previous_id[:8].upper()
        message = (
            f"SELECTION CHANGED · {noun} {label} is no longer listed after refresh. "
            f"Select another {noun} to inspect its current provenance."
        )
        details.setPlainText(message)
        widget.setProperty("pathenaSelectionDisappeared", previous_id)
        details.setProperty("pathenaSelectionDisappeared", previous_id)
        widget.setAccessibleDescription(message)
        details.setAccessibleDescription(message)
        widget.setStatusTip(message)
        set_pathena_ui_state(details, "empty")

    def _clear_disappearance_on_new_selection(
        self,
        widget: QListWidget,
        current: QListWidgetItem | None,
    ) -> None:
        if current is None:
            return
        _previous_id, details, _noun = self._selection_context(widget)
        if not widget.property("pathenaSelectionDisappeared") and not details.property(
            "pathenaSelectionDisappeared"
        ):
            return
        widget.setProperty("pathenaSelectionDisappeared", "")
        details.setProperty("pathenaSelectionDisappeared", "")
        widget.setStatusTip("")

    def _selection_context(
        self,
        widget: QListWidget,
    ) -> tuple[str | None, QPlainTextEdit, str]:
        workspace = self.workspace
        if widget is workspace.knowledge_list:
            return workspace._selected_knowledge_id, workspace.knowledge_details, "Knowledge"
        if widget is workspace.claim_list:
            return workspace._selected_claim_id, workspace.claim_details, "Claim"
        return workspace._selected_review_id, workspace.review_details, "Decision"

    def _clear_selection_state(self, widget: QListWidget) -> None:
        workspace = self.workspace
        if widget is workspace.knowledge_list:
            workspace._selected_knowledge_id = None
            workspace.history_button.setEnabled(False)
            return
        if widget is workspace.claim_list:
            workspace._selected_claim_id = None
            workspace.claim_history_button.setEnabled(False)
            return
        workspace._selected_review_id = None
        workspace.review_accept_button.setEnabled(False)
        workspace.review_reject_button.setEnabled(False)


def install_knowledge_selection_continuity(
    workspace: KnowledgeWorkspace,
) -> KnowledgeSelectionContinuity:
    """Install identity-safe refresh semantics for canonical memory lists."""
    return KnowledgeSelectionContinuity(workspace)
