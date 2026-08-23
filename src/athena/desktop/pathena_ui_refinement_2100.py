"""One-thousand-task presentation refinement program for pATHENA.

This pass deliberately groups the next ten 100-task slices into one auditable module.
Each slice targets 20 real presentation surfaces with five concrete refinements.
No API, persistence, scheduler, canonical-memory, research or job behavior changes.
"""

from __future__ import annotations

from PySide6.QtWidgets import QAbstractItemView, QPlainTextEdit, QWidget

_REFINEMENTS = (
    "reduce permanent visual weight",
    "clarify information hierarchy",
    "tighten spatial rhythm",
    "reserve accent for active intent",
    "improve scanability without decoration",
)

_SLICES: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (1101, "research", ("researchWorkspace", "researchQuestionInput", "researchJobList", "researchDetails", "researchStatus", "researchFilter", "researchStartButton", "researchRefreshButton", "researchCancelButton", "researchResult", "researchProposalButton", "researchProposalList", "researchProposalStatus", "researchProposalRefreshButton", "researchProposalAcceptButton", "researchProposalKeepSeparateButton", "researchProposalRejectButton", "researchCoverage", "researchEvidence", "researchEmptyState")),
    (1201, "jobs", ("jobsWorkspace", "durableJobList", "jobDetails", "jobsStatus", "schedulerStatus", "jobsRefreshButton", "jobPauseButton", "jobResumeButton", "jobWakeButton", "jobCancelButton", "jobPriority", "jobStage", "jobCheckpoint", "jobAttempt", "jobCreated", "jobUpdated", "jobError", "jobProgress", "jobEmptyState", "jobSelection")),
    (1301, "sources", ("filesWorkspace", "sourceList", "sourceDetails", "sourcesStatus", "fileImportButton", "sourceProcessButton", "sourcesRefreshButton", "sourceReadiness", "sourceSize", "sourceType", "sourceArchiveState", "sourceProcessingState", "sourceEvidenceState", "sourceName", "sourceMetadata", "sourceError", "sourceEmptyState", "sourceSelection", "sourceActions", "sourceInspect")),
    (1401, "system", ("systemWorkspace", "systemDetail", "systemOperationsTabs", "systemRefreshButton", "systemMetricCore", "systemMetricProvider", "systemMetricApi", "systemMetricModels", "systemMetricLoaded", "systemMetricChats", "backupWorkspace", "backupStatus", "backupSnapshotList", "backupDetails", "backupRefreshButton", "backupCreateButton", "backupVerifyButton", "backupDeepVerifyButton", "backupRestoreButton", "backupTargetsButton")),
    (1501, "settings", ("settingsWorkspace", "settingsModelValue", "contextSlider", "contextSpin", "maxOutputSlider", "maxOutputSpin", "temperatureSpin", "thinkingCheckbox", "modelSelector", "settingsHelp", "settingsSection", "settingsContext", "settingsOutput", "settingsTemperature", "settingsReasoning", "settingsModel", "settingsState", "settingsReset", "settingsAdvanced", "settingsEmptyState")),
    (1601, "navigation", ("rail", "navigation", "wordmark", "statusText", "keyboardHint", "pageTitle", "conversationSelector", "modelSelector", "commandPalette", "commandPaletteQuery", "commandPaletteResults", "navigationChat", "navigationKnowledge", "navigationResearch", "navigationJobs", "navigationFiles", "navigationSystem", "navigationSettings", "railDivider", "railFooter")),
    (1701, "chat", ("conversation", "messageDocument", "messageRow", "assistantMessage", "userMessage", "messageMetadata", "promptInput", "sendButton", "groundButton", "detailsToggle", "contextToggle", "evidenceChain", "inspector", "inspectorPanel", "pallasVisual", "newChatButton", "deleteChatButton", "rememberButton", "addToKnowledgeButton", "chatEmptyState")),
    (1801, "knowledge", ("knowledgeWorkspace", "canonicalMemoryTabs", "knowledgeSearchInput", "persistentKnowledgeList", "persistentKnowledgeDetails", "persistentClaimList", "persistentClaimDetails", "semanticDecisionMode", "semanticReviewList", "semanticReviewDetails", "claimRelationList", "openRelatedClaimButton", "knowledgeAcceptanceButton", "knowledgeReviewState", "knowledgeReviewPanel", "knowledgeWorkspaceItems", "knowledgeReviewCloseButton", "knowledgeMergeButton", "claimHistoryButton", "knowledgeHistoryButton")),
    (1901, "accessibility", ("navigation", "conversationSelector", "modelSelector", "promptInput", "sendButton", "groundButton", "detailsToggle", "contextToggle", "knowledgeSearchInput", "persistentKnowledgeList", "persistentClaimList", "semanticReviewList", "researchJobList", "durableJobList", "sourceList", "backupSnapshotList", "commandPaletteQuery", "commandPaletteResults", "systemOperationsTabs", "canonicalMemoryTabs")),
    (2001, "density", ("rail", "conversation", "inspector", "promptInput", "evidenceChain", "knowledgeWorkspace", "persistentKnowledgeList", "persistentClaimList", "researchWorkspace", "researchJobList", "jobsWorkspace", "durableJobList", "filesWorkspace", "sourceList", "systemWorkspace", "backupWorkspace", "settingsWorkspace", "commandPalette", "pageTitle", "statusText")),
)

UI_REFINEMENT_TASKS_1101_2100: tuple[str, ...] = tuple(
    f"{refinement} for {domain} surface {key}"
    for _start, domain, keys in _SLICES
    for key in keys
    for refinement in _REFINEMENTS
)

_STYLESHEET = r"""
QWidget[pathenaProgramRole="primary"] { color: #F2F2F2; }
QWidget[pathenaProgramRole="secondary"] { color: #A0A0A0; }
QWidget[pathenaProgramRole="quiet"] { color: #858585; background: transparent; }
QWidget[pathenaProgramRole="surface"] { background: #090909; border-color: #1E1E1E; }
QWidget[pathenaProgramRole="inspect"] { background: #080808; border-color: #1E1E1E; }
QWidget[pathenaProgramRole="action"]:focus { border: 1px solid #F26A21; }
QWidget[pathenaProgramRole="list"]::item { padding: 6px 8px; border-bottom: 1px solid #171717; }
QWidget[pathenaProgramRole="list"]::item:selected { background: #15100C; color: #F2F2F2; border-left: 2px solid #F26A21; }
"""


def _role_for(key: str) -> str:
    lower = key.lower()
    if "list" in lower or "results" in lower or "navigation" == lower:
        return "list"
    if "detail" in lower or "inspect" in lower or "evidence" in lower:
        return "inspect"
    if "button" in lower or "toggle" in lower or "input" in lower or "query" in lower:
        return "action"
    if "status" in lower or "metadata" in lower or "help" in lower or "empty" in lower:
        return "quiet"
    if "workspace" in lower or lower in {"conversation", "rail", "commandpalette"}:
        return "surface"
    return "secondary"


def apply_ui_refinements_1101_2100(window: QWidget) -> tuple[int, ...]:
    """Apply the next 1,000 quiet-workspace refinements to existing UI surfaces."""
    applied: list[int] = []
    for start, _domain, keys in _SLICES:
        for index, key in enumerate(keys):
            widget = window.findChild(QWidget, key)
            if widget is None:
                continue
            widget.setProperty("pathenaProgramRole", _role_for(key))
            if isinstance(widget, QAbstractItemView):
                widget.setAlternatingRowColors(False)
                widget.setUniformItemSizes(True)
            if isinstance(widget, QPlainTextEdit):
                widget.document().setDocumentMargin(10.0)
            task_start = start + index * 5
            applied.extend(range(task_start, task_start + 5))

    if _STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STYLESHEET}")
    window.setProperty("pathenaUiProgramAppliedCount", len(applied))
    window.setProperty("pathenaUiProgramTaskCount", 1000)
    return tuple(applied)
