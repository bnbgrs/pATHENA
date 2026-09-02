"""Action hierarchy and destructive-safety refinements 3401-3500 for pATHENA.

This presentation-only pass classifies existing actions as primary, secondary,
caution or destructive. It gives risky controls explicit visual and assistive cues,
keeps them out of implicit default-button behavior, and preserves the existing domain
confirmation/preview paths without adding a new action or backend transition.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QPushButton, QWidget


@dataclass(frozen=True)
class ActionTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    label: str
    role: str
    risk_copy: str


_TARGETS: tuple[ActionTarget, ...] = (
    ActionTarget(
        None,
        None,
        "sendButton",
        "send message",
        "primary",
        "Sends the current message.",
    ),
    ActionTarget(
        None,
        None,
        "newChatButton",
        "new conversation",
        "secondary",
        "Starts a new empty conversation.",
    ),
    ActionTarget(
        None,
        None,
        "deleteChatButton",
        "delete conversation",
        "destructive",
        "Deletes the selected persistent conversation after the existing preview and "
        "confirmation.",
    ),
    ActionTarget(
        "knowledgeWorkspace",
        "refresh_knowledge_button",
        None,
        "refresh knowledge",
        "secondary",
        "Reloads canonical memory without changing it.",
    ),
    ActionTarget(
        "knowledgeWorkspace",
        "open_chat_button",
        None,
        "open source chat",
        "secondary",
        "Navigates to the source conversation.",
    ),
    ActionTarget(
        "knowledgeWorkspace",
        "review_accept_button",
        None,
        "accept contradiction",
        "caution",
        "Commits the reviewed contradiction decision.",
    ),
    ActionTarget(
        "knowledgeWorkspace",
        "review_reject_button",
        None,
        "reject contradiction",
        "caution",
        "Rejects the selected pending contradiction decision.",
    ),
    ActionTarget(
        "knowledgeWorkspace",
        None,
        "knowledgeAcceptanceButton",
        "add reviewed items",
        "primary",
        "Commits exactly the reviewed canonical preflight.",
    ),
    ActionTarget(
        "researchWorkspace",
        "start_button",
        None,
        "start research",
        "primary",
        "Queues a durable local research run.",
    ),
    ActionTarget(
        "researchWorkspace",
        "refresh_button",
        None,
        "refresh research",
        "secondary",
        "Reloads durable research state.",
    ),
    ActionTarget(
        "researchWorkspace",
        "cancel_button",
        None,
        "cancel research",
        "destructive",
        "Persists a cancellation request for the selected research run.",
    ),
    ActionTarget(
        "jobsWorkspace",
        "refresh_button",
        None,
        "refresh jobs",
        "secondary",
        "Reloads the durable job queue.",
    ),
    ActionTarget(
        "jobsWorkspace",
        "pause_button",
        None,
        "pause job",
        "caution",
        "Pauses an eligible durable job.",
    ),
    ActionTarget(
        "jobsWorkspace",
        "resume_button",
        None,
        "resume job",
        "primary",
        "Resumes the selected paused durable job.",
    ),
    ActionTarget(
        "jobsWorkspace",
        "cancel_button",
        None,
        "cancel job",
        "destructive",
        "Persists cancellation for the selected durable job.",
    ),
    ActionTarget(
        "filesWorkspace",
        "import_button",
        None,
        "import file",
        "primary",
        "Captures a local file and queues supported retrieval processing.",
    ),
    ActionTarget(
        "filesWorkspace",
        "process_button",
        None,
        "process source",
        "primary",
        "Queues processing or retry for the selected Source.",
    ),
    ActionTarget(
        "systemWorkspace",
        "refresh_button",
        None,
        "refresh system",
        "secondary",
        "Refreshes local runtime status.",
    ),
    ActionTarget(
        "backupWorkspace",
        "create_button",
        None,
        "create backup",
        "primary",
        "Creates a verified backup using the existing BackupService.",
    ),
    ActionTarget(
        "backupWorkspace",
        "restore_button",
        None,
        "restore isolated",
        "caution",
        "Restores the selected verified snapshot only into a new isolated root.",
    ),
)

_DIMENSIONS: tuple[str, ...] = (
    "semantic action role",
    "visual action hierarchy",
    "risk cue",
    "keyboard activation safety",
    "assistive action explanation",
)

UI_REFINEMENT_TASKS_3401_3500: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_ACTION_STYLESHEET = """
/* pATHENA action hierarchy 3500 */
QPushButton[pathenaActionRole="primary"] {
    border-color: #F26A21;
}
QPushButton[pathenaActionRole="secondary"] {
    border-color: #2A2A2A;
}
QPushButton[pathenaActionRole="caution"] {
    color: #C9A67B;
    border-color: #665038;
}
QPushButton[pathenaActionRole="destructive"] {
    color: #D59A95;
    border-color: #653C39;
    background: transparent;
}
QPushButton[pathenaActionRole="destructive"]:hover {
    border-color: #87504B;
}
QPushButton[pathenaActionRole="destructive"]:disabled,
QPushButton[pathenaActionRole="caution"]:disabled {
    color: #5C5554;
    border-color: #282525;
}
"""


def _resolve_target(window: QWidget, target: ActionTarget) -> QAbstractButton | None:
    if target.workspace_name is None:
        if target.object_name is None:
            return None
        return window.findChild(QAbstractButton, target.object_name)

    workspace = window.findChild(QWidget, target.workspace_name)
    if workspace is None:
        return None
    if target.attribute_name is not None:
        candidate = getattr(workspace, target.attribute_name, None)
        return candidate if isinstance(candidate, QAbstractButton) else None
    if target.object_name is not None:
        return workspace.findChild(QAbstractButton, target.object_name)
    return None


def _apply_keyboard_safety(button: QAbstractButton, role: str) -> None:
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    button.setProperty(
        "pathenaExplicitActivation",
        role in {"caution", "destructive"},
    )
    if isinstance(button, QPushButton):
        button.setAutoDefault(False)
        if role in {"caution", "destructive"}:
            button.setDefault(False)


def apply_ui_refinements_3401_3500(window: QWidget) -> tuple[int, ...]:
    """Apply 100 hierarchy/safety outcomes to existing pATHENA actions."""
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        button = _resolve_target(window, target)
        if button is None:
            continue
        start = 3401 + index * len(_DIMENSIONS)

        button.setProperty("pathenaActionRole", target.role)
        button.setProperty("pathenaActionHierarchy3500", True)
        applied.append(start)

        button.setProperty("pathenaVisualPriority", target.role)
        applied.append(start + 1)

        button.setProperty("pathenaRiskCue", target.risk_copy)
        risk_level = (
            "high"
            if target.role == "destructive"
            else "medium"
            if target.role == "caution"
            else "normal"
        )
        button.setProperty("pathenaRiskLevel", risk_level)
        applied.append(start + 2)

        _apply_keyboard_safety(button, target.role)
        applied.append(start + 3)

        prefix = (
            "Destructive action. "
            if target.role == "destructive"
            else "Review before activating. "
            if target.role == "caution"
            else ""
        )
        button.setAccessibleDescription(prefix + target.risk_copy)
        button.setStatusTip(prefix + target.risk_copy)
        applied.append(start + 4)

        style = button.style()
        style.unpolish(button)
        style.polish(button)
        button.update()

    if _ACTION_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_ACTION_STYLESHEET}")

    window.setProperty(
        "pathenaActionHierarchyTargetCount",
        len(applied) // len(_DIMENSIONS),
    )
    window.setProperty("pathenaActionHierarchyTaskCount", len(applied))
    return tuple(applied)
