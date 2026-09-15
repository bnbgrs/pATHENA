"""Final shared-shell alignment for the eleven pATHENA UI references.

pATHENA is assembled by functional workspace controllers first. This module runs
last and owns only common visual hierarchy, geometry and shell affordances. It
must not invent capabilities or replace workspace routing/state semantics.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SHELL, SPACE, TYPE
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

# These widgets accumulated local presentation rules during earlier UI passes.
# Clearing only their local styles lets the final reference layer own appearance
# without changing widget state, signals, routing, data, or backend behavior.
_LEGACY_INLINE_STYLE_OBJECTS = (
    "settingsSecondaryNavigation",
    "canonicalMemoryTabs",
    "knowledgeSearchInput",
    "persistentKnowledgeList",
    "persistentKnowledgeDetails",
    "persistentClaimList",
    "persistentClaimDetails",
    "semanticReviewList",
    "semanticReviewDetails",
    "researchJobList",
    "researchDetails",
    "durableJobList",
    "jobDetails",
)

_REFERENCE_WORKSPACE_OBJECTS = (
    "knowledgeWorkspace",
    "researchWorkspace",
    "jobsWorkspace",
    "filesWorkspace",
    "systemWorkspace",
    "settingsSecondaryContent",
)

_REFERENCE_PARITY_STYLESHEET = f"""
/* Eleven-screen reference layer. Applied after all older presentation passes. */
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
QWidget#knowledgeWorkspaceItems,
QWidget#researchWorkspace,
QWidget#jobsWorkspace,
QWidget#filesWorkspace,
QWidget#systemWorkspace,
QWidget#systemMain,
QWidget#settingsSecondaryContent,
QFrame#settingsSecondaryContainer,
QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace {{
    background: {PALETTE.canvas};
    color: {PALETTE.text};
}}

QScrollArea#chatScroll,
QScrollArea#knowledgeWorkspaceScroll,
QScrollArea#settingsSecondaryScroll,
QScrollArea#chatScroll > QWidget > QWidget,
QScrollArea#knowledgeWorkspaceScroll > QWidget > QWidget,
QScrollArea#settingsSecondaryScroll > QWidget > QWidget,
QWidget#chatMessages {{
    background: {PALETTE.canvas};
    border: 0;
}}

/* Top bar: one textual primary navigation + quiet utilities. */
QFrame#topBar {{
    background: {PALETTE.surface};
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
}}
QLabel#topWordmark {{
    color: {PALETTE.text};
    font-family: {TYPE.content_family};
    font-size: 18px;
    font-weight: 650;
    padding-right: 22px;
}}
QFrame#topPrimaryNavigation {{
    background: transparent;
    border: 0;
}}
QPushButton#topPrimaryNavButton {{
    min-height: {SHELL.top_bar_height - 2}px;
    padding: 0 14px;
    border: 0;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    background: transparent;
    color: {PALETTE.text_subtle};
    font-family: {TYPE.content_family};
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#topPrimaryNavButton:hover {{
    color: {PALETTE.text};
    background: transparent;
}}
QPushButton#topPrimaryNavButton:focus {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-bottom: 2px solid {PALETTE.accent};
}}
QPushButton#topPrimaryNavButton[selected="true"] {{
    color: {PALETTE.accent};
    border-bottom: 2px solid {PALETTE.accent};
    background: transparent;
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
    border-color: {PALETTE.accent};
    background: {PALETTE.accent_soft};
}}

/* Narrow icon rail stays secondary to textual navigation. */
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
    background: transparent;
    border: 1px solid transparent;
    border-left: 2px solid transparent;
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
    color: {PALETTE.accent};
    background: {PALETTE.accent_soft};
    border-left: 2px solid {PALETTE.accent};
}}

/* Editorial page hierarchy visible across the opened reference family. */
QLabel#pageTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: {TYPE.title_px}px;
    font-weight: 500;
    padding: 4px 0 12px 0;
}}
QLabel#keyboardHint {{
    color: {PALETTE.text_quiet};
    font-size: 11px;
}}
QLabel[role="section"] {{
    color: {PALETTE.text};
    font-family: {TYPE.content_family};
    font-size: {TYPE.section_px}px;
    font-weight: 600;
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
QFrame#inspectorRouteContext {{
    background: {PALETTE.surface};
    border: 0;
}}
QLabel#inspectorTitle {{
    color: {PALETTE.accent};
    font-size: 13px;
    font-weight: 650;
}}
QLabel#inspectorHeading {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: 22px;
    font-weight: 500;
}}
QLabel#inspectorBody {{
    color: {PALETTE.text_muted};
    font-size: 13px;
}}

/* Empty workspaces should read as a document field, not a black card. */
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
    font-family: {TYPE.display_family};
    font-size: 26px;
    font-weight: 500;
}}
QLabel#emptyStateBody {{
    color: {PALETTE.text_subtle};
    font-size: 13px;
}}

/* Large centered work composer from the Workspace references. */
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
    padding: 0 {SPACE.md}px;
}}
QLineEdit#promptInput:disabled {{ color: {PALETTE.text_quiet}; }}
QPushButton#groundButton,
QPushButton#groundButton:disabled {{
    color: {PALETTE.text_subtle};
    background: transparent;
    border: 0;
}}
QPushButton#groundButton:hover,
QPushButton#groundButton:checked {{
    color: {PALETTE.accent};
    background: {PALETTE.accent_soft};
}}
QPushButton#sendButton {{
    min-width: {SHELL.composer_action_size}px;
    max-width: {SHELL.composer_action_size}px;
    min-height: {SHELL.composer_action_size}px;
    max-height: {SHELL.composer_action_size}px;
    border: 0;
    border-radius: {SHELL.composer_action_size // 2}px;
    background: {PALETTE.accent};
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
}}
QPushButton#sendButton:hover {{ background: {PALETTE.accent_hover}; }}
QPushButton#sendButton:focus {{
    background: {PALETTE.accent_hover};
    border: 2px solid {PALETTE.text};
}}
QPushButton#sendButton:pressed {{ background: {PALETTE.accent_pressed}; }}
QPushButton#sendButton:disabled {{
    background: {PALETTE.surface_selected};
    color: {PALETTE.text_quiet};
    border: 1px solid {PALETTE.border};
}}

/* Reassert canonical reference colours over older orange-centric passes. */
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
QPlainTextEdit:hover {{ border-color: {PALETTE.border_strong}; }}
QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QPlainTextEdit:focus {{ border-color: {PALETTE.accent}; }}
QPushButton {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
}}
QPushButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}
QPushButton:focus {{ border-color: {PALETTE.accent}; }}
QCheckBox {{ color: {PALETTE.text_muted}; }}
QCheckBox::indicator {{
    border: 1px solid {PALETTE.border_strong};
    background: {PALETTE.surface};
}}
QCheckBox::indicator:checked {{
    border-color: {PALETTE.accent};
    background: {PALETTE.accent};
}}
QSlider::groove:horizontal {{ background: {PALETTE.border}; height: 2px; }}
QSlider::sub-page:horizontal {{ background: {PALETTE.accent}; }}
QSlider::handle:horizontal {{ background: {PALETTE.accent}; border: 0; }}
QProgressBar::chunk {{ background: {PALETTE.accent}; }}
QSplitter::handle {{ background: {PALETTE.border}; }}
QSplitter::handle:horizontal {{ width: 1px; margin: 0 {SPACE.xs}px; }}
QWidget[pathenaStateSurface="true"] {{ border-color: {PALETTE.border}; }}
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

/* Knowledge reference: flat browser, cobalt tabs, no legacy orange/black islands. */
QTabWidget#canonicalMemoryTabs {{
    background: {PALETTE.canvas};
    border: 0;
}}
QTabWidget#canonicalMemoryTabs::pane {{
    background: {PALETTE.canvas};
    border: 0;
    border-top: 1px solid {PALETTE.border};
    top: -1px;
}}
QTabWidget#canonicalMemoryTabs QTabBar::tab {{
    color: {PALETTE.text_subtle};
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    min-height: 34px;
    padding: 0 18px;
}}
QTabWidget#canonicalMemoryTabs QTabBar::tab:hover {{
    color: {PALETTE.text};
}}
QTabWidget#canonicalMemoryTabs QTabBar::tab:selected {{
    color: {PALETTE.accent};
    border-bottom: 2px solid {PALETTE.accent};
}}
QLineEdit#knowledgeSearchInput {{
    min-height: 40px;
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    padding: 0 12px;
}}
QLineEdit#knowledgeSearchInput:focus {{ border-color: {PALETTE.accent}; }}
QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    outline: 0;
}}
QListWidget#persistentKnowledgeList::item,
QListWidget#persistentClaimList::item,
QListWidget#semanticReviewList::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
    min-height: 40px;
    padding: 4px 10px;
}}
QListWidget#persistentKnowledgeList::item:selected,
QListWidget#persistentClaimList::item:selected,
QListWidget#semanticReviewList::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-left: 2px solid {PALETTE.accent};
}}

/* Research and Jobs share the reference master-detail language. */
QListWidget#researchJobList,
QListWidget#durableJobList {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    outline: 0;
    padding: 4px;
}}
QListWidget#researchJobList::item,
QListWidget#durableJobList::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    min-height: 42px;
    padding: 4px 9px;
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
}}
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-left: 2px solid {PALETTE.accent};
}}
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: 12px;
}}
QLabel#researchStatus,
QLabel#schedulerStatus,
QLabel#jobsStatus {{ color: {PALETTE.text_subtle}; }}

/* Sources use the same master-detail language rather than base-theme black. */
QListWidget#sourceList {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    outline: 0;
}}
QListWidget#sourceList::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    min-height: 42px;
    padding: 4px 9px;
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
}}
QListWidget#sourceList::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-left: 2px solid {PALETTE.accent};
}}
QPlainTextEdit#sourceDetails {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: 12px;
}}
QLabel#sourceStatus {{ color: {PALETTE.text_subtle}; }}

/* Settings reference: quiet secondary rail + broad configuration surface. */
QListWidget#settingsSecondaryNavigation {{
    background: {PALETTE.surface};
    border: 0;
    border-right: 1px solid {PALETTE.border};
    border-radius: 0;
    padding: 8px 12px 8px 0;
}}
QListWidget#settingsSecondaryNavigation::item {{
    color: {PALETTE.text_muted};
    min-height: 42px;
    padding: 0 12px;
    border: 0;
    border-left: 2px solid transparent;
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
QWidget#settingsRuntimePanel {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
}}

/* Search / command palette reference: broad centered search surface. */
QDialog#commandPalette {{
    min-width: 700px;
    min-height: 510px;
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.panel}px;
}}
QDialog#helpDialog {{
    min-width: 920px;
    min-height: 700px;
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
}}
QLabel#commandPaletteTitle,
QLabel#helpDialogTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: 22px;
    font-weight: 500;
}}
QLabel#commandPaletteHint,
QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {{ color: {PALETTE.text_subtle}; }}
QLineEdit#commandPaletteQuery {{
    min-height: 48px;
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.control}px;
    padding: 0 14px;
    font-size: 15px;
}}
QLineEdit#commandPaletteQuery:focus {{ border-color: {PALETTE.accent}; }}
QListWidget#commandPaletteResults {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    outline: 0;
}}
QListWidget#commandPaletteResults::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
    min-height: 42px;
    padding: 5px 14px;
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
    padding: 16px;
}}

/* PALLAS reference: graph is the workspace, controls stay quiet. */
QFrame#pallasShellWorkspaceHost {{
    background: {PALETTE.canvas};
    border: 0;
}}
QLabel#pallasLivingStatus {{
    color: {PALETTE.success};
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {{
    min-height: 30px;
    padding: 0 10px;
    color: {PALETTE.text_subtle};
    background: transparent;
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
}}
QPushButton#pallasLensSemanticButton:hover,
QPushButton#pallasLensAgeButton:hover,
QPushButton#pallasLensVitalityButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QPushButton#pallasLensSemanticButton:checked,
QPushButton#pallasLensAgeButton:checked,
QPushButton#pallasLensVitalityButton:checked {{
    color: {PALETTE.accent};
    background: {PALETTE.accent_soft};
    border-color: {PALETTE.accent};
}}

/* System reference: secondary rail, structured health rows, posture column. */
QFrame#systemSubnav {{
    background: {PALETTE.surface};
    border: 0;
    border-right: 1px solid {PALETTE.border};
}}
QLabel#systemSubnavItem {{
    color: {PALETTE.text_quiet};
    min-height: 38px;
    padding-left: 10px;
}}
QLabel#systemSubnavItem[selected="true"] {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-left: 2px solid {PALETTE.accent};
}}
QFrame#systemStatusRow {{
    background: {PALETTE.surface};
    border: 0;
    border-bottom: 1px solid {PALETTE.border};
    border-radius: 0;
}}
QLabel#systemStatusTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: 19px;
    font-weight: 500;
}}
QLabel#systemStatusIcon {{ color: {PALETTE.success}; font-size: 18px; }}
QFrame#systemSecurityPosture {{
    background: {PALETTE.surface};
    border: 0;
    border-left: 1px solid {PALETTE.border};
}}
QLabel#systemRecentEventsEmpty,
QLabel#systemDetail {{ color: {PALETTE.text_subtle}; }}
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
        self._clear_legacy_inline_styles()
        self._install_top_navigation()
        self._apply_shared_geometry()
        self._apply_reference_styles()
        self.window.navigation.currentRowChanged.connect(self._sync_navigation)
        self._sync_navigation(self.window.navigation.currentRow())

    def _clear_legacy_inline_styles(self) -> None:
        for object_name in _LEGACY_INLINE_STYLE_OBJECTS:
            widget = self.window.findChild(QWidget, object_name)
            if widget is not None and widget.styleSheet():
                widget.setStyleSheet("")

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

        # Older accessibility proxy buttons remain connected to the router but
        # must not compete visually with the canonical reference navigation.
        for proxy in top_bar.findChildren(QPushButton, "topNavButton"):
            proxy.hide()

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
            button.setAccessibleDescription(f"Open {label.title()} workspace")
            button.setToolTip(f"Open {label.title()}")
            button.clicked.connect(
                lambda _checked=False, index=row: self.window.navigation.setCurrentRow(index)
            )
            primary_layout.addWidget(button)
            self._primary_buttons[row] = button

        top_layout.insertWidget(1, primary)

        old_search = top_bar.findChild(QPushButton, "topSearchButton")
        if old_search is not None:
            old_search.deleteLater()
        search = QPushButton("⌕", top_bar)
        search.setObjectName("topSearchButton")
        search.setAccessibleName("Search and commands")
        search.setAccessibleDescription("Open search and command palette")
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
        for object_name in _REFERENCE_WORKSPACE_OBJECTS:
            surface = self.window.findChild(QWidget, object_name)
            if surface is not None:
                surface.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

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

        secondary_navigation = self.window.findChild(
            QListWidget, "settingsSecondaryNavigation"
        )
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
        self.window.send_button.setFixedSize(
            SHELL.composer_action_size,
            SHELL.composer_action_size,
        )
        self.window.ground_button.setMinimumHeight(36)
        self.window.ground_button.setMaximumHeight(40)

        keyboard_hint = self.window.findChild(QWidget, "keyboardHint")
        if keyboard_hint is not None:
            keyboard_hint.hide()

    def _apply_reference_styles(self) -> None:
        self.window.setStyleSheet(
            self.window.styleSheet() + _REFERENCE_PARITY_STYLESHEET
        )
        # Child-local styling wins Qt's cascade. Force the two real Research
        # text inputs onto the shared cobalt focus contract after all legacy
        # presentation layers have installed their styles.
        for object_name in ("researchQuestionInput", "researchJobFilter"):
            field = self.window.findChild(QLineEdit, object_name)
            if field is None:
                continue
            field.setStyleSheet(
                f"""
                QLineEdit {{
                    color: {PALETTE.text};
                    background: {PALETTE.surface};
                    border: 1px solid {PALETTE.border};
                    border-radius: {RADII.control}px;
                    padding: 6px 10px;
                    selection-color: {PALETTE.text};
                    selection-background-color: {PALETTE.accent_soft};
                }}
                QLineEdit:hover {{ border-color: {PALETTE.border_strong}; }}
                QLineEdit:focus {{ border-color: {PALETTE.accent}; }}
                """
            )

    def _sync_navigation(self, row: int) -> None:
        if 0 <= row < len(_PAGE_TITLES):
            self.window.page_title.setText(_PAGE_TITLES[row])
            # Chat and System already have their own strong content hierarchy in
            # the opened references; avoid a redundant generic shell heading.
            self.window.page_title.setVisible(row not in {0, 5})

        for index, button in self._primary_buttons.items():
            selected = index == row
            button.setProperty("selected", selected)
            button.setAccessibleDescription(
                f"{button.text().title()}; current workspace"
                if selected
                else f"Open {button.text().title()} workspace"
            )
            _repolish(button)
        for index, button in self._utility_buttons.items():
            button.setProperty("selected", index == row)
            _repolish(button)

        # The reference family reserves the work composer for Chat. Other
        # workspaces own task-specific controls.
        composer = self.window.findChild(QFrame, "composer")
        if composer is not None:
            composer.setVisible(row == 0)

        # Dedicated workspaces own their detail panes. The generic inspector is
        # evidence-centric and appears only when Chat has real context to show.
        inspector = self.window.findChild(QFrame, "inspector")
        if inspector is not None:
            context_button = getattr(self.window, "context_button", None)
            context_available = (
                isinstance(context_button, QPushButton)
                and not context_button.isHidden()
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
