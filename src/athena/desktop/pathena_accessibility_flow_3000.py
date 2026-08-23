"""Accessibility and keyboard-flow refinements 2901-3000 for pATHENA.

This pass only annotates controls that already exist and already have controller or
workspace behavior. It adds explicit assistive names, concise purpose descriptions,
state-independent help, intentional focus participation, and stable focus metadata.
No new domain action is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class AccessibilityTarget:
    object_name: str
    label: str
    accessible_name: str
    description: str
    help_text: str
    focus_policy: Qt.FocusPolicy


_TARGETS: tuple[AccessibilityTarget, ...] = (
    AccessibilityTarget("navigation", "workspace navigation", "Workspace navigation", "Choose the active pATHENA workspace.", "Use arrow keys to move between Chat, Knowledge, Research, Jobs, Files, System and Settings.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("chatSelector", "conversation selector", "Conversation", "Choose an existing local conversation or the new-conversation state.", "Choose the conversation shown in the central workspace.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("newChatButton", "new conversation", "New conversation", "Start a new empty local conversation without deleting the current one.", "Start a new conversation.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("deleteChatButton", "delete conversation", "Delete conversation", "Preview deletion of the selected persistent conversation before committing it.", "Delete the selected conversation after confirmation.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("modelSelector", "local model selector", "Local model", "Choose the local language model used for chat.", "Choose a model exposed by the local provider.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("promptInput", "chat composer", "Message", "Write the next message for the selected local model.", "Type a message. Press Ctrl+Enter to send.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("groundButton", "sources toggle", "Use sources", "Toggle grounding for this message using available local knowledge and evidence.", "Include available sources and evidence in this turn.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("sendButton", "send message", "Send message", "Send the current composer text to the selected local model.", "Send message. Keyboard shortcut: Ctrl+Enter.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("detailsToggle", "details disclosure", "Conversation details", "Show or hide details and provenance for the active conversation.", "Show conversation details only when needed.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("contextToggle", "evidence disclosure", "Sources and evidence", "Show or hide source and evidence context for a grounded response.", "Show sources and evidence for the latest grounded response.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("contextSlider", "context slider", "Context window slider", "Adjust the request context budget for the selected model.", "Adjust context tokens; use the numeric field for an exact value.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("contextSpin", "context value", "Context window tokens", "Set the exact request context budget for the selected model.", "Enter the exact context window in tokens.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("maxOutputSlider", "response length slider", "Maximum response slider", "Adjust the maximum response token budget for the selected model.", "Adjust maximum response length; use the numeric field for an exact value.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("maxOutputTokens", "response length value", "Maximum response tokens", "Set the exact maximum response token budget for the selected model.", "Enter the maximum response length in tokens.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("temperatureSpin", "temperature value", "Temperature", "Adjust sampling temperature for the selected local model.", "Lower values are more deterministic; higher values allow more variation.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("thinkingToggle", "reasoning toggle", "Model reasoning", "Allow model reasoning when the selected model supports it.", "Toggle reasoning for the selected model.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("knowledgeReviewCloseButton", "knowledge review close", "Close knowledge review", "Close the current knowledge extraction review without changing canonical knowledge.", "Close this review panel.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("inspectorCopyButton", "copy provenance", "Copy provenance", "Copy the currently displayed provenance text to the clipboard.", "Copy provenance details.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("knowledgeReviewScroll", "knowledge review content", "Knowledge review", "Scrollable review of extracted knowledge, claims and merge decisions.", "Review extracted knowledge before accepting canonical changes.", Qt.FocusPolicy.StrongFocus),
    AccessibilityTarget("chatScroll", "conversation document", "Conversation messages", "Scrollable document containing the active conversation.", "Read the active conversation; the composer follows after the message document.", Qt.FocusPolicy.StrongFocus),
)

_DIMENSIONS: tuple[str, ...] = (
    "accessible name",
    "assistive description",
    "context help",
    "keyboard focus policy",
    "focus-order metadata",
)

UI_REFINEMENT_TASKS_2901_3000: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


def apply_ui_refinements_2901_3000(window: QWidget) -> tuple[int, ...]:
    """Apply 100 explicit accessibility outcomes to existing UI surfaces."""
    applied: list[int] = []
    focus_widgets: list[QWidget] = []

    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.object_name)
        if widget is None:
            continue
        start = 2901 + index * len(_DIMENSIONS)

        widget.setAccessibleName(target.accessible_name)
        applied.append(start)

        widget.setAccessibleDescription(target.description)
        applied.append(start + 1)

        widget.setToolTip(target.help_text)
        widget.setStatusTip(target.help_text)
        applied.append(start + 2)

        widget.setFocusPolicy(target.focus_policy)
        applied.append(start + 3)

        widget.setProperty("pathenaFocusOrder", index + 1)
        widget.setProperty("pathenaAccessibility3000", True)
        applied.append(start + 4)
        focus_widgets.append(widget)

    for previous, current in zip(focus_widgets, focus_widgets[1:]):
        QWidget.setTabOrder(previous, current)

    window.setProperty("pathenaAccessibilityTargetCount", len(focus_widgets))
    window.setProperty("pathenaAccessibilityTaskCount", len(applied))
    return tuple(applied)
