"""Fourth 100-task, presentation-only refinement pass for pATHENA.

This pass gives 50 existing interactive controls a restrained, visible keyboard-focus
cue and establishes 50 deterministic tab-order links across the real desktop workflow.
It changes no domain state, persistence, API contract, scheduler behavior, or data.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_FOCUS_TARGETS: tuple[tuple[str, str], ...] = (
    ("@chat_selector", "conversation selector"),
    ("@model_selector", "local model selector"),
    ("@prompt_input", "message composer"),
    ("@ground_button", "source grounding"),
    ("@send_button", "send message"),
    ("detailsToggle", "conversation details"),
    ("contextToggle", "evidence context"),
    ("@new_chat_button", "new conversation"),
    ("@delete_chat_button", "delete conversation"),
    ("knowledgeSearchInput", "canonical memory search"),
    ("persistentKnowledgeList", "canonical Knowledge list"),
    ("persistentClaimList", "canonical Claim list"),
    ("semanticReviewList", "semantic review list"),
    ("claimRelationList", "Claim relation list"),
    ("semanticDecisionMode", "semantic decision mode"),
    ("openRelatedClaimButton", "related Claim navigation"),
    ("knowledgeAcceptanceButton", "canonical acceptance"),
    ("researchQueryInput", "research question"),
    ("researchJobFilter", "research run filter"),
    ("researchJobList", "research run list"),
    ("researchStartButton", "start research"),
    ("researchRefreshButton", "refresh research"),
    ("researchCancelButton", "cancel research"),
    ("researchResultButton", "research result"),
    ("researchProposeButton", "research proposals"),
    ("researchProposalRefreshButton", "refresh proposals"),
    ("researchProposalList", "proposal list"),
    ("researchProposalAcceptButton", "accept proposal"),
    ("researchProposalSeparateButton", "keep proposal separate"),
    ("researchProposalRejectButton", "reject proposal"),
    ("durableJobList", "durable Jobs list"),
    ("jobRefreshButton", "refresh Jobs"),
    ("jobPauseButton", "pause Job"),
    ("jobResumeButton", "resume Job"),
    ("jobWakeButton", "wake Job"),
    ("jobCancelButton", "cancel Job"),
    ("sourceList", "source list"),
    ("fileImportButton", "file import"),
    ("fileProcessButton", "source processing"),
    ("fileRefreshButton", "refresh sources"),
    ("systemOperationsTabs", "System operations"),
    ("backupSnapshotList", "backup snapshots"),
    ("backupCreateButton", "create backup"),
    ("backupVerifyButton", "verify backup"),
    ("backupDeepVerifyButton", "deep verify backup"),
    ("backupRestoreButton", "isolated restore"),
    ("backupTargetsButton", "backup targets"),
    ("backupAddTargetButton", "register backup target"),
    ("commandPaletteQuery", "command palette query"),
    ("commandPaletteResults", "command palette results"),
)

_TAB_SEQUENCE: tuple[str, ...] = (
    "navigation",
    "@chat_selector",
    "@model_selector",
    "@prompt_input",
    "@ground_button",
    "@send_button",
    "detailsToggle",
    "contextToggle",
    "@new_chat_button",
    "@delete_chat_button",
    "knowledgeSearchInput",
    "persistentKnowledgeList",
    "persistentClaimList",
    "semanticReviewList",
    "claimRelationList",
    "semanticDecisionMode",
    "openRelatedClaimButton",
    "knowledgeAcceptanceButton",
    "researchQueryInput",
    "researchJobFilter",
    "researchJobList",
    "researchStartButton",
    "researchRefreshButton",
    "researchCancelButton",
    "researchResultButton",
    "researchProposeButton",
    "researchProposalRefreshButton",
    "researchProposalList",
    "researchProposalAcceptButton",
    "researchProposalSeparateButton",
    "researchProposalRejectButton",
    "durableJobList",
    "jobRefreshButton",
    "jobPauseButton",
    "jobResumeButton",
    "jobWakeButton",
    "jobCancelButton",
    "sourceList",
    "fileImportButton",
    "fileProcessButton",
    "fileRefreshButton",
    "systemOperationsTabs",
    "backupSnapshotList",
    "backupCreateButton",
    "backupVerifyButton",
    "backupDeepVerifyButton",
    "backupRestoreButton",
    "backupTargetsButton",
    "backupAddTargetButton",
    "commandPaletteQuery",
    "commandPaletteResults",
)

UI_REFINEMENT_TASKS_301_400: tuple[str, ...] = (
    *(f"Install restrained visible keyboard-focus cue for {label}" for _, label in _FOCUS_TARGETS),
    *(
        f"Set deterministic tab order: {_TAB_SEQUENCE[index]} -> {_TAB_SEQUENCE[index + 1]}"
        for index in range(len(_TAB_SEQUENCE) - 1)
    ),
)

_FOCUS_STYLESHEET = """
QWidget[pathenaKeyboardFocus="true"]:focus {
    border: 1px solid #F26A21;
}
"""


def _resolve(window: QWidget, key: str) -> QWidget | None:
    if key.startswith("@"):
        value = getattr(window, key[1:], None)
        return value if isinstance(value, QWidget) else None
    return window.findChild(QWidget, key)


def apply_ui_refinements_301_400(window: QWidget) -> tuple[int, ...]:
    """Apply visible focus cues and deterministic keyboard traversal."""
    applied: list[int] = []

    for offset, (key, _label) in enumerate(_FOCUS_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setProperty("pathenaKeyboardFocus", True)
        applied.append(301 + offset)

    if applied and _FOCUS_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_FOCUS_STYLESHEET}")

    for offset in range(len(_TAB_SEQUENCE) - 1):
        before = _resolve(window, _TAB_SEQUENCE[offset])
        after = _resolve(window, _TAB_SEQUENCE[offset + 1])
        if before is None or after is None:
            continue
        QWidget.setTabOrder(before, after)
        applied.append(351 + offset)

    window.setProperty("pathenaUiKeyboardFlowAppliedCount", len(applied))
    window.setProperty("pathenaUiKeyboardFlowTaskCount", 100)
    return tuple(applied)
