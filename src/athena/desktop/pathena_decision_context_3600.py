"""Confirmation and decision-context refinements 3501-3600 for pATHENA.

This presentation-only pass clarifies the stage, scope and consequence of existing
review/commit/cancel/restore actions. It also restores keyboard context when an
invoked action disables or hides itself while work begins. Existing previews,
confirmations, file dialogs, domain transitions and persistence behavior are kept.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtWidgets import QAbstractButton, QWidget


@dataclass(frozen=True)
class DecisionTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    anchor_attribute: str | None
    anchor_object_name: str | None
    label: str
    stage: str
    scope: str
    consequence: str
    cancel_path: str


_TARGETS: tuple[DecisionTarget, ...] = (
    DecisionTarget(
        None,
        None,
        "deleteChatButton",
        None,
        "chatSelector",
        "delete conversation",
        "preview then confirm",
        "selected persistent conversation and owned messages",
        "canonical deletion is committed only after the existing preview and confirmation",
        "Cancel or Escape keeps the conversation",
    ),
    DecisionTarget(
        None,
        None,
        "newChatButton",
        None,
        "chatSelector",
        "new conversation",
        "navigate",
        "current conversation view",
        "opens a new empty conversation state without deleting the current conversation",
        "return to the existing conversation from the selector",
    ),
    DecisionTarget(
        None,
        None,
        "sendButton",
        None,
        "promptInput",
        "send message",
        "commit request",
        "current composer text and selected model",
        "submits the current message to the selected local model",
        "edit the composer before activation",
    ),
    DecisionTarget(
        "knowledgeWorkspace",
        "review_accept_button",
        None,
        "review_list",
        None,
        "accept contradiction",
        "review decision",
        "selected pending contradiction",
        "creates the reviewed contradiction evidence through the existing knowledge command",
        "leave the decision pending by not activating",
    ),
    DecisionTarget(
        "knowledgeWorkspace",
        "review_reject_button",
        None,
        "review_list",
        None,
        "reject contradiction",
        "review decision",
        "selected pending contradiction",
        "rejects the selected contradiction without creating semantic evidence",
        "leave the decision pending by not activating",
    ),
    DecisionTarget(
        "knowledgeWorkspace",
        None,
        "knowledgeAcceptanceButton",
        "browser_tabs",
        None,
        "add reviewed items",
        "canonical commit",
        "exact reviewed preflight",
        "commits only the reviewed Knowledge and Claim preflight after revalidation",
        "close or continue review before activating",
    ),
    DecisionTarget(
        "researchWorkspace",
        "start_button",
        None,
        "query_input",
        None,
        "start research",
        "queue",
        "current research question",
        "queues a durable local research run",
        "edit the question before activation",
    ),
    DecisionTarget(
        "researchWorkspace",
        "cancel_button",
        None,
        "jobs",
        None,
        "cancel research",
        "cancel request",
        "selected durable research run",
        "persists a cancellation request for the selected research run",
        "leave the run active by not activating",
    ),
    DecisionTarget(
        "jobsWorkspace",
        "pause_button",
        None,
        "jobs",
        None,
        "pause job",
        "state transition",
        "selected eligible durable job",
        "moves the selected job into its existing paused transition",
        "leave the job in its current state",
    ),
    DecisionTarget(
        "jobsWorkspace",
        "resume_button",
        None,
        "jobs",
        None,
        "resume job",
        "state transition",
        "selected paused durable job",
        "resumes the selected job through the existing durable job service",
        "leave the job paused",
    ),
    DecisionTarget(
        "jobsWorkspace",
        "wake_button",
        None,
        "jobs",
        None,
        "wake job",
        "state transition",
        "selected waiting durable job",
        "requests the existing wake transition for the selected waiting job",
        "leave the job waiting",
    ),
    DecisionTarget(
        "jobsWorkspace",
        "cancel_button",
        None,
        "jobs",
        None,
        "cancel durable job",
        "cancel request",
        "selected non-terminal durable job",
        "persists cancellation for the selected durable job",
        "leave the job active by not activating",
    ),
    DecisionTarget(
        "filesWorkspace",
        "import_button",
        None,
        "sources",
        None,
        "import file",
        "choose then capture",
        "file selected in the existing file dialog",
        "captures selected bytes and queues supported retrieval processing",
        "cancel the file dialog to make no change",
    ),
    DecisionTarget(
        "filesWorkspace",
        "process_button",
        None,
        "sources",
        None,
        "process source",
        "queue processing",
        "selected processable Source",
        "queues canonical representation and chunking or retry",
        "leave the Source unchanged by not activating",
    ),
    DecisionTarget(
        "backupWorkspace",
        "create_button",
        None,
        "snapshots",
        None,
        "create backup",
        "choose target then create",
        "backup target selected in the existing folder dialog",
        "creates and verifies a new backup without modifying the live runtime",
        "cancel the folder dialog to make no change",
    ),
    DecisionTarget(
        "backupWorkspace",
        "verify_button",
        None,
        "snapshots",
        None,
        "verify backup",
        "verify",
        "selected backup snapshot",
        "runs the existing light verification for the selected snapshot",
        "leave verification state unchanged by not activating",
    ),
    DecisionTarget(
        "backupWorkspace",
        "deep_verify_button",
        None,
        "snapshots",
        None,
        "deep verify backup",
        "verify plus restore smoke",
        "selected backup snapshot",
        "hashes backup objects and performs the existing isolated restore smoke",
        "leave verification state unchanged by not activating",
    ),
    DecisionTarget(
        "backupWorkspace",
        "restore_button",
        None,
        "snapshots",
        None,
        "restore isolated",
        "choose destination then restore",
        "selected verified snapshot and newly chosen parent folder",
        "restores only into a new isolated child root and does not overwrite the live runtime",
        "cancel the folder dialog to make no change",
    ),
    DecisionTarget(
        "backupWorkspace",
        "register_target_button",
        None,
        "snapshots",
        None,
        "register backup target",
        "choose then register",
        "folder selected in the existing folder dialog",
        "registers the selected folder as a backup target",
        "cancel the folder dialog to make no change",
    ),
    DecisionTarget(
        "systemWorkspace",
        "refresh_button",
        None,
        None,
        "systemDetail",
        "refresh system",
        "refresh",
        "local runtime status",
        "requests a fresh Core, model and chat status snapshot",
        "no persistent state is changed",
    ),
)

_DIMENSIONS: tuple[str, ...] = (
    "decision stage",
    "decision scope",
    "consequence explanation",
    "safe focus return",
    "cancel path",
)

UI_REFINEMENT_TASKS_3501_3600: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


class DecisionContextController(QObject):
    """Preserve decision context while existing actions transition to busy state."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._anchors: dict[QAbstractButton, QWidget | None] = {}

    def register(self, button: QAbstractButton, anchor: QWidget | None) -> None:
        self._anchors[button] = anchor
        button.clicked.connect(
            lambda _checked=False, source=button: QTimer.singleShot(
                0,
                lambda: self._restore_context_if_needed(source),
            )
        )

    def _restore_context_if_needed(self, source: QAbstractButton) -> None:
        try:
            if source.isVisible() and source.isEnabled():
                return
        except RuntimeError:
            self._anchors.pop(source, None)
            return

        anchor = self._anchors.get(source)
        if anchor is None:
            return

        try:
            if not anchor.isVisibleTo(anchor.window()) or not anchor.isEnabled():
                return
            if anchor.focusPolicy() == Qt.FocusPolicy.NoFocus:
                anchor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            anchor.setFocus(Qt.FocusReason.OtherFocusReason)
            anchor.setProperty("pathenaDecisionFocusReturned", True)
        except RuntimeError:
            self._anchors.pop(source, None)


def _workspace(window: QWidget, name: str | None) -> QWidget:
    if name is None:
        return window
    found = window.findChild(QWidget, name)
    return found if found is not None else window


def _resolve_widget(
    window: QWidget,
    workspace_name: str | None,
    attribute_name: str | None,
    object_name: str | None,
) -> QWidget | None:
    workspace = _workspace(window, workspace_name)
    if attribute_name is not None:
        candidate = getattr(workspace, attribute_name, None)
        return candidate if isinstance(candidate, QWidget) else None
    if object_name is not None:
        return workspace.findChild(QWidget, object_name)
    return None


def apply_ui_refinements_3501_3600(window: QWidget) -> tuple[int, ...]:
    """Apply 100 decision-context outcomes to existing pATHENA actions."""
    controller = DecisionContextController(window)
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        candidate = _resolve_widget(
            window,
            target.workspace_name,
            target.attribute_name,
            target.object_name,
        )
        if not isinstance(candidate, QAbstractButton):
            continue
        anchor = _resolve_widget(
            window,
            target.workspace_name,
            target.anchor_attribute,
            target.anchor_object_name,
        )
        start = 3501 + index * len(_DIMENSIONS)

        candidate.setProperty("pathenaDecisionStage", target.stage)
        applied.append(start)

        candidate.setProperty("pathenaDecisionScope", target.scope)
        applied.append(start + 1)

        candidate.setProperty("pathenaDecisionConsequence", target.consequence)
        candidate.setToolTip(
            f"{target.stage.capitalize()} · Scope: {target.scope}. "
            f"{target.consequence.capitalize()}."
        )
        applied.append(start + 2)

        candidate.setProperty(
            "pathenaDecisionFocusAnchor",
            anchor.objectName() if anchor else "",
        )
        controller.register(candidate, anchor)
        applied.append(start + 3)

        candidate.setProperty("pathenaDecisionCancelPath", target.cancel_path)
        candidate.setAccessibleDescription(
            f"{target.label.capitalize()}. Scope: {target.scope}. "
            f"Consequence: {target.consequence}. Safe path: {target.cancel_path}."
        )
        candidate.setStatusTip(f"Safe path: {target.cancel_path}.")
        applied.append(start + 4)

    window.setProperty("pathenaDecisionContextController", controller)
    window.setProperty(
        "pathenaDecisionContextTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaDecisionContextTaskCount", len(applied))
    return tuple(applied)
