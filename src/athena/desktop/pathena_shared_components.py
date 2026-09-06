"""Shared pATHENA shell and component presentation contract.

The selectors intentionally target existing object names and dynamic
properties. They add no controls, actions, status claims, or backend paths.
"""

from __future__ import annotations

from typing import Final

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SPACE, TYPE

SHARED_OBJECT_NAMES: Final = (
    "athenaMainWindow",
    "root",
    "rail",
    "navigation",
    "conversation",
    "pageTitle",
    "inspector",
    "inspectorPanel",
    "groundedInspectorPanel",
    "inspectorEvidenceCard",
    "pallasVisualPlaceholder",
    "composer",
    "promptInput",
    "groundButton",
    "sendButton",
    "commandPalette",
    "commandPaletteQuery",
    "commandPaletteResults",
)

SHARED_DYNAMIC_PROPERTIES: Final = (
    "pathenaActionRole",
    "pathenaDisabledClarity",
    "pathenaKeyboardFocus",
    "pathenaUiState",
)


def build_foundation_stylesheet() -> str:
    """Build the flat shared foundation from the immutable token contract."""
    return f"""
/* pATHENA shared design foundation DS-001 */
QMainWindow#athenaMainWindow,
QWidget#root,
QFrame#conversation {{
    background: {PALETTE.canvas};
    color: {PALETTE.text};
}}

QWidget {{
    color: {PALETTE.text};
    font-family: {TYPE.content_family};
    font-size: {TYPE.body_px}px;
}}

QFrame#rail {{
    background: {PALETTE.surface};
    border: none;
    border-right: 1px solid {PALETTE.border};
}}

QLabel#wordmark,
QLabel#pageTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.display_family};
    font-weight: 600;
}}

QLabel#pageTitle {{
    font-size: {TYPE.title_px}px;
}}

QLabel#localStatus,
QLabel#networkState,
QLabel#keyboardHint,
QLabel#breadcrumb,
QLabel#speaker,
QLabel#sessionLabel,
QLabel#settingsLabel,
QLabel#inspectorEvidenceMeta,
QLabel#inspectorActivityItem {{
    color: {PALETTE.text_subtle};
    font-family: {TYPE.metadata_family};
    font-size: {TYPE.metadata_px}px;
}}

QFrame#rule,
QFrame[role="rule"] {{
    background: {PALETTE.border};
    border: none;
    min-height: 1px;
    max-height: 1px;
}}

QListWidget#navigation {{
    background: transparent;
    border: none;
    outline: none;
    padding: 0;
}}

QListWidget#navigation::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: none;
    border-left: 2px solid transparent;
    border-radius: {RADII.control}px;
    padding: {SPACE.xs}px {SPACE.sm}px;
    margin: 1px 0;
}}

QListWidget#navigation::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}

QListWidget#navigation::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}

QFrame#inspector,
QFrame#inspectorPanel {{
    background: {PALETTE.surface};
    border: none;
    border-left: 1px solid {PALETTE.border};
}}

QFrame#groundedInspectorPanel {{
    background: transparent;
    border: none;
    border-top: 1px solid {PALETTE.border};
}}

QLabel#inspectorSectionTitle {{
    color: {PALETTE.text};
    font-family: {TYPE.content_family};
    font-size: {TYPE.body_px}px;
    font-weight: 600;
}}

QFrame#inspectorEvidenceCard {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
}}

QFrame#inspectorEvidenceCard[cited="true"] {{
    border-left: 2px solid {PALETTE.accent};
}}

QLabel#inspectorEvidenceTitle {{
    color: {PALETTE.text};
    font-weight: 600;
}}

QLabel#inspectorEvidenceEmpty {{
    color: {PALETTE.text_muted};
}}

QLabel#inspectorActivityItem {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    padding: {SPACE.sm}px;
}}

QFrame#pallasVisualPlaceholder {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.prominent}px;
}}

QFrame#composer {{
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.prominent}px;
}}

QLineEdit#promptInput {{
    background: transparent;
    border: none;
    min-height: 42px;
    padding: 0 {SPACE.sm}px;
}}

QLineEdit#promptInput:focus {{
    border: none;
}}

QPushButton#groundButton {{
    color: {PALETTE.text_muted};
    background: transparent;
    border-color: transparent;
}}

QPushButton#groundButton:hover,
QPushButton#groundButton:checked {{
    color: {PALETTE.accent};
    background: {PALETTE.accent_soft};
    border-color: {PALETTE.accent_soft};
}}

QPushButton {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    min-height: 30px;
    padding: 0 {SPACE.sm}px;
}}

QPushButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}

QPushButton:pressed {{
    background: {PALETTE.accent_soft};
    border-color: {PALETTE.accent_pressed};
}}

QPushButton#sendButton,
QPushButton[role="primary"],
QPushButton[pathenaActionRole="primary"] {{
    color: {PALETTE.canvas};
    background: {PALETTE.accent};
    border-color: {PALETTE.accent};
    font-weight: 600;
}}

QPushButton#sendButton {{
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    border-radius: 22px;
    padding: 0;
}}

QPushButton#sendButton:hover,
QPushButton[role="primary"]:hover,
QPushButton[pathenaActionRole="primary"]:hover {{
    background: {PALETTE.accent_hover};
    border-color: {PALETTE.accent_hover};
}}

QPushButton:disabled,
QWidget[pathenaDisabledClarity="true"]:disabled {{
    color: {PALETTE.text_quiet};
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
}}

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
QDoubleSpinBox:hover {{
    border-color: {PALETTE.border_strong};
}}

QPushButton:focus,
QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QListWidget:focus,
QPlainTextEdit#persistentKnowledgeDetails:focus,
QPlainTextEdit#persistentClaimDetails:focus,
QPlainTextEdit#semanticReviewDetails:focus,
QPlainTextEdit#researchDetails:focus,
QPlainTextEdit#jobDetails:focus,
QPlainTextEdit#helpText:focus,
QWidget[pathenaKeyboardFocus="true"] {{
    border: 1px solid {PALETTE.accent};
}}

QDialog#commandPalette,
QDialog#helpDialog {{
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
}}

QListWidget#commandPaletteResults::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border-radius: {RADII.control}px;
    min-height: 32px;
    padding: {SPACE.xs}px {SPACE.sm}px;
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

QListWidget#persistentKnowledgeList:focus::item:current,
QListWidget#persistentClaimList:focus::item:current,
QListWidget#semanticReviewList:focus::item:current,
QListWidget#researchJobList:focus::item:current,
QListWidget#durableJobList:focus::item:current {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-left: 2px solid {PALETTE.accent};
}}

QTabWidget#canonicalMemoryTabs QTabBar:focus::tab:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-bottom: 2px solid {PALETTE.accent};
}}

QToolTip {{
    color: {PALETTE.text};
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
    padding: {SPACE.xs}px {SPACE.sm}px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {PALETTE.border_strong};
    border-radius: 4px;
    min-height: 28px;
}}

QScrollBar::handle:vertical:hover {{
    background: {PALETTE.text_quiet};
}}
"""


PATHENA_FOUNDATION_STYLESHEET: Final = build_foundation_stylesheet()
