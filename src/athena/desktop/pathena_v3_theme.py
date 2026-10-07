"""V4 visual system: deep ink canvas, warm-white type and calm cobalt accents."""

from __future__ import annotations

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, TYPE

V3_BG = PALETTE.canvas
V3_CANVAS = PALETTE.surface
V3_SURFACE = PALETTE.surface_raised
V3_SURFACE_RAISED = PALETTE.surface_hover
V3_SURFACE_HOVER = PALETTE.surface_hover
V3_BORDER = PALETTE.border
V3_BORDER_STRONG = PALETTE.border_strong
V3_TEXT = PALETTE.text
V3_TEXT_MUTED = PALETTE.text_muted
V3_TEXT_DIM = PALETTE.text_quiet
V3_ACCENT = PALETTE.accent
V3_ACCENT_SOFT = PALETTE.accent_soft
V3_MINT = PALETTE.info
V3_WARNING = PALETTE.warning
V3_DANGER = PALETTE.error
V3_COMPOSER_ACTION_SIZE = SHELL.composer_action_size

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
    border-right: 1px solid #20272D;
}

QLabel#v3Mark {
    color: #090B0E;
    background: #78D1C5;
    border-radius: 16px;
    font-size: 10.5pt;
    font-weight: 800;
}

QToolButton[v3Nav="true"] {
    color: #89929A;
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
    color: #99A3AB;
    background: #11151A;
    border: 1px solid #282F35;
    border-radius: 11px;
    padding: 7px 11px;
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
    color: #D9DDDF;
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
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0;
    font-size: 15pt;
    font-weight: 800;
}

QPushButton#sendButton:hover {
    background: #9BE3D9;
}

QPushButton#sendButton:disabled {
    color: #646E76;
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
    background: #11151A;
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
    background: #11151A;
    border: 1px solid #282F35;
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
    background: #11151A;
    border: 1px solid #282F35;
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
    color: #9099A1;
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
    background: #11151A;
    border: none;
    border-left: 1px solid #282F35;
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
    border: 1px solid #20272D;
    border-radius: 14px;
}

QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticSelection {
    color: #A5ACB4;
    font-size: 9pt;
}

QLabel#pallasSemanticLegend {
    color: #68727A;
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
    color: #646E76;
    background: #11151A;
    border-color: #282F35;
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
    color: #68727A;
    background: #11151A;
    border-color: #282F35;
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
    background: #10161A;
    border-color: #263137;
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
    color: #99A3AB;
    font-size: 8.8pt;
}

QLabel#v3KnowledgeMeta {
    color: #6F7A84;
    font-size: 8pt;
}

QLabel#v3ProgressLabel {
    color: #77818B;
    font-size: 8pt;
}

QProgressBar#v3ActivityProgress {
    background: #20272D;
    border: none;
    border-radius: 2px;
    min-height: 4px;
    max-height: 5px;
}

QProgressBar#v3ActivityProgress::chunk {
    background: #78D1C5;
    border-radius: 2px;
}

QTabWidget#v3KnowledgeTabs::pane {
    background: #11151A;
    border: 1px solid #282F35;
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
    border-bottom: 1px solid #20272D;
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
    color: #C9CED2;
    background: #11151A;
    border: 1px solid #282F35;
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
    color: #D9DDDF;
    background: #11151A;
    border: 1px solid #282F35;
    border-radius: 12px;
}

QSplitter#v3ResearchSplit::handle,
QSplitter#v3JobsSplit::handle,
QSplitter#v3SourcesSplit::handle {
    background: #20272D;
    width: 1px;
    margin: 0 7px;
}

QFrame#v3SystemActivity,
QFrame#v3SecurityPosture,
QFrame[v3HealthTile="true"] {
    border-color: #282F35;
}

QPushButton#pallasBackButton {
    color: #C9CED2;
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
    border: 1px solid #343B42;
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
    background: #11151A;
    border: 1px solid #282F35;
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
    background: #11151A;
    border: 1px solid #282F35;
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
    color: #D9DDDF;
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
    color: #C9CED2;
    background: #14181D;
    border-color: #29313A;
}

QPushButton#comfyUiReleaseVram:hover {
    color: #F1F3F5;
    background: #1A2026;
    border-color: #3B4652;
}

/* --- Final coherence: quiet secondary structure ----------------------- */

QFrame#v3SettingsRuntimeSection {
    background: transparent;
    border: none;
    border-top: 1px solid #20272D;
    border-radius: 0;
}

QFrame#v3SystemActivity,
QFrame#v3SecurityPosture {
    background: transparent;
    border: none;
    border-top: 1px solid #20272D;
    border-radius: 0;
}

QPushButton[v3QuietDanger="true"] {
    color: #858F99;
    background: transparent;
    border: 1px solid transparent;
}

QPushButton[v3QuietDanger="true"]:hover {
    color: #F2C2C2;
    background: #21171C;
    border-color: #443039;
}

QPushButton[v3QuietDanger="true"]:focus {
    color: #D8A3A3;
    border-color: #5D434B;
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
    color: #99A3AB;
    font-size: 9.5pt;
}
"""

def _apply_v4_token_bridge(stylesheet: str) -> str:
    """Project the stable V3 selector set onto the active V4 visual tokens."""
    replacements = {
        "#090B0E": PALETTE.canvas,
        "#0D1014": PALETTE.surface,
        "#0F1317": PALETTE.surface,
        "#0F1318": PALETTE.surface,
        "#101318": PALETTE.surface,
        "#10161A": PALETTE.surface,
        "#11151A": PALETTE.surface,
        "#111718": PALETTE.surface,
        "#12191A": PALETTE.surface_raised,
        "#14181D": PALETTE.surface_raised,
        "#1A2026": PALETTE.surface_hover,
        "#222930": PALETTE.surface_hover,
        "#163033": PALETTE.surface_selected,
        "#20272D": PALETTE.border,
        "#242B31": PALETTE.border,
        "#252C33": PALETTE.border,
        "#282F35": PALETTE.border,
        "#29313A": PALETTE.border,
        "#293638": PALETTE.border,
        "#2A333B": PALETTE.border,
        "#303748": PALETTE.border_strong,
        "#343B42": PALETTE.border_strong,
        "#3B4652": PALETTE.border_strong,
        "#334143": PALETTE.border_strong,
        "#F1F3F5": PALETTE.text,
        "#D9DDDF": PALETTE.text,
        "#D7DBDF": PALETTE.text,
        "#C9CED2": PALETTE.text_muted,
        "#A5ACB4": PALETTE.text_muted,
        "#99A3AB": PALETTE.text_subtle,
        "#9099A1": PALETTE.text_subtle,
        "#8E98A3": PALETTE.text_subtle,
        "#89929A": PALETTE.text_subtle,
        "#8B949E": PALETTE.text_subtle,
        "#77818B": PALETTE.text_quiet,
        "#6F7A84": PALETTE.text_quiet,
        "#68727A": PALETTE.text_quiet,
        "#646E76": PALETTE.text_quiet,
        "#78D1C5": PALETTE.accent,
        "#9BE3D9": PALETTE.accent_hover,
        "#5DAEA5": PALETTE.accent_pressed,
        "#13292B": PALETTE.accent_soft,
        "#173033": PALETTE.accent_soft,
        "#11191A": PALETTE.accent_soft,
        "#2C5D61": PALETTE.border_strong,
        "#326B6D": PALETTE.border_strong,
        "#3B7779": PALETTE.accent_pressed,
    }
    rendered = stylesheet
    for legacy, current in replacements.items():
        rendered = rendered.replace(legacy, current)
    rendered = rendered.replace(
        '"Segoe UI Variable", "Segoe UI", sans-serif',
        TYPE.content_family,
    )
    rendered = rendered.replace('"Cascadia Mono"', TYPE.metadata_family)
    return rendered


PATHENA_V3_STYLESHEET = _apply_v4_token_bridge(PATHENA_V3_STYLESHEET)

# V4 structural cleanup: high-information workspaces use document/list structure
# rather than stacking bordered dashboard cards.
PATHENA_V3_STYLESHEET += f"""
QFrame#v3ResearchBrief,
QFrame#v3KnowledgeBrowser {{
    background: transparent;
    border: none;
    border-top: 1px solid {PALETTE.border};
    border-bottom: 1px solid {PALETTE.border};
    border-radius: 0;
}}

QFrame#helpCapabilityRow {{
    background: transparent;
    border: none;
    border-bottom: 1px solid {PALETTE.border};
    border-radius: 0;
}}

QFrame#helpCapabilityRow:hover {{
    background: {PALETTE.surface_hover};
    border-bottom-color: {PALETTE.border_strong};
}}

QFrame#v3Workbar {{
    background: {PALETTE.surface};
    border-bottom: 1px solid {PALETTE.border};
}}

QFrame#v3Composer {{
    background: {PALETTE.surface};
    border-color: {PALETTE.border_strong};
}}

QPushButton#sendButton {{
    min-width: {SHELL.composer_action_size}px;
    max-width: {SHELL.composer_action_size}px;
    min-height: {SHELL.composer_action_size}px;
    max-height: {SHELL.composer_action_size}px;
    border-radius: {SHELL.composer_action_size // 2}px;
}}
"""

