"""Fourth 100-task, presentation-only refinement pass for pATHENA.

This pass adds concise status-bar guidance to 50 existing interactive controls and
establishes 50 deterministic tab-order links across the real desktop workflow.
It changes no domain state, persistence, API contract, scheduler behavior, or data.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_STATUS_TARGETS: tuple[tuple[str, str, str], ...] = (
    ("@chat_selector", "conversation selector", "Choose the active persisted conversation."),
    ("@model_selector", "local model selector", "Choose the local model for this conversation."),
    ("@prompt_input", "message composer", "Write the next message."),
    ("@ground_button", "source grounding", "Include available local evidence in the next answer."),
    ("@send_button", "send message", "Send the current message."),
    ("detailsToggle", "conversation details", "Show or hide conversation metadata."),
    ("contextToggle", "evidence context", "Show or hide evidence for the latest grounded answer."),
    ("@new_chat_button", "new conversation", "Create a new persisted conversation."),
    ("@delete_chat_button", "delete conversation", "Delete the selected persisted conversation."),
    ("knowledgeSearchInput", "canonical memory search", "Filter canonical Knowledge, Claims, and decisions."),
    ("persistentKnowledgeList", "canonical Knowledge list", "Select a Knowledge item to inspect."),
    ("persistentClaimList", "canonical Claim list", "Select a Claim to inspect."),
    ("semanticReviewList", "semantic review list", "Select an unresolved semantic decision."),
    ("claimRelationList", "Claim relation list", "Select a relation connected to this Claim."),
    ("semanticDecisionMode", "semantic decision mode", "Choose the review decision type."),
    ("openRelatedClaimButton", "related Claim navigation", "Open the Claim referenced by this relation."),
    ("knowledgeAcceptanceButton", "canonical acceptance", "Persist the reviewed accepted material."),
    ("researchQueryInput", "research question", "Enter the question for a durable research run."),
    ("researchJobFilter", "research run filter", "Filter visible research runs."),
    ("researchJobList", "research run list", "Select a research run to inspect."),
    ("researchStartButton", "start research", "Start a durable research run."),
    ("researchRefreshButton", "refresh research", "Reload research state."),
    ("researchCancelButton", "cancel research", "Request cancellation of the selected research run."),
    ("researchResultButton", "research result", "Open the immutable result for this run."),
    ("researchProposeButton", "research proposals", "Create reviewable memory proposals from this result."),
    ("researchProposalRefreshButton", "refresh proposals", "Reload proposals for this result."),
    ("researchProposalList", "proposal list", "Select a proposal for explicit review."),
    ("researchProposalAcceptButton", "accept proposal", "Accept this proposal into canonical memory."),
    ("researchProposalSeparateButton", "keep proposal separate", "Accept without merging into the related entity."),
    ("researchProposalRejectButton", "reject proposal", "Reject without adding to canonical memory."),
    ("durableJobList", "durable Jobs list", "Select a durable background job."),
    ("jobRefreshButton", "refresh Jobs", "Reload durable scheduler state."),
    ("jobPauseButton", "pause Job", "Pause at the next supported checkpoint."),
    ("jobResumeButton", "resume Job", "Continue the selected paused job."),
    ("jobWakeButton", "wake Job", "Make an eligible waiting job runnable."),
    ("jobCancelButton", "cancel Job", "Request durable cancellation of the selected job."),
    ("sourceList", "source list", "Select a captured local source."),
    ("fileImportButton", "file import", "Capture a local file as a durable source."),
    ("fileProcessButton", "source processing", "Process or retry the selected source."),
    ("fileRefreshButton", "refresh sources", "Reload source and processing state."),
    ("systemOperationsTabs", "System operations", "Switch between runtime and Backup / Recovery."),
    ("backupSnapshotList", "backup snapshots", "Select a completed backup snapshot."),
    ("backupCreateButton", "create backup", "Create a verified backup in the selected target."),
    ("backupVerifyButton", "verify backup", "Run light verification for this snapshot."),
    ("backupDeepVerifyButton", "deep verify backup", "Run hash verification and isolated restore smoke check."),
    ("backupRestoreButton", "isolated restore", "Restore only into a newly created isolated root."),
    ("backupTargetsButton", "backup targets", "Show registered backup target folders."),
    ("backupAddTargetButton", "register backup target", "Register a local backup target folder."),
    ("commandPaletteQuery", "command palette query", "Filter available pATHENA commands."),
    ("commandPaletteResults", "command palette results", "Choose a matching pATHENA command."),
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
    *(f"Add concise status guidance for {label}" for _, label, _ in _STATUS_TARGETS),
    *(
        f"Set deterministic tab order: {_TAB_SEQUENCE[index]} -> {_TAB_SEQUENCE[index + 1]}"
        for index in range(len(_TAB_SEQUENCE) - 1)
    ),
)


def _resolve(window: QWidget, key: str) -> QWidget | None:
    if key.startswith("@"):
        value = getattr(window, key[1:], None)
        return value if isinstance(value, QWidget) else None
    return window.findChild(QWidget, key)


def apply_ui_refinements_301_400(window: QWidget) -> tuple[int, ...]:
    """Apply status guidance and deterministic keyboard traversal."""
    applied: list[int] = []

    for offset, (key, _label, status_text) in enumerate(_STATUS_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setStatusTip(status_text)
        applied.append(301 + offset)

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
