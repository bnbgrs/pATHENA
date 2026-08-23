"""Eleventh 100-task, presentation-only refinement pass for pATHENA.

Canonical memory already exposes Knowledge, Claims, semantic decisions, evidence,
relations and provenance. This pass gives those real surfaces a calmer information
hierarchy: browse first, inspect second, relations third, decisions only when needed.
No canonical-memory data, API contract, persistence or decision behavior is changed.
"""

from __future__ import annotations

from PySide6.QtWidgets import QAbstractItemView, QPlainTextEdit, QWidget

_KNOWLEDGE_SURFACES: tuple[tuple[str, str, str], ...] = (
    ("knowledgeWorkspace", "knowledge workspace", "workspace"),
    ("canonicalMemoryTabs", "canonical memory tabs", "navigation"),
    ("knowledgeSearchInput", "knowledge search", "filter"),
    ("persistentKnowledgeList", "knowledge browser", "browse"),
    ("persistentKnowledgeDetails", "knowledge provenance", "inspect"),
    ("persistentClaimList", "claim browser", "browse"),
    ("persistentClaimDetails", "claim evidence", "inspect"),
    ("semanticDecisionMode", "semantic decision mode", "decision"),
    ("semanticReviewList", "semantic decision browser", "decision"),
    ("semanticReviewDetails", "semantic decision comparison", "decision"),
    ("claimRelationList", "claim relations", "relation"),
    ("openRelatedClaimButton", "related claim navigation", "relation"),
    ("knowledgeAcceptanceButton", "canonical acceptance", "decision"),
    ("knowledgeReviewState", "review state", "status"),
    ("knowledgeReviewPanel", "session review panel", "review"),
    ("knowledgeWorkspaceItems", "session review items", "review"),
    ("knowledgeReviewCloseButton", "review close", "secondary"),
    ("knowledgeMergeButton", "merge decision", "decision"),
    ("claimHistoryButton", "claim history", "secondary"),
    ("knowledgeHistoryButton", "knowledge history", "secondary"),
)

_REFINEMENTS: tuple[str, ...] = (
    "reduce permanent visual weight",
    "clarify browse-to-inspect hierarchy",
    "de-emphasize metadata until inspection",
    "reserve orange for selected intent",
    "tighten evidence and provenance rhythm",
)

UI_REFINEMENT_TASKS_1001_1100: tuple[str, ...] = tuple(
    f"{refinement} for {label}"
    for _key, label, _role in _KNOWLEDGE_SURFACES
    for refinement in _REFINEMENTS
)

_KNOWLEDGE_STYLESHEET = r"""
QWidget[pathenaKnowledgeRole="workspace"] {
    background: #060606;
}
QWidget[pathenaKnowledgeRole="browse"] {
    background: #090909;
    border: 1px solid #1E1E1E;
}
QWidget[pathenaKnowledgeRole="browse"]::item {
    padding: 7px 9px;
    border-bottom: 1px solid #171717;
    color: #B8B8B8;
}
QWidget[pathenaKnowledgeRole="browse"]::item:hover {
    background: #0F0F0F;
    color: #E5E5E5;
}
QWidget[pathenaKnowledgeRole="browse"]::item:selected {
    background: #15100C;
    color: #F2F2F2;
    border-left: 2px solid #F26A21;
}
QWidget[pathenaKnowledgeRole="inspect"] {
    background: #080808;
    border: 1px solid #1E1E1E;
    color: #D5D5D5;
}
QWidget[pathenaKnowledgeRole="relation"] {
    background: transparent;
    border-color: #1E1E1E;
    color: #A9A9A9;
}
QWidget[pathenaKnowledgeRole="decision"] {
    border-color: #2A2420;
}
QWidget[pathenaKnowledgeRole="decision"]:focus {
    border: 1px solid #F26A21;
}
QWidget[pathenaKnowledgeRole="review"] {
    background: #080808;
    border-color: #1E1E1E;
}
QWidget[pathenaKnowledgeRole="status"] {
    color: #929292;
}
QWidget[pathenaKnowledgeRole="secondary"] {
    background: transparent;
    border-color: transparent;
    color: #858585;
}
QWidget[pathenaKnowledgeRole="secondary"]:hover {
    color: #D8D8D8;
    border-color: #242424;
}
QWidget[pathenaKnowledgeRole="filter"] {
    background: #090909;
    border-color: #242424;
}
QWidget[pathenaKnowledgeRole="filter"]:focus {
    border-color: #F26A21;
}
QWidget[pathenaKnowledgeRole="navigation"] {
    background: transparent;
}
"""


def _find(window: QWidget, key: str) -> QWidget | None:
    direct = window.findChild(QWidget, key)
    if direct is not None:
        return direct

    # A few extension controls historically received generic object names. Resolve
    # them conservatively by visible copy, then assign stable presentation identities.
    text_aliases = {
        "openRelatedClaimButton": {"OPEN RELATED CLAIM", "Open related claim"},
        "knowledgeAcceptanceButton": {"ADD TO KNOWLEDGE", "Add to knowledge", "Accept"},
        "knowledgeReviewCloseButton": {"CLOSE", "Close"},
        "knowledgeMergeButton": {"MERGE", "Merge", "KEEP SEPARATE", "Keep separate"},
        "claimHistoryButton": {"HISTORY", "History"},
        "knowledgeHistoryButton": {"HISTORY", "History"},
    }
    aliases = text_aliases.get(key)
    if not aliases:
        return None

    from PySide6.QtWidgets import QPushButton

    candidates = [button for button in window.findChildren(QPushButton) if button.text() in aliases]
    if not candidates:
        return None

    if key == "claimHistoryButton" and len(candidates) > 1:
        widget = candidates[-1]
    else:
        widget = candidates[0]
    widget.setObjectName(key)
    return widget


def apply_ui_refinements_1001_1100(window: QWidget) -> tuple[int, ...]:
    """Apply a quiet browse/inspect/relation/decision hierarchy to canonical memory."""
    applied: list[int] = []

    for surface_index, (key, _label, role) in enumerate(_KNOWLEDGE_SURFACES):
        widget = _find(window, key)
        if widget is None:
            continue
        widget.setProperty("pathenaKnowledgeRole", role)

        if isinstance(widget, QAbstractItemView):
            widget.setAlternatingRowColors(False)
            widget.setUniformItemSizes(True)
        if isinstance(widget, QPlainTextEdit):
            widget.setFrameStyle(0)
            widget.document().setDocumentMargin(10.0)

        start = 1001 + surface_index * len(_REFINEMENTS)
        applied.extend(range(start, start + len(_REFINEMENTS)))

    if _KNOWLEDGE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_KNOWLEDGE_STYLESHEET}")

    window.setProperty("pathenaUiKnowledgeHierarchyAppliedCount", len(applied))
    window.setProperty("pathenaUiKnowledgeHierarchyTaskCount", 100)
    return tuple(applied)
