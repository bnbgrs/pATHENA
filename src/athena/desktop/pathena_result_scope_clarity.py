"""Quiet result-scope summaries for dense pATHENA list workspaces."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ScopeTarget:
    workspace_name: str
    list_attribute: str
    status_attribute: str
    label: str
    filter_object_name: str | None = None


_TARGETS: tuple[ScopeTarget, ...] = (
    ScopeTarget(
        "researchWorkspace",
        "jobs",
        "status",
        "Research jobs",
        filter_object_name="researchJobFilter",
    ),
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
        self._connect_list(list_widget, self.schedule_sync)
        if filter_input is not None:
            filter_input.textChanged.connect(self.schedule_sync)
            scope_label.setProperty("pathenaResultScopeFilterBound", filter_input.objectName())
        self._sync_one(list_widget, scope_label, label)

    @staticmethod
    def _connect_list(list_widget: QListWidget, callback: object) -> None:
        model = list_widget.model()
        model.rowsInserted.connect(callback)  # type: ignore[arg-type]
        model.rowsRemoved.connect(callback)  # type: ignore[arg-type]
        model.modelReset.connect(callback)  # type: ignore[arg-type]
        list_widget.currentItemChanged.connect(callback)  # type: ignore[arg-type]

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
        scope_label.setProperty("pathenaResultScopeMode", "list")

    @staticmethod
    def _selected_identity(item: QListWidgetItem | None) -> str:
        if item is None:
            return "none selected"
        value = item.data(Qt.ItemDataRole.UserRole)
        identity = (
            f"selected {value[:8].upper()}"
            if isinstance(value, str) and value
            else "selection active"
        )
        return f"{identity} (filtered)" if item.isHidden() else identity


class KnowledgeTabbedScopeController(QObject):
    """Bind the shared Knowledge scope row to the currently visible canonical tab."""

    def __init__(self, workspace: QWidget, scope_label: QLabel) -> None:
        super().__init__(workspace)
        self.workspace = workspace
        self.scope_label = scope_label
        self.tabs = getattr(workspace, "browser_tabs", None)
        self.search = getattr(workspace, "search_input", None)
        self._lists: dict[int, tuple[QListWidget, str]] = {}

        for index, attribute, label in (
            (0, "knowledge_list", "Knowledge"),
            (1, "claim_list", "Claims"),
            (2, "review_list", "Decisions"),
        ):
            candidate = getattr(workspace, attribute, None)
            if isinstance(candidate, QListWidget):
                self._lists[index] = (candidate, label)
                ResultScopeController._connect_list(candidate, self.schedule_sync)

        if isinstance(self.tabs, QTabWidget):
            self.tabs.currentChanged.connect(self.schedule_sync)
        if isinstance(self.search, QLineEdit):
            self.search.textChanged.connect(self.schedule_sync)
            scope_label.setProperty(
                "pathenaResultScopeFilterBound",
                self.search.objectName(),
            )
        self.sync()

    def schedule_sync(self, *_args: object) -> None:
        QTimer.singleShot(0, self.sync)

    def sync(self) -> None:
        index = self.tabs.currentIndex() if isinstance(self.tabs, QTabWidget) else 0
        active = self._lists.get(index)
        if active is not None:
            list_widget, label = active
            ResultScopeController._sync_one(list_widget, self.scope_label, label)
            self.scope_label.setProperty("pathenaKnowledgeScopeTab", index)
            return

        text = "Session review · scope is shown inside the review panel"
        self.scope_label.setText(text)
        self.scope_label.setAccessibleName("Session review scope")
        self.scope_label.setAccessibleDescription(text)
        self.scope_label.setProperty("pathenaResultTotal", None)
        self.scope_label.setProperty("pathenaResultVisible", None)
        self.scope_label.setProperty("pathenaSelectedIdentity", "session review")
        self.scope_label.setProperty("pathenaResultScopeMode", "session-review")
        self.scope_label.setProperty("pathenaKnowledgeScopeTab", index)


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


def _resolve_filter(workspace: QWidget, target: ScopeTarget) -> QLineEdit | None:
    if target.filter_object_name is None:
        return None
    return workspace.findChild(QLineEdit, target.filter_object_name)


def _install_knowledge_scope(window: QWidget) -> KnowledgeTabbedScopeController | None:
    workspace = window.findChild(QWidget, "knowledgeWorkspace")
    if workspace is None:
        return None
    status = getattr(workspace, "browser_status", None)
    if not isinstance(status, QWidget):
        return None
    scope_label = _install_scope_label(
        workspace,
        status,
        "pathenaResultScopeknowledgeWorkspace",
    )
    if scope_label is None:
        return None
    return KnowledgeTabbedScopeController(workspace, scope_label)


def apply_result_scope_clarity(window: QWidget) -> tuple[int, ...]:
    """Install truthful list-scope summaries for existing dense workspaces."""
    controller = ResultScopeController(window)
    knowledge_controller = _install_knowledge_scope(window)
    applied: list[int] = [6101] if knowledge_controller is not None else []

    for offset, target in enumerate(_TARGETS, start=1):
        workspace = window.findChild(QWidget, target.workspace_name)
        if workspace is None:
            continue
        list_widget = getattr(workspace, target.list_attribute, None)
        status = getattr(workspace, target.status_attribute, None)
        if not isinstance(list_widget, QListWidget) or not isinstance(status, QWidget):
            continue
        filter_input = _resolve_filter(workspace, target)

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
    window.setProperty("pathenaKnowledgeResultScopeController", knowledge_controller)
    window.setProperty("pathenaResultScopeTargetCount", len(applied))
    return tuple(applied)
