"""Final shared-shell alignment for the eleven pATHENA UI references.

The desktop is assembled by a long sequence of functional workspace controllers.
This module intentionally runs after those controllers: it owns only shared visual
hierarchy and geometry, while routing remains on the existing navigation model.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SHELL
from athena.desktop.pathena_window import PathenaMainWindow

_PRIMARY_NAVIGATION: tuple[tuple[str, int], ...] = (
    ("CHAT", 0),
    ("KNOWLEDGE", 1),
    ("RESEARCH", 2),
    ("JOBS", 3),
    ("SOURCES", 4),
)
_PAGE_TITLES = (
    "Chat",
    "Knowledge",
    "Research",
    "Jobs",
    "Sources",
    "System",
    "Settings",
)

_REFERENCE_PARITY_STYLESHEET = f"""
/* Final screenshot-family layer. This intentionally follows all older UI passes. */
QWidget#referenceShell,
QFrame#referenceBody,
QFrame#conversation,
QWidget#pageChat,
QWidget#pageKnowledge,
QWidget#pageResearch,
QWidget#pageJobs,
QWidget#pageFiles,
QWidget#pageSystem,
QWidget#pageSettings,
QWidget#knowledgeWorkspace,
QWidget#researchWorkspace,
QWidget#jobsWorkspace,
QWidget#filesWorkspace,
QWidget#systemWorkspace,
QWidget#settingsSecondaryContent,
QFrame#settingsSecondaryContainer {{
    background: {PALETTE.canvas};
}}

QScrollArea#chatScroll,
QScrollArea#settingsSecondaryScroll,
QScrollArea#chatScroll > QWidget > QWidget,
QScrollArea#settingsSecondaryScroll > QWidget > QWidget,
QWidget#chatMessages {{
    background: {PALETTE.canvas};
    border: 0;
}}

QFrame#topBar {{
    background: {PALETTE.surface};
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
}}
QLabel#topWordmark {{
    color: {PALETTE.text};
    font-size: 18px;
    font-weight: 700;
    padding-right: 22px;
}}
QFrame#topPrimaryNavigation {{
    background: transparent;
    border: 0;
}}
QPushButton#topPrimaryNavButton {{
    min-height: {SHELL.top_bar_height - 2}px;
    padding: 0 13px;
    border: 0;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    background: transparent;
    color: {PALETTE.text_subtle};
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#topPrimaryNavButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QPushButton#topPrimaryNavButton:focus {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-bottom: 2px solid {PALETTE.accent};
}}
QPushButton#topPrimaryNavButton[selected="true"] {{
    color: {PALETTE.text};
    border-bottom: 2px solid {PALETTE.accent};
    background: {PALETTE.accent_soft};
}}

QPushButton#topSearchButton,
QPushButton#topUtilityButton {{
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border: 1px solid transparent;
    border-radius: {RADII.control}px;
    background: transparent;
    color: {PALETTE.text_muted};
    font-size: 15px;
}}
QPushButton#topSearchButton:hover,
QPushButton#topUtilityButton:hover {{
    color: {PALETTE.text};
    border-color: {PALETTE.border};
    background: {PALETTE.surface_hover};
}}
QPushButton#topSearchButton:focus,
QPushButton#topUtilityButton:focus {{
    color: {PALETTE.text};
    border-color: {PALETTE.accent};
    background: {PALETTE.surface_hover};
}}
QPushButton#topUtilityButton[selected="true"] {{
    color: {PALETTE.accent};
    border-color: {PALETTE.border_strong};
    background: {PALETTE.surface_selected};
}}

QFrame#iconRail,
QFrame#rail {{
    background: {PALETTE.surface};
    border: 0;
    border-right: 1px solid {PALETTE.border};
}}
QListWidget#navigation {{
    background: transparent;
    border: 0;
    outline: 0;
}}
QListWidget#navigation::item {{
    color: {PALETTE.text_subtle};
    border: 1px solid transparent;
    border-radius: {RADII.control}px;
    margin: 2px 0;
}}
QListWidget#navigation::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QListWidget#navigation:focus::item:current {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-left: 2px solid {PALETTE.accent};
}}
QListWidget#navigation::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}

QLabel#pageTitle {{
    color: {PALETTE.text};
    font-size: 26px;
    font-weight: 500;
    padding: 5px 0 8px 0;
}}
QLabel#keyboardHint {{
    color: {PALETTE.text_quiet};
    font-size: 11px;
}}
QFrame#rule,
QFrame[role="rule"] {{
    background: {PALETTE.border};
    border: 0;
    min-height: 1px;
    max-height: 1px;
}}

QFrame#inspector {{
    background: {PALETTE.surface};
    border: 0;
    border-left: 1px solid {PALETTE.border};
}}

/* The opened workspace references use a navy document field, not an inner black slab. */
QFrame#emptyStatePanel {{
    background: transparent;
    border: 0;
}}
QLabel#emptyStateEyebrow {{
    color: {PALETTE.accent};
    font-size: 10px;
    font-weight: 650;
}}
QLabel#emptyStateTitle {{
    color: {PALETTE.text};
    font-size: 22px;
    font-weight: 600;
}}
QLabel#emptyStateBody {{
    color: {PALETTE.text_subtle};
    font-size: 13px;
}}

QFrame#composer {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.composer}px;
}}
QLineEdit#promptInput,
QLineEdit#promptInput:disabled {{
    color: {PALETTE.text};
    background: {PALETTE.surface};
    border: 0;
    border-radius: 16px;
}}
QLineEdit#promptInput:disabled {{
    color: {PALETTE.text_quiet};
}}
QPushButton#groundButton,
QPushButton#groundButton:disabled {{
    color: {PALETTE.text_subtle};
    background: transparent;
    border: 0;
}}
QPushButton#sendButton {{
    min-width: 48px;
    max-width: 48px;
    min-height: 48px;
    max-height: 48px;
    border: 0;
    border-radius: 24px;
    background: {PALETTE.accent};
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
}}
QPushButton#sendButton:hover {{
    background: {PALETTE.accent_hover};
}}
QPushButton#sendButton:focus {{
    background: {PALETTE.accent_hover};
    border: 2px solid {PALETTE.text};
}}
QPushButton#sendButton:pressed {{
    background: {PALETTE.accent_pressed};
}}
QPushButton#sendButton:disabled {{
    background: {PALETTE.surface_selected};
    color: {PALETTE.text_quiet};
    border: 1px solid {PALETTE.border};
}}

/* Reassert the reference palette over older orange-centric refinement sheets. */
QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QPlainTextEdit {{
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    selection-color: {PALETTE.text};
    selection-background-color: {PALETTE.accent_soft};
}}
QLineEdit:hover,
QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover,
QPlainTextEdit:hover {{
    border-color: {PALETTE.border_strong};
}}
QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QPlainTextEdit:focus {{
    border-color: {PALETTE.accent};
}}
QCheckBox {{
    color: {PALETTE.text_muted};
}}
QCheckBox::indicator {{
    border: 1px solid {PALETTE.border_strong};
    background: {PALETTE.surface};
}}
QCheckBox::indicator:checked {{
    border-color: {PALETTE.accent};
    background: {PALETTE.accent};
}}
QSlider::groove:horizontal {{
    background: {PALETTE.border};
    height: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {PALETTE.accent};
}}
QSlider::handle:horizontal {{
    background: {PALETTE.accent};
    border: 0;
}}
QProgressBar::chunk {{
    background: {PALETTE.accent};
}}
QWidget[pathenaStateSurface="true"] {{
    border-color: {PALETTE.border};
}}
QWidget[pathenaUiState="busy"] {{
    color: {PALETTE.text_muted};
    border-color: {PALETTE.border_strong};
}}
QWidget[pathenaUiState="success"] {{
    color: {PALETTE.success};
    border-color: {PALETTE.success};
}}
QWidget[pathenaUiState="error"] {{
    color: {PALETTE.error};
    border-color: {PALETTE.error};
}}
QWidget[pathenaUiState="empty"],
QWidget[pathenaUiState="idle"] {{
    color: {PALETTE.text_subtle};
    border-color: {PALETTE.border};
}}

QListWidget#settingsSecondaryNavigation {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: 8px;
}}
QListWidget#settingsSecondaryNavigation::item {{
    color: {PALETTE.text_muted};
    min-height: 40px;
    padding: 0 10px;
    border-radius: {RADII.control}px;
}}
QListWidget#settingsSecondaryNavigation::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QListWidget#settingsSecondaryNavigation::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}

QDialog#commandPalette,
QDialog#helpDialog {{
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
}}
QLabel#commandPaletteTitle,
QLabel#helpDialogTitle {{
    color: {PALETTE.text};
    font-size: 18px;
    font-weight: 600;
}}
QLabel#commandPaletteHint,
QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {{
    color: {PALETTE.text_subtle};
}}
QLineEdit#commandPaletteQuery {{
    min-height: 42px;
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.control}px;
    padding: 0 12px;
}}
QLineEdit#commandPaletteQuery:focus {{
    border-color: {PALETTE.accent};
}}
QListWidget#commandPaletteResults {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    outline: 0;
}}
QListWidget#commandPaletteResults::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
    min-height: 38px;
    padding: 4px 12px;
}}
QListWidget#commandPaletteResults::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QListWidget#commandPaletteResults::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}
QPlainTextEdit#helpText {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: 14px;
}}
"""


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class ReferenceParityController(QObject):
    """Apply the common screenshot DNA after all functional workspaces exist."""

    def __init__(
        self,
        window: PathenaMainWindow,
        open_command_palette: Callable[[], None],
    ) -> None:
        super().__init__(window)
        self.window = window
        self._open_command_palette = open_command_palette
        self._primary_buttons: dict[int, QPushButton] = {}
        self._utility_buttons: dict[int, QPushButton] = {}
        self._install_top_navigation()
        self._apply_shared_geometry()
        self._apply_reference_styles()
        self.window.navigation.currentRowChanged.connect(self._sync_navigation)
        self._sync_navigation(self.window.navigation.currentRow())

    def _install_top_navigation(self) -> None:
        top_bar = self.window.findChild(QFrame, "topBar")
        if top_bar is None:
            return
        top_layout = top_bar.layout()
        if not isinstance(top_layout, QHBoxLayout):
            return

        existing = top_bar.findChild(QFrame, "topPrimaryNavigation")
        if existing is not None:
            existing.deleteLater()

        primary = QFrame(top_bar)
        primary.setObjectName("topPrimaryNavigation")
        primary.setAccessibleName("Primary workspace navigation")
        primary_layout = QHBoxLayout(primary)
        primary_layout.setContentsMargins(0, 0, 0, 0)
        primary_layout.setSpacing(0)

        for label, row in _PRIMARY_NAVIGATION:
            button = QPushButton(label, primary)
            button.setObjectName("topPrimaryNavButton")
            button.setFlat(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(label.title())
            button.setToolTip(f"Open {label.title()}")
            button.clicked.connect(
                lambda _checked=False, index=row: self.window.navigation.setCurrentRow(index)
            )
            primary_layout.addWidget(button)
            self._primary_buttons[row] = button

        top_layout.insertWidget(1, primary)

        search = QPushButton("⌕", top_bar)
        search.setObjectName("topSearchButton")
        search.setAccessibleName("Search and commands")
        search.setToolTip("Search and commands (Ctrl+K)")
        search.clicked.connect(self._open_command_palette)

        first_utility_index = top_layout.count()
        for index in range(top_layout.count()):
            item = top_layout.itemAt(index)
            widget = item.widget() if item is not None else None
            if isinstance(widget, QPushButton) and widget.objectName() == "topUtilityButton":
                first_utility_index = index
                break
        top_layout.insertWidget(first_utility_index, search)

        for button in top_bar.findChildren(QPushButton, "topUtilityButton"):
            name = button.accessibleName().casefold()
            if name == "system":
                self._utility_buttons[5] = button
            elif name == "settings":
                self._utility_buttons[6] = button

    def _apply_shared_geometry(self) -> None:
        top_bar = self.window.findChild(QFrame, "topBar")
        if top_bar is not None:
            top_bar.setFixedHeight(SHELL.top_bar_height)
            layout = top_bar.layout()
            if isinstance(layout, QHBoxLayout):
                layout.setContentsMargins(20, 0, 18, 0)
                layout.setSpacing(6)

        icon_rail = self.window.findChild(QFrame, "iconRail")
        if icon_rail is not None:
            icon_rail.setFixedWidth(SHELL.icon_rail_width)

        for row, title in enumerate(_PAGE_TITLES):
            if row >= self.window.navigation.count():
                break
            self.window.navigation.item(row).setToolTip(title)

        secondary_navigation = self.window.findChild(QListWidget, "settingsSecondaryNavigation")
        if secondary_navigation is not None:
            secondary_navigation.setFixedWidth(SHELL.secondary_nav_width)

        inspector = self.window.findChild(QFrame, "inspector")
        if inspector is not None:
            inspector.setFixedWidth(SHELL.inspector_width)

        center = self.window.findChild(QFrame, "conversation")
        if center is not None:
            center_layout = center.layout()
            if isinstance(center_layout, QVBoxLayout):
                center_layout.setContentsMargins(32, 24, 32, 18)
                center_layout.setSpacing(14)

        composer = self.window.findChild(QFrame, "composer")
        if composer is not None:
            composer.setMinimumHeight(80)
            composer.setMaximumHeight(92)
            composer.setMinimumWidth(620)
            composer.setMaximumWidth(980)
            composer_layout = composer.layout()
            if composer_layout is not None:
                composer_layout.setContentsMargins(12, 12, 10, 12)
                composer_layout.setSpacing(10)
            parent = composer.parentWidget()
            parent_layout = parent.layout() if parent is not None else None
            if isinstance(parent_layout, QVBoxLayout):
                parent_layout.setAlignment(composer, Qt.AlignmentFlag.AlignHCenter)

        self.window.prompt_input.setMinimumHeight(48)
        self.window.prompt_input.setMaximumHeight(56)
        self.window.send_button.setFixedSize(48, 48)
        self.window.ground_button.setMinimumHeight(36)
        self.window.ground_button.setMaximumHeight(40)

        keyboard_hint = self.window.findChild(QWidget, "keyboardHint")
        if keyboard_hint is not None:
            keyboard_hint.hide()

    def _apply_reference_styles(self) -> None:
        self.window.setStyleSheet(self.window.styleSheet() + _REFERENCE_PARITY_STYLESHEET)

    def _sync_navigation(self, row: int) -> None:
        if 0 <= row < len(_PAGE_TITLES):
            self.window.page_title.setText(_PAGE_TITLES[row])

        for index, button in self._primary_buttons.items():
            button.setProperty("selected", index == row)
            _repolish(button)
        for index, button in self._utility_buttons.items():
            button.setProperty("selected", index == row)
            _repolish(button)

        # The reference family reserves the work composer for the conversational
        # workspace. Administrative pages use their own task-specific controls.
        composer = self.window.findChild(QFrame, "composer")
        if composer is not None:
            composer.setVisible(row == 0)

        # The generic inspector is evidence-centric. Dedicated workspaces own their
        # detail panes, so showing this panel on every non-chat page creates a fourth
        # column that is absent from the reference family.
        inspector = self.window.findChild(QFrame, "inspector")
        if inspector is not None:
            context_button = getattr(self.window, "context_button", None)
            context_available = (
                isinstance(context_button, QPushButton) and not context_button.isHidden()
            )
            inspector.setVisible(row == 0 and context_available)

    def dispose(self) -> None:
        """Disconnect the final shared-shell listener before application teardown."""
        try:
            self.window.navigation.currentRowChanged.disconnect(self._sync_navigation)
        except (RuntimeError, TypeError):
            pass


def install_reference_parity(
    window: PathenaMainWindow,
    open_command_palette: Callable[[], None],
) -> ReferenceParityController:
    """Install the final eleven-reference shared presentation layer."""
    existing = getattr(window, "_pathena_reference_parity_controller", None)
    if isinstance(existing, ReferenceParityController):
        existing.dispose()
        existing.deleteLater()
    controller = ReferenceParityController(window, open_command_palette)
    window.__dict__["_pathena_reference_parity_controller"] = controller
    return controller
