"""Visual system for the pATHENA v2 desktop experience."""

from __future__ import annotations

V2_BG = "#090B0F"
V2_SURFACE = "#0F1319"
V2_SURFACE_RAISED = "#151A22"
V2_SURFACE_HOVER = "#1A202A"
V2_BORDER = "#242B36"
V2_BORDER_STRONG = "#343E4D"
V2_TEXT = "#F4F6FA"
V2_TEXT_MUTED = "#98A2B3"
V2_TEXT_DIM = "#697386"
V2_ACCENT = "#7C9CFF"
V2_ACCENT_HOVER = "#91ACFF"
V2_ACCENT_SOFT = "#18213A"
V2_SUCCESS = "#68D6A3"
V2_DANGER = "#F07C86"

PATHENA_V2_STYLESHEET = f"""
QMainWindow#athenaMainWindow {{
    background: {V2_BG};
    color: {V2_TEXT};
}}

QWidget {{
    color: {V2_TEXT};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 10pt;
    outline: none;
}}

QToolTip {{
    color: {V2_TEXT};
    background: {V2_SURFACE_RAISED};
    border: 1px solid {V2_BORDER_STRONG};
    border-radius: 6px;
    padding: 6px 8px;
}}

QFrame#v2Shell,
QFrame#v2Body,
QFrame#conversation {{
    background: {V2_BG};
    border: none;
}}

QFrame#v2Sidebar {{
    background: #0C0F14;
    border: none;
    border-right: 1px solid {V2_BORDER};
}}

QLabel#v2Brand {{
    color: {V2_TEXT};
    font-size: 18pt;
    font-weight: 650;
    letter-spacing: -0.6px;
}}

QLabel#v2BrandCaption {{
    color: {V2_TEXT_DIM};
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 1.6px;
}}

QPushButton[v2Nav="true"] {{
    color: {V2_TEXT_MUTED};
    background: transparent;
    border: 0;
    border-radius: 9px;
    padding: 10px 12px;
    text-align: left;
    font-size: 10pt;
    font-weight: 520;
}}

QPushButton[v2Nav="true"]:hover {{
    color: {V2_TEXT};
    background: {V2_SURFACE_HOVER};
}}

QPushButton[v2Nav="true"][active="true"] {{
    color: {V2_TEXT};
    background: {V2_ACCENT_SOFT};
    border-left: 3px solid {V2_ACCENT};
    padding-left: 9px;
    font-weight: 640;
}}

QFrame#v2Main {{
    background: {V2_BG};
    border: none;
}}

QFrame#v2Header {{
    background: {V2_BG};
    border: none;
    border-bottom: 1px solid {V2_BORDER};
}}

QLabel#v2PageTitle {{
    color: {V2_TEXT};
    font-size: 17pt;
    font-weight: 650;
    letter-spacing: -0.4px;
}}

QLabel#v2PageHint {{
    color: {V2_TEXT_MUTED};
    font-size: 9pt;
}}

QPushButton#v2CommandButton {{
    color: {V2_TEXT_MUTED};
    background: {V2_SURFACE};
    border: 1px solid {V2_BORDER};
    border-radius: 9px;
    padding: 8px 12px;
    text-align: left;
    min-width: 240px;
}}

QPushButton#v2CommandButton:hover {{
    color: {V2_TEXT};
    background: {V2_SURFACE_RAISED};
    border-color: {V2_BORDER_STRONG};
}}

QLabel#v2StatusDot {{
    color: {V2_SUCCESS};
    font-size: 9pt;
}}

QLabel#v2StatusText {{
    color: {V2_TEXT_MUTED};
    font-size: 9pt;
}}

QFrame#v2Workspace {{
    background: {V2_BG};
    border: none;
}}

QStackedWidget#pages {{
    background: {V2_BG};
    border: none;
}}

QWidget#v2ChatPage {{
    background: {V2_BG};
}}

QFrame#v2SessionBar {{
    background: transparent;
    border: none;
}}

QLabel#v2Eyebrow {{
    color: {V2_TEXT_DIM};
    font-size: 8pt;
    font-weight: 650;
    letter-spacing: 1.1px;
}}

QComboBox#chatSelector,
QComboBox#modelSelector,
QComboBox#settingsModelSelector {{
    color: {V2_TEXT};
    background: {V2_SURFACE};
    border: 1px solid {V2_BORDER};
    border-radius: 9px;
    padding: 7px 28px 7px 10px;
    min-height: 20px;
}}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover,
QComboBox#settingsModelSelector:hover {{
    background: {V2_SURFACE_RAISED};
    border-color: {V2_BORDER_STRONG};
}}

QComboBox QAbstractItemView {{
    color: {V2_TEXT};
    background: {V2_SURFACE_RAISED};
    border: 1px solid {V2_BORDER_STRONG};
    selection-background-color: {V2_ACCENT_SOFT};
    selection-color: {V2_TEXT};
    padding: 5px;
}}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle,
QPushButton#groundButton {{
    color: {V2_TEXT_MUTED};
    background: transparent;
    border: 1px solid {V2_BORDER};
    border-radius: 8px;
    padding: 7px 10px;
    min-height: 18px;
}}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#contextToggle:hover,
QPushButton#groundButton:hover {{
    color: {V2_TEXT};
    background: {V2_SURFACE_HOVER};
    border-color: {V2_BORDER_STRONG};
}}

QPushButton#groundButton:checked,
QPushButton#contextToggle:checked {{
    color: {V2_TEXT};
    background: {V2_ACCENT_SOFT};
    border-color: {V2_ACCENT};
}}

QPushButton#deleteChatButton:hover {{
    color: {V2_DANGER};
}}

QScrollArea#chatScroll,
QWidget#chatMessages {{
    background: {V2_BG};
    border: none;
}}

QFrame#v2ConversationSurface {{
    background: {V2_BG};
    border: none;
}}

QFrame#v2Composer {{
    background: {V2_SURFACE_RAISED};
    border: 1px solid {V2_BORDER_STRONG};
    border-radius: 14px;
}}

QLineEdit#promptInput {{
    color: {V2_TEXT};
    background: transparent;
    border: 0;
    padding: 8px 4px;
    selection-background-color: {V2_ACCENT};
}}

QLineEdit#promptInput:disabled {{
    color: {V2_TEXT_DIM};
}}

QPushButton#sendButton {{
    color: #09101F;
    background: {V2_ACCENT};
    border: 0;
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    font-weight: 700;
}}

QPushButton#sendButton:hover {{
    background: {V2_ACCENT_HOVER};
}}

QPushButton#sendButton:disabled {{
    color: {V2_TEXT_DIM};
    background: #242A35;
}}

QFrame#knowledgeReviewPanel,
QFrame#evidenceChain,
QFrame#evidenceRail {{
    background: {V2_SURFACE};
    border: 1px solid {V2_BORDER};
    border-radius: 10px;
}}

QFrame#inspector {{
    background: {V2_SURFACE};
    border: none;
    border-left: 1px solid {V2_BORDER};
}}

QLabel#inspectorTitle {{
    color: {V2_TEXT_DIM};
    font-size: 8pt;
    font-weight: 650;
    letter-spacing: 1.2px;
}}

QLabel#inspectorHeading {{
    color: {V2_TEXT};
    font-size: 13pt;
    font-weight: 620;
}}

QLabel#inspectorBody {{
    color: {V2_TEXT_MUTED};
    line-height: 1.35;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: #303846;
    min-height: 30px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #465165;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background: transparent;
    height: 0;
}}

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox {{
    color: {V2_TEXT};
    background: {V2_SURFACE};
    border: 1px solid {V2_BORDER};
    border-radius: 8px;
    padding: 7px 9px;
    selection-background-color: {V2_ACCENT};
}}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QComboBox:focus {{
    border-color: {V2_ACCENT};
}}

QPushButton {{
    color: {V2_TEXT_MUTED};
    background: {V2_SURFACE};
    border: 1px solid {V2_BORDER};
    border-radius: 8px;
    padding: 7px 10px;
}}

QPushButton:hover {{
    color: {V2_TEXT};
    background: {V2_SURFACE_HOVER};
    border-color: {V2_BORDER_STRONG};
}}

QPushButton:disabled {{
    color: {V2_TEXT_DIM};
    background: #101319;
    border-color: #1B2029;
}}

QCheckBox {{
    color: {V2_TEXT};
    spacing: 8px;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: #252C37;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    width: 14px;
    margin: -5px 0;
    background: {V2_ACCENT};
    border-radius: 7px;
}}

QFrame#rule {{
    background: {V2_BORDER};
    border: none;
    max-height: 1px;
}}

QLabel[role="muted"],
QLabel#commandMeta,
QLabel#chainState,
QLabel#jobMeta,
QLabel#settingsHelp {{
    color: {V2_TEXT_MUTED};
}}
"""
