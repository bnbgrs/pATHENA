"""Sixth 100-task, presentation-only refinement pass for pATHENA.

This pass establishes a shared semantic state language for the real Knowledge,
Research, Jobs and Sources workspaces. Twenty visible state surfaces receive five
explicit presentation states: idle, busy, success, error and empty. The helper is
presentation-only and does not alter domain, persistence, API or scheduler state.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_STATE_SURFACES: tuple[tuple[str, str], ...] = (
    ("knowledgeReviewState", "knowledge review state"),
    ("canonicalMemoryTabs", "canonical memory tabs"),
    ("persistentKnowledgeList", "canonical Knowledge list"),
    ("persistentKnowledgeDetails", "canonical Knowledge details"),
    ("persistentClaimList", "canonical Claim list"),
    ("persistentClaimDetails", "canonical Claim details"),
    ("semanticReviewList", "semantic decision list"),
    ("semanticReviewDetails", "semantic decision details"),
    ("researchStatus", "research status"),
    ("researchJobList", "research job list"),
    ("researchDetails", "research details"),
    ("jobsStatus", "durable jobs status"),
    ("schedulerStatus", "scheduler status"),
    ("durableJobList", "durable job list"),
    ("jobDetails", "durable job details"),
    ("sourceStatus", "source status"),
    ("sourceList", "source list"),
    ("sourceDetails", "source details"),
    ("systemDetail", "system runtime detail"),
    ("backupSnapshotList", "backup snapshot list"),
)

_STATE_NAMES: tuple[str, ...] = ("idle", "busy", "success", "error", "empty")

UI_REFINEMENT_TASKS_501_600: tuple[str, ...] = tuple(
    f"Define {state} presentation for {label}"
    for _key, label in _STATE_SURFACES
    for state in _STATE_NAMES
)

_STATE_STYLESHEET = """
QWidget[pathenaStateSurface="true"] {
    border-color: #242424;
}
QWidget[pathenaUiState="busy"] {
    color: #D8B08A;
    border-color: #6E4B31;
}
QWidget[pathenaUiState="success"] {
    color: #AFC9B4;
    border-color: #405947;
}
QWidget[pathenaUiState="error"] {
    color: #E1A19B;
    border-color: #713C38;
}
QWidget[pathenaUiState="empty"] {
    color: #777777;
    border-color: #242424;
}
QWidget[pathenaUiState="idle"] {
    color: #A7A7A7;
}
"""


def set_pathena_ui_state(widget: QWidget, state: str) -> None:
    """Set one quiet semantic UI state and refresh Qt style resolution."""
    if state not in _STATE_NAMES:
        raise ValueError(f"unsupported pATHENA UI state: {state}")
    widget.setProperty("pathenaStateSurface", True)
    widget.setProperty("pathenaUiState", state)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def apply_ui_refinements_501_600(window: QWidget) -> tuple[int, ...]:
    """Register semantic state surfaces and install their restrained visual language."""
    applied: list[int] = []

    for surface_index, (key, _label) in enumerate(_STATE_SURFACES):
        widget = window.findChild(QWidget, key)
        if widget is None:
            continue
        set_pathena_ui_state(widget, "idle")
        start = 501 + surface_index * len(_STATE_NAMES)
        applied.extend(range(start, start + len(_STATE_NAMES)))

    if applied and _STATE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STATE_STYLESHEET}")

    window.setProperty("pathenaUiSemanticStateAppliedCount", len(applied))
    window.setProperty("pathenaUiSemanticStateTaskCount", 100)
    return tuple(applied)
