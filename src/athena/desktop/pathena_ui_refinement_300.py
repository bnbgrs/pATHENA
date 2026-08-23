"""Third 100-task, presentation-only refinement pass for pATHENA.

The pass repairs six Backup QObject identities required by the existing accessibility
layer, then adds contextual What's This help and explicit keyboard focus semantics
to 47 real interactive controls. No domain, persistence, API or scheduler behavior
is changed.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

_BACKUP_OBJECT_NAMES: tuple[tuple[str, str], ...] = (
    ("CREATE BACKUP…", "backupCreateButton"),
    ("VERIFY", "backupVerifyButton"),
    ("DEEP VERIFY", "backupDeepVerifyButton"),
    ("RESTORE ISOLATED…", "backupRestoreButton"),
    ("TARGETS", "backupTargetsButton"),
    ("REGISTER TARGET…", "backupAddTargetButton"),
)

_TARGETS: tuple[tuple[str, str, str], ...] = (
    ("@prompt_input", "message composer", "Compose the next local pATHENA message."),
    ("@ground_button", "source grounding", "Toggle local-source grounding for the next answer."),
    ("@send_button", "send message", "Send the current message using the selected local model."),
    ("detailsToggle", "conversation details", "Reveal conversation metadata only when it is needed."),
    ("contextToggle", "evidence context", "Reveal evidence used by the latest grounded answer."),
    ("@new_chat_button", "new conversation", "Create a new persisted local conversation."),
    ("@delete_chat_button", "delete conversation", "Delete the currently selected persisted conversation."),
    ("knowledgeSearchInput", "canonical memory search", "Filter canonical Knowledge, Claims and decisions."),
    ("persistentKnowledgeList", "canonical Knowledge list", "Choose a durable Knowledge item to inspect."),
    ("persistentClaimList", "canonical Claim list", "Choose a canonical Claim to inspect evidence and relations."),
    ("semanticReviewList", "semantic review list", "Choose an unresolved semantic-memory decision."),
    ("claimRelationList", "Claim relation list", "Choose an explicit relation connected to the selected Claim."),
    ("semanticDecisionMode", "semantic decision mode", "Choose the supported decision type for the selected review item."),
    ("openRelatedClaimButton", "related Claim navigation", "Open the Claim referenced by the selected relation."),
    ("knowledgeAcceptanceButton", "canonical acceptance", "Persist only the currently reviewed accepted material."),
    ("researchQueryInput", "research question", "Describe the question for a durable local research run."),
    ("researchJobFilter", "research run filter", "Filter visible research runs without changing stored state."),
    ("researchJobList", "research run list", "Choose a durable research run to inspect."),
    ("researchStartButton", "start research", "Create a durable research job for the current question."),
    ("researchRefreshButton", "refresh research", "Reload current durable research state."),
    ("researchCancelButton", "cancel research", "Request cancellation of the selected research run."),
    ("researchResultButton", "research result", "Open the immutable result for the selected completed run."),
    ("researchProposeButton", "research proposals", "Create reviewable canonical-memory proposals from this result."),
    ("researchProposalRefreshButton", "refresh proposals", "Reload proposal state for the selected result."),
    ("researchProposalList", "proposal list", "Choose a research-derived proposal for explicit review."),
    ("researchProposalAcceptButton", "accept proposal", "Accept the selected proposal into canonical memory."),
    ("researchProposalSeparateButton", "keep proposal separate", "Accept the proposal without merging it into the related entity."),
    ("researchProposalRejectButton", "reject proposal", "Reject the selected proposal without adding it to canonical memory."),
    ("durableJobList", "durable Jobs list", "Choose a background job to inspect checkpoints and controls."),
    ("jobRefreshButton", "refresh Jobs", "Reload durable scheduler state."),
    ("jobPauseButton", "pause Job", "Request a safe pause at the next supported checkpoint."),
    ("jobResumeButton", "resume Job", "Continue the selected paused durable job."),
    ("jobWakeButton", "wake Job", "Make an eligible waiting job runnable again."),
    ("jobCancelButton", "cancel Job", "Request durable cancellation of the selected job."),
    ("sourceList", "source list", "Choose a captured local source to inspect."),
    ("fileImportButton", "file import", "Capture a local file as a durable source."),
    ("fileProcessButton", "source processing", "Process or retry the selected captured source."),
    ("fileRefreshButton", "refresh sources", "Reload the durable source list and processing state."),
    ("systemOperationsTabs", "System operations", "Switch between runtime status and verified Backup / Recovery."),
    ("backupSnapshotList", "backup snapshots", "Choose a completed backup snapshot to inspect or verify."),
    ("backupCreateButton", "create backup", "Create a verified pATHENA backup in the selected target folder."),
    ("backupVerifyButton", "verify backup", "Run light verification for the selected backup snapshot."),
    ("backupDeepVerifyButton", "deep verify backup", "Hash backup objects and run the isolated restore smoke check."),
    ("backupRestoreButton", "isolated restore", "Restore the selected snapshot only into a newly created isolated root."),
    ("backupTargetsButton", "backup targets", "Show registered backup target folders."),
    ("backupAddTargetButton", "register backup target", "Register a local folder as an available backup target."),
    ("commandPaletteQuery", "command palette query", "Type to filter available pATHENA commands."),
)

UI_REFINEMENT_TASKS_201_300: tuple[str, ...] = (
    *(f"Repair Backup object identity: {name}" for _, name in _BACKUP_OBJECT_NAMES),
    *(f"Add contextual What's This help for {label}" for _, label, _ in _TARGETS),
    *(f"Guarantee keyboard focus for {label}" for _, label, _ in _TARGETS),
)


def _resolve(window: QWidget, key: str) -> QWidget | None:
    if key.startswith("@"):
        value = getattr(window, key[1:], None)
        return value if isinstance(value, QWidget) else None
    return window.findChild(QWidget, key)


def apply_ui_refinement_target_repairs(window: QWidget) -> tuple[int, ...]:
    """Repair Backup object identities before earlier accessibility passes run."""
    backup = window.findChild(QWidget, "backupWorkspace")
    if backup is None:
        return ()

    applied: list[int] = []
    buttons = backup.findChildren(QPushButton)
    for offset, (text, object_name) in enumerate(_BACKUP_OBJECT_NAMES):
        button = next((candidate for candidate in buttons if candidate.text() == text), None)
        if button is None:
            continue
        button.setObjectName(object_name)
        applied.append(201 + offset)
    return tuple(applied)


def apply_ui_refinements_207_300(window: QWidget) -> tuple[int, ...]:
    """Apply contextual help and explicit keyboard focus to real controls."""
    applied: list[int] = []

    for offset, (key, _label, help_text) in enumerate(_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setWhatsThis(help_text)
        applied.append(207 + offset)

    for offset, (key, _label, _help_text) in enumerate(_TARGETS):
        widget = _resolve(window, key)
        if widget is None:
            continue
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        applied.append(254 + offset)

    window.setProperty("pathenaUiContextHelpAppliedCount", len(applied))
    window.setProperty("pathenaUiContextHelpTaskCount", 94)
    return tuple(applied)
