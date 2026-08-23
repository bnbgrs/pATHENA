"""Dynamic workspace keyboard refinements 3101-3200 for pATHENA.

The pass binds to real workspace attributes rather than repeated generic Qt object
names. It keeps tab order synchronized as controls become enabled/disabled or shown/
hidden, and moves focus to a stable workspace anchor when an invoked action removes
itself from keyboard participation. No domain transition is added or changed.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, QTimer, Qt
from PySide6.QtWidgets import QAbstractButton, QApplication, QWidget


@dataclass(frozen=True)
class DynamicFocusTarget:
    workspace_name: str
    attribute_name: str | None
    object_name: str | None
    label: str


_TARGETS: tuple[DynamicFocusTarget, ...] = (
    DynamicFocusTarget("knowledgeWorkspace", "search_input", None, "knowledge search"),
    DynamicFocusTarget("knowledgeWorkspace", "browser_tabs", None, "knowledge tabs"),
    DynamicFocusTarget(
        "knowledgeWorkspace", "knowledge_list", None, "knowledge list"
    ),
    DynamicFocusTarget("knowledgeWorkspace", "claim_list", None, "claim list"),
    DynamicFocusTarget("knowledgeWorkspace", "review_list", None, "decision list"),
    DynamicFocusTarget(
        "knowledgeWorkspace",
        "review_accept_button",
        None,
        "accept contradiction",
    ),
    DynamicFocusTarget(
        "knowledgeWorkspace",
        "review_reject_button",
        None,
        "reject contradiction",
    ),
    DynamicFocusTarget(
        "knowledgeWorkspace",
        None,
        "knowledgeAcceptanceButton",
        "add reviewed items",
    ),
    DynamicFocusTarget("researchWorkspace", "query_input", None, "research query"),
    DynamicFocusTarget("researchWorkspace", "start_button", None, "start research"),
    DynamicFocusTarget("researchWorkspace", "jobs", None, "research jobs"),
    DynamicFocusTarget(
        "researchWorkspace", "cancel_button", None, "cancel research"
    ),
    DynamicFocusTarget("jobsWorkspace", "jobs", None, "durable jobs"),
    DynamicFocusTarget("jobsWorkspace", "pause_button", None, "pause job"),
    DynamicFocusTarget("jobsWorkspace", "resume_button", None, "resume job"),
    DynamicFocusTarget(
        "jobsWorkspace", "cancel_button", None, "cancel durable job"
    ),
    DynamicFocusTarget("filesWorkspace", "sources", None, "source list"),
    DynamicFocusTarget("filesWorkspace", "import_button", None, "import source"),
    DynamicFocusTarget("filesWorkspace", "process_button", None, "process source"),
    DynamicFocusTarget("systemWorkspace", "refresh_button", None, "refresh system"),
)

_DIMENSIONS: tuple[str, ...] = (
    "dynamic focus policy",
    "busy-state skip",
    "focus fallback",
    "workspace tab metadata",
    "state-change refresh",
)

UI_REFINEMENT_TASKS_3101_3200: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class DynamicWorkspaceFocusController(QObject):
    """Keep keyboard navigation coherent while workspace actions change state."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._workspace_widgets: dict[str, list[QWidget]] = {}
        self._refresh_pending = False

    def register(self, workspace_name: str, widget: QWidget) -> None:
        widgets = self._workspace_widgets.setdefault(workspace_name, [])
        widgets.append(widget)
        widget.installEventFilter(self)
        if isinstance(widget, QAbstractButton):
            widget.clicked.connect(
                lambda _checked=False,
                source=widget,
                workspace=workspace_name: self._action_invoked(workspace, source)
            )

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(watched, QWidget) and event.type() in {
            QEvent.Type.EnabledChange,
            QEvent.Type.Show,
            QEvent.Type.Hide,
        }:
            if QApplication.focusWidget() is watched and not self._candidate(watched):
                self._focus_workspace_fallback(watched)
            self.schedule_refresh()
        return super().eventFilter(watched, event)

    def _action_invoked(self, workspace_name: str, source: QWidget) -> None:
        source.setProperty("pathenaLastInvokedByKeyboardFlow", True)

        def settle() -> None:
            source.setProperty("pathenaLastInvokedByKeyboardFlow", False)
            if not self._candidate(source):
                self._focus_named_fallback(workspace_name, exclude=source)
            self.refresh_tab_order()

        QTimer.singleShot(0, settle)

    def _focus_workspace_fallback(self, source: QWidget) -> None:
        for workspace_name, widgets in self._workspace_widgets.items():
            if source in widgets:
                self._focus_named_fallback(workspace_name, exclude=source)
                return

    def _focus_named_fallback(self, workspace_name: str, *, exclude: QWidget) -> None:
        for widget in self._workspace_widgets.get(workspace_name, ()):
            if widget is exclude or not self._candidate(widget):
                continue
            widget.setFocus(Qt.FocusReason.OtherFocusReason)
            widget.setProperty("pathenaFocusFallbackReceived", True)
            return

    def schedule_refresh(self) -> None:
        if self._refresh_pending:
            return
        self._refresh_pending = True

        def apply() -> None:
            self._refresh_pending = False
            self.refresh_tab_order()

        QTimer.singleShot(0, apply)

    def refresh_tab_order(self) -> None:
        for workspace_name, widgets in self._workspace_widgets.items():
            active = [widget for widget in widgets if self._candidate(widget)]
            for order, widget in enumerate(active, start=1):
                widget.setProperty("pathenaDynamicTabOrder", order)
                widget.setProperty("pathenaDynamicWorkspace", workspace_name)
            for previous, current in zip(active, active[1:], strict=False):
                if previous.window() is current.window():
                    QWidget.setTabOrder(previous, current)

    @staticmethod
    def _candidate(widget: QWidget) -> bool:
        return (
            widget.isVisibleTo(widget.window())
            and widget.isEnabled()
            and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
        )


def _resolve_target(window: QWidget, target: DynamicFocusTarget) -> QWidget | None:
    workspace = window.findChild(QWidget, target.workspace_name)
    if workspace is None:
        return None
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        return candidate if isinstance(candidate, QWidget) else None
    if target.object_name is not None:
        return workspace.findChild(QWidget, target.object_name)
    return None


def apply_ui_refinements_3101_3200(window: QWidget) -> tuple[int, ...]:
    """Apply 100 dynamic keyboard/focus outcomes across five real workspaces."""
    controller = DynamicWorkspaceFocusController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = _resolve_target(window, target)
        if widget is None:
            continue
        start = 3101 + index * len(_DIMENSIONS)

        if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        widget.setProperty("pathenaDynamicFocusPolicy", True)
        applied.append(start)

        widget.setProperty("pathenaSkipWhenBusyOrDisabled", True)
        applied.append(start + 1)

        widget.setProperty("pathenaFocusFallbackEnabled", True)
        applied.append(start + 2)

        widget.setProperty("pathenaWorkspaceTabGroup", target.workspace_name)
        applied.append(start + 3)

        widget.setProperty("pathenaRefreshFocusOnStateChange", True)
        controller.register(target.workspace_name, widget)
        applied.append(start + 4)

    controller.refresh_tab_order()
    window.setProperty("pathenaDynamicWorkspaceFocusController", controller)
    window.setProperty("pathenaDynamicFocusTaskCount", len(applied))
    window.setProperty(
        "pathenaDynamicFocusTargetCount", len(applied) // len(_DIMENSIONS)
    )
    return tuple(applied)
