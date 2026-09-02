"""Error-state coverage and consistency refinements 4401-4500 for pATHENA.

Older desktop paths sometimes expose a failure only as visible status/detail text while
newer presentation layers consume the semantic ``pathenaUiState`` property. This
presentation-only pass bridges those existing signals. It never catches, retries,
changes, suppresses or reinterprets a backend/domain failure; it only mirrors explicit
visible failure/busy/success language into the existing UI-state vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QWidget


@dataclass(frozen=True)
class CoverageTarget:
    object_name: str
    label: str
    source_workspace: str
    source_attribute: str


_TARGETS: tuple[CoverageTarget, ...] = (
    CoverageTarget("knowledgeReviewState", "knowledge review state", "knowledgeWorkspace", "state"),
    CoverageTarget("canonicalMemoryTabs", "canonical memory tabs", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("persistentKnowledgeList", "knowledge list", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("persistentKnowledgeDetails", "knowledge details", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("persistentClaimList", "claim list", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("persistentClaimDetails", "claim details", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("semanticReviewList", "decision list", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("semanticReviewDetails", "decision details", "knowledgeWorkspace", "browser_status"),
    CoverageTarget("researchStatus", "research status", "researchWorkspace", "status"),
    CoverageTarget("researchJobList", "research job list", "researchWorkspace", "status"),
    CoverageTarget("researchDetails", "research details", "researchWorkspace", "status"),
    CoverageTarget("jobsStatus", "jobs status", "jobsWorkspace", "status"),
    CoverageTarget("schedulerStatus", "scheduler status", "jobsWorkspace", "scheduler_status"),
    CoverageTarget("durableJobList", "durable job list", "jobsWorkspace", "status"),
    CoverageTarget("jobDetails", "job details", "jobsWorkspace", "status"),
    CoverageTarget("sourceStatus", "source status", "filesWorkspace", "status"),
    CoverageTarget("sourceList", "source list", "filesWorkspace", "status"),
    CoverageTarget("sourceDetails", "source details", "filesWorkspace", "status"),
    CoverageTarget("systemDetail", "system detail", "systemWorkspace", "detail"),
    CoverageTarget("backupSnapshotList", "backup snapshots", "backupWorkspace", "status"),
)

_DIMENSIONS: tuple[str, ...] = (
    "semantic state coverage",
    "visible signal binding",
    "explicit failure normalization",
    "recovery state clearing",
    "coverage diagnostics",
)

UI_REFINEMENT_TASKS_4401_4500: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_ERROR_TOKENS = (
    " failed",
    "failed ",
    "failure",
    " error",
    "error ",
    "unavailable",
    "disconnected",
    "could not",
    "cannot ",
    "unable to",
    "exit ",
)
_BUSY_TOKENS = (
    "loading ",
    "refreshing ",
    "creating ",
    "verifying ",
    "restoring ",
    "processing ",
    "running ",
    "starting ",
    "cancelling ",
    "canceling ",
    "pausing ",
    "resuming ",
)
_SUCCESS_TOKENS = (
    " completed",
    "complete",
    " created",
    " restored",
    " loaded",
    " ready",
    " succeeded",
)


class ErrorStateCoverageController(QObject):
    """Normalize explicit visible operation text into the existing UI-state property."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._bindings: list[tuple[QWidget, QWidget, CoverageTarget]] = []
        self._last_text: dict[QWidget, str] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(
        self,
        widget: QWidget,
        source: QWidget,
        target: CoverageTarget,
    ) -> None:
        self._bindings.append((widget, source, target))
        widget.setProperty("pathenaErrorCoverageManaged", True)
        widget.setProperty("pathenaErrorCoverageSource", target.source_attribute)
        widget.setProperty("pathenaErrorCoverageLabel", target.label)
        self._sync_one(widget, source)

    def sync(self) -> None:
        for widget, source, _target in self._bindings:
            self._sync_one(widget, source)

    def _sync_one(self, widget: QWidget, source: QWidget) -> None:
        text = self._visible_text(source).strip()
        previous_text = self._last_text.get(widget)
        if previous_text == text:
            return
        self._last_text[widget] = text

        normalized = f" {text.casefold()} "
        inferred = self._classify(normalized)
        previous_state = str(widget.property("pathenaUiState") or "idle")
        managed_state = str(widget.property("pathenaCoverageOwnedState") or "")

        widget.setProperty("pathenaErrorCoverageSignal", text[:240])
        widget.setProperty("pathenaErrorCoverageClassification", inferred or "neutral")

        if inferred is not None:
            widget.setProperty("pathenaUiState", inferred)
            widget.setProperty("pathenaCoverageOwnedState", inferred)
            return

        if managed_state and previous_state == managed_state:
            widget.setProperty("pathenaUiState", "idle")
            widget.setProperty("pathenaCoverageOwnedState", "")

    @staticmethod
    def _classify(normalized: str) -> str | None:
        if any(token in normalized for token in _ERROR_TOKENS):
            return "error"
        if any(token in normalized for token in _BUSY_TOKENS):
            return "busy"
        if any(token in normalized for token in _SUCCESS_TOKENS):
            return "success"
        return None

    @staticmethod
    def _visible_text(widget: QWidget) -> str:
        if isinstance(widget, QLabel):
            return widget.text()
        if isinstance(widget, QPlainTextEdit):
            return widget.toPlainText()
        return ""


def _source_for(window: QWidget, target: CoverageTarget) -> QWidget | None:
    workspace = window.findChild(QWidget, target.source_workspace)
    if workspace is None:
        return None
    candidate = getattr(workspace, target.source_attribute, None)
    return candidate if isinstance(candidate, QWidget) else None


def apply_ui_refinements_4401_4500(window: QWidget) -> tuple[int, ...]:
    """Apply 100 semantic error-state coverage outcomes to existing UI surfaces."""
    controller = ErrorStateCoverageController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        source = _source_for(window, target)
        if widget is None or source is None:
            continue
        controller.register(widget, source, target)
        start = 4401 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaErrorStateCoverageController", controller)
    window.setProperty(
        "pathenaErrorStateCoverageTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaErrorStateCoverageTaskCount", len(applied))
    return tuple(applied)
