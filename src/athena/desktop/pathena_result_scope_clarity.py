"""Quiet result-scope summaries for dense pATHENA list workspaces."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ScopeTarget:
    workspace_name: str
    list_attribute: str
    status_attribute: str
    label: str
    filter_attribute: str | None = None


_TARGETS: tuple[ScopeTarget, ...] = (
    ScopeTarget(
        "knowledgeWorkspace",
        "knowledge_list",
        "browser_status",
        "Knowledge",
        "search_input",
    ),
    ScopeTarget("researchWorkspace", "jobs", "status", "Research jobs"),
    ScopeTarget("jobsWorkspace", "jobs", "status", "Durable jobs"),
    ScopeTarget("filesWorkspace", "sources", "status", "Sources"),
    ScopeTarget("backupWorkspace", "snapshots", "status", "Backup snapshots"),
)


class ResultScopeController(QObject):
    """Keep total, visible and selected list scope explicit without rewriting status."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._entries: list[tuple[QListWidget, QLabel, str]] = []

    def register(
        self,
        list_widget: QListWidget,
        scope_label: QLabel,
        label: str,
        filter_input: QLineEdit | None,
    ) -> None:
        self._entries.append((list_widget, scope_label, label))
        model = list_widget.model()
        model.rowsInserted.connect(self.schedule_sync)
        model.rowsRemoved.connect(self.schedule_sync)
        model.modelReset.connect(self.schedule_sync)
        list_widget.currentItemChanged.connect(self.schedule_sync)
        if filter_input is not None:
            filter_input.textChanged.connect(self.schedule_sync)
        self._sync_one(list_widget, scope_label, label)

    def schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        for list_widget, scope_label, label in self._entries:
            self._sync_one(list_widget, scope_label, label)

    @staticmethod
    def _sync_one(list_widget: QListWidget, scope_label: QLabel, label: str) -> None:
        total = list_widget.count()
        visible = sum(
            1
            for row in range(total)
            if not list_widget.item(row).isHidden()
        )
        selected = ResultScopeController._selected_identity(list_widget.currentItem())

        if total == 0:
            text = f"{label} · 0 items · none selected"
        elif visible != total:
            text = f"{label} · {visible} shown / {total} total · {selected}"
        else:
            text = f"{label} · {total} shown · {selected}"

        scope_label.setText(text)
        scope_label.setAccessibleName(f"{label} result scope")
        scope_label.setAccessibleDescription(text)
        scope_label.setProperty("pathenaResultTotal", total)
        scope_label.setProperty("pathenaResultVisible", visible)
        scope_label.setProperty("pathenaSelectedIdentity", selected)

    @staticmethod
    def _selected_identity(item: QListWidgetItem | None) -> str:
        if item is None:
            return "none selected"
        value = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(value, str) and value:
            return f"selected {value[:8].upper()}"
        return "selection active"


def _install_scope_label(
    workspace: QWidget,
    status: QWidget,
    object_name: str,
) -> QLabel | None:
    layout = workspace.layout()
    if not isinstance(layout, QVBoxLayout):
        return None
    existing = workspace.findChild(QLabel, object_name)
    if existing is not None:
        return existing

    label = QLabel(workspace)
    label.setObjectName(object_name)
    label.setProperty("role", "dim")
    label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    index = layout.indexOf(status)
    layout.insertWidget(index + 1 if index >= 0 else layout.count(), label)
    return label


def apply_result_scope_clarity(window: QWidget) -> tuple[int, ...]:
    """Install truthful list-scope summaries for existing dense workspaces."""
    controller = ResultScopeController(window)
    applied: list[int] = []

    for offset, target in enumerate(_TARGETS):
        workspace = window.findChild(QWidget, target.workspace_name)
        if workspace is None:
            continue
        list_widget = getattr(workspace, target.list_attribute, None)
        status = getattr(workspace, target.status_attribute, None)
        if not isinstance(list_widget, QListWidget) or not isinstance(status, QWidget):
            continue
        filter_input = (
            getattr(workspace, target.filter_attribute, None)
            if target.filter_attribute is not None
            else None
        )
        if filter_input is not None and not isinstance(filter_input, QLineEdit):
            filter_input = None

        scope_label = _install_scope_label(
            workspace,
            status,
            f"pathenaResultScope{target.workspace_name}",
        )
        if scope_label is None:
            continue
        controller.register(list_widget, scope_label, target.label, filter_input)
        applied.append(6101 + offset)

    window.setProperty("pathenaResultScopeController", controller)
    window.setProperty("pathenaResultScopeTargetCount", len(applied))
    return tuple(applied)
