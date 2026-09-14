"""Late presentation layer for the eleven pATHENA visual references.

The long-lived workspace controllers remain authoritative for data, actions and
state.  This module runs after the refinement stack and only normalizes visual
presentation where older component-local styles would otherwise win over the
shared navy/cobalt design system.
"""

from __future__ import annotations

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QDialog, QGraphicsView, QPushButton, QWidget

from athena.desktop import pathena_pallas_field as pallas_field
from athena.desktop.pathena_design_tokens import PALETTE, RADII, SPACE, TYPE

_WORKSPACE_ROOTS = (
    "knowledgeWorkspace",
    "researchWorkspace",
    "jobsWorkspace",
    "filesWorkspace",
    "systemWorkspace",
    "pageSettings",
)

_PRIMARY_ACTION_TEXT = frozenset(
    {
        "START RESEARCH",
        "IMPORT FILE",
        "QUEUE WORKFLOW",
        "RUN WORKFLOW",
        "SAVE CHANGES",
    }
)

_REFERENCE_WORKSPACE_STYLESHEET = f"""
QWidget {{
    color: {PALETTE.text};
}}
QLabel#speaker,
QLabel[role="section"] {{
    color: {PALETTE.text_muted};
    font-family: {TYPE.metadata_family};
    font-size: {TYPE.metadata_px}px;
    font-weight: 600;
}}
QLabel#settingsHelp,
QLabel[role="muted"],
QLabel[role="dim"] {{
    color: {PALETTE.text_subtle};
}}
QLabel#settingsValue {{
    color: {PALETTE.text_muted};
}}
QLineEdit,
QPlainTextEdit,
QListWidget,
QComboBox,
QSpinBox,
QDoubleSpinBox {{
    color: {PALETTE.text};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    selection-color: {PALETTE.text};
    selection-background-color: {PALETTE.surface_selected};
}}
QLineEdit {{
    min-height: 36px;
    padding: 0 11px;
}}
QPlainTextEdit {{
    padding: 10px 12px;
}}
QListWidget {{
    outline: none;
    padding: 2px;
}}
QListWidget::item {{
    min-height: 28px;
    padding: 6px 10px;
    color: {PALETTE.text_muted};
    background: transparent;
    border: none;
    border-bottom: 1px solid {PALETTE.border};
}}
QListWidget::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QListWidget::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}
QLineEdit:hover,
QPlainTextEdit:hover,
QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover {{
    border-color: {PALETTE.border_strong};
}}
QLineEdit:focus,
QPlainTextEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {{
    border-color: {PALETTE.accent};
}}
QTabWidget::pane {{
    background: {PALETTE.canvas};
    border: none;
    border-top: 1px solid {PALETTE.border};
}}
QTabBar::tab {{
    min-height: 30px;
    padding: 0 12px;
    margin-right: 3px;
    color: {PALETTE.text_subtle};
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QTabBar::tab:selected {{
    color: {PALETTE.text};
    border-bottom-color: {PALETTE.accent};
}}
QPushButton#newChatButton {{
    min-height: 30px;
    padding: 0 11px;
    color: {PALETTE.text_muted};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    font-size: 11px;
    font-weight: 600;
}}
QPushButton#newChatButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}
QPushButton#newChatButton:focus {{
    color: {PALETTE.text};
    border-color: {PALETTE.accent};
}}
QPushButton#newChatButton:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
}}
QPushButton[pathenaReferencePrimary="true"] {{
    color: #FFFFFF;
    background: {PALETTE.accent};
    border: 1px solid {PALETTE.accent};
}}
QPushButton[pathenaReferencePrimary="true"]:hover {{
    color: #FFFFFF;
    background: {PALETTE.accent_hover};
    border-color: {PALETTE.accent_hover};
}}
QSplitter::handle {{
    background: {PALETTE.border};
}}
QSplitter::handle:horizontal {{
    width: 1px;
    margin: 0 8px;
}}
QScrollArea {{
    background: {PALETTE.canvas};
    border: none;
}}
QFrame#systemStatusRow {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
}}
QFrame#systemStatusRow:hover {{
    background: {PALETTE.surface_raised};
    border-color: {PALETTE.border_strong};
}}
QLabel#systemStatusIcon {{
    color: {PALETTE.success};
    font-size: 18px;
}}
QLabel#systemStatusTitle,
QLabel#inspectorHeading {{
    color: {PALETTE.text};
    font-size: 14px;
    font-weight: 600;
}}
QFrame#systemSubnav {{
    background: transparent;
    border: none;
    border-right: 1px solid {PALETTE.border};
}}
QLabel#systemSubnavItem {{
    min-height: 30px;
    padding: 4px 8px;
    color: {PALETTE.text_subtle};
    border-radius: {RADII.control}px;
}}
QLabel#systemSubnavItem[selected="true"] {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
}}
QFrame#systemSecurityPosture {{
    background: transparent;
    border: none;
    border-left: 1px solid {PALETTE.border};
}}
QListWidget#settingsSecondaryNavigation {{
    background: transparent;
    border: none;
    border-right: 1px solid {PALETTE.border};
}}
QListWidget#settingsSecondaryNavigation::item {{
    border-bottom: none;
    margin: 2px 8px 2px 0;
}}
QFrame#settingsRuntimePanel {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: 12px;
}}
QLabel#settingsRuntimeTitle {{
    color: {PALETTE.text};
    font-size: 14px;
    font-weight: 600;
}}
"""

_REFERENCE_DIALOG_STYLESHEET = f"""
QDialog#commandPalette,
QWidget#helpWorkspace,
QDialog#comfyUiDialog {{
    color: {PALETTE.text};
    background: {PALETTE.canvas};
    border: 1px solid {PALETTE.border_strong};
}}
QDialog#commandPalette QLabel,
QWidget#helpWorkspace QLabel,
QDialog#comfyUiDialog QLabel {{
    color: {PALETTE.text_muted};
}}
QLabel#commandPaletteTitle,
QLabel#helpHeadline,
QLabel#comfyUiTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: 30px;
    font-weight: 500;
}}
QLabel#commandPaletteHint,
QLabel#commandPaletteFooter,
QLabel#helpSummary,
QLabel#comfyUiSectionLabel,
QLabel#comfyUiResourceStatus {{
    color: {PALETTE.text_subtle};
}}
QLineEdit#commandPaletteQuery,
QLineEdit#helpSearch,
QLineEdit#comfyUiEndpoint,
QLineEdit#comfyUiWorkflowPath {{
    min-height: 40px;
    padding: 0 12px;
    color: {PALETTE.text};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.control}px;
    selection-color: {PALETTE.text};
    selection-background-color: {PALETTE.surface_selected};
}}
QLineEdit#commandPaletteQuery:focus,
QLineEdit#helpSearch:focus {{
    border-color: {PALETTE.accent};
}}
QListWidget#commandPaletteResults,
QListWidget#helpSections,
QListWidget#helpCapabilities {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    outline: none;
}}
QListWidget#commandPaletteResults::item,
QListWidget#helpSections::item,
QListWidget#helpCapabilities::item {{
    min-height: 32px;
    padding: 7px 11px;
    color: {PALETTE.text_muted};
    background: transparent;
    border: none;
    border-bottom: 1px solid {PALETTE.border};
}}
QListWidget#commandPaletteResults::item:hover,
QListWidget#helpSections::item:hover,
QListWidget#helpCapabilities::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}
QListWidget#commandPaletteResults::item:selected,
QListWidget#helpSections::item:selected,
QListWidget#helpCapabilities::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}
QFrame#helpSecondaryNavigation {{
    background: {PALETTE.surface};
    border: none;
    border-right: 1px solid {PALETTE.border};
}}
QFrame#helpCapabilityContent {{
    background: transparent;
    border: none;
}}
QFrame#helpCapabilityRow {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
}}
QLabel#helpCapabilityTitle {{
    color: {PALETTE.text};
}}
QLabel#helpCapabilitySummary {{
    color: {PALETTE.text_subtle};
}}
QPushButton#comfyUiCheckConnection,
QPushButton#comfyUiBrowseWorkflow,
QPushButton#comfyUiQueueWorkflow,
QPushButton#comfyUiRefreshJob,
QPushButton#comfyUiReleaseVram {{
    min-height: 34px;
    padding: 0 12px;
    color: {PALETTE.text_muted};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
}}
QPushButton#comfyUiCheckConnection:hover,
QPushButton#comfyUiBrowseWorkflow:hover,
QPushButton#comfyUiRefreshJob:hover,
QPushButton#comfyUiReleaseVram:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}
QPushButton#comfyUiQueueWorkflow {{
    color: #FFFFFF;
    background: {PALETTE.accent};
    border-color: {PALETTE.accent};
}}
QPushButton#comfyUiQueueWorkflow:hover {{
    color: #FFFFFF;
    background: {PALETTE.accent_hover};
    border-color: {PALETTE.accent_hover};
}}
QPushButton#comfyUiQueueWorkflow:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
}}
QLabel#comfyUiStatus[pathenaUiState="success"],
QLabel#comfyUiJobStatus[pathenaUiState="success"] {{
    color: {PALETTE.success};
}}
QLabel#comfyUiStatus[pathenaUiState="error"],
QLabel#comfyUiJobStatus[pathenaUiState="error"] {{
    color: {PALETTE.error};
}}
"""

_PALLAS_STYLESHEET = f"""
QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace,
QWidget#pallasWorkspace,
QWidget#pallasSemanticField {{
    background: {PALETTE.canvas};
    color: {PALETTE.text};
    border: none;
}}
QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticState,
QLabel#pallasSemanticSelection {{
    color: {PALETTE.text_subtle};
}}
QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {{
    min-height: 30px;
    padding: 0 11px;
    color: {PALETTE.text_subtle};
    background: {PALETTE.surface};
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
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-color: {PALETTE.accent};
}}
"""


def _mark_primary_actions(root: QWidget) -> None:
    for button in root.findChildren(QPushButton):
        primary = button.text().strip().upper() in _PRIMARY_ACTION_TEXT
        button.setProperty("pathenaReferencePrimary", primary)
        style = button.style()
        style.unpolish(button)
        style.polish(button)
        button.update()


def _apply_pallas_palette(window: QWidget) -> None:
    """Update renderer presentation constants before future graph items are built."""
    pallas_field._CANVAS = QColor(PALETTE.canvas)  # type: ignore[attr-defined]
    pallas_field._TEXT = QColor(PALETTE.text)  # type: ignore[attr-defined]
    pallas_field._MUTED = QColor(PALETTE.text_muted)  # type: ignore[attr-defined]
    pallas_field._QUIET = QColor(PALETTE.text_quiet)  # type: ignore[attr-defined]
    pallas_field._BORDER = QColor(PALETTE.border)  # type: ignore[attr-defined]
    pallas_field._ACCENT = QColor(PALETTE.accent)  # type: ignore[attr-defined]
    pallas_field._CONFLICT = QColor(PALETTE.error)  # type: ignore[attr-defined]
    pallas_field._UNCERTAIN = QColor(PALETTE.warning)  # type: ignore[attr-defined]
    for canvas in window.findChildren(QGraphicsView, "pallasSemanticCanvas"):
        canvas.setBackgroundBrush(QBrush(QColor(PALETTE.canvas)))
    for root_name in ("pallasShellWorkspaceHost", "pallasWorkspace"):
        root = window.findChild(QWidget, root_name)
        if root is not None:
            root.setStyleSheet(root.styleSheet() + _PALLAS_STYLESHEET)


def apply_reference_surface_styles(window: QWidget) -> None:
    """Apply the final reference presentation without changing workspace behavior."""
    for root_name in _WORKSPACE_ROOTS:
        root = window.findChild(QWidget, root_name)
        if root is None:
            continue
        root.setStyleSheet(root.styleSheet() + _REFERENCE_WORKSPACE_STYLESHEET)
        _mark_primary_actions(root)

    command_palette = window.findChild(QDialog, "commandPalette")
    if command_palette is not None:
        command_palette.setStyleSheet(
            command_palette.styleSheet() + _REFERENCE_DIALOG_STYLESHEET
        )
        command_palette.resize(860, 620)

    help_workspace = window.findChild(QWidget, "helpWorkspace")
    if help_workspace is not None:
        help_workspace.setStyleSheet(
            help_workspace.styleSheet() + _REFERENCE_DIALOG_STYLESHEET
        )

    comfyui = window.findChild(QDialog, "comfyUiDialog")
    if comfyui is not None:
        comfyui.setStyleSheet(comfyui.styleSheet() + _REFERENCE_DIALOG_STYLESHEET)
        comfyui.resize(980, 680)
        _mark_primary_actions(comfyui)

    _apply_pallas_palette(window)
