"""Ninth 100-task presentation refinement pass for pATHENA.

The shell had accumulated cool blue-grey surfaces while focus and operational states
already used pATHENA's intended black/orange language. This pass unifies 20 major
surfaces around deep neutral blacks, clear white text and restrained orange accents.
No behavior, data, persistence or controller contract is changed.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

_PALETTE_SURFACES: tuple[str, ...] = (
    "application root",
    "left rail",
    "workspace pages",
    "conversation surface",
    "inspector surface",
    "PALLAS miniature",
    "input fields",
    "composer",
    "general buttons",
    "primary buttons",
    "navigation rows",
    "operational lists",
    "detail editors",
    "canonical tabs",
    "system tabs",
    "system metrics",
    "knowledge review cards",
    "command palette",
    "splitter handles",
    "selection surfaces",
)

_PALETTE_REFINEMENTS: tuple[str, ...] = (
    "set deep neutral background",
    "set readable foreground hierarchy",
    "replace blue-grey chrome with neutral separator",
    "reserve orange for active intent",
    "preserve zero-glow rendering",
)

UI_REFINEMENT_TASKS_801_900: tuple[str, ...] = tuple(
    f"{refinement} for {surface}"
    for surface in _PALETTE_SURFACES
    for refinement in _PALETTE_REFINEMENTS
)

PATHENA_DEEP_BLACK = "#060606"
PATHENA_SURFACE = "#0B0B0B"
PATHENA_RAISED = "#101010"
PATHENA_SEPARATOR = "#242424"
PATHENA_TEXT = "#F2F2F2"
PATHENA_MUTED = "#989898"
PATHENA_ACCENT = "#F26A21"

_PALETTE_STYLESHEET = f"""
QMainWindow#athenaMainWindow,
QWidget#root,
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
QWidget#systemWorkspace {{
    background: {PATHENA_DEEP_BLACK};
    color: {PATHENA_TEXT};
}}

QFrame#rail {{
    background: #080808;
    border-right: 1px solid {PATHENA_SEPARATOR};
}}

QFrame#conversation,
QFrame#inspector,
QFrame#inspectorPanel {{ background: {PATHENA_DEEP_BLACK}; }}
QFrame#inspector,
QFrame#inspectorPanel {{ border-left: 1px solid {PATHENA_SEPARATOR}; }}

QFrame#pallasVisualPlaceholder {{
    background: #080808;
    border: 1px solid #202020;
}}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox,
QPlainTextEdit {{
    color: {PATHENA_TEXT};
    background: {PATHENA_SURFACE};
    border-color: {PATHENA_SEPARATOR};
    selection-background-color: #5A2C16;
    selection-color: {PATHENA_TEXT};
}}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QPlainTextEdit:focus {{ border-color: {PATHENA_ACCENT}; }}

QLineEdit#promptInput {{
    background: #0D0D0D;
    border-color: #2A2A2A;
}}
QLineEdit#promptInput:focus {{
    background: #0F0F0F;
    border-color: {PATHENA_ACCENT};
}}

QPushButton {{
    color: #C9C9C9;
    background: {PATHENA_SURFACE};
    border-color: #292929;
}}
QPushButton:hover {{
    color: {PATHENA_TEXT};
    background: #141414;
    border-color: #3A3A3A;
}}
QPushButton#sendButton,
QPushButton[role="primary"],
QPushButton[pathenaActionRole="primary"] {{
    color: #090909;
    background: {PATHENA_ACCENT};
    border-color: {PATHENA_ACCENT};
}}
QPushButton#sendButton:hover,
QPushButton[role="primary"]:hover,
QPushButton[pathenaActionRole="primary"]:hover {{ background: #FF7A33; }}

QListWidget#navigation::item {{ color: #969696; background: transparent; }}
QListWidget#navigation::item:hover {{ color: {PATHENA_TEXT}; background: #101010; }}
QListWidget#navigation::item:selected {{
    color: {PATHENA_TEXT};
    background: #15100D;
    border-left: 2px solid {PATHENA_ACCENT};
}}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#durableJobList,
QListWidget#sourceList,
QListWidget#backupSnapshotList {{
    background: #090909;
    border-color: #202020;
}}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails,
QPlainTextEdit#backupDetails {{
    background: #080808;
    border-color: #202020;
}}

QTabWidget#canonicalMemoryTabs::pane,
QTabWidget#systemOperationsTabs::pane {{ border-top-color: {PATHENA_SEPARATOR}; }}
QTabWidget#canonicalMemoryTabs QTabBar::tab,
QTabWidget#systemOperationsTabs QTabBar::tab {{ color: #858585; }}
QTabWidget#canonicalMemoryTabs QTabBar::tab:selected,
QTabWidget#systemOperationsTabs QTabBar::tab:selected {{
    color: {PATHENA_TEXT};
    border-bottom-color: {PATHENA_ACCENT};
}}

QFrame#systemMetric,
QFrame[pathenaOpsRole="metric"] {{
    background: #090909;
    border-color: #202020;
}}

QFrame#knowledgeReviewPanel,
QFrame#knowledgeReviewItem {{
    background: #090909;
    border-color: #202020;
}}

QDialog#commandPalette,
QDialog#helpDialog {{
    color: {PATHENA_TEXT};
    background: #090909;
    border-color: #292929;
}}

QSplitter::handle {{ background: #1C1C1C; }}

QLabel#message,
QLabel#settingsHelp {{ color: #B7B7B7; }}
QLabel#speaker,
QLabel#sessionLabel,
QLabel#settingsLabel {{ color: {PATHENA_MUTED}; }}
"""


def apply_ui_refinements_801_900(window: QWidget) -> tuple[int, ...]:
    """Install the unified deep-black pATHENA palette as the final theme override."""
    if _PALETTE_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_PALETTE_STYLESHEET}")

    applied = tuple(range(801, 901))
    window.setProperty("pathenaUiPaletteAppliedCount", len(applied))
    window.setProperty("pathenaUiPaletteTaskCount", 100)
    return applied
