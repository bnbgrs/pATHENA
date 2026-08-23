"""Keyboard discoverability refinements 4101-4200 for pATHENA.

This presentation-only pass documents existing keyboard behavior and native Qt
activation. It does not register new global shortcuts. Hints are limited to behavior
already wired in the desktop shell or standard focused-control activation.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QComboBox, QLineEdit, QWidget


@dataclass(frozen=True)
class KeyboardTarget:
    workspace_name: str | None
    attribute_name: str | None
    object_name: str | None
    label: str
    keyboard_hint: str
    activation_model: str


_TARGETS: tuple[KeyboardTarget, ...] = (
    KeyboardTarget(None, None, "promptInput", "composer input", "Enter sends; Ctrl+Enter also sends", "text-entry"),
    KeyboardTarget(None, None, "sendButton", "send message", "Ctrl+Enter sends from chat; Space activates when focused", "action"),
    KeyboardTarget(None, None, "chatSelector", "conversation selector", "Arrow keys change the focused selection", "selection"),
    KeyboardTarget(None, None, "modelSelector", "model selector", "Arrow keys change the focused model selection", "selection"),
    KeyboardTarget(None, None, "groundButton", "sources toggle", "Space toggles when focused", "toggle"),
    KeyboardTarget(None, None, "detailsToggle", "details toggle", "Space toggles when focused; Escape closes an open disclosure", "toggle"),
    KeyboardTarget(None, None, "contextToggle", "evidence toggle", "Space toggles when focused; Escape closes an open disclosure", "toggle"),
    KeyboardTarget(None, None, "newChatButton", "new conversation", "Space activates when focused", "action"),
    KeyboardTarget(None, None, "deleteChatButton", "delete conversation", "Space opens the existing deletion preview when focused", "action"),
    KeyboardTarget("knowledgeWorkspace", "search_input", None, "knowledge search", "Type to filter canonical memory", "text-entry"),
    KeyboardTarget("knowledgeWorkspace", "review_accept_button", None, "accept contradiction", "Space activates the focused review decision", "decision"),
    KeyboardTarget("knowledgeWorkspace", "review_reject_button", None, "reject contradiction", "Space activates the focused review decision", "decision"),
    KeyboardTarget("researchWorkspace", "query_input", None, "research query", "Enter queues the typed research question", "text-entry"),
    KeyboardTarget("researchWorkspace", "start_button", None, "start research", "Space activates when focused", "action"),
    KeyboardTarget("researchWorkspace", "cancel_button", None, "cancel research", "Space activates the focused cancellation action", "decision"),
    KeyboardTarget("jobsWorkspace", "pause_button", None, "pause job", "Space activates when focused", "decision"),
    KeyboardTarget("jobsWorkspace", "resume_button", None, "resume job", "Space activates when focused", "action"),
    KeyboardTarget("jobsWorkspace", "cancel_button", None, "cancel job", "Space activates the focused cancellation action", "decision"),
    KeyboardTarget("filesWorkspace", "import_button", None, "import file", "Space opens the existing file picker when focused", "action"),
    KeyboardTarget("filesWorkspace", "process_button", None, "process source", "Space activates when focused", "action"),
)

_DIMENSIONS: tuple[str, ...] = (
    "keyboard activation model",
    "truthful keyboard hint",
    "tooltip discovery",
    "focus guidance",
    "assistive keyboard description",
)

UI_REFINEMENT_TASKS_4101_4200: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


def _resolve(window: QWidget, target: KeyboardTarget) -> QWidget | None:
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


def _append_tooltip(widget: QWidget, hint: str) -> None:
    current = widget.toolTip().strip()
    keyboard_line = f"Keyboard: {hint}."
    if keyboard_line in current:
        return
    widget.setToolTip(f"{current}\n{keyboard_line}".strip())


def apply_ui_refinements_4101_4200(window: QWidget) -> tuple[int, ...]:
    """Apply 100 truthful keyboard-discovery outcomes to existing controls."""
    applied: list[int] = []

    for index, target in enumerate(_TARGETS):
        widget = _resolve(window, target)
        if widget is None:
            continue
        start = 4101 + index * len(_DIMENSIONS)

        widget.setProperty("pathenaKeyboardActivationModel", target.activation_model)
        applied.append(start)

        widget.setProperty("pathenaKeyboardHint", target.keyboard_hint)
        widget.setProperty("pathenaShortcutTruthOnly", True)
        applied.append(start + 1)

        _append_tooltip(widget, target.keyboard_hint)
        applied.append(start + 2)

        if widget.focusPolicy() == Qt.FocusPolicy.NoFocus:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        widget.setProperty("pathenaKeyboardDiscoverable", True)
        applied.append(start + 3)

        widget.setAccessibleDescription(
            f"{target.label.capitalize()}. Keyboard: {target.keyboard_hint}."
        )
        widget.setStatusTip(f"Keyboard: {target.keyboard_hint}.")
        applied.append(start + 4)

        if isinstance(widget, QAbstractButton):
            widget.setProperty("pathenaNativeButtonActivation", True)
        elif isinstance(widget, QComboBox):
            widget.setProperty("pathenaNativeSelectionKeys", True)
        elif isinstance(widget, QLineEdit):
            widget.setProperty("pathenaNativeTextEntry", True)

    window.setProperty("pathenaKeyboardDiscoveryTargetCount", len(applied) // len(_DIMENSIONS))
    window.setProperty("pathenaKeyboardDiscoveryTaskCount", len(applied))
    return tuple(applied)
