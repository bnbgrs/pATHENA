"""V3 visual system: ink-black canvas, porcelain type and sea-glass accents."""

from __future__ import annotations

V3_BG = "#0A0D0E"
V3_CANVAS = "#0E1213"
V3_SURFACE = "#14191A"
V3_SURFACE_RAISED = "#1A2021"
V3_SURFACE_HOVER = "#222A2B"
V3_BORDER = "#2A3334"
V3_BORDER_STRONG = "#3B4A4C"
V3_TEXT = "#F3F0F5"
V3_TEXT_MUTED = "#A8A3AE"
V3_TEXT_DIM = "#706D76"
V3_ACCENT = "#89E0CA"
V3_ACCENT_SOFT = "#17302B"
V3_MINT = "#89E0CA"
V3_WARNING = "#E6C07A"
V3_DANGER = "#FF8178"

PATHENA_V3_STYLESHEET = """
QMainWindow#athenaMainWindow {
    background: #0A0D0E;
    color: #F3F0F5;
}

QWidget {
    color: #F3F0F5;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 10pt;
    outline: none;
}

QToolTip {
    color: #F3F0F5;
    background: #222A2B;
    border: 1px solid #3B4A4C;
    border-radius: 8px;
    padding: 7px 9px;
}

/* --- V3 shell ---------------------------------------------------------- */

QFrame#v3Shell,
QFrame#referenceBody,
QFrame#conversation,
QFrame#v3Workspace {
    background: #0A0D0E;
    border: none;
}

QFrame#v3Rail {
    background: #0D1112;
    border: none;
    border-right: 1px solid #25271F;
}

QLabel#v3Mark {
    color: #0A0D0E;
    background: #89E0CA;
    border-radius: 17px;
    font-size: 11pt;
    font-weight: 800;
}

QLabel#v3BuildMark {
    color: #706D76;
    font-size: 7.5pt;
    font-weight: 650;
}

QPushButton[v3Nav="true"] {
    color: #85818C;
    background: transparent;
    border: 0;
    border-radius: 14px;
    padding: 0;
}

QPushButton[v3Nav="true"]:hover {
    background: #1A2021;
}

QPushButton[v3Nav="true"][active="true"] {
    background: #17302B;
    border: 1px solid #28584D;
}

QFrame#v3RailDivider {
    background: #2A3334;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QFrame#v3Workbar {
    background: #0A0D0E;
    border: none;
}

QLabel#v3PageTitle {
    color: #F3F0F5;
    font-size: 16pt;
    font-weight: 690;
    letter-spacing: -0.45px;
}

QLabel#v3PageHint {
    color: #706D76;
    font-size: 8.7pt;
}

QFrame#v3WorkbarActions {
    background: transparent;
    border: none;
}

QPushButton#v3CommandButton {
    color: #A8A3AE;
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 12px;
    padding: 8px 13px;
    min-width: 210px;
    text-align: left;
}

QPushButton#v3CommandButton:hover {
    color: #F3F0F5;
    background: #1A2021;
    border-color: #3B4A4C;
}

QLabel#v3RuntimeDot {
    color: #89E0CA;
    font-size: 9pt;
}

QLabel#v3RuntimeText {
    color: #A8A3AE;
    font-size: 8.7pt;
}

QLabel#v3Pill {
    color: #A8A3AE;
    background: #1A2021;
    border: 1px solid #2A3334;
    border-radius: 10px;
    padding: 4px 9px;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#v3Pill[tone="live"] {
    color: #CBF5EB;
    background: #15332D;
    border-color: #2B5B50;
}

QLabel#v3Pill[tone="accent"] {
    color: #CFF8EE;
    background: #17302B;
    border-color: #28584D;
}

/* --- Chat -------------------------------------------------------------- */

QWidget#v3ChatPage {
    background: #0A0D0E;
}

QFrame#v3ChatMeta {
    background: transparent;
    border: none;
}

QLabel#v3MetaLabel,
QLabel#v3Kicker {
    color: #706D76;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QComboBox#chatSelector,
QComboBox#modelSelector,
QComboBox#settingsModelSelector {
    color: #F3F0F5;
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 10px;
    padding: 7px 30px 7px 11px;
    min-height: 22px;
}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover,
QComboBox#settingsModelSelector:hover {
    background: #1A2021;
    border-color: #3B4A4C;
}

QComboBox QAbstractItemView {
    color: #F3F0F5;
    background: #1A2021;
    border: 1px solid #3B4A4C;
    border-radius: 8px;
    selection-background-color: #17302B;
    selection-color: #F3F0F5;
    padding: 5px;
}

QFrame#v3ConversationStage {
    background: transparent;
    border: none;
    border-radius: 0;
}

QScrollArea#chatScroll,
QWidget#chatMessages {
    background: transparent;
    border: none;
}

QFrame#v3Composer {
    background: #171D1E;
    border: 1px solid #344244;
    border-radius: 20px;
}

QFrame#v3Composer:focus-within {
    border-color: #4B8D7E;
}

QLineEdit#promptInput {
    color: #F3F0F5;
    background: transparent;
    border: 0;
    padding: 10px 6px;
    font-size: 10.5pt;
    selection-background-color: #2E675D;
}

QPushButton#sendButton {
    color: #0D1112;
    background: #89E0CA;
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
    background: #A5EBD9;
}

QPushButton#sendButton:disabled {
    color: #5D6667;
    background: #2A3334;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle,
QPushButton#groundButton {
    color: #A8A3AE;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 6px 9px;
}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#contextToggle:hover,
QPushButton#groundButton:hover {
    color: #F3F0F5;
    background: #1A2021;
    border-color: #2A3334;
}

QPushButton#contextToggle:checked,
QPushButton#groundButton:checked {
    color: #CFF8EE;
    background: #17302B;
    border-color: #28584D;
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
    background: #0A0D0E;
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
    background: #121718;
    border: none;
    border-radius: 14px;
}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#researchProposalList,
QListWidget#durableJobList,
QListWidget#sourceList {
    color: #F3F0F5;
    background: #121718;
    border: 1px solid #273031;
    border-radius: 14px;
    padding: 6px;
}

QListWidget::item {
    border-radius: 9px;
    padding: 9px 10px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background: #1E2526;
}

QListWidget::item:selected {
    color: #F3F0F5;
    background: #17302B;
    border: 1px solid #28584D;
}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {
    color: #E8E3EC;
    background: #121718;
    border: 1px solid #273031;
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
    border-top: 1px solid #2A3334;
    top: -1px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab {
    color: #85818C;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 14px;
    margin-right: 4px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:hover {
    color: #F3F0F5;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:selected {
    color: #F3F0F5;
    border-bottom-color: #89E0CA;
}

/* --- Settings ---------------------------------------------------------- */

QFrame#v3ControlRow {
    background: transparent;
    border: none;
    border-bottom: 1px solid #2A3334;
}

QLabel#v3ControlTitle,
QLabel#v2FormLabel,
QLabel#v2PanelTitle,
QLabel#v2SectionTitle {
    color: #F3F0F5;
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
    color: #A8A3AE;
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
    background: #121718;
    border: none;
    border-left: 1px solid #273031;
}

QLabel#inspectorTitle,
QLabel#v3PallasInspectorKind {
    color: #706D76;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#inspectorHeading,
QLabel#v3PallasInspectorTitle {
    color: #F3F0F5;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#inspectorBody,
QLabel#v3PallasInspectorBody {
    color: #A8A3AE;
}

/* --- PALLAS living field ---------------------------------------------- */

QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace,
QWidget#pallasWorkspace,
QWidget#pallasSemanticField {
    background: #0A0D0E;
    border: none;
}

QFrame#v3PallasTopbar {
    background: #121718;
    border: none;
    border-radius: 16px;
}

QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticSelection {
    color: #A8A3AE;
    font-size: 9pt;
}

QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {
    min-height: 32px;
    padding: 0 12px;
    color: #85818C;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
}

QPushButton#pallasLensSemanticButton:hover,
QPushButton#pallasLensAgeButton:hover,
QPushButton#pallasLensVitalityButton:hover {
    color: #F3F0F5;
    background: #1A2021;
    border-color: #2A3334;
}

QPushButton#pallasLensSemanticButton:checked,
QPushButton#pallasLensAgeButton:checked,
QPushButton#pallasLensVitalityButton:checked {
    color: #CFF8EE;
    background: #17302B;
    border-color: #28584D;
}

/* --- Generic controls -------------------------------------------------- */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox {
    color: #F3F0F5;
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: #2E675D;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QComboBox:focus {
    border-color: #4B8D7E;
}

QPushButton {
    color: #A8A3AE;
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton:hover {
    color: #F3F0F5;
    background: #1A2021;
    border-color: #3B4A4C;
}

QPushButton:disabled {
    color: #5D6667;
    background: #101415;
    border-color: #202829;
}

QCheckBox {
    color: #F3F0F5;
    spacing: 8px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #2A3334;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #89E0CA;
    border-radius: 7px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #343E3F;
    min-height: 32px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #485758;
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
    color: #A8A3AE;
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
    background: #0A0D0E;
    border: none;
}

QFrame#v3KnowledgeHeader,
QFrame#v3KnowledgeMetaStrip {
    background: transparent;
    border: none;
}

QFrame#v3KnowledgeCommand {
    background: #121718;
    border: none;
    border-radius: 16px;
}

QLabel#v3LibraryTitle {
    color: #F3F0F5;
    font-size: 18pt;
    font-weight: 690;
    letter-spacing: -0.55px;
}

QFrame#v3KnowledgeBrowser,
QFrame#v3ResearchBrief,
QFrame#v3JobsCommand,
QFrame#v3SourcesCommand,
QFrame#v3SystemCommand,
QFrame#v3RuntimeCard,
QFrame#v3SystemActivity,
QFrame#v3SecurityPosture {
    background: #121718;
    border: none;
    border-radius: 16px;
}

QFrame#v3ResearchBrief {
    background: #121718;
}

QLabel#v3KnowledgeState {
    color: #CFF8EE;
    background: #17302B;
    border: 1px solid #28584D;
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
    color: #918B98;
    font-size: 8.8pt;
}

QTabWidget#v3KnowledgeTabs::pane {
    background: #121718;
    border: none;
    border-radius: 16px;
    top: -1px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab {
    color: #85818C;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 15px;
    margin-right: 4px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:hover {
    color: #F3F0F5;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:selected {
    color: #F3F0F5;
    border-bottom-color: #89E0CA;
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
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 14px;
    padding: 4px;
}

QLabel#v3SectionTitle,
QLabel#v3RuntimeCardTitle {
    color: #F3F0F5;
    font-size: 11pt;
    font-weight: 680;
}

QLabel#v3SettingsIntro {
    color: #A8A3AE;
    font-size: 9.5pt;
}

QWidget#v3SettingsRuntimePanel {
    background: transparent;
    border: none;
}

QFrame#v2PallasInspector {
    background: #121718;
    border: none;
    border-left: 1px solid #273031;
}

QLabel#v2PallasInspectorKind {
    color: #706D76;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#v2PallasInspectorTitle {
    color: #F3F0F5;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#v2PallasInspectorBody {
    color: #A8A3AE;
}

/* --- Commands, help and local tools ------------------------------------ */

QDialog#commandPalette,
QDialog#helpDialog,
QDialog#comfyUiDialog {
    background: #0D1112;
    border: 1px solid #344244;
    border-radius: 18px;
}

QLabel#commandPaletteTitle,
QLabel#helpDialogTitle,
QLabel#comfyUiTitle {
    color: #F3F0F5;
    font-size: 15pt;
    font-weight: 700;
    letter-spacing: -0.35px;
}

QLabel#commandPaletteHint {
    color: #A8A3AE;
    background: #1A2021;
    border: 1px solid #2A3334;
    border-radius: 8px;
    padding: 3px 7px;
    font-size: 8pt;
    font-weight: 650;
}

QLineEdit#commandPaletteQuery {
    color: #F3F0F5;
    background: #171D1E;
    border: 1px solid #3C4B4D;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 11pt;
}

QLineEdit#commandPaletteQuery:focus {
    border-color: #4B8D7E;
}

QListWidget#commandPaletteResults {
    color: #E8E3EC;
    background: transparent;
    border: none;
    padding: 4px 0;
}

QListWidget#commandPaletteResults::item {
    border-radius: 10px;
    padding: 10px 12px;
    margin: 1px 0;
}

QListWidget#commandPaletteResults::item:hover {
    background: #1A2021;
}

QListWidget#commandPaletteResults::item:selected {
    color: #F3F0F5;
    background: #17302B;
}

QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {
    color: #706D76;
    font-size: 8.7pt;
}

QPlainTextEdit#helpText {
    color: #DCD7E0;
    background: #121718;
    border: 1px solid #273031;
    border-radius: 14px;
    padding: 16px;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 9.5pt;
}

/* --- System operations tabs ------------------------------------------- */

QTabWidget#systemOperationsTabs::pane {
    background: #0A0D0E;
    border: none;
    top: -1px;
}

QTabWidget#systemOperationsTabs QTabBar::tab {
    color: #706D76;
    background: transparent;
    border: none;
    border-bottom: 1px solid transparent;
    padding: 8px 13px;
    margin-right: 3px;
}

QTabWidget#systemOperationsTabs QTabBar::tab:hover {
    color: #A8A3AE;
    background: #14191A;
}

QTabWidget#systemOperationsTabs QTabBar::tab:selected {
    color: #F3F0F5;
    background: #14191A;
    border-bottom: 2px solid #89E0CA;
}

QWidget#backupWorkspace {
    background: #0A0D0E;
}

/* --- Hosted help workspace -------------------------------------------- */

QWidget#helpWorkspace,
QFrame#helpBody,
QFrame#helpCapabilityContent {
    background: #0A0D0E;
    border: none;
}

QFrame#helpSecondaryNavigation {
    background: transparent;
    border: none;
    border-right: 1px solid #2A3334;
}

QLabel#helpSecondaryTitle,
QLabel#helpHeadline,
QLabel#helpCapabilityTitle {
    color: #F3F0F5;
}

QLineEdit#helpSearch {
    color: #F3F0F5;
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 10px;
    padding: 8px 11px;
}

QLineEdit#helpSearch:focus {
    border-color: #4B8D7E;
}

QListWidget#helpCapabilities {
    background: transparent;
    border: none;
}

QFrame#helpCapabilityRow {
    background: #14191A;
    border: 1px solid #2A3334;
    border-radius: 10px;
}

QLabel#helpCapabilitySummary,
QLabel#helpCapabilityState {
    color: #A8A3AE;
}

QLabel#helpCapabilityState[pathenaUiState="available"] {
    color: #89E0CA;
}

QDialog#comfyUiDialog {
    background: #0A0D0E;
}

QLabel#comfyUiSectionLabel {
    color: #706D76;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.15px;
    padding-top: 8px;
}

QLabel#comfyUiStatus[pathenaUiState="success"],
QLabel#comfyUiJobStatus[pathenaUiState="completed"] {
    color: #CBF5EB;
}

QLabel#comfyUiStatus[pathenaUiState="error"],
QLabel#comfyUiJobStatus[pathenaUiState="error"] {
    color: #FF9D96;
}

QLabel#comfyUiResourceStatus,
QLabel#comfyUiQueueReceipt,
QLabel#comfyUiJobStatus {
    color: #A8A3AE;
}

QPushButton#comfyUiQueueWorkflow {
    color: #0D1112;
    background: #89E0CA;
    border-color: #89E0CA;
    font-weight: 700;
}

QPushButton#comfyUiQueueWorkflow:hover {
    background: #A5EBD9;
    border-color: #A5EBD9;
}

QPushButton#comfyUiReleaseVram {
    color: #F0D18A;
    background: #282217;
    border-color: #554725;
}
"""
