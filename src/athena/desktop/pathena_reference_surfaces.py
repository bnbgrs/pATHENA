"""Late presentation layer for the eleven pATHENA visual references.

The long-lived workspace controllers remain authoritative for data, actions and
state. This module runs after the refinement stack and only normalizes visual
presentation where older component-local styles would otherwise win over the
shared navy/cobalt design system.
"""

from __future__ import annotations

from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop import pathena_pallas_field as pallas_field
from athena.desktop.pathena_design_tokens import PALETTE, RADII, SPACE, TYPE

_WORKSPACE_ROOTS = (
    "pageChat",
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
    background: transparent;
}}
QWidget#pageChat,
QWidget#knowledgeWorkspace,
QWidget#researchWorkspace,
QWidget#jobsWorkspace,
QWidget#filesWorkspace,
QWidget#systemWorkspace,
QWidget#pageSettings {{
    color: {PALETTE.text};
    background: {PALETTE.canvas};
}}
QFrame {{
    background: transparent;
    border: none;
}}
QSplitter {{
    background: transparent;
    border: none;
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
    padding: 0 {SPACE.sm}px;
}}
QPlainTextEdit {{
    padding: {SPACE.xs}px {SPACE.sm}px;
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
    background: transparent;
    border: none;
    border-top: 1px solid {PALETTE.border};
}}
QTabBar::tab {{
    min-height: 30px;
    padding: 0 {SPACE.sm}px;
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
    margin: 0 {SPACE.xs}px;
}}
QScrollArea,
QWidget#chatMessages {{
    background: transparent;
    border: none;
}}
QScrollArea#chatScroll,
QScrollArea#chatScroll QWidget,
QScrollArea#knowledgeWorkspaceScroll,
QScrollArea#knowledgeWorkspaceScroll QWidget {{
    background: {PALETTE.canvas};
    border: none;
}}
QFrame#emptyStatePanel {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.prominent}px;
}}
QLabel#emptyStateEyebrow {{
    color: {PALETTE.accent};
    font-size: 10px;
    font-weight: 650;
}}
QLabel#emptyStateTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-size: 24px;
    font-weight: 500;
}}
QLabel#emptyStateBody {{
    color: {PALETTE.text_subtle};
    font-size: 12px;
}}
QLineEdit#promptInput:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
}}
QPushButton#sendButton:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface_selected};
    border: 1px solid {PALETTE.border};
}}
QComboBox#chatSelector:disabled,
QComboBox#modelSelector:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
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
    padding: 4px {SPACE.xs}px;
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
    margin: 2px {SPACE.xs}px 2px 0;
}}
QFrame#settingsRuntimePanel {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: {SPACE.sm}px;
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
    background: transparent;
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
    padding: 0 {SPACE.sm}px;
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
QFrame#comfyUiStudio,
QFrame#comfyUiCenter {{
    background: {PALETTE.canvas};
    border: none;
}}
QFrame#comfyUiIntegrationNav {{
    background: {PALETTE.surface};
    border: none;
    border-right: 1px solid {PALETTE.border};
}}
QFrame#comfyUiConnectionPanel {{
    background: {PALETTE.surface};
    border: none;
    border-left: 1px solid {PALETTE.border};
}}
QLabel#comfyUiNavTitle {{
    color: {PALETTE.text};
    font-size: 14px;
    font-weight: 600;
}}
QLabel#comfyUiNavItem {{
    min-height: 30px;
    padding: 4px 9px;
    color: {PALETTE.text_subtle};
    border-radius: {RADII.control}px;
}}
QLabel#comfyUiNavItem[selected="true"] {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}
QLabel#comfyUiPanelTitle {{
    color: {PALETTE.text};
    font-size: 14px;
    font-weight: 600;
}}
QPushButton#comfyUiCheckConnection,
QPushButton#comfyUiBrowseWorkflow,
QPushButton#comfyUiQueueWorkflow,
QPushButton#comfyUiRefreshJob,
QPushButton#comfyUiReleaseVram {{
    min-height: 34px;
    padding: 0 {SPACE.sm}px;
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


def _clear_layout(layout: QLayout) -> None:
    """Detach visual layout items without deleting the controls they contain."""
    while layout.count():
        item = layout.takeAt(0)
        child_layout = item.layout()
        if child_layout is not None:
            _clear_layout(child_layout)
            child_layout.deleteLater()


def _label_with_text(root: QWidget, text: str) -> QLabel | None:
    normalized = text.casefold()
    return next(
        (
            label
            for label in root.findChildren(QLabel)
            if label.text().strip().casefold() == normalized
        ),
        None,
    )


def _compose_comfyui_studio(dialog: QDialog) -> None:
    """Reflow existing real ComfyUI controls into the three-column reference studio."""
    if dialog.findChild(QFrame, "comfyUiStudio") is not None:
        return
    outer = dialog.layout()
    if not isinstance(outer, QVBoxLayout):
        return

    title = dialog.findChild(QLabel, "comfyUiTitle")
    intro = next(
        (
            label
            for label in dialog.findChildren(QLabel)
            if label.text().startswith("Local image + video workflow")
        ),
        None,
    )
    endpoint = dialog.findChild(QWidget, "comfyUiEndpoint")
    workflow = dialog.findChild(QWidget, "comfyUiWorkflowPath")
    check = dialog.findChild(QPushButton, "comfyUiCheckConnection")
    browse = dialog.findChild(QPushButton, "comfyUiBrowseWorkflow")
    queue = dialog.findChild(QPushButton, "comfyUiQueueWorkflow")
    refresh = dialog.findChild(QPushButton, "comfyUiRefreshJob")
    release = dialog.findChild(QPushButton, "comfyUiReleaseVram")
    status = dialog.findChild(QLabel, "comfyUiStatus")
    resources = dialog.findChild(QLabel, "comfyUiResourceStatus")
    receipt = dialog.findChild(QLabel, "comfyUiQueueReceipt")
    job_status = dialog.findChild(QLabel, "comfyUiJobStatus")
    required = (
        title,
        intro,
        endpoint,
        workflow,
        check,
        browse,
        queue,
        refresh,
        release,
        status,
        resources,
        receipt,
        job_status,
    )
    if any(widget is None for widget in required):
        return

    _clear_layout(outer)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    studio = QFrame(dialog)
    studio.setObjectName("comfyUiStudio")
    studio.setProperty("pathenaReferenceStudio", True)
    studio.setAccessibleName("ComfyUI integration studio")
    studio_layout = QHBoxLayout(studio)
    studio_layout.setContentsMargins(0, 0, 0, 0)
    studio_layout.setSpacing(0)

    nav = QFrame(studio)
    nav.setObjectName("comfyUiIntegrationNav")
    nav.setFixedWidth(196)
    nav_layout = QVBoxLayout(nav)
    nav_layout.setContentsMargins(18, 24, 16, 20)
    nav_layout.setSpacing(8)
    nav_title = QLabel("Integrations", nav)
    nav_title.setObjectName("comfyUiNavTitle")
    nav_layout.addWidget(nav_title)
    nav_layout.addSpacing(8)
    for text, selected in (
        ("LM Studio", False),
        ("Obsidian", False),
        ("ComfyUI", True),
    ):
        item = QLabel(text, nav)
        item.setObjectName("comfyUiNavItem")
        item.setProperty("selected", selected)
        item.setAccessibleName(f"Integration: {text}")
        if not selected:
            item.setToolTip("Configured from its existing pATHENA surface")
        nav_layout.addWidget(item)
    nav_layout.addStretch(1)

    center = QFrame(studio)
    center.setObjectName("comfyUiCenter")
    center_layout = QVBoxLayout(center)
    center_layout.setContentsMargins(30, 24, 30, 24)
    center_layout.setSpacing(12)
    center_layout.addWidget(title)
    center_layout.addWidget(intro)
    center_layout.addSpacing(10)

    workflow_heading = QLabel("Workflow", center)
    workflow_heading.setObjectName("comfyUiPanelTitle")
    center_layout.addWidget(workflow_heading)
    workflow_row = QHBoxLayout()
    workflow_row.setSpacing(8)
    workflow_row.addWidget(workflow, 1)
    workflow_row.addWidget(browse)
    center_layout.addLayout(workflow_row)
    center_layout.addWidget(queue, 0)
    center_layout.addWidget(receipt)
    center_layout.addSpacing(10)

    activity_heading = QLabel("Activity", center)
    activity_heading.setObjectName("comfyUiPanelTitle")
    center_layout.addWidget(activity_heading)
    center_layout.addWidget(job_status)
    activity_actions = QHBoxLayout()
    activity_actions.setSpacing(8)
    activity_actions.addWidget(refresh)
    activity_actions.addWidget(release)
    activity_actions.addStretch(1)
    center_layout.addLayout(activity_actions)
    center_layout.addStretch(1)

    connection = QFrame(studio)
    connection.setObjectName("comfyUiConnectionPanel")
    connection.setFixedWidth(310)
    connection_layout = QVBoxLayout(connection)
    connection_layout.setContentsMargins(22, 24, 22, 20)
    connection_layout.setSpacing(10)
    connection_title = QLabel("Connection", connection)
    connection_title.setObjectName("comfyUiPanelTitle")
    connection_layout.addWidget(connection_title)
    endpoint_label = QLabel("Endpoint", connection)
    endpoint_label.setProperty("role", "muted")
    connection_layout.addWidget(endpoint_label)
    connection_layout.addWidget(endpoint)
    connection_layout.addWidget(check)
    connection_layout.addWidget(status)
    connection_layout.addSpacing(8)
    resource_heading = QLabel("Resources", connection)
    resource_heading.setObjectName("comfyUiPanelTitle")
    connection_layout.addWidget(resource_heading)
    connection_layout.addWidget(resources)
    connection_layout.addStretch(1)

    studio_layout.addWidget(nav)
    studio_layout.addWidget(center, 1)
    studio_layout.addWidget(connection)
    outer.addWidget(studio, 1)


def _apply_pallas_palette(window: QWidget) -> None:
    """Update renderer presentation constants before future graph items are built."""
    pallas_field._CANVAS = QColor(PALETTE.canvas)  # noqa: SLF001
    pallas_field._TEXT = QColor(PALETTE.text)  # noqa: SLF001
    pallas_field._MUTED = QColor(PALETTE.text_muted)  # noqa: SLF001
    pallas_field._QUIET = QColor(PALETTE.text_quiet)  # noqa: SLF001
    pallas_field._BORDER = QColor(PALETTE.border)  # noqa: SLF001
    pallas_field._ACCENT = QColor(PALETTE.accent)  # noqa: SLF001
    pallas_field._CONFLICT = QColor(PALETTE.error)  # noqa: SLF001
    pallas_field._UNCERTAIN = QColor(PALETTE.warning)  # noqa: SLF001
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
        _compose_comfyui_studio(comfyui)
        comfyui.setStyleSheet(comfyui.styleSheet() + _REFERENCE_DIALOG_STYLESHEET)
        comfyui.resize(1180, 700)
        _mark_primary_actions(comfyui)

    _apply_pallas_palette(window)
