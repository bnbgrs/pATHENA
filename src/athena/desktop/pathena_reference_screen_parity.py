"""Presentation-only parity layer for the eleven pATHENA reference screens.

The August 24 reference family converged on a stable visible information
architecture: Chat, Knowledge, Research, Jobs and Sources in the top bar,
with System and Settings remaining utility destinations. The underlying
legacy page indexes are intentionally left untouched here; this module only
normalizes user-facing presentation and wires reference affordances to real
existing actions.
"""

from __future__ import annotations

from typing import Final, cast

from PySide6.QtCore import QObject, QSize, QTimer, Slot
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL


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
    0: "Chat",
    1: "Knowledge",
    2: "Research",
    3: "Jobs",
    4: "Sources",
}
COMPOSER_PLACEHOLDER: Final = "Ask, explore, or build…"
SEARCH_PLACEHOLDER: Final = "Search commands or workspaces…"
_STARTUP_RAIL_WIDTH: Final = 248
_STARTUP_NAV_LABELS: Final = (
    "›  CHAT",
    "◇  KNOWLEDGE",
    "◎  RESEARCH",
    "▣  JOBS",
    "▱  SOURCES",
)
_JOBS_REFERENCE_OVERRIDE_MARKER: Final = "/* 11-screen jobs parity */"
_SHELL_REFERENCE_OVERRIDE_MARKER: Final = "/* 11-screen shell parity */"


class ReferenceScreenParity(QObject):
    """Keep the live shell aligned with the selected reference-screen family."""

    def __init__(self, window: object) -> None:
        parent = cast(QObject, window)
        super().__init__(parent)
        self._window = window
        self._search_button: QPushButton | None = None
        self._startup_wordmark: QLabel | None = None
        self._startup_utilities: QFrame | None = None
        self._chat_shell_active = False
        self._page_title_was_visible = True

        navigation = getattr(window, "navigation", None)
        count = navigation.count() if hasattr(navigation, "count") else 0
        self._normal_navigation_texts = tuple(
            navigation.item(index).text() for index in range(count)
        )

        self.setObjectName("referenceScreenParity")
        self._apply_static_presentation()

        current_row_changed = getattr(navigation, "currentRowChanged", None)
        connect = getattr(current_row_changed, "connect", None)
        if callable(connect):
            connect(self._sync_navigation)

        current_row = getattr(navigation, "currentRow", None)
        index = current_row() if callable(current_row) else 0
        self._sync_navigation(index)

        self._chat_shell_watch = QTimer(self)
        self._chat_shell_watch.setInterval(500)
        self._chat_shell_watch.timeout.connect(self._sync_chat_shell_mode)
        self._chat_shell_watch.start()

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
        self._sync_chat_shell_mode()
        # StartupExperience also uses a zero-delay sync. Queue one final copy pass
        # behind it so the reference copy wins without owning startup behavior.
        QTimer.singleShot(0, self._sync_deferred_startup_copy)

    def _sync_deferred_startup_copy(self) -> None:
        navigation = getattr(self._window, "navigation", None)
        current_row = getattr(navigation, "currentRow", None)
        index = current_row() if callable(current_row) else 0
        self._sync_startup_copy(index)
        self._sync_chat_shell_mode()

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
QLabel#startupRailWordmark {{
    color: {PALETTE.accent};
    font-size: 22px;
    font-weight: 500;
    padding: 4px 8px 18px 8px;
}}
QFrame#startupRailUtilities {{
    background: transparent;
    border: none;
}}
QPushButton#startupRailUtility {{
    background: transparent;
    color: {PALETTE.text_muted};
    border: none;
    min-width: 36px;
    min-height: 32px;
}}
QPushButton#startupRailUtility:hover {{
    color: {PALETTE.text};
}}
QLabel#emptyStateEyebrow {{
    color: {PALETTE.accent};
    font-size: 9px;
    font-weight: 600;
}}
QLabel#emptyStateTitle {{
    color: {PALETTE.text};
    font-size: 34px;
    font-weight: 400;
}}
QLabel#emptyStateBody {{
    color: {PALETTE.text_subtle};
    font-size: 14px;
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

    def _sync_startup_copy(self, index: int) -> None:
        if index != 0 or bool(getattr(self._window, "_core_transport_ready", False)):
            return
        window = cast(QObject, self._window)
        eyebrow = window.findChild(QLabel, "emptyStateEyebrow")
        title = window.findChild(QLabel, "emptyStateTitle")
        body = window.findChild(QLabel, "emptyStateBody")
        if isinstance(eyebrow, QLabel):
            eyebrow.setText("LOCAL CORE · CONNECTING")
        if isinstance(title, QLabel):
            title.setText("Getting pATHENA ready")
        if isinstance(body, QLabel):
            body.setText("What shall we explore today?")

    def _set_navigation_row(self, row: int) -> None:
        navigation = getattr(self._window, "navigation", None)
        set_current_row = getattr(navigation, "setCurrentRow", None)
        if callable(set_current_row):
            set_current_row(row)

    def _ensure_startup_rail_extras(self, icon_rail: QFrame) -> None:
        layout = icon_rail.layout()
        if not isinstance(layout, QVBoxLayout):
            return

        if self._startup_wordmark is None:
            wordmark = QLabel("pATHENA  ∘", icon_rail)
            wordmark.setObjectName("startupRailWordmark")
            wordmark.setAccessibleName("pATHENA")
            layout.insertWidget(0, wordmark)
            self._startup_wordmark = wordmark

        if self._startup_utilities is None:
            utilities = QFrame(icon_rail)
            utilities.setObjectName("startupRailUtilities")
            utility_layout = QHBoxLayout(utilities)
            utility_layout.setContentsMargins(6, 0, 6, 0)
            utility_layout.setSpacing(8)

            system_button = QPushButton(">_", utilities)
            system_button.setObjectName("startupRailUtility")
            system_button.setToolTip("Open System")
            system_button.setAccessibleName("System")
            system_button.clicked.connect(
                lambda _checked=False: self._set_navigation_row(5)
            )
            settings_button = QPushButton("⚙", utilities)
            settings_button.setObjectName("startupRailUtility")
            settings_button.setToolTip("Open Settings")
            settings_button.setAccessibleName("Settings")
            settings_button.clicked.connect(
                lambda _checked=False: self._set_navigation_row(6)
            )
            utility_layout.addWidget(system_button)
            utility_layout.addStretch(1)
            utility_layout.addWidget(settings_button)
            layout.addWidget(utilities)
            self._startup_utilities = utilities

    @Slot()
    def _sync_chat_shell_mode(self) -> None:
        """Use the wide left navigation only for the disconnected Chat reference state."""
        navigation = getattr(self._window, "navigation", None)
        current_row = getattr(navigation, "currentRow", None)
        index = current_row() if callable(current_row) else 0
        should_expand = index == 0 and not bool(
            getattr(self._window, "_core_transport_ready", False)
        )
        if should_expand == self._chat_shell_active:
            return

        window = cast(QObject, self._window)
        top_bar = window.findChild(QFrame, "topBar")
        icon_rail = window.findChild(QFrame, "iconRail")
        page_title = getattr(self._window, "page_title", None)
        if not isinstance(icon_rail, QFrame):
            return

        if should_expand:
            self._chat_shell_active = True
            if isinstance(top_bar, QFrame):
                top_bar.hide()
            icon_rail.setFixedWidth(_STARTUP_RAIL_WIDTH)
            rail_layout = icon_rail.layout()
            if isinstance(rail_layout, QVBoxLayout):
                rail_layout.setContentsMargins(18, 26, 16, 16)
                rail_layout.setSpacing(8)
            self._ensure_startup_rail_extras(icon_rail)
            if self._startup_wordmark is not None:
                self._startup_wordmark.show()
            if self._startup_utilities is not None:
                self._startup_utilities.show()

            if hasattr(navigation, "setFixedWidth"):
                navigation.setFixedWidth(_STARTUP_RAIL_WIDTH - 34)
                navigation.setFixedHeight(len(_STARTUP_NAV_LABELS) * 44 + 12)
            for row, label in enumerate(_STARTUP_NAV_LABELS):
                if row >= navigation.count():
                    break
                item = navigation.item(row)
                item.setHidden(False)
                item.setText(label)
                item.setSizeHint(QSize(_STARTUP_RAIL_WIDTH - 34, 40))
            for row in range(len(_STARTUP_NAV_LABELS), navigation.count()):
                navigation.item(row).setHidden(True)

            if isinstance(page_title, QLabel):
                self._page_title_was_visible = not page_title.isHidden()
                page_title.hide()
            return

        self._chat_shell_active = False
        if isinstance(top_bar, QFrame):
            top_bar.show()
        icon_rail.setFixedWidth(SHELL.icon_rail_width)
        rail_layout = icon_rail.layout()
        if isinstance(rail_layout, QVBoxLayout):
            rail_layout.setContentsMargins(8, 14, 8, 14)
            rail_layout.setSpacing(8)
        if self._startup_wordmark is not None:
            self._startup_wordmark.hide()
        if self._startup_utilities is not None:
            self._startup_utilities.hide()

        if hasattr(navigation, "setFixedWidth"):
            navigation.setFixedWidth(SHELL.icon_rail_width - 8)
            navigation.setFixedHeight(min(360, navigation.count() * 48))
        for row in range(navigation.count()):
            item = navigation.item(row)
            item.setHidden(False)
            if row < len(self._normal_navigation_texts):
                item.setText(self._normal_navigation_texts[row])
            item.setSizeHint(QSize(52, 44))

        if isinstance(page_title, QLabel) and self._page_title_was_visible:
            page_title.show()

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
        self._sync_startup_copy(index)
        self._sync_chat_shell_mode()


def install_reference_screen_parity(window: object) -> ReferenceScreenParity:
    """Install the small reference-family presentation adapter."""
    return ReferenceScreenParity(window)
