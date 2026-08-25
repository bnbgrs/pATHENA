"""Canonical pATHENA desktop presentation layer."""

from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SPACE, TYPE
from athena.desktop.pathena_shared_components import PATHENA_FOUNDATION_STYLESHEET
from athena.desktop.theme import APP_STYLESHEET as ATHENA_BASE_STYLESHEET


def _build_specialized_stylesheet() -> str:
    """Style pATHENA-specific surfaces without creating a second palette."""
    return f"""
/* pATHENA specialized surfaces: presentation only, canonical tokens only. */
QLabel#wordmark {{
    color: {PALETTE.text};
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 0 0 {SPACE.xxs}px 0;
}}

QLabel#statusSquare {{
    color: {PALETTE.success};
}}

QWidget#chatMessage {{
    background: transparent;
}}

QWidget#chatMessage QFrame#rule,
QWidget#chatMessage QFrame[role="rule"] {{
    background: transparent;
}}

QWidget#chatMessage QLabel#speaker,
QWidget#chatMessage QLabel#userMeta {{
    color: {PALETTE.text_subtle};
    font-family: {TYPE.metadata_family};
    font-size: {TYPE.metadata_px}px;
}}

QWidget#chatMessage QLabel#message {{
    color: {PALETTE.text_muted};
    font-size: {TYPE.body_px}px;
}}

QWidget#chatMessage QLabel#userMessage {{
    color: {PALETTE.text};
    font-size: {TYPE.body_px}px;
}}

QLabel#emptyChatState,
QLabel#settingsHelp {{
    color: {PALETTE.text_subtle};
}}

/* Meaning-bearing metadata inherited from the legacy base theme must not
   remain on its low-contrast TEXT_DIM tier. Decorative arrows and disabled
   controls intentionally keep their quieter inherited/foundation styling. */
QLabel#commandMeta,
QLabel#chainState {{
    color: {PALETTE.text_subtle};
}}

QPushButton:checked {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-color: {PALETTE.accent_pressed};
}}

QPushButton#detailsToggle,
QPushButton#contextToggle,
QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#rememberMessageButton,
QPushButton#addKnowledgeButton,
QPushButton#groundButton {{
    background: transparent;
    border-color: transparent;
}}

QPushButton#detailsToggle,
QPushButton#contextToggle {{
    min-height: 26px;
    padding: 0 {SPACE.xs}px;
    font-size: {TYPE.metadata_px}px;
}}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#rememberMessageButton,
QPushButton#addKnowledgeButton {{
    min-height: 22px;
    padding: 0 {SPACE.xs}px;
    color: {PALETTE.text_subtle};
    font-size: 10px;
}}

QPushButton#detailsToggle:hover,
QPushButton#contextToggle:hover,
QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#rememberMessageButton:hover,
QPushButton#addKnowledgeButton:hover,
QPushButton#groundButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border};
}}

QPushButton#detailsToggle:checked,
QPushButton#contextToggle:checked,
QPushButton#groundButton:checked {{
    color: {PALETTE.text};
    background: {PALETTE.accent_soft};
    border-color: {PALETTE.accent_pressed};
}}

QPushButton#rememberMessageButton:disabled,
QPushButton#addKnowledgeButton:disabled {{
    color: {PALETTE.text_quiet};
    background: transparent;
    border-color: transparent;
}}

QLineEdit#promptInput {{
    min-height: 42px;
    padding: 0 {SPACE.sm}px;
    font-size: {TYPE.body_px}px;
    background: {PALETTE.surface_raised};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.prominent}px;
}}

QLineEdit#promptInput:focus {{
    background: {PALETTE.surface_raised};
    border-color: {PALETTE.accent};
}}

QLabel#promptMarker {{
    min-width: 0;
    max-width: 0;
    color: transparent;
    padding: 0;
    margin: 0;
}}

QComboBox#chatSelector,
QComboBox#modelSelector {{
    min-height: 30px;
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
    color: {PALETTE.text_muted};
}}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover {{
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}

QLabel#commandPaletteTitle,
QLabel#helpDialogTitle {{
    color: {PALETTE.text};
    font-size: 14px;
    font-weight: 600;
}}

QLabel#commandPaletteHint,
QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {{
    color: {PALETTE.text_subtle};
    font-family: {TYPE.metadata_family};
}}

QLineEdit#commandPaletteQuery {{
    min-height: 38px;
    padding: 0 {SPACE.sm}px;
    background: {PALETTE.canvas};
    border: 1px solid {PALETTE.border_strong};
    border-radius: {RADII.control}px;
}}

QPlainTextEdit#helpText {{
    color: {PALETTE.text_muted};
    background: {PALETTE.canvas};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    padding: {SPACE.sm}px;
    selection-background-color: {PALETTE.accent_soft};
}}

QScrollArea,
QWidget#chatMessages,
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
    background: {PALETTE.canvas};
    border: none;
}}

QTabWidget#canonicalMemoryTabs::pane {{
    background: transparent;
    border: none;
    border-top: 1px solid {PALETTE.border};
    top: -1px;
}}

QTabWidget#canonicalMemoryTabs QTabBar::tab {{
    color: {PALETTE.text_subtle};
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    min-height: 30px;
    padding: 0 {SPACE.sm}px;
    margin-right: {SPACE.xxs}px;
    font-family: {TYPE.metadata_family};
    font-size: {TYPE.metadata_px}px;
}}

QTabWidget#canonicalMemoryTabs QTabBar::tab:hover {{
    color: {PALETTE.text_muted};
}}

QTabWidget#canonicalMemoryTabs QTabBar::tab:selected {{
    color: {PALETTE.text};
    border-bottom-color: {PALETTE.accent};
}}

QLineEdit#knowledgeSearchInput {{
    background: {PALETTE.surface};
    border-color: {PALETTE.border};
}}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#durableJobList,
QListWidget#sourceList,
QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {{
    color: {PALETTE.text_muted};
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
    padding: {SPACE.xs}px;
    selection-background-color: {PALETTE.accent_soft};
    selection-color: {PALETTE.text};
}}

QListWidget#persistentKnowledgeList::item,
QListWidget#persistentClaimList::item,
QListWidget#semanticReviewList::item,
QListWidget#researchJobList::item,
QListWidget#durableJobList::item,
QListWidget#sourceList::item {{
    color: {PALETTE.text_muted};
    background: transparent;
    border: none;
    border-bottom: 1px solid {PALETTE.border};
    padding: {SPACE.xs}px {SPACE.sm}px;
}}

QListWidget#persistentKnowledgeList::item:hover,
QListWidget#persistentClaimList::item:hover,
QListWidget#semanticReviewList::item:hover,
QListWidget#researchJobList::item:hover,
QListWidget#durableJobList::item:hover,
QListWidget#sourceList::item:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
}}

QListWidget#persistentKnowledgeList::item:selected,
QListWidget#persistentClaimList::item:selected,
QListWidget#semanticReviewList::item:selected,
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected,
QListWidget#sourceList::item:selected {{
    color: {PALETTE.text};
    background: {PALETTE.surface_selected};
    border-left: 2px solid {PALETTE.accent};
}}

QFrame#systemMetric,
QFrame#knowledgeReviewPanel {{
    background: {PALETTE.surface};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.panel}px;
}}

QFrame#knowledgeReviewItem {{
    background: {PALETTE.canvas};
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
}}

QLabel#knowledgeReviewTitle,
QLabel#knowledgeReviewItemTitle {{
    color: {PALETTE.text};
    font-weight: 600;
}}

QLabel#knowledgeReviewState {{
    color: {PALETTE.text_subtle};
}}

QLabel#knowledgeReviewItemBody {{
    color: {PALETTE.text_muted};
}}

QPushButton#knowledgeReviewCloseButton,
QPushButton#knowledgeMergeButton {{
    min-height: 24px;
    padding: 0 {SPACE.xs}px;
    color: {PALETTE.text_subtle};
    background: transparent;
    border: 1px solid {PALETTE.border};
    border-radius: {RADII.control}px;
    font-size: {TYPE.metadata_px}px;
}}

QPushButton#knowledgeReviewCloseButton:hover,
QPushButton#knowledgeMergeButton:hover {{
    color: {PALETTE.text};
    background: {PALETTE.surface_hover};
    border-color: {PALETTE.border_strong};
}}

QSplitter::handle {{
    background: {PALETTE.border};
}}

QSplitter::handle:horizontal {{
    width: 1px;
    margin: 0 {SPACE.xs}px;
}}

QFrame#sessionControls,
QFrame#evidenceChain {{
    background: transparent;
    border: none;
}}
"""


PATHENA_SPECIALIZED_STYLESHEET = _build_specialized_stylesheet()
PATHENA_STYLESHEET = (
    ATHENA_BASE_STYLESHEET
    + PATHENA_SPECIALIZED_STYLESHEET
    + PATHENA_FOUNDATION_STYLESHEET
)
