"""V3 visual system: warm graphite, mineral surfaces and living citron accents."""

from __future__ import annotations

V3_BG = "#0E0F0D"
V3_CANVAS = "#121310"
V3_SURFACE = "#171814"
V3_SURFACE_RAISED = "#1D1F1A"
V3_SURFACE_HOVER = "#24261F"
V3_BORDER = "#2B2D26"
V3_BORDER_STRONG = "#3A3D32"
V3_TEXT = "#F2F0E8"
V3_TEXT_MUTED = "#A8A59A"
V3_TEXT_DIM = "#747269"
V3_ACCENT = "#C6F277"
V3_ACCENT_SOFT = "#28321D"
V3_MINT = "#78D7C4"
V3_WARNING = "#E7C56B"
V3_DANGER = "#FF7D6E"

PATHENA_V3_STYLESHEET = """
QMainWindow#athenaMainWindow {
    background: #0E0F0D;
    color: #F2F0E8;
}

QWidget {
    color: #F2F0E8;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 10pt;
    outline: none;
}

QToolTip {
    color: #F2F0E8;
    background: #24261F;
    border: 1px solid #3A3D32;
    border-radius: 8px;
    padding: 7px 9px;
}

/* --- V3 shell ---------------------------------------------------------- */

QFrame#v3Shell,
QFrame#referenceBody,
QFrame#conversation,
QFrame#v3Workspace {
    background: #0E0F0D;
    border: none;
}

QFrame#v3Rail {
    background: #11120F;
    border: none;
    border-right: 1px solid #25271F;
}

QLabel#v3Mark {
    color: #0E0F0D;
    background: #C6F277;
    border-radius: 17px;
    font-size: 11pt;
    font-weight: 800;
}

QLabel#v3BuildMark {
    color: #747269;
    font-size: 7.5pt;
    font-weight: 650;
}

QPushButton[v3Nav="true"] {
    color: #817F77;
    background: transparent;
    border: 0;
    border-radius: 14px;
    padding: 0;
}

QPushButton[v3Nav="true"]:hover {
    background: #1D1F1A;
}

QPushButton[v3Nav="true"][active="true"] {
    background: #28321D;
    border: 1px solid #3B4B29;
}

QFrame#v3RailDivider {
    background: #2B2D26;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QFrame#v3Workbar {
    background: #0E0F0D;
    border: none;
    border-bottom: 1px solid #24261F;
}

QLabel#v3PageTitle {
    color: #F2F0E8;
    font-size: 16pt;
    font-weight: 690;
    letter-spacing: -0.45px;
}

QLabel#v3PageHint {
    color: #747269;
    font-size: 8.7pt;
}

QFrame#v3WorkbarActions {
    background: transparent;
    border: none;
}

QPushButton#v3CommandButton {
    color: #A8A59A;
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 12px;
    padding: 8px 13px;
    min-width: 210px;
    text-align: left;
}

QPushButton#v3CommandButton:hover {
    color: #F2F0E8;
    background: #1D1F1A;
    border-color: #3A3D32;
}

QLabel#v3RuntimeDot {
    color: #78D7C4;
    font-size: 9pt;
}

QLabel#v3RuntimeText {
    color: #A8A59A;
    font-size: 8.7pt;
}

QLabel#v3Pill {
    color: #A8A59A;
    background: #1D1F1A;
    border: 1px solid #2B2D26;
    border-radius: 10px;
    padding: 4px 9px;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#v3Pill[tone="live"] {
    color: #B9F1E4;
    background: #17302A;
    border-color: #27584D;
}

QLabel#v3Pill[tone="accent"] {
    color: #DDF7A7;
    background: #28321D;
    border-color: #3B4B29;
}

/* --- Chat -------------------------------------------------------------- */

QWidget#v3ChatPage {
    background: #0E0F0D;
}

QFrame#v3ChatMeta {
    background: transparent;
    border: none;
}

QLabel#v3MetaLabel,
QLabel#v3Kicker {
    color: #747269;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QComboBox#chatSelector,
QComboBox#modelSelector,
QComboBox#settingsModelSelector {
    color: #F2F0E8;
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 10px;
    padding: 7px 30px 7px 11px;
    min-height: 22px;
}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover,
QComboBox#settingsModelSelector:hover {
    background: #1D1F1A;
    border-color: #3A3D32;
}

QComboBox QAbstractItemView {
    color: #F2F0E8;
    background: #1D1F1A;
    border: 1px solid #3A3D32;
    border-radius: 8px;
    selection-background-color: #28321D;
    selection-color: #F2F0E8;
    padding: 5px;
}

QFrame#v3ConversationStage {
    background: #121310;
    border: 1px solid #24261F;
    border-radius: 18px;
}

QScrollArea#chatScroll,
QWidget#chatMessages {
    background: transparent;
    border: none;
}

QFrame#v3Composer {
    background: #1D1F1A;
    border: 1px solid #35382E;
    border-radius: 18px;
}

QFrame#v3Composer:focus-within {
    border-color: #657B46;
}

QLineEdit#promptInput {
    color: #F2F0E8;
    background: transparent;
    border: 0;
    padding: 10px 6px;
    font-size: 10.5pt;
    selection-background-color: #566C3B;
}

QPushButton#sendButton {
    color: #11120F;
    background: #C6F277;
    border: 0;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    font-size: 15pt;
    font-weight: 800;
}

QPushButton#sendButton:hover {
    background: #D5FA91;
}

QPushButton#sendButton:disabled {
    color: #5C5E54;
    background: #2B2D26;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle,
QPushButton#groundButton {
    color: #A8A59A;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 6px 9px;
}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#contextToggle:hover,
QPushButton#groundButton:hover {
    color: #F2F0E8;
    background: #1D1F1A;
    border-color: #2B2D26;
}

QPushButton#contextToggle:checked,
QPushButton#groundButton:checked {
    color: #DDF7A7;
    background: #28321D;
    border-color: #3B4B29;
}

/* --- Shared workspaces ------------------------------------------------- */

QStackedWidget#pages,
QWidget#v2KnowledgeWorkspace,
QWidget#v2ResearchWorkspace,
QWidget#v2JobsWorkspace,
QWidget#v2SourcesWorkspace,
QWidget#v2SystemWorkspace,
QWidget#v2SettingsPage,
QWidget#v2SettingsForm,
QScrollArea#v2SettingsScroll,
QScrollArea#v2SettingsScroll > QWidget > QWidget {
    background: #0E0F0D;
    border: none;
}

QFrame#v3Section,
QFrame#knowledgeReviewPanel,
QFrame#evidenceChain,
QFrame#evidenceRail,
QFrame#v2KnowledgeContext,
QFrame#v2ResearchMeta,
QFrame#v2SourcesToolbar,
QFrame#v2JobsToolbar,
QFrame#v2SystemToolbar,
QFrame#v2SecurityPosture,
QFrame#v2SettingsStatus {
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 14px;
}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#researchProposalList,
QListWidget#durableJobList,
QListWidget#sourceList {
    color: #F2F0E8;
    background: #151612;
    border: 1px solid #292B24;
    border-radius: 14px;
    padding: 6px;
}

QListWidget::item {
    border-radius: 9px;
    padding: 9px 10px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background: #20221C;
}

QListWidget::item:selected {
    color: #F2F0E8;
    background: #28321D;
    border: 1px solid #3B4B29;
}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {
    color: #E7E4DA;
    background: #151612;
    border: 1px solid #292B24;
    border-radius: 14px;
    padding: 15px;
}

QSplitter::handle {
    background: transparent;
    width: 10px;
    height: 10px;
}

QTabWidget#v2KnowledgeTabs::pane {
    background: transparent;
    border: 0;
    border-top: 1px solid #2B2D26;
    top: -1px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab {
    color: #817F77;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 14px;
    margin-right: 4px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:hover {
    color: #F2F0E8;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:selected {
    color: #F2F0E8;
    border-bottom-color: #C6F277;
}

/* --- Settings ---------------------------------------------------------- */

QFrame#v3ControlRow {
    background: transparent;
    border: none;
    border-bottom: 1px solid #2B2D26;
}

QLabel#v3ControlTitle,
QLabel#v2FormLabel,
QLabel#v2PanelTitle,
QLabel#v2SectionTitle {
    color: #F2F0E8;
    font-size: 10.5pt;
    font-weight: 650;
}

QLabel#v3ControlDescription,
QLabel#v2FormDescription,
QLabel#v2PanelHint,
QLabel#v2SettingsIntro,
QLabel#v2SystemDetail,
QLabel#v2KnowledgeSummary,
QLabel#v2ResearchStatus,
QLabel#v2SourcesStatus,
QLabel#v2JobsStatus,
QLabel#v2SchedulerStatus {
    color: #A8A59A;
    font-size: 9pt;
}

QWidget#v3ControlHost,
QFrame#v2FormControl {
    background: transparent;
    border: none;
}

/* --- Inspector --------------------------------------------------------- */

QFrame#inspector,
QFrame#v3PallasInspector {
    background: #151612;
    border: none;
    border-left: 1px solid #292B24;
}

QLabel#inspectorTitle,
QLabel#v3PallasInspectorKind {
    color: #747269;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#inspectorHeading,
QLabel#v3PallasInspectorTitle {
    color: #F2F0E8;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#inspectorBody,
QLabel#v3PallasInspectorBody {
    color: #A8A59A;
}

/* --- PALLAS living field ---------------------------------------------- */

QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace,
QWidget#pallasWorkspace,
QWidget#pallasSemanticField {
    background: #0E0F0D;
    border: none;
}

QFrame#v3PallasTopbar {
    background: #11120F;
    border: 1px solid #25271F;
    border-radius: 14px;
}

QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticSelection {
    color: #A8A59A;
    font-size: 9pt;
}

QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {
    min-height: 32px;
    padding: 0 12px;
    color: #817F77;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
}

QPushButton#pallasLensSemanticButton:hover,
QPushButton#pallasLensAgeButton:hover,
QPushButton#pallasLensVitalityButton:hover {
    color: #F2F0E8;
    background: #1D1F1A;
    border-color: #2B2D26;
}

QPushButton#pallasLensSemanticButton:checked,
QPushButton#pallasLensAgeButton:checked,
QPushButton#pallasLensVitalityButton:checked {
    color: #DDF7A7;
    background: #28321D;
    border-color: #3B4B29;
}

/* --- Generic controls -------------------------------------------------- */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox {
    color: #F2F0E8;
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: #566C3B;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QComboBox:focus {
    border-color: #657B46;
}

QPushButton {
    color: #A8A59A;
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton:hover {
    color: #F2F0E8;
    background: #1D1F1A;
    border-color: #3A3D32;
}

QPushButton:disabled {
    color: #5C5E54;
    background: #131410;
    border-color: #22231D;
}

QCheckBox {
    color: #F2F0E8;
    spacing: 8px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #2B2D26;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #C6F277;
    border-radius: 7px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #36382F;
    min-height: 32px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #4B4E40;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    height: 0;
}

QLabel[role="muted"],
QLabel#commandMeta,
QLabel#chainState,
QLabel#jobMeta,
QLabel#settingsHelp {
    color: #A8A59A;
}

/* --- V3 workspace-specific composition -------------------------------- */

QWidget#v3KnowledgeWorkspace,
QWidget#v3ResearchWorkspace,
QWidget#v3JobsWorkspace,
QWidget#v3SourcesWorkspace,
QWidget#v3SystemWorkspace,
QWidget#v3SettingsPage,
QWidget#v3SettingsForm,
QScrollArea#v3SettingsScroll,
QScrollArea#v3SettingsScroll > QWidget > QWidget {
    background: #0E0F0D;
    border: none;
}

QFrame#v3KnowledgeSearch,
QFrame#v3KnowledgeIdentity {
    background: transparent;
    border: none;
}

QFrame#v3KnowledgeBrowser,
QFrame#v3ResearchBrief,
QFrame#v3JobsCommand,
QFrame#v3SourcesCommand,
QFrame#v3SystemCommand,
QFrame#v3RuntimeCard,
QFrame#v3SystemActivity,
QFrame#v3SecurityPosture {
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 14px;
}

QFrame#v3ResearchBrief {
    background: #151711;
    border-color: #303626;
}

QLabel#v3KnowledgeState {
    color: #DDF7A7;
    background: #28321D;
    border: 1px solid #3B4B29;
    border-radius: 9px;
    padding: 4px 8px;
    font-size: 8pt;
    font-weight: 680;
}

QLabel#v3KnowledgeSummary,
QLabel#v3KnowledgeMeta,
QLabel#v3KnowledgeBrowserStatus,
QLabel#v3ResearchStatus,
QLabel#v3JobsStatus,
QLabel#v3SchedulerStatus,
QLabel#v3SourcesStatus,
QLabel#v3SystemDetail,
QLabel#v3RuntimeCardHint {
    color: #8F8C82;
    font-size: 8.8pt;
}

QTabWidget#v3KnowledgeTabs::pane {
    background: #151612;
    border: 1px solid #292B24;
    border-radius: 14px;
    top: -1px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab {
    color: #817F77;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 15px;
    margin-right: 4px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:hover {
    color: #F2F0E8;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:selected {
    color: #F2F0E8;
    border-bottom-color: #C6F277;
}

QSplitter#v3ResearchSplit,
QSplitter#v3JobsSplit,
QSplitter#v3SourcesSplit {
    background: transparent;
    border: none;
}

QFrame#v3HealthGrid {
    background: transparent;
    border: none;
}

QFrame[v3HealthTile="true"] {
    background: #171814;
    border: 1px solid #2B2D26;
    border-radius: 14px;
    padding: 4px;
}

QLabel#v3SectionTitle,
QLabel#v3RuntimeCardTitle {
    color: #F2F0E8;
    font-size: 11pt;
    font-weight: 680;
}

QLabel#v3SettingsIntro {
    color: #A8A59A;
    font-size: 9.5pt;
}

QWidget#v3SettingsRuntimePanel {
    background: transparent;
    border: none;
}

QFrame#v2PallasInspector {
    background: #151612;
    border: none;
    border-left: 1px solid #292B24;
}

QLabel#v2PallasInspectorKind {
    color: #747269;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#v2PallasInspectorTitle {
    color: #F2F0E8;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#v2PallasInspectorBody {
    color: #A8A59A;
}
"""
