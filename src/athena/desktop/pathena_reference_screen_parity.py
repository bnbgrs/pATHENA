"""Presentation-only parity layer for the eleven pATHENA reference screens.

The August 24 reference family converged on a stable visible information
architecture: CHAT, KNOWLEDGE, RESEARCH, JOBS and SOURCES in the top bar,
with SYSTEM and SETTINGS remaining utility destinations.  The underlying
legacy page indexes are intentionally left untouched here; this module only
normalizes user-facing labels, composer copy, and accessibility text.
"""

from __future__ import annotations

from typing import Final, Protocol, cast

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QLabel, QPushButton


REFERENCE_FAMILY: Final = "11-screen-2026-08-24"
PAGE_LABELS: Final = (
    "Chat",
    "Knowledge",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)
TOP_NAV_LABELS: Final = {
    0: "CHAT",
    1: "KNOWLEDGE",
    2: "RESEARCH",
    3: "JOBS",
    4: "SOURCES",
}
COMPOSER_PLACEHOLDER: Final = "Ask, explore, or build…"


class _Navigation(Protocol):
    currentRowChanged: object

    def currentRow(self) -> int: ...


class ReferenceScreenParity(QObject):
    """Keep the live shell aligned with the selected reference-screen family."""

    def __init__(self, window: object) -> None:
        parent = cast(QObject, window)
        super().__init__(parent)
        self._window = window
        self.setObjectName("referenceScreenParity")
        self._apply_static_presentation()

        navigation = getattr(window, "navigation", None)
        current_row_changed = getattr(navigation, "currentRowChanged", None)
        connect = getattr(current_row_changed, "connect", None)
        if callable(connect):
            connect(self._sync_navigation)

        current_row = getattr(navigation, "currentRow", None)
        index = current_row() if callable(current_row) else 0
        self._sync_navigation(index)

    def _apply_static_presentation(self) -> None:
        window = self._window
        set_property = getattr(window, "setProperty", None)
        if callable(set_property):
            set_property("referenceFamily", REFERENCE_FAMILY)

        for button in getattr(window, "reference_top_nav_buttons", ()):
            if not isinstance(button, QPushButton):
                continue
            raw_index = button.property("pageIndex")
            if not isinstance(raw_index, int):
                continue
            label = TOP_NAV_LABELS.get(raw_index)
            if label is None:
                continue
            button.setText(label)
            button.setToolTip(f"Open {PAGE_LABELS[raw_index]}")
            button.setAccessibleName(PAGE_LABELS[raw_index])

        prompt_input = getattr(window, "prompt_input", None)
        set_placeholder = getattr(prompt_input, "setPlaceholderText", None)
        if callable(set_placeholder):
            set_placeholder(COMPOSER_PLACEHOLDER)
        set_accessible_name = getattr(prompt_input, "setAccessibleName", None)
        if callable(set_accessible_name):
            set_accessible_name("Ask pATHENA")

        send_button = getattr(window, "send_button", None)
        if isinstance(send_button, QPushButton):
            send_button.setText("↑")
            send_button.setToolTip("Send message (Ctrl+Enter)")
            send_button.setAccessibleName("Send message")

        local_status = None
        find_child = getattr(window, "findChild", None)
        if callable(find_child):
            local_status = find_child(QLabel, "localPrivateStatus")
        if isinstance(local_status, QLabel):
            local_status.setText("Local · Private")
            local_status.setAccessibleName("Local and private")

    @Slot(int)
    def _sync_navigation(self, index: int) -> None:
        if not 0 <= index < len(PAGE_LABELS):
            return

        page_title = getattr(self._window, "page_title", None)
        if isinstance(page_title, QLabel):
            page_title.setText(PAGE_LABELS[index])

        for button in getattr(self._window, "reference_top_nav_buttons", ()):
            if not isinstance(button, QPushButton):
                continue
            raw_index = button.property("pageIndex")
            if isinstance(raw_index, int):
                button.setChecked(raw_index == index)


def install_reference_screen_parity(window: object) -> ReferenceScreenParity:
    """Install the small reference-family presentation adapter."""
    return ReferenceScreenParity(window)
