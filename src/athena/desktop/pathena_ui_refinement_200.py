"""Second 100-task, presentation-only refinement pass for pATHENA.

This pass adds complexity-on-demand guidance to real desktop controls. It does not
change domain state, controller wiring, persistence, scheduling, or API behavior.
"""

from PySide6.QtWidgets import QWidget

UI_REFINEMENT_TASKS_101_200: tuple[str, ...] = tuple(
    task
    for label in (
        "message composer",
        "source grounding",
        "send message",
        "conversation details",
        "evidence context",
        "new conversation",
        "delete conversation",
        "context window slider",
        "context window field",
        "response length slider",
        "response length field",
        "temperature",
        "reasoning",
        "canonical memory search",
        "canonical knowledge list",
        "canonical knowledge details",
        "canonical claim list",
        "canonical claim details",
        "semantic review list",
        "semantic review details",
        "claim relation list",
        "semantic decision mode",
        "open related claim",
        "accept reviewed knowledge",
        "research question",
        "research run filter",
        "research run list",
        "research run details",
        "start research",
        "refresh research",
        "cancel research",
        "view research result",
        "create research proposals",
        "refresh research proposals",
        "research proposal list",
        "accept research proposal",
        "keep research proposal separate",
        "reject research proposal",
        "durable jobs list",
        "job details",
        "refresh jobs",
        "pause job",
        "resume job",
        "wake job",
        "cancel job",
        "source list",
        "source details",
        "import source",
        "process source",
        "refresh sources",
    )
    for task in (f"Add concise tooltip for {label}", f"Add status guidance for {label}")
)


# (attribute-or-object-name, tooltip, status-tip). A leading '@' means an attribute
# on PathenaMainWindow; all other names are real QObject names installed before this
# pass runs in desktop.app.
_GUIDANCE: tuple[tuple[str, str, str], ...] = (
    ("@prompt_input", "Message pATHENA", "Type a message; Ctrl+Enter sends it."),
    (
        "@ground_button",
        "Ground the next answer in local sources",
        "Toggle source grounding for the next response.",
    ),
    (
        "@send_button",
        "Send message",
        "Send the current message with the selected model and settings.",
    ),
    (
        "detailsToggle",
        "Show conversation provenance and metadata",
        "Open conversation details only when needed.",
    ),
    (
        "contextToggle",
        "Show evidence used by the latest grounded answer",
        "Reveal or hide grounded evidence.",
    ),
    (
        "@new_chat_button",
        "Start a new conversation",
        "Create a new persisted local conversation.",
    ),
    (
        "@delete_chat_button",
        "Delete the selected conversation",
        "Remove the selected persisted conversation.",
    ),
    (
        "@context_slider",
        "Adjust the context window",
        "Change how much conversation context is sent to the model.",
    ),
    (
        "@context_spin",
        "Set the context window precisely",
        "Enter the context-window token count directly.",
    ),
    (
        "@max_output_slider",
        "Adjust maximum response length",
        "Change the response-token budget.",
    ),
    (
        "@max_output_spin",
        "Set maximum response tokens precisely",
        "Enter the response-token budget directly.",
    ),
    (
        "@temperature_spin",
        "Adjust response variability",
        "Lower values are more deterministic; higher values are more varied.",
    ),
    (
        "@thinking_checkbox",
        "Enable model reasoning when supported",
        "Toggle the selected model's reasoning mode.",
    ),
    (
        "knowledgeSearchInput",
        "Search canonical Knowledge, Claims and decisions",
        "Filter durable canonical memory without changing it.",
    ),
    (
        "persistentKnowledgeList",
        "Canonical Knowledge",
        "Select a durable Knowledge item to inspect provenance and history.",
    ),
    (
        "persistentKnowledgeDetails",
        "Knowledge details and provenance",
        "Read the selected durable Knowledge item; this view is non-editing.",
    ),
    (
        "persistentClaimList",
        "Canonical Claims",
        "Select a Claim to inspect evidence and relationships.",
    ),
    (
        "persistentClaimDetails",
        "Claim evidence and provenance",
        "Read evidence and provenance for the selected Claim.",
    ),
    (
        "semanticReviewList",
        "Items requiring a semantic decision",
        "Select an unresolved canonical-memory decision.",
    ),
    (
        "semanticReviewDetails",
        "Compare the proposed and canonical entities",
        "Review evidence before confirming a semantic decision.",
    ),
    (
        "claimRelationList",
        "Related Claims and evidence",
        "Inspect explicit relations for the selected Claim.",
    ),
    (
        "semanticDecisionMode",
        "Choose the semantic decision type",
        "Switch between supported review decisions for the selected item.",
    ),
    (
        "openRelatedClaimButton",
        "Open the related Claim",
        "Navigate to the Claim referenced by the selected relation.",
    ),
    (
        "knowledgeAcceptanceButton",
        "Add reviewed material to canonical memory",
        "Persist only the currently reviewed accepted material.",
    ),
    (
        "researchQueryInput",
        "Describe the research question",
        "Create a durable research run across captured local sources.",
    ),
    (
        "researchJobFilter",
        "Filter research runs",
        "Narrow the visible research-run list without changing stored runs.",
    ),
    (
        "researchJobList",
        "Durable research runs",
        "Select a research run to inspect its current state and result.",
    ),
    (
        "researchDetails",
        "Research run details",
        "Read progress, result, and provenance for the selected research run.",
    ),
    (
        "researchStartButton",
        "Start a durable research run",
        "Create a new research job for the current question.",
    ),
    (
        "researchRefreshButton",
        "Refresh research runs",
        "Reload current durable research state.",
    ),
    (
        "researchCancelButton",
        "Cancel the selected research run",
        "Request cancellation of the selected durable research job.",
    ),
    (
        "researchResultButton",
        "View the immutable research result",
        "Open the result associated with the selected completed run.",
    ),
    (
        "researchProposeButton",
        "Create canonical-memory proposals",
        "Derive reviewable Knowledge and Claim proposals from this result.",
    ),
    (
        "researchProposalRefreshButton",
        "Refresh research proposals",
        "Reload proposal state for the selected research result.",
    ),
    (
        "researchProposalList",
        "Research-derived memory proposals",
        "Select a proposal for explicit review before persistence.",
    ),
    (
        "researchProposalAcceptButton",
        "Accept the selected proposal",
        "Persist the selected reviewed proposal into canonical memory.",
    ),
    (
        "researchProposalSeparateButton",
        "Keep the proposal as a separate entity",
        "Accept without merging it into the related canonical entity.",
    ),
    (
        "researchProposalRejectButton",
        "Reject the selected proposal",
        "Mark the selected proposal rejected without adding it to canonical memory.",
    ),
    (
        "durableJobList",
        "Durable background jobs",
        "Select a background job to inspect checkpoints and controls.",
    ),
    (
        "jobDetails",
        "Background job details",
        "Read state, checkpoints, and recovery information for the selected job.",
    ),
    (
        "jobRefreshButton",
        "Refresh background jobs",
        "Reload durable scheduler state.",
    ),
    (
        "jobPauseButton",
        "Pause the selected job",
        "Request a safe pause at the next supported checkpoint.",
    ),
    (
        "jobResumeButton",
        "Resume the selected job",
        "Continue a paused durable job.",
    ),
    (
        "jobWakeButton",
        "Wake the selected job",
        "Make an eligible waiting job runnable again.",
    ),
    (
        "jobCancelButton",
        "Cancel the selected job",
        "Request durable cancellation of the selected job.",
    ),
    (
        "sourceList",
        "Captured local sources",
        "Select a source to inspect capture and processing state.",
    ),
    (
        "sourceDetails",
        "Source capture and retrieval details",
        "Read metadata and processing information for the selected source.",
    ),
    (
        "fileImportButton",
        "Import a local file",
        "Capture a file as a durable local source.",
    ),
    (
        "fileProcessButton",
        "Process or retry the selected source",
        "Run the supported processing path for the selected captured source.",
    ),
    (
        "fileRefreshButton",
        "Refresh imported sources",
        "Reload the durable source list and current processing state.",
    ),
)


def _resolve(window: QWidget, key: str) -> QWidget | None:
    if key.startswith("@"):
        value = getattr(window, key[1:], None)
        return value if isinstance(value, QWidget) else None
    return window.findChild(QWidget, key)


def apply_ui_refinements_101_200(window: QWidget) -> tuple[int, ...]:
    """Apply tooltip/status guidance and return the applied task IDs (101..200)."""
    applied: list[int] = []
    task_id = 101
    for key, tooltip, status_tip in _GUIDANCE:
        widget = _resolve(window, key)
        if widget is not None:
            widget.setToolTip(tooltip)
            applied.append(task_id)
            widget.setStatusTip(status_tip)
            applied.append(task_id + 1)
        task_id += 2

    window.setProperty("pathenaUiGuidanceAppliedCount", len(applied))
    window.setProperty("pathenaUiGuidanceTaskCount", len(UI_REFINEMENT_TASKS_101_200))
    return tuple(applied)
