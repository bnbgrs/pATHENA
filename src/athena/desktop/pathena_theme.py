"""Quiet Cognitive Workspace presentation layer for the pATHENA desktop shell."""

from __future__ import annotations

from athena.desktop.theme import APP_STYLESHEET as ATHENA_BASE_STYLESHEET

# Keep the mature ATHENA widget coverage, then override the shell with pATHENA's
# calmer visual language. This intentionally changes presentation only: object
# names, signals, controller bindings and workspace behaviour remain untouched.
PATHENA_STYLESHEET = ATHENA_BASE_STYLESHEET + r"""
QMainWindow#athenaMainWindow,
QWidget#root,
QFrame#conversation {
    background: #111315;
    color: #e9ecee;
}

QWidget {
    font-family: "Segoe UI", "Inter", sans-serif;
}

QFrame#rail {
    background: #15181b;
    border: none;
    border-right: 1px solid #262b30;
}

QLabel#wordmark {
    color: #f4f5f6;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 0 0 4px 0;
}

QLabel#localStatus,
QLabel#networkState,
QLabel#keyboardHint,
QLabel#breadcrumb {
    color: #778189;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
}

QLabel#statusSquare {
    color: #8fa59f;
}

QFrame#rule,
QFrame[role="rule"] {
    background: #272c30;
    min-height: 1px;
    max-height: 1px;
    border: none;
}

QListWidget#navigation {
    background: transparent;
    border: none;
    outline: none;
    padding: 0;
}

QListWidget#navigation::item {
    color: #9da5ab;
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 7px 10px;
    margin: 1px 0;
}

QListWidget#navigation::item:hover {
    color: #e9ecee;
    background: #1c2024;
}

QListWidget#navigation::item:selected {
    color: #f7f8f8;
    background: #262b30;
    border: none;
}

QLabel#pageTitle {
    color: #f3f5f6;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.2px;
}

QLabel#speaker,
QLabel#sessionLabel,
QLabel#settingsLabel {
    color: #8d979e;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QWidget#chatMessage QLabel#speaker,
QWidget#chatMessage QLabel#userMeta {
    color: #7f8990;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.2px;
}

QLabel#message,
QLabel#settingsHelp {
    color: #b5bcc1;
    font-size: 12px;
}

QPushButton {
    min-height: 30px;
    padding: 0 11px;
    color: #cbd1d5;
    background: #181c1f;
    border: 1px solid #2a3035;
    border-radius: 8px;
    font-weight: 500;
}

QPushButton:hover {
    color: #f4f6f7;
    background: #20252a;
    border-color: #353c42;
}

QPushButton:pressed {
    background: #252b30;
}

QPushButton:checked {
    color: #eef3f1;
    background: #2a3535;
    border-color: #40504f;
}

QPushButton#detailsToggle,
QPushButton#contextToggle {
    min-height: 26px;
    padding: 0 8px;
    color: #879198;
    background: transparent;
    border: 1px solid transparent;
    font-size: 10px;
    font-weight: 500;
}

QPushButton#detailsToggle:hover,
QPushButton#contextToggle:hover {
    color: #dce1e4;
    background: #1a1e21;
    border-color: #2a3035;
}

QPushButton#detailsToggle:checked,
QPushButton#contextToggle:checked {
    color: #e9eeee;
    background: #202728;
    border-color: #344041;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#rememberMessageButton,
QPushButton#addKnowledgeButton {
    min-height: 24px;
    padding: 0 7px;
    color: #7f8990;
    background: transparent;
    border: 1px solid transparent;
    font-size: 10px;
    font-weight: 500;
}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#rememberMessageButton:hover,
QPushButton#addKnowledgeButton:hover {
    color: #e4e7e9;
    background: #1a1e21;
    border-color: #2a3035;
}

QPushButton#sendButton,
QPushButton[role="primary"] {
    color: #151719;
    background: #e8ebed;
    border-color: #e8ebed;
    font-weight: 600;
}

QPushButton#sendButton:hover,
QPushButton[role="primary"]:hover {
    background: #f7f8f9;
    border-color: #f7f8f9;
}

QLineEdit,
QComboBox,
QSpinBox,
QDoubleSpinBox {
    color: #e8ebed;
    background: #181c1f;
    border: 1px solid #2b3136;
    border-radius: 8px;
    min-height: 32px;
    padding: 0 10px;
    selection-background-color: #4c5b5d;
}

QComboBox#chatSelector,
QComboBox#modelSelector {
    min-height: 30px;
    background: #15191c;
    border-color: #252b30;
    color: #c9cfd3;
}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover {
    border-color: #353c42;
    background: #181c1f;
}

QLineEdit:hover,
QComboBox:hover,
QSpinBox:hover,
QDoubleSpinBox:hover {
    border-color: #394148;
}

QLineEdit:focus,
QComboBox:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border-color: #64767a;
}

QLineEdit#promptInput {
    min-height: 42px;
    padding: 0 14px;
    font-size: 13px;
    background: #171b1e;
    border: 1px solid #30363b;
    border-radius: 10px;
}

QDialog#commandPalette,
QDialog#helpDialog {
    color: #e9ecee;
    background: #15181b;
    border: 1px solid #30363b;
}

QLabel#commandPaletteTitle,
QLabel#helpDialogTitle {
    color: #f1f3f4;
    font-size: 14px;
    font-weight: 600;
}

QLabel#commandPaletteHint,
QLabel#commandPaletteFooter {
    color: #727c83;
    font-size: 10px;
    font-weight: 500;
}

QLabel#helpDialogIntro {
    color: #929ca3;
    font-size: 11px;
}

QLineEdit#commandPaletteQuery {
    min-height: 38px;
    padding: 0 12px;
    background: #111416;
    border: 1px solid #30363b;
    border-radius: 8px;
    font-size: 13px;
}

QListWidget#commandPaletteResults {
    color: #c9cfd3;
    background: transparent;
    border: none;
    outline: none;
    padding: 2px 0;
}

QListWidget#commandPaletteResults::item {
    min-height: 32px;
    padding: 5px 10px;
    margin: 1px 0;
    border: none;
    border-radius: 7px;
}

QListWidget#commandPaletteResults::item:hover {
    color: #f1f3f4;
    background: #1d2226;
}

QListWidget#commandPaletteResults::item:selected {
    color: #f5f6f7;
    background: #252b30;
}

QPlainTextEdit#helpText {
    color: #bec5ca;
    background: #111416;
    border: 1px solid #252b30;
    border-radius: 8px;
    padding: 12px;
    selection-background-color: #293235;
}

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
QWidget#systemWorkspace {
    background: #111315;
    border: none;
}

QListWidget#persistentKnowledgeList,
QListWidget#researchJobList,
QListWidget#durableJobList,
QListWidget#sourceList,
QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {
    color: #c5cbd0;
    background: #14171a;
    border: 1px solid #252b30;
    border-radius: 8px;
    padding: 6px;
    selection-background-color: #293235;
    selection-color: #f0f2f3;
}

QListWidget#persistentKnowledgeList::item,
QListWidget#researchJobList::item,
QListWidget#durableJobList::item,
QListWidget#sourceList::item {
    color: #aeb6bc;
    background: transparent;
    border: none;
    border-bottom: 1px solid #202529;
    padding: 9px 10px;
}

QListWidget#persistentKnowledgeList::item:hover,
QListWidget#researchJobList::item:hover,
QListWidget#durableJobList::item:hover,
QListWidget#sourceList::item:hover {
    color: #e3e6e8;
    background: #191d20;
}

QListWidget#persistentKnowledgeList::item:selected,
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected,
QListWidget#sourceList::item:selected {
    color: #f2f4f5;
    background: #22282c;
}

QFrame#systemMetric {
    background: #14171a;
    border: 1px solid #252b30;
    border-radius: 8px;
}

QSplitter::handle {
    background: #202529;
}

QSplitter::handle:horizontal {
    width: 1px;
    margin: 0 8px;
}

QFrame#sessionControls,
QFrame#evidenceChain {
    background: transparent;
    border: none;
}

QFrame#knowledgeReviewPanel {
    background: #14171a;
    border: 1px solid #252b30;
    border-radius: 9px;
}

QLabel#knowledgeReviewTitle {
    color: #d9dee1;
    font-size: 11px;
    font-weight: 600;
}

QLabel#knowledgeReviewState {
    color: #7f8b91;
    font-size: 10px;
    font-weight: 500;
}

QFrame#knowledgeReviewItem {
    background: #111416;
    border: 1px solid #202529;
    border-radius: 7px;
}

QLabel#knowledgeReviewItemTitle {
    color: #cdd3d7;
    font-size: 10px;
    font-weight: 600;
}

QLabel#knowledgeReviewItemBody {
    color: #aeb6bc;
    font-size: 11px;
}

QPushButton#knowledgeReviewCloseButton,
QPushButton#knowledgeMergeButton {
    min-height: 24px;
    padding: 0 7px;
    color: #89939a;
    background: transparent;
    border: 1px solid #293036;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 500;
}

QPushButton#knowledgeReviewCloseButton:hover,
QPushButton#knowledgeMergeButton:hover {
    color: #eef0f1;
    background: #1c2125;
    border-color: #394148;
}

QFrame#inspector,
QFrame#inspectorPanel {
    background: #131619;
    border: none;
    border-left: 1px solid #262b30;
}

QFrame#pallasVisualPlaceholder {
    background: #101214;
    border: 1px solid #252b30;
    border-radius: 10px;
}

QToolTip {
    color: #e7eaec;
    background: #202428;
    border: 1px solid #343a40;
    padding: 6px 8px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #343a3f;
    border-radius: 4px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: #454c52;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
}
"""
