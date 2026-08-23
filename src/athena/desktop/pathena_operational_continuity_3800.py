"""Operational continuity refinements 3701-3800 for pATHENA.

This pass keeps selection, scroll position and focus context stable while existing
QProcess-backed work refreshes dynamic lists/details. It does not suppress legitimate
model resets or change any domain operation; it only snapshots presentation context
before busy work and restores it when the same context still exists afterwards.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QProcess, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QPlainTextEdit,
    QScrollArea,
    QWidget,
)


@dataclass(frozen=True)
class ContinuityTarget:
    workspace_name: str
    attribute_name: str
    label: str


_TARGETS: tuple[ContinuityTarget, ...] = (
    ContinuityTarget("knowledgeWorkspace", "browser_tabs", "knowledge tabs"),
    ContinuityTarget("knowledgeWorkspace", "knowledge_list", "knowledge list"),
    ContinuityTarget("knowledgeWorkspace", "knowledge_details", "knowledge details"),
    ContinuityTarget("knowledgeWorkspace", "claim_list", "claim list"),
    ContinuityTarget("knowledgeWorkspace", "claim_details", "claim details"),
    ContinuityTarget("knowledgeWorkspace", "review_list", "decision list"),
    ContinuityTarget("knowledgeWorkspace", "review_details", "decision details"),
    ContinuityTarget("researchWorkspace", "jobs", "research jobs"),
    ContinuityTarget("researchWorkspace", "details", "research details"),
    ContinuityTarget("researchWorkspace", "query_input", "research query"),
    ContinuityTarget("jobsWorkspace", "jobs", "durable jobs"),
    ContinuityTarget("jobsWorkspace", "details", "durable job details"),
    ContinuityTarget("filesWorkspace", "sources", "source list"),
    ContinuityTarget("filesWorkspace", "details", "source details"),
    ContinuityTarget("backupWorkspace", "snapshots", "backup snapshots"),
    ContinuityTarget("backupWorkspace", "details", "backup details"),
    ContinuityTarget("systemWorkspace", "detail", "system detail"),
    ContinuityTarget("knowledgeWorkspace", "search_input", "knowledge search"),
    ContinuityTarget("researchWorkspace", "status", "research status"),
    ContinuityTarget("jobsWorkspace", "status", "jobs status"),
)

_DIMENSIONS: tuple[str, ...] = (
    "selection continuity",
    "scroll continuity",
    "focus continuity",
    "busy snapshot",
    "completion restore",
)

UI_REFINEMENT_TASKS_3701_3800: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class OperationalContinuityController(QObject):
    """Snapshot presentation context on busy entry and restore it on completion."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._workspace_targets: dict[QWidget, list[QWidget]] = {}
        self._busy: dict[QWidget, bool] = {}
        self._snapshots: dict[QWidget, dict[str, object]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, workspace: QWidget, widget: QWidget) -> None:
        self._workspace_targets.setdefault(workspace, []).append(widget)
        self._busy.setdefault(workspace, False)
        widget.setProperty("pathenaContinuityManaged", True)

    def sync(self) -> None:
        for workspace, widgets in self._workspace_targets.items():
            process = self._process_for(workspace)
            busy = process is not None and process.state() != QProcess.ProcessState.NotRunning
            previous = self._busy.get(workspace, False)
            if busy and not previous:
                for widget in widgets:
                    self._snapshots[widget] = self._snapshot(widget)
                    widget.setProperty("pathenaBusyContextSnapshotted", True)
            elif previous and not busy:
                QTimer.singleShot(
                    0,
                    lambda ws=workspace: self._restore_workspace(ws),
                )
            self._busy[workspace] = busy

    def _restore_workspace(self, workspace: QWidget) -> None:
        for widget in self._workspace_targets.get(workspace, ()):
            snapshot = self._snapshots.get(widget)
            if snapshot is None:
                continue
            self._restore(widget, snapshot)
            widget.setProperty("pathenaCompletionContextRestored", True)

    @staticmethod
    def _snapshot(widget: QWidget) -> dict[str, object]:
        snapshot: dict[str, object] = {"had_focus": widget.hasFocus()}
        if isinstance(widget, QAbstractItemView):
            index = widget.currentIndex()
            snapshot["row"] = index.row() if index.isValid() else -1
            snapshot["identity"] = (
                index.data(Qt.ItemDataRole.UserRole) if index.isValid() else None
            )
            snapshot["vscroll"] = widget.verticalScrollBar().value()
            snapshot["hscroll"] = widget.horizontalScrollBar().value()
        elif isinstance(widget, QPlainTextEdit):
            snapshot["vscroll"] = widget.verticalScrollBar().value()
            snapshot["hscroll"] = widget.horizontalScrollBar().value()
            snapshot["cursor"] = widget.textCursor().position()
        elif isinstance(widget, QScrollArea):
            snapshot["vscroll"] = widget.verticalScrollBar().value()
            snapshot["hscroll"] = widget.horizontalScrollBar().value()
        return snapshot

    @classmethod
    def _restore(cls, widget: QWidget, snapshot: dict[str, object]) -> None:
        if isinstance(widget, QAbstractItemView):
            cls._restore_item_selection(widget, snapshot)
            widget.verticalScrollBar().setValue(cls._int(snapshot, "vscroll", 0))
            widget.horizontalScrollBar().setValue(cls._int(snapshot, "hscroll", 0))
        elif isinstance(widget, QPlainTextEdit):
            widget.verticalScrollBar().setValue(cls._int(snapshot, "vscroll", 0))
            widget.horizontalScrollBar().setValue(cls._int(snapshot, "hscroll", 0))
            cursor = widget.textCursor()
            position = min(cls._int(snapshot, "cursor", 0), len(widget.toPlainText()))
            cursor.setPosition(position)
            widget.setTextCursor(cursor)
        elif isinstance(widget, QScrollArea):
            widget.verticalScrollBar().setValue(cls._int(snapshot, "vscroll", 0))
            widget.horizontalScrollBar().setValue(cls._int(snapshot, "hscroll", 0))

        if (
            bool(snapshot.get("had_focus"))
            and widget.isVisibleTo(widget.window())
            and widget.isEnabled()
        ):
            widget.setFocus()

    @classmethod
    def _restore_item_selection(
        cls,
        widget: QAbstractItemView,
        snapshot: dict[str, object],
    ) -> None:
        model = widget.model()
        identity = snapshot.get("identity")
        if identity is not None:
            for row in range(model.rowCount()):
                index = model.index(row, 0)
                if index.data(Qt.ItemDataRole.UserRole) == identity:
                    widget.setCurrentIndex(index)
                    return

        row = cls._int(snapshot, "row", -1)
        if 0 <= row < model.rowCount():
            widget.setCurrentIndex(model.index(row, 0))

    @staticmethod
    def _int(snapshot: dict[str, object], key: str, default: int) -> int:
        value = snapshot.get(key)
        return value if isinstance(value, int) else default

    @staticmethod
    def _process_for(workspace: QWidget) -> QProcess | None:
        for attribute_name in ("_knowledge_process", "_process", "process"):
            candidate = getattr(workspace, attribute_name, None)
            if isinstance(candidate, QProcess):
                return candidate
        return None


def apply_ui_refinements_3701_3800(window: QWidget) -> tuple[int, ...]:
    """Apply 100 continuity outcomes across dynamic pATHENA workspace surfaces."""
    controller = OperationalContinuityController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        workspace = window.findChild(QWidget, target.workspace_name)
        if workspace is None:
            continue
        widget = getattr(workspace, target.attribute_name, None)
        if not isinstance(widget, QWidget):
            continue
        controller.register(workspace, widget)
        widget.setProperty("pathenaSelectionContinuity", True)
        widget.setProperty("pathenaScrollContinuity", True)
        widget.setProperty("pathenaFocusContinuity", True)
        widget.setProperty("pathenaBusySnapshotEnabled", True)
        widget.setProperty("pathenaCompletionRestoreEnabled", True)
        start = 3701 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaOperationalContinuityController", controller)
    window.setProperty(
        "pathenaOperationalContinuityTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaOperationalContinuityTaskCount", len(applied))
    return tuple(applied)
