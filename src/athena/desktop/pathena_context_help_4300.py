"""Contextual help and comprehension refinements 4201-4300 for pATHENA.

This presentation-only pass makes existing workspaces easier to understand without
adding a Help workspace or inventing controls. Twenty real surfaces receive concise
purpose, content, mutation, provenance and recovery guidance through native Qt help,
tooltip/status metadata and accessibility descriptions.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class HelpTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    label: str
    purpose: str
    content: str
    mutation: str
    provenance: str
    recovery: str


_TARGETS: tuple[HelpTarget, ...] = (
    HelpTarget(
        None,
        "prompt_input",
        None,
        "composer",
        "Write the next message for the selected local model.",
        "The field contains only the unsent message draft.",
        "Sending creates a chat turn; typing alone changes no persistent data.",
        "Grounded provenance appears only when grounding is enabled and evidence exists.",
        "If sending is unavailable, check the local Core and selected loaded model.",
    ),
    HelpTarget(
        None,
        "chat_selector",
        None,
        "conversation selector",
        "Switch between the new-chat state and persisted conversations.",
        "Entries represent local chat identities and their message counts.",
        "Selecting loads a chat; selection itself does not edit or delete it.",
        "Conversation content remains associated with its persisted local chat identity.",
        "If loading fails, the previous committed conversation remains the safe fallback.",
    ),
    HelpTarget(
        None,
        "model_selector",
        None,
        "model selector",
        "Choose the discovered local language model used for direct chat.",
        "Entries distinguish loaded models from models that are merely available.",
        "Selection changes session inference configuration but does not load a model itself.",
        "Model readiness comes from the local provider discovery snapshot.",
        "If chat stays disabled, load the chosen model in the configured local provider.",
    ),
    HelpTarget(
        None,
        "ground_button",
        None,
        "grounding toggle",
        "Request local Knowledge and Raw Archive evidence for the next turn.",
        "The toggle controls whether the next chat request asks for grounded evidence.",
        "Toggling changes request mode only; it does not alter stored Knowledge.",
        "Grounded responses expose source, claim and knowledge relationships when available.",
        "Turn grounding off for direct model chat when evidence is not required.",
    ),
    HelpTarget(
        "knowledgeWorkspace",
        "browser_tabs",
        None,
        "canonical memory tabs",
        "Move between canonical Knowledge, Claims, pending decisions and session review.",
        "Each tab presents a different existing canonical-memory surface.",
        "Changing tabs is read-only; review actions are separate explicit controls.",
        "Knowledge and Claims retain their existing revision and provenance information.",
        "Use Refresh Knowledge if the visible canonical view appears stale.",
    ),
    HelpTarget(
        "knowledgeWorkspace",
        "knowledge_list",
        None,
        "canonical knowledge list",
        "Browse persisted canonical Knowledge units.",
        "Rows represent current canonical Knowledge entities available to the desktop.",
        "Selecting a row only loads details; it does not mutate canonical memory.",
        "Details expose current revision and provenance through the existing canonical service.",
        "Refresh the current tab if an expected Knowledge item is missing.",
    ),
    HelpTarget(
        "knowledgeWorkspace",
        "claim_list",
        None,
        "canonical claim list",
        "Browse persisted canonical Claims independently from Knowledge units.",
        "Rows represent current Claims returned by the canonical-memory CLI surface.",
        "Selection is read-only and loads the existing Claim detail view.",
        "Claim details preserve evidence and revision provenance supplied by the Core.",
        "Refresh the Claims tab if the visible list no longer matches recent review work.",
    ),
    HelpTarget(
        "knowledgeWorkspace",
        "review_list",
        None,
        "contradiction decisions",
        "Review pending contradiction decisions before an explicit accept or reject action.",
        "Rows are unresolved decisions surfaced by the existing Knowledge review workflow.",
        "Selection is read-only; Accept and Reject are separate explicit state transitions.",
        "The decision detail keeps both claims visible so the evidence can be inspected.",
        "Leave the decision pending when evidence is insufficient; no action is required.",
    ),
    HelpTarget(
        "researchWorkspace",
        "query_input",
        None,
        "research question",
        "Define the question for a new durable local research run.",
        "The field contains the pending research query before it is queued.",
        "Editing is local UI state; Start Research queues the durable run.",
        "Research output retains the existing durable job and source relationships.",
        "Edit the question before starting if the requested scope is unclear.",
    ),
    HelpTarget(
        "researchWorkspace",
        "jobs",
        None,
        "research job list",
        "Inspect durable research runs and select one for detail.",
        "Rows reflect existing research jobs and their current durable state.",
        "Selection does not change a run; Start and Cancel are explicit actions.",
        "Run details are derived from persisted research/job state rather than UI estimates.",
        "Refresh Research when a long-running job appears stale.",
    ),
    HelpTarget(
        "researchWorkspace",
        "details",
        None,
        "research details",
        "Inspect the selected research run, including scope, work items and current state.",
        "The pane shows existing durable research detail returned by pATHENA.",
        "The detail pane itself is read-only.",
        "Displayed state remains tied to the selected persisted research job.",
        "Use Refresh Research if the selected run has advanced in the background.",
    ),
    HelpTarget(
        "jobsWorkspace",
        "jobs",
        None,
        "durable job list",
        "Inspect background work managed by the existing durable scheduler.",
        "Rows show durable job identities and persisted lifecycle states.",
        "Selection is read-only; Pause, Resume, Wake and Cancel are explicit actions.",
        "Job state comes from the durable job service rather than transient UI state.",
        "Refresh Jobs when scheduler state has changed outside the current view.",
    ),
    HelpTarget(
        "jobsWorkspace",
        "details",
        None,
        "job details",
        "Inspect checkpoints, leases and lifecycle information for the selected job.",
        "The pane presents the existing durable-job detail surface.",
        "Reading the pane changes no job state.",
        "Lifecycle information remains associated with the selected durable job identity.",
        "Return to the job list and refresh if the selected job has already transitioned.",
    ),
    HelpTarget(
        "filesWorkspace",
        "sources",
        None,
        "source list",
        "Browse files captured into pATHENA as local Sources.",
        "Rows represent existing Source records and their retrieval-processing state.",
        "Selection is read-only; Import and Process are separate explicit operations.",
        "Source identity and processing state come from the existing local source pipeline.",
        "Refresh or retry processing when a Source remains in a retryable state.",
    ),
    HelpTarget(
        "filesWorkspace",
        "details",
        None,
        "source details",
        "Inspect capture and retrieval readiness for the selected local Source.",
        "The pane shows existing Source metadata and processing output.",
        "Reading details changes no captured bytes or processing state.",
        "The displayed metadata remains tied to the selected Source identity.",
        "Use Process Source only when the existing UI marks the selected Source eligible.",
    ),
    HelpTarget(
        "systemWorkspace",
        "detail",
        None,
        "system detail",
        "Inspect local Core, model and desktop runtime status.",
        "The pane presents the existing runtime snapshot exposed to the desktop.",
        "Refresh requests a new status snapshot and does not mutate domain data.",
        "Status reflects local runtime discovery rather than inferred connectivity.",
        "Refresh System after changing the local provider or Core runtime externally.",
    ),
    HelpTarget(
        "backupWorkspace",
        "snapshots",
        None,
        "backup snapshot list",
        "Browse backups created through the existing verified BackupService.",
        "Rows show snapshot identity, state, verification state and object count.",
        "Selection is read-only; Create, Verify and Restore are explicit operations.",
        "Each row remains tied to the persisted backup snapshot and source commit metadata.",
        "Create a backup if the list is empty; Refresh after external backup changes.",
    ),
    HelpTarget(
        "backupWorkspace",
        "details",
        None,
        "backup details",
        "Inspect verification or restore output for the selected backup workflow.",
        "The pane shows command output from the existing BackupService-backed operations.",
        "Reading details changes no snapshot or live runtime data.",
        "Restore output refers to the selected snapshot and the isolated destination root.",
        "Deep Verify is the stronger existing check when light verification is insufficient.",
    ),
    HelpTarget(
        "backupWorkspace",
        "restore_button",
        None,
        "isolated restore",
        "Restore the selected snapshot into a newly created isolated child root.",
        "The operation uses the selected verified backup and a user-chosen parent folder.",
        "It creates an isolated restore and does not overwrite the live runtime root.",
        "The restore remains associated with the selected snapshot identity.",
        "Cancel the folder chooser to make no change.",
    ),
    HelpTarget(
        None,
        None,
        "pallasVisualPlaceholder",
        "PALLAS miniature",
        "Reserve a small visual area for the local reactive knowledge visualization.",
        "The current surface is explicitly a renderer placeholder, not a knowledge graph.",
        "The placeholder is presentation-only and performs no domain mutation.",
        "No provenance is implied by the placeholder; evidence stays in real source surfaces.",
        "Use Knowledge, Research and Sources for actionable evidence until rendering exists.",
    ),
)

_DIMENSIONS: tuple[str, ...] = (
    "purpose guidance",
    "content model guidance",
    "mutation boundary guidance",
    "provenance guidance",
    "recovery guidance",
)

UI_REFINEMENT_TASKS_4201_4300: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


def _resolve(window: QWidget, target: HelpTarget) -> QWidget | None:
    workspace = window
    if target.workspace_name is not None:
        found = window.findChild(QWidget, target.workspace_name)
        if found is None:
            return None
        workspace = found
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        return candidate if isinstance(candidate, QWidget) else None
    if target.object_name is not None:
        return workspace.findChild(QWidget, target.object_name)
    return None


def _help_text(target: HelpTarget) -> str:
    return "\n\n".join(
        (
            f"Purpose: {target.purpose}",
            f"Shows: {target.content}",
            f"Changes: {target.mutation}",
            f"Provenance: {target.provenance}",
            f"If needed: {target.recovery}",
        )
    )


def apply_ui_refinements_4201_4300(window: QWidget) -> tuple[int, ...]:
    """Apply 100 contextual-help outcomes to existing pATHENA UI surfaces."""
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = _resolve(window, target)
        if widget is None:
            continue
        start = 4201 + index * len(_DIMENSIONS)

        widget.setProperty("pathenaHelpPurpose", target.purpose)
        applied.append(start)

        widget.setProperty("pathenaHelpContentModel", target.content)
        applied.append(start + 1)

        widget.setProperty("pathenaHelpMutationBoundary", target.mutation)
        applied.append(start + 2)

        widget.setProperty("pathenaHelpProvenance", target.provenance)
        applied.append(start + 3)

        widget.setProperty("pathenaHelpRecovery", target.recovery)
        widget.setWhatsThis(_help_text(target))
        widget.setStatusTip(target.recovery)
        widget.setAccessibleDescription(
            f"{target.label.capitalize()}. {target.purpose} {target.recovery}"
        )
        applied.append(start + 4)

    window.setProperty("pathenaContextHelpTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaContextHelpTaskCount", len(applied))
    return tuple(applied)
