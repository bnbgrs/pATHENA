"""Stable assistive names and final reference styling for primary desktop inputs."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit, QWidget

from athena.desktop.pathena_design_tokens import PALETTE, RADII

_REFERENCE_WORKSPACE_STYLESHEET = f"""
QLineEdit[pathenaPrimaryInput="true"] {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    color: {PALETTE.text};
    selection-background-color: {PALETTE.accent};
}}
QLineEdit[pathenaPrimaryInput="true"]:hover {{
    border-color: {PALETTE.border_strong};
}}
QLineEdit[pathenaPrimaryInput="true"]:focus {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.accent};
}}

QWidget#knowledgeWorkspace,
QWidget#researchWorkspace,
QWidget#jobsWorkspace,
QWidget#filesWorkspace {{
    background: {PALETTE.canvas};
}}

QTabWidget#canonicalMemoryTabs::pane {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
}}
QTabWidget#canonicalMemoryTabs QTabBar::tab {{
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    color: {PALETTE.text_subtle};
    padding: 9px 14px;
}}
QTabWidget#canonicalMemoryTabs QTabBar::tab:selected {{
    color: {PALETTE.text};
    border-bottom: 2px solid {PALETTE.accent};
}}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#durableJobList,
QListWidget#sourceList {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    color: {PALETTE.text_muted};
    outline: 0;
}}
QListWidget#persistentKnowledgeList::item,
QListWidget#persistentClaimList::item,
QListWidget#semanticReviewList::item,
QListWidget#researchJobList::item,
QListWidget#durableJobList::item,
QListWidget#sourceList::item {{
    min-height: 34px;
    padding: 5px 9px;
    border-radius: 3px;
}}
QListWidget#persistentKnowledgeList::item:selected,
QListWidget#persistentClaimList::item:selected,
QListWidget#semanticReviewList::item:selected,
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected,
QListWidget#sourceList::item:selected {{
    background: {PALETTE.surface_selected};
    color: {PALETTE.text};
    border-left: 2px solid {PALETTE.accent};
}}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    color: {PALETTE.text_muted};
    selection-background-color: {PALETTE.accent};
}}
QPlainTextEdit#persistentKnowledgeDetails:focus,
QPlainTextEdit#persistentClaimDetails:focus,
QPlainTextEdit#semanticReviewDetails:focus,
QPlainTextEdit#researchDetails:focus,
QPlainTextEdit#jobDetails:focus,
QPlainTextEdit#sourceDetails:focus {{
    border-color: {PALETTE.border_strong};
}}
"""


@dataclass(frozen=True)
class PrimaryInputTarget:
    control: QLineEdit | QPlainTextEdit
    accessible_name: str
    purpose: str
    keyboard_context: str


class PrimaryInputAccessibility(QObject):
    """Describe existing text-entry controls without changing input behavior."""

    def __init__(
        self,
        parent: QWidget,
        targets: tuple[PrimaryInputTarget, ...],
    ) -> None:
        super().__init__(parent)
        self.targets = targets
        for target in targets:
            self._apply(target)
        if _REFERENCE_WORKSPACE_STYLESHEET not in parent.styleSheet():
            parent.setStyleSheet(
                f"{parent.styleSheet()}\n{_REFERENCE_WORKSPACE_STYLESHEET}"
            )

    @staticmethod
    def _apply(target: PrimaryInputTarget) -> None:
        control = target.control
        control.setAccessibleName(target.accessible_name)
        control.setAccessibleDescription(
            f"{target.purpose} {target.keyboard_context}"
        )
        control.setProperty("pathenaPrimaryInput", True)
        control.setProperty("pathenaPrimaryInputPurpose", target.purpose)
        control.setProperty("pathenaPrimaryInputKeyboardContext", target.keyboard_context)


def install_primary_input_accessibility(
    window: QWidget,
    *,
    chat_prompt: QLineEdit | QPlainTextEdit,
    knowledge_filter: QLineEdit,
    research_query: QLineEdit,
    research_filter: QLineEdit,
) -> PrimaryInputAccessibility:
    """Install assistive input purpose on the four existing primary text controls."""
    targets = (
        PrimaryInputTarget(
            chat_prompt,
            "Chat message",
            "Compose the next message for the selected local conversation and model.",
            "Enter or Ctrl+Enter sends using the existing chat behavior.",
        ),
        PrimaryInputTarget(
            knowledge_filter,
            "Knowledge filter",
            "Filter the currently visible canonical Knowledge, Claims, or Decisions view.",
            "Ctrl+F focuses this existing filter while the Knowledge workspace is active.",
        ),
        PrimaryInputTarget(
            research_query,
            "Research question",
            "Enter the question for a new durable local Research run.",
            "Enter uses the existing Start Research action.",
        ),
        PrimaryInputTarget(
            research_filter,
            "Research run filter",
            "Filter the currently listed durable Research runs without changing them.",
            "Typing updates only the visible Research run list.",
        ),
    )
    return PrimaryInputAccessibility(window, targets)
