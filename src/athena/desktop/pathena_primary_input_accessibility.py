"""Stable assistive names for pATHENA's existing primary text inputs."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLineEdit, QWidget


@dataclass(frozen=True)
class PrimaryInputTarget:
    control: QLineEdit
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

    @staticmethod
    def _apply(target: PrimaryInputTarget) -> None:
        control = target.control
        control.setAccessibleName(target.accessible_name)
        control.setAccessibleDescription(
            f"{target.purpose} {target.keyboard_context}"
        )
        control.setProperty("pathenaPrimaryInputPurpose", target.purpose)
        control.setProperty("pathenaPrimaryInputKeyboardContext", target.keyboard_context)


def install_primary_input_accessibility(
    window: QWidget,
    *,
    chat_prompt: QLineEdit,
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
