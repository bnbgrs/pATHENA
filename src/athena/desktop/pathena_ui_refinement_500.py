"""Fifth 100-task, presentation-only refinement pass for pATHENA.

This pass gives 50 real controls an explicit visual action hierarchy and a quiet,
legible disabled state. It changes no controller behavior, persistence, API contract,
scheduler state, or data.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_ACTION_TARGETS: tuple[tuple[str, str, str], ...] = (
    ("@chat_selector", "conversation selector", "inspect"),
    ("@model_selector", "local model selector", "inspect"),
    ("@prompt_input", "message composer", "primary"),
    ("@ground_button", "source grounding", "secondary"),
    ("@send_button", "send message", "primary"),
    ("detailsToggle", "conversation details", "inspect"),
    ("contextToggle", "evidence context", "inspect"),
    ("@new_chat_button", "new conversation", "secondary"),
    ("@delete_chat_button", "delete conversation", "destructive"),
    ("knowledgeSearchInput", "canonical memory search", "inspect"),
    ("persistentKnowledgeList", "canonical Knowledge list", "inspect"),
    ("persistentClaimList", "canonical Claim list", "inspect"),
    ("semanticReviewList", "semantic review list", "inspect"),
    ("claimRelationList", "Claim relation list", "inspect"),
    ("semanticDecisionMode", "semantic decision mode", "secondary"),
    ("openRelatedClaimButton", "related Claim navigation", "inspect"),
    ("knowledgeAcceptanceButton", "canonical acceptance", "primary"),
    ("researchQueryInput", "research question", "primary"),
    ("researchJobFilter", "research run filter", "inspect"),
    ("researchJobList", "research run list", "inspect"),
    ("researchStartButton", "start research", "primary"),
    ("researchRefreshButton", "refresh research", "secondary"),
    ("researchCancelButton", "cancel research", "destructive"),
    ("researchResultButton", "research result", "inspect"),
    ("researchProposeButton", "research proposals", "secondary"),
    ("researchProposalRefreshButton", "refresh proposals", "secondary"),
    ("researchProposalList", "proposal list", "inspect"),
    ("researchProposalAcceptButton", "accept proposal", "primary"),
    ("researchProposalSeparateButton", "keep proposal separate", "secondary"),
    ("researchProposalRejectButton", "reject proposal", "destructive"),
    ("durableJobList", "durable Jobs list", "inspect"),
    ("jobRefreshButton", "refresh Jobs", "secondary"),
    ("jobPauseButton", "pause Job", "secondary"),
    ("jobResumeButton", "resume Job", "primary"),
    ("jobWakeButton", "wake Job", "secondary"),
    ("jobCancelButton", "cancel Job", "destructive"),
    ("sourceList", "source list", "inspect"),
    ("fileImportButton", "file import", "primary"),
    ("fileProcessButton", "source processing", "primary"),
    ("fileRefreshButton", "refresh sources", "secondary"),
    ("systemOperationsTabs", "System operations", "inspect"),
    ("backupSnapshotList", "backup snapshots", "inspect"),
    ("backupCreateButton", "create backup", "primary"),
    ("backupVerifyButton", "verify backup", "secondary"),
    ("backupDeepVerifyButton", "deep verify backup", "secondary"),
    ("backupRestoreButton", "isolated restore", "destructive"),
    ("backupTargetsButton", "backup targets", "inspect"),
    ("backupAddTargetButton", "register backup target", "secondary"),
    ("commandPaletteQuery", "command palette query", "primary"),
    ("commandPaletteResults", "command palette results", "inspect"),
)

UI_REFINEMENT_TASKS_401_500: tuple[str, ...] = (
    *(f"Set visual action hierarchy for {label}: {role}" for _, label, role in _ACTION_TARGETS),
    *(f"Install quiet disabled-state treatment for {label}" for _, label, _ in _ACTION_TARGETS),
)

_STATE_STYLESHEET = """
QWidget[pathenaActionRole="primary"] { border-color: #F26A21; }
QWidget[pathenaActionRole="secondary"] { border-color: #343434; }
QWidget[pathenaActionRole="inspect"] { border-color: #242424; }
QWidget[pathenaActionRole="destructive"] { color: #E9A09A; border-color: #713C38; }
QWidget[pathenaActionRole="destructive"]:focus { border: 1px solid #C85A52; }
QWidget[pathenaDisabledClarity="true"]:disabled {
    color: #666666;
    border-color: #242424;
    background-color: #0B0B0B;
}
"""


def _resolve(window: QWidget, key: str) -> QWidget | None:
    if key.startswith("@"):
        value = getattr(window, key[1:], None)
        return value if isinstance(value, QWidget) else None
    return window.findChild(QWidget, key)


def apply_ui_refinements_401_500(window: QWidget) -> tuple[int, ...]:
    """Apply action hierarchy and legible disabled states to real controls."""
    applied: list[int] = []

    for offset, (key, _label, role) in enumerate(_ACTION_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setProperty("pathenaActionRole", role)
        applied.append(401 + offset)

    for offset, (key, _label, _role) in enumerate(_ACTION_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setProperty("pathenaDisabledClarity", True)
        applied.append(451 + offset)

    if applied and _STATE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STATE_STYLESHEET}")

    window.setProperty("pathenaUiStateClarityAppliedCount", len(applied))
    window.setProperty("pathenaUiStateClarityTaskCount", 100)
    return tuple(applied)
