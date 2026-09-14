"""Presentation-only parity layer for the eleven pATHENA reference screens.

The August 24 reference family converged on a stable visible information
architecture: CHAT, KNOWLEDGE, RESEARCH, JOBS and SOURCES in the top bar,
with SYSTEM and SETTINGS remaining utility destinations. The underlying
legacy page indexes are intentionally left untouched here; this module only
normalizes user-facing presentation and wires reference affordances to real
existing actions.
"""

from __future__ import annotations

from typing import Final, cast

from PySide6.QtCore import QObject, QTimer, Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE


REFERENCE_FAMILY: Final = "11-screen-2026-08-24"
PAGE_DESTINATIONS: Final = (
    "Chat",
    "Knowledge",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)
PAGE_TITLES: Final = (
    "Chat",
    "Library",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)
# Kept as a compatibility alias for tests/extensions that only need page count.
PAGE_LABELS: Final = PAGE_DESTINATIONS
TOP_NAV_LABELS: Final = {
    0: "CHAT",
    1: "KNOWLEDGE",
    2: "RESEARCH",
    3: "JOBS",
    4: "SOURCES",
}
COMPOSER_PLACEHOLDER: Final = "Ask, explore, or build…"
SEARCH_PLACEHOLDER: Final = "Search commands or workspaces…"
_JOBS_REFERENCE_OVERRIDE_MARKER: Final = "/* 11-screen jobs parity */"
_SHELL_REFERENCE_OVERRIDE_MARKER: Final = "/* 11-screen shell parity */"


class ReferenceScreenParity(QObject):
    """Keep the live shell aligned with the selected reference-screen family."""

    def __init__(self, window: object) -> None:
        parent = cast(QObject, window)
        super().__init__(parent)
        self._window = window
        self._search_button: QPushButton | None = None
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

        # Presentation extensions are installed later during desktop composition.
        # A zero-delay handoff runs only after startup composition has completed.
        QTimer.singleShot(0, self._finish_startup_parity)

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
            button.setToolTip(f"Open {PAGE_DESTINATIONS[raw_index]}")
            button.setAccessibleName(PAGE_DESTINATIONS[raw_index])

        prompt_input = getattr(window, "prompt_input", None)
        set_placeholder = getattr(prompt_input, "setPlaceholderText", None)
        if callable(set_placeholder):
            set_placeholder(COMPOSER_PLACEHOLDER)
        set_accessible_name = getattr(prompt_input, "setAccessibleName", None)
        if callable(set_accessible_name):
            set_accessible_name("Ask pATHENA")

        send_button = getattr(window, "send_button", None)
        if isinstance(send_button, QPushButton):
            send_button.setText("→")
            send_button.setToolTip("Send message (Ctrl+Enter)")
            send_button.setAccessibleName("Send message")

        local_status = None
        find_child = getattr(window, "findChild", None)
        if callable(find_child):
            local_status = find_child(QLabel, "localPrivateStatus")
        if isinstance(local_status, QLabel):
            local_status.setText("Local · Private")
            local_status.setAccessibleName("Local and private")

    def bind_command_palette(self, command_palette: object) -> QPushButton | None:
        """Expose the existing command palette as the reference top-bar search control."""
        open_palette = getattr(command_palette, "open", None)
        if not callable(open_palette):
            return None

        query = getattr(command_palette, "query", None)
        if isinstance(query, QLineEdit):
            query.setPlaceholderText(SEARCH_PLACEHOLDER)

        if self._search_button is not None:
            return self._search_button

        find_child = getattr(self._window, "findChild", None)
        if not callable(find_child):
            return None
        top_bar = find_child(QFrame, "topBar")
        if not isinstance(top_bar, QFrame):
            return None
        layout = top_bar.layout()
        if not isinstance(layout, QHBoxLayout):
            return None

        button = QPushButton("⌕", top_bar)
        button.setObjectName("topUtilityButton")
        button.setProperty("referenceRole", "globalSearch")
        button.setToolTip("Search and commands (Ctrl+K)")
        button.setAccessibleName("Search and commands")
        button.clicked.connect(lambda _checked=False: open_palette())

        # The reference shell ends with System, Settings, status dot, and status text.
        # Insert immediately before those four items so Search remains a global utility.
        layout.insertWidget(max(0, layout.count() - 4), button)
        self._search_button = button
        return button

    def _finish_startup_parity(self) -> None:
        """Bind late-installed real controls and remove safe legacy surface drift."""
        self._bind_installed_command_palette()
        self._apply_shell_reference_palette()
        self._apply_pallas_canvas_palette()
        self._apply_jobs_reference_palette()
        navigation = getattr(self._window, "navigation", None)
        current_row = getattr(navigation, "currentRow", None)
        index = current_row() if callable(current_row) else 0
        self._sync_inspector_title(index)

    def _bind_installed_command_palette(self) -> None:
        """Find the real palette after startup composition and bind it once."""
        from athena.desktop.command_palette import CommandPaletteController

        window = cast(QObject, self._window)
        command_palette = window.findChild(CommandPaletteController)
        if isinstance(command_palette, CommandPaletteController):
            self.bind_command_palette(command_palette)

    def _apply_shell_reference_palette(self) -> None:
        """Apply the final low-risk shell selectors after all startup refinements."""
        window = cast(QWidget, self._window)
        current = window.styleSheet()
        if _SHELL_REFERENCE_OVERRIDE_MARKER in current:
            return
        override = f"""
{_SHELL_REFERENCE_OVERRIDE_MARKER}
QFrame#topBar {{
    background: {PALETTE.surface};
    border: none;
    border-bottom: 1px solid {PALETTE.border};
}}
QFrame#iconRail {{
    background: {PALETTE.surface_raised};
    border: none;
    border-right: 1px solid {PALETTE.border};
}}
QFrame#inspector {{
    background: {PALETTE.canvas};
    border: none;
    border-left: 1px solid {PALETTE.border};
}}
QPushButton#topNavButton:checked {{
    color: {PALETTE.text};
    background: transparent;
    border-bottom: 1px solid {PALETTE.border_strong};
}}
QListWidget#navigation::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}
QLineEdit:focus,
QPlainTextEdit:focus {{
    border-color: {PALETTE.accent};
}}
"""
        window.setStyleSheet(f"{current}\n{override}")

    def _apply_pallas_canvas_palette(self) -> None:
        """Align live PALLAS canvases without replacing renderer behavior."""
        window = cast(QObject, self._window)
        for canvas in window.findChildren(QGraphicsView, "pallasSemanticCanvas"):
            canvas.setBackgroundBrush(QBrush(QColor(PALETTE.canvas)))
            canvas.viewport().update()

    def _apply_jobs_reference_palette(self) -> None:
        """Override the Jobs refinement's pre-reference local black/orange stylesheet."""
        window = cast(QObject, self._window)
        workspace = window.findChild(QWidget, "jobsWorkspace")
        if not isinstance(workspace, QWidget):
            return
        current = workspace.styleSheet()
        if _JOBS_REFERENCE_OVERRIDE_MARKER in current:
            return
        override = f"""
{_JOBS_REFERENCE_OVERRIDE_MARKER}
QLineEdit#jobsFilter {{
    background: {PALETTE.surface};
    color: {PALETTE.text};
    border: 1px solid {PALETTE.border};
}}
QLineEdit#jobsFilter:focus {{
    border-color: {PALETTE.accent};
}}
QPlainTextEdit#jobDetails {{
    background: {PALETTE.surface};
    color: {PALETTE.text_muted};
    border: 1px solid {PALETTE.border};
}}
QPushButton[pathenaJobsSecondary="true"] {{
    background: transparent;
    color: {PALETTE.text_subtle};
    border-color: transparent;
}}
QPushButton[pathenaJobsSecondary="true"]:hover {{
    color: {PALETTE.text};
    border-color: {PALETTE.border_strong};
}}
QPushButton[pathenaJobsDestructive="true"] {{
    background: transparent;
    color: {PALETTE.error};
    border-color: {PALETTE.border};
}}
"""
        workspace.setStyleSheet(f"{current}\n{override}")

    def _sync_inspector_title(self, index: int) -> None:
        window = cast(QObject, self._window)
        title = window.findChild(QLabel, "inspectorTitle")
        if not isinstance(title, QLabel):
            return
        # The chat reference is knowledge-oriented; all workbench screens use the
        # persistent evidence/activity rail heading.
        title.setText("KNOWLEDGE" if index == 0 else "EVIDENCE & ACTIVITY")

    @Slot(int)
    def _sync_navigation(self, index: int) -> None:
        if not 0 <= index < len(PAGE_TITLES):
            return

        page_title = getattr(self._window, "page_title", None)
        if isinstance(page_title, QLabel):
            page_title.setText(PAGE_TITLES[index])

        for button in getattr(self._window, "reference_top_nav_buttons", ()):
            if not isinstance(button, QPushButton):
                continue
            raw_index = button.property("pageIndex")
            if isinstance(raw_index, int):
                button.setChecked(raw_index == index)

        self._sync_inspector_title(index)


def install_reference_screen_parity(window: object) -> ReferenceScreenParity:
    """Install the small reference-family presentation adapter."""
    return ReferenceScreenParity(window)
