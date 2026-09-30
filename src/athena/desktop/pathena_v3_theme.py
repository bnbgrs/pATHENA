"""V3 visual system: ink canvas, porcelain type and sea-glass accents."""

from __future__ import annotations

V3_BG = "#090B0E"
V3_CANVAS = "#101318"
V3_SURFACE = "#14181D"
V3_SURFACE_RAISED = "#1A2026"
V3_SURFACE_HOVER = "#222930"
V3_BORDER = "#29313A"
V3_BORDER_STRONG = "#3B4652"
V3_TEXT = "#F1F3F5"
V3_TEXT_MUTED = "#A5ACB4"
V3_TEXT_DIM = "#77818B"
V3_ACCENT = "#78D1C5"
V3_ACCENT_SOFT = "#13292B"
V3_MINT = "#68B8C6"
V3_WARNING = "#E7B96F"
V3_DANGER = "#F17878"
V3_COMPOSER_ACTION_SIZE = 44

PATHENA_V3_STYLESHEET = """
QMainWindow#athenaMainWindow {
    background: #090B0E;
    color: #F1F3F5;
}

QWidget {
    color: #F1F3F5;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 10pt;
    outline: none;
}

QToolTip {
    color: #F1F3F5;
    background: #222930;
    border: 1px solid #3B4652;
    border-radius: 8px;
    padding: 7px 9px;
}

/* --- V3 shell ---------------------------------------------------------- */

QFrame#v3Shell,
QFrame#referenceBody,
QFrame#conversation,
QFrame#v3Workspace {
    background: #090B0E;
    border: none;
}

QFrame#v3Rail {
    background: #0D1014;
    border: none;
    border-right: 1px solid #202532;
}

QLabel#v3Mark {
    color: #090B0E;
    background: #78D1C5;
    border-radius: 16px;
    font-size: 10.5pt;
    font-weight: 800;
}

QToolButton[v3Nav="true"] {
    color: #8992A2;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 11px;
    padding: 4px 1px 3px 1px;
    font-size: 8pt;
    font-weight: 620;
}

QToolButton[v3Nav="true"]:hover {
    color: #F1F3F5;
    background: #1A2026;
}

QToolButton[v3Nav="true"]:focus {
    color: #D7DBDF;
    background: #14181D;
    border-color: #3B4652;
}

QToolButton[v3Nav="true"][active="true"] {
    color: #F1F3F5;
    background: #11191A;
    border: 1px solid transparent;
    border-left: 2px solid #78D1C5;
}

QToolButton[v3Nav="true"][active="true"]:focus {
    background: #14181D;
    border: 1px solid #3B4652;
    border-left: 2px solid #78D1C5;
}

QFrame#v3RailDivider {
    background: #29313A;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QFrame#v3Workbar {
    background: #090B0E;
    border: none;
    border-bottom: 1px solid #222930;
}

QLabel#v3PageTitle {
    color: #F1F3F5;
    font-size: 16.5pt;
    font-weight: 700;
    letter-spacing: -0.45px;
}

QLabel#v3PageHint {
    color: #77818B;
    font-size: 9pt;
}

QFrame#v3WorkbarActions {
    background: transparent;
    border: none;
}

QPushButton#v3CommandButton {
    color: #98A1B1;
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 11px;
    padding: 7px 11px;
    min-width: 174px;
    text-align: left;
}

QPushButton#v3CommandButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

QLabel#v3RuntimeDot {
    color: #78D1C5;
    font-size: 9pt;
}

QLabel#v3RuntimeText {
    color: #A5ACB4;
    font-size: 9pt;
}

QLabel#v3Pill {
    color: #A5ACB4;
    background: #1A2026;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 4px 9px;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#v3Pill[tone="live"] {
    color: #D7F3EE;
    background: #173033;
    border-color: #326B6D;
}

QLabel#v3Pill[tone="accent"] {
    color: #DDF5F1;
    background: #13292B;
    border-color: #2C5D61;
}

QTabWidget#systemOperationsTabs {
    background: transparent;
    border: none;
}

QTabWidget#systemOperationsTabs::pane {
    background: transparent;
    border: none;
    border-top: 1px solid #202532;
    top: -1px;
}

QTabWidget#systemOperationsTabs QTabBar::tab {
    color: #77818B;
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 9px 12px 8px 12px;
    margin-right: 2px;
    font-size: 8.5pt;
    font-weight: 600;
}

QTabWidget#systemOperationsTabs QTabBar::tab:hover {
    color: #D6DCE7;
}

QTabWidget#systemOperationsTabs QTabBar::tab:selected {
    color: #F1F3F5;
    border-bottom-color: #78D1C5;
}

/* --- Chat -------------------------------------------------------------- */

QWidget#v3ChatPage {
    background: #090B0E;
}

QFrame#v3ChatMeta {
    background: transparent;
    border: none;
    border-bottom: 1px solid #20272D;
    border-radius: 0;
}

QLabel#v3MetaLabel {
    color: #8B949E;
    font-size: 8.5pt;
    font-weight: 600;
    letter-spacing: 0px;
}

QLabel#v3Kicker {
    color: #77818B;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QComboBox#chatSelector,
QComboBox#modelSelector,
QComboBox#settingsModelSelector {
    color: #F1F3F5;
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 7px 30px 7px 11px;
    min-height: 22px;
}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover,
QComboBox#settingsModelSelector:hover {
    background: #1A2026;
    border-color: #3B4652;
}

QComboBox QAbstractItemView {
    color: #F1F3F5;
    background: #1A2026;
    border: 1px solid #3B4652;
    border-radius: 8px;
    selection-background-color: #13292B;
    selection-color: #F1F3F5;
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

QFrame#emptyStatePanel {
    background: transparent;
    border: none;
}

QLabel#emptyStateTitle {
    color: #F1F3F5;
    font-size: 17pt;
    font-weight: 680;
    letter-spacing: -0.25px;
}

QLabel#emptyStateBody {
    color: #A5ACB4;
    font-size: 10pt;
}

QFrame#v3Composer {
    background: #111718;
    border: 1px solid #293638;
    border-radius: 18px;
}

QFrame#v3Composer:focus-within {
    background: #12191A;
    border-color: #5DAEA5;
}

QPlainTextEdit#promptInput {
    color: #F1F3F5;
    background: transparent;
    border: 0;
    padding: 8px 6px;
    font-size: 11pt;
    selection-background-color: #3B7779;
}

QPushButton#sendButton {
    color: #0D1014;
    background: #78D1C5;
    border: 0;
    border-radius: 22px;
    min-width: 44px;
    max-width: 44px;
    min-height: 44px;
    max-height: 44px;
    padding: 0;
    font-size: 15pt;
    font-weight: 800;
}

QPushButton#sendButton:hover {
    background: #9BE3D9;
}

QPushButton#sendButton:disabled {
    color: #626C7D;
    background: #29313A;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle,
QPushButton#groundButton {
    color: #A5ACB4;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 6px 9px;
}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#contextToggle:hover,
QPushButton#groundButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #29313A;
}

QPushButton#contextToggle:checked,
QPushButton#groundButton:checked {
    color: #DDF5F1;
    background: #13292B;
    border-color: #2C5D61;
}

QComboBox#chatSelector {
    background: transparent;
    border-color: transparent;
    font-weight: 620;
}

QComboBox#chatSelector:hover,
QComboBox#chatSelector:focus {
    background: #14181D;
    border-color: #29313A;
}

QComboBox#modelSelector {
    background: #11151D;
    border-color: #252C33;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle {
    padding: 6px 8px;
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
    background: #090B0E;
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
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 14px;
}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#researchProposalList,
QListWidget#durableJobList,
QListWidget#sourceList {
    color: #F1F3F5;
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 14px;
    padding: 6px;
}

QListWidget::item {
    border-radius: 9px;
    padding: 9px 10px;
    margin: 2px 0;
}

QListWidget::item:hover {
    background: #1A2026;
}

QListWidget::item:selected {
    color: #F1F3F5;
    background: #13292B;
    border: 1px solid #2C5D61;
}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {
    color: #F1F3F5;
    background: #11151D;
    border: 1px solid #252C39;
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
    border-top: 1px solid #29313A;
    top: -1px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab {
    color: #77818B;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 14px;
    margin-right: 4px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:hover {
    color: #F1F3F5;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:selected {
    color: #F1F3F5;
    border-bottom-color: #78D1C5;
}

/* --- Settings ---------------------------------------------------------- */

QFrame#v3ControlRow {
    background: transparent;
    border: none;
    border-bottom: 1px solid #20272D;
    border-radius: 0;
}

QLabel#v3ControlTitle,
QLabel#v2FormLabel,
QLabel#v2PanelTitle,
QLabel#v2SectionTitle {
    color: #F1F3F5;
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
    color: #A5ACB4;
    font-size: 9pt;
}

QWidget#v3ControlHost,
QFrame#v2FormControl {
    background: transparent;
    border: none;
}

QFrame#v3ControlRow:hover {
    background: #0F1317;
    border-bottom-color: #2A333B;
}

QFrame#v3RuntimeCard {
    background: #11151A;
    border: 1px solid #242B31;
    border-radius: 14px;
}

QLabel#v3RuntimeCardTitle {
    color: #F1F3F5;
    font-size: 12pt;
    font-weight: 700;
}

QLabel#v3RuntimeCardHint,
QWidget#v3SettingsRuntimePanel {
    color: #9099A9;
}

QWidget#v3SettingsPage {
    background: #090B0E;
}

QScrollArea#v3SettingsScroll,
QWidget#v3SettingsForm {
    background: transparent;
    border: none;
}

/* --- Inspector --------------------------------------------------------- */

QFrame#inspector,
QFrame#v3PallasInspector {
    background: #11151D;
    border: none;
    border-left: 1px solid #252C39;
}

QLabel#inspectorTitle,
QLabel#v3PallasInspectorKind {
    color: #77818B;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#inspectorHeading,
QLabel#v3PallasInspectorTitle {
    color: #F1F3F5;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#inspectorBody,
QLabel#v3PallasInspectorBody {
    color: #A5ACB4;
}

/* --- PALLAS living field ---------------------------------------------- */

QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace,
QWidget#pallasWorkspace,
QWidget#pallasSemanticField {
    background: #090B0E;
    border: none;
}

QFrame#v3PallasTopbar {
    background: #0D1014;
    border: 1px solid #202532;
    border-radius: 14px;
}

QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticSelection {
    color: #A5ACB4;
    font-size: 9pt;
}

QLabel#pallasSemanticLegend {
    color: #687284;
    font-family: "Cascadia Mono";
    font-size: 8pt;
    letter-spacing: 0.2px;
    padding: 0 4px;
}

QPushButton#pallasBackButton,
QPushButton#pallasFitButton,
QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {
    min-height: 32px;
    padding: 0 12px;
    color: #77818B;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
}

QPushButton#pallasBackButton:hover,
QPushButton#pallasFitButton:hover,
QPushButton#pallasLensSemanticButton:hover,
QPushButton#pallasLensAgeButton:hover,
QPushButton#pallasLensVitalityButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #29313A;
}

QPushButton#pallasLensSemanticButton:checked,
QPushButton#pallasLensAgeButton:checked,
QPushButton#pallasLensVitalityButton:checked {
    color: #DDF5F1;
    background: #13292B;
    border-color: #2C5D61;
}

/* --- Generic controls -------------------------------------------------- */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox,
QTimeEdit {
    color: #F1F3F5;
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: #3B7779;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QTimeEdit:focus,
QComboBox:focus {
    border-color: #78D1C5;
}

QPushButton {
    color: #A5ACB4;
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

QPushButton:focus {
    border-color: #78D1C5;
}

QPushButton:disabled {
    color: #626C7D;
    background: #11151D;
    border-color: #252C39;
}

/* Semantic workspace actions stay legible after legacy object-name refinement. */
QPushButton#researchStartButton,
QPushButton#fileImportButton {
    color: #0D1014;
    background: #78D1C5;
    border: 1px solid #78D1C5;
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 680;
}

QPushButton#researchStartButton:hover,
QPushButton#fileImportButton:hover {
    color: #0D1014;
    background: #9BE3D9;
    border-color: #9BE3D9;
}

QPushButton#researchStartButton:focus,
QPushButton#fileImportButton:focus {
    border-color: #F1F3F5;
}

QPushButton#researchStartButton:disabled,
QPushButton#fileImportButton:disabled {
    color: #77818B;
    background: #182021;
    border-color: #293638;
}

QPushButton#researchRefreshButton,
QPushButton#researchCancelButton,
QPushButton#fileRefreshButton,
QPushButton#fileProcessButton {
    color: #A5ACB4;
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton#researchRefreshButton:hover,
QPushButton#researchCancelButton:hover,
QPushButton#fileRefreshButton:hover,
QPushButton#fileProcessButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

QPushButton#researchRefreshButton:focus,
QPushButton#researchCancelButton:focus,
QPushButton#fileRefreshButton:focus,
QPushButton#fileProcessButton:focus {
    border-color: #78D1C5;
}

QPushButton#researchCancelButton:disabled,
QPushButton#fileProcessButton:disabled {
    color: #687284;
    background: #11151D;
    border-color: #252C39;
}

QPushButton#sendButton:disabled {
    color: #AEBFBD;
    background: #20292A;
    border: 1px solid #334143;
}

QPushButton#groundButton:disabled {
    color: #7F8D8D;
    background: #141A1B;
    border-color: #2B3738;
}

QCheckBox {
    color: #F1F3F5;
    spacing: 8px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #29313A;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #78D1C5;
    border-radius: 7px;
}

QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #303748;
    min-height: 32px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #465168;
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
    color: #A5ACB4;
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
    background: #090B0E;
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
    background: #11151A;
    border: 1px solid #242B31;
    border-radius: 14px;
}

QFrame#v3ResearchBrief {
    background: #121722;
    border-color: #252C39;
}

QFrame#v3JobsCommand,
QFrame#v3SourcesCommand,
QFrame#v3SystemCommand {
    background: transparent;
    border: none;
    border-bottom: 1px solid #20272D;
    border-radius: 0;
}

QLabel#v3KnowledgeState {
    color: #DDF5F1;
    background: #13292B;
    border: 1px solid #2C5D61;
    border-radius: 9px;
    padding: 4px 8px;
    font-size: 8pt;
    font-weight: 680;
}

QLabel#v3KnowledgeSummary,
QLabel#v3KnowledgeBrowserStatus,
QLabel#v3ResearchStatus,
QLabel#v3JobsStatus,
QLabel#v3SchedulerStatus,
QLabel#v3SourcesStatus,
QLabel#v3SystemDetail,
QLabel#v3RuntimeCardHint {
    color: #98A1B1;
    font-size: 8.8pt;
}

QLabel#v3KnowledgeMeta {
    color: #6F7A84;
    font-size: 8pt;
}

QTabWidget#v3KnowledgeTabs::pane {
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 14px;
    top: -1px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab {
    color: #77818B;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 15px;
    margin-right: 4px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:hover {
    color: #F1F3F5;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:selected {
    color: #F1F3F5;
    border-bottom-color: #78D1C5;
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
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 14px;
    padding: 4px;
}

QLabel#v3SectionTitle,
QLabel#v3RuntimeCardTitle {
    color: #F1F3F5;
    font-size: 11pt;
    font-weight: 680;
}

QLabel#v3SettingsIntro {
    color: #A5ACB4;
    font-size: 9.5pt;
}

QWidget#v3SettingsRuntimePanel {
    background: transparent;
    border: none;
}


QFrame#v3KnowledgeSearch {
    background: transparent;
    border: none;
    border-bottom: 1px solid #20272D;
    border-radius: 0;
}

QFrame#v3KnowledgeIdentity {
    background: transparent;
    border: none;
    border-bottom: 1px solid #202532;
}

QLabel#v3WorkspaceLead {
    color: #A5ACB4;
    font-size: 9.2pt;
}

QPushButton[v3PrimaryAction="true"] {
    color: #0D1014;
    background: #78D1C5;
    border: 1px solid #78D1C5;
    font-weight: 680;
}

QPushButton[v3PrimaryAction="true"]:hover {
    color: #0D1014;
    background: #9BE3D9;
    border-color: #9BE3D9;
}

QPushButton[v3PrimaryAction="true"]:focus {
    border-color: #F1F3F5;
}

QPushButton[v3PrimaryAction="true"]:disabled {
    color: #77818B;
    background: #182021;
    border-color: #293638;
}

QPushButton[v3DestructiveAction="true"] {
    color: #D8A3A3;
    background: #14181D;
    border-color: #443039;
}

QPushButton[v3DestructiveAction="true"]:hover {
    color: #F2C2C2;
    background: #21171C;
    border-color: #72505C;
}

QPushButton[v3DestructiveAction="true"]:disabled {
    color: #6F6267;
    background: transparent;
    border-color: #2A2428;
}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#durableJobList,
QListWidget#sourceList {
    color: #C6CDD9;
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 12px;
    padding: 6px;
    outline: 0;
}

QListWidget#persistentKnowledgeList::item,
QListWidget#persistentClaimList::item,
QListWidget#semanticReviewList::item,
QListWidget#researchJobList::item,
QListWidget#durableJobList::item,
QListWidget#sourceList::item {
    padding: 9px 10px;
    margin: 1px 0;
    border-radius: 8px;
}

QListWidget#persistentKnowledgeList::item:hover,
QListWidget#persistentClaimList::item:hover,
QListWidget#semanticReviewList::item:hover,
QListWidget#researchJobList::item:hover,
QListWidget#durableJobList::item:hover,
QListWidget#sourceList::item:hover {
    color: #F1F3F5;
    background: #1A2026;
}

QListWidget#persistentKnowledgeList::item:selected,
QListWidget#persistentClaimList::item:selected,
QListWidget#semanticReviewList::item:selected,
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected,
QListWidget#sourceList::item:selected {
    color: #F1F3F5;
    background: #163033;
}

QWidget#persistentKnowledgeDetails,
QWidget#persistentClaimDetails,
QWidget#semanticReviewDetails,
QWidget#researchDetails,
QWidget#jobDetails,
QWidget#sourceDetails {
    color: #D6DCE7;
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 12px;
}

QSplitter#v3ResearchSplit::handle,
QSplitter#v3JobsSplit::handle,
QSplitter#v3SourcesSplit::handle {
    background: #202532;
    width: 1px;
    margin: 0 7px;
}

QFrame#v3SystemActivity,
QFrame#v3SecurityPosture,
QFrame[v3HealthTile="true"] {
    border-color: #252C39;
}

QPushButton#pallasBackButton {
    color: #C6CDD9;
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 9px;
    padding: 6px 11px;
}

QPushButton#pallasBackButton:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

QPushButton#pallasBackButton:focus {
    border-color: #78D1C5;
}

/* --- Commands, help and local tools ------------------------------------ */

QDialog#commandPalette,
QDialog#helpDialog,
QWidget#helpWorkspace,
QDialog#comfyUiDialog {
    color: #F1F3F5;
    background: #0D1014;
    border: 1px solid #343D4E;
    border-radius: 18px;
}

QFrame#helpBody,
QFrame#helpCapabilityContent {
    background: #0D1014;
    border: none;
}

QFrame#helpSecondaryNavigation {
    background: #0D1014;
    border: none;
    border-right: 1px solid #29313A;
}

QLabel#helpSecondaryTitle,
QLabel#helpHeadline {
    color: #F1F3F5;
    font-weight: 680;
}

QLineEdit#helpSearch {
    color: #F1F3F5;
    background: #14181D;
    border: 1px solid #3B4652;
    border-radius: 12px;
    padding: 10px 12px;
    min-height: 24px;
    selection-background-color: #3B7779;
}

QLineEdit#helpSearch:focus {
    border-color: #78D1C5;
}

QListWidget#helpSections,
QListWidget#helpCapabilities {
    color: #F1F3F5;
    background: transparent;
    border: none;
}

QListWidget#helpCapabilities::item {
    border: none;
    padding: 0;
}

QFrame#helpCapabilityRow {
    background: #14181D;
    border: 1px solid #29313A;
    border-radius: 12px;
}

QFrame#helpCapabilityRow:hover {
    background: #1A2026;
    border-color: #3B4652;
}

QLabel#helpCapabilityTitle {
    color: #F1F3F5;
}

QLabel#helpCapabilityState {
    color: #77818B;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#helpCapabilitySummary,
QLabel#helpSummary {
    color: #A5ACB4;
}

QLabel#commandPaletteTitle,
QLabel#helpDialogTitle,
QLabel#comfyUiTitle {
    color: #F1F3F5;
    font-size: 15pt;
    font-weight: 700;
    letter-spacing: -0.35px;
}

QLabel#commandPaletteHint {
    color: #A5ACB4;
    background: #1A2026;
    border: 1px solid #29313A;
    border-radius: 8px;
    padding: 3px 7px;
    font-size: 8pt;
    font-weight: 650;
}

QLineEdit#commandPaletteQuery {
    color: #F1F3F5;
    background: #14181D;
    border: 1px solid #3B4652;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 11pt;
}

QLineEdit#commandPaletteQuery:focus {
    border-color: #78D1C5;
}

QListWidget#commandPaletteResults {
    color: #F1F3F5;
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
    background: #1A2026;
}

QListWidget#commandPaletteResults::item:selected {
    color: #F1F3F5;
    background: #13292B;
}

QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {
    color: #77818B;
    font-size: 9pt;
}

QPlainTextEdit#helpText {
    color: #DCD7E0;
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 14px;
    padding: 16px;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 9.5pt;
}

QDialog#comfyUiDialog {
    background: #090B0E;
}

QDialog#comfyUiDialog[pathenaShellHosted="true"] {
    border: none;
    border-radius: 0;
}

QFrame#comfyUiPanel,
QFrame#comfyUiActivityPanel {
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 14px;
}

QFrame#comfyUiActivityPanel {
    background: #0F1318;
}

QLabel#comfyUiSectionTitle {
    color: #F1F3F5;
    font-size: 11pt;
    font-weight: 680;
}

QLabel#comfyUiPanelHint,
QLabel#comfyUiFieldLabel {
    color: #8E98A3;
    font-size: 9pt;
}

QLabel#comfyUiFieldLabel {
    font-weight: 600;
}

QLineEdit#comfyUiEndpoint,
QLineEdit#comfyUiWorkflowPath {
    color: #D6DCE7;
    background: #0D1116;
    border: 1px solid #29313A;
    border-radius: 10px;
    padding: 8px 10px;
    min-height: 22px;
}

QLabel#comfyUiSectionLabel {
    color: #77818B;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.15px;
    padding-top: 8px;
}

QLabel#comfyUiStatus[pathenaUiState="success"],
QLabel#comfyUiJobStatus[pathenaUiState="completed"] {
    color: #D7F3EE;
}

QLabel#comfyUiStatus[pathenaUiState="error"],
QLabel#comfyUiJobStatus[pathenaUiState="error"] {
    color: #FF9D96;
}

QLabel#comfyUiResourceStatus,
QLabel#comfyUiQueueReceipt,
QLabel#comfyUiJobStatus {
    color: #A5ACB4;
}

QPushButton#comfyUiQueueWorkflow {
    color: #0D1014;
    background: #78D1C5;
    border-color: #78D1C5;
    font-weight: 700;
}

QPushButton#comfyUiQueueWorkflow:hover {
    background: #9BE3D9;
    border-color: #9BE3D9;
}

QPushButton#comfyUiQueueWorkflow:disabled {
    color: #77818B;
    background: #182021;
    border-color: #293638;
}

QPushButton#comfyUiReleaseVram {
    color: #C6CDD9;
    background: #14181D;
    border-color: #29313A;
}

QPushButton#comfyUiReleaseVram:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

/* --- Editorial empty states ------------------------------------------- */

QFrame#v3EmptyState {
    background: transparent;
    border: none;
}

QLabel#v3EmptyTitle {
    color: #F1F3F5;
    font-size: 16pt;
    font-weight: 700;
    letter-spacing: -0.35px;
}

QLabel#v3EmptyBody {
    color: #98A1B1;
    font-size: 9.5pt;
}
"""
