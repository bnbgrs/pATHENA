"""Selection ownership for canonical Knowledge detail operations."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QProcess, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QPlainTextEdit

from athena.desktop.knowledge_workspace import KnowledgeWorkspace
from athena.desktop.pathena_ui_refinement_600 import set_pathena_ui_state

_DETAIL_OPERATIONS = frozenset(
    {
        "show",
        "history",
        "claim-show",
        "claim-history",
        "review-show",
        "review-accept",
        "review-reject",
    }
)


class KnowledgeDetailOwnership(QObject):
    """Keep streamed detail output attached to the identity that started it."""

    def __init__(self, workspace: KnowledgeWorkspace) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self._operation = ""
        self._owner_id: str | None = None
        self._original_start: Callable[[str, list[str], str], None] = (
            workspace._start_knowledge
        )
        self._original_drain: Callable[[], None] = workspace._drain_knowledge_output

        object.__setattr__(workspace, "_start_knowledge", self._start_knowledge)
        object.__setattr__(workspace, "_drain_knowledge_output", self._drain_output)
        workspace._knowledge_process.readyReadStandardOutput.disconnect(self._original_drain)
        workspace._knowledge_process.readyReadStandardOutput.connect(self._drain_output)
        workspace._knowledge_process.finished.connect(self._after_finished)
        workspace._knowledge_process.errorOccurred.connect(self._after_error)
        workspace.knowledge_list.currentItemChanged.connect(self._selection_changed)
        workspace.claim_list.currentItemChanged.connect(self._selection_changed)
        workspace.review_list.currentItemChanged.connect(self._selection_changed)

    def _start_knowledge(self, operation: str, arguments: list[str], label: str) -> None:
        self._operation = operation
        self._owner_id = self._current_id_for_operation(operation)
        target = self._detail_target(operation)
        if target is not None:
            target.setProperty("pathenaBackgroundOperationOwner", "")
        self._original_start(operation, arguments, label)

    def _drain_output(self) -> None:
        workspace = self.workspace
        chunk = bytes(workspace._knowledge_process.readAllStandardOutput().data()).decode(
            "utf-8",
            errors="replace",
        )
        if not chunk:
            return
        workspace._knowledge_buffer += chunk
        target = self._detail_target(self._operation)
        if target is not None and self._operation_owns_current():
            target.moveCursor(QTextCursor.MoveOperation.End)
            target.insertPlainText(chunk)

    def _selection_changed(
        self,
        _current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if not self.workspace._knowledge_busy() or self._operation not in _DETAIL_OPERATIONS:
            return
        target = self._detail_target(self._operation)
        if target is None:
            return

        if self._operation_owns_current():
            background_owner = target.property("pathenaBackgroundOperationOwner")
            if background_owner:
                target.setPlainText(self.workspace._knowledge_buffer)
                target.setProperty("pathenaBackgroundOperationOwner", "")
                target.setAccessibleDescription(
                    "Output belongs to the currently selected canonical-memory item."
                )
                set_pathena_ui_state(target, "busy")
            return

        owner_label = self._label(self._owner_id)
        current_id = self._current_id_for_operation(self._operation)
        current_label = self._label(current_id)
        noun = self._noun(self._operation)
        current_copy = (
            f"CURRENT · {noun} {current_label} remains selected; background output "
            "will not be written into this pane."
            if current_id
            else f"CURRENT · No {noun} is selected."
        )
        message = (
            f"BACKGROUND · {self._operation.upper()} for {noun} {owner_label} is still "
            f"running.\n{current_copy}"
        )
        target.setPlainText(message)
        target.setProperty("pathenaBackgroundOperationOwner", self._owner_id or "")
        target.setAccessibleDescription(message)
        set_pathena_ui_state(target, "idle")

    def _after_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        operation = self._operation
        owner_id = self._owner_id
        if operation not in _DETAIL_OPERATIONS:
            self._reset()
            return

        current_id = self._current_id_for_operation(operation)
        visual_review_id = self._current_item_id(self.workspace.review_list)
        if operation in {"review-accept", "review-reject"}:
            if visual_review_id and visual_review_id != owner_id:
                self.workspace._selected_review_id = visual_review_id
                enabled = not self.workspace._knowledge_busy()
                self.workspace.review_accept_button.setEnabled(enabled)
                self.workspace.review_reject_button.setEnabled(enabled)
                current_id = visual_review_id

        target = self._detail_target(operation)
        if target is not None and owner_id != current_id:
            noun = self._noun(operation)
            owner_label = self._label(owner_id)
            current_label = self._label(current_id)
            result = "failed" if exit_code != 0 else "finished"
            current_copy = (
                f" Current selection remains {current_label}."
                if current_id
                else " No current selection is active."
            )
            message = (
                f"{noun.capitalize()} {owner_label} {operation.replace('-', ' ')} {result} "
                f"in the background.{current_copy}"
            )
            self.workspace.browser_status.setText(message)
            self.workspace.browser_status.setAccessibleDescription(message)
            target.setProperty("pathenaBackgroundOperationOwner", owner_id or "")
        elif target is not None:
            target.setProperty("pathenaBackgroundOperationOwner", "")

        self._reset()

    def _after_error(self, error: QProcess.ProcessError) -> None:
        if self._operation not in _DETAIL_OPERATIONS or self._operation_owns_current():
            self._reset()
            return
        noun = self._noun(self._operation)
        owner_label = self._label(self._owner_id)
        current_id = self._current_id_for_operation(self._operation)
        current_label = self._label(current_id)
        current_copy = (
            f" Current selection remains {current_label}."
            if current_id
            else " No current selection is active."
        )
        message = (
            f"Unable to start {self._operation.replace('-', ' ')} for {noun} "
            f"{owner_label} in the background ({error.name}).{current_copy}"
        )
        self.workspace.browser_status.setText(message)
        self.workspace.browser_status.setAccessibleDescription(message)
        self._reset()

    def _operation_owns_current(self) -> bool:
        return self._owner_id == self._current_id_for_operation(self._operation)

    def _current_id_for_operation(self, operation: str) -> str | None:
        workspace = self.workspace
        if operation in {"show", "history"}:
            return workspace._selected_knowledge_id
        if operation in {"claim-show", "claim-history"}:
            return workspace._selected_claim_id
        if operation in {"review-show", "review-accept", "review-reject"}:
            return workspace._selected_review_id
        return None

    def _detail_target(self, operation: str) -> QPlainTextEdit | None:
        return self.workspace._detail_target_for_operation(operation)

    @staticmethod
    def _current_item_id(widget: QListWidget) -> str | None:
        current_item: QListWidgetItem | None = widget.currentItem()
        if current_item is None:
            return None
        value = current_item.data(Qt.ItemDataRole.UserRole)
        return str(value) if value else None

    @staticmethod
    def _noun(operation: str) -> str:
        if operation.startswith("claim-"):
            return "Claim"
        if operation.startswith("review-"):
            return "Decision"
        return "Knowledge"

    @staticmethod
    def _label(identifier: str | None) -> str:
        return identifier[:8].upper() if identifier else "UNKNOWN"

    def _reset(self) -> None:
        self._operation = ""
        self._owner_id = None


def install_knowledge_detail_ownership(
    workspace: KnowledgeWorkspace,
) -> KnowledgeDetailOwnership:
    """Install identity ownership for shared canonical-memory detail panes."""
    return KnowledgeDetailOwnership(workspace)
