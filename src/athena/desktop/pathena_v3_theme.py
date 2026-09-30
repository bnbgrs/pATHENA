"""V3 visual system: ink canvas, porcelain type and sea-glass accents."""

from __future__ import annotations

V3_BG = "#0A0C11"
V3_CANVAS = "#0F1218"
V3_SURFACE = "#151922"
V3_SURFACE_RAISED = "#1B202B"
V3_SURFACE_HOVER = "#222836"
V3_BORDER = "#2A3140"
V3_BORDER_STRONG = "#3B4558"
V3_TEXT = "#F2F4F8"
V3_TEXT_MUTED = "#A3AAB7"
V3_TEXT_DIM = "#7E8797"
V3_ACCENT = "#7C9CFF"
V3_ACCENT_SOFT = "#18213A"
V3_MINT = "#65C3D8"
V3_WARNING = "#E7B96F"
V3_DANGER = "#F17878"
V3_COMPOSER_ACTION_SIZE = 44

PATHENA_V3_STYLESHEET = """
QMainWindow#athenaMainWindow {
    background: #0A0C11;
    color: #F2F4F8;
}

QWidget {
    color: #F2F4F8;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    font-size: 10pt;
    outline: none;
}

QToolTip {
    color: #F2F4F8;
    background: #222836;
    border: 1px solid #3B4558;
    border-radius: 8px;
    padding: 7px 9px;
}

/* --- V3 shell ---------------------------------------------------------- */

QFrame#v3Shell,
QFrame#referenceBody,
QFrame#conversation,
QFrame#v3Workspace {
    background: #0A0C11;
    border: none;
}

QFrame#v3Rail {
    background: #0D1016;
    border: none;
    border-right: 1px solid #202532;
}

QLabel#v3Mark {
    color: #0A0C11;
    background: #7C9CFF;
    border-radius: 17px;
    font-size: 11pt;
    font-weight: 800;
}

QToolButton[v3Nav="true"] {
    color: #8992A2;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 11px;
    padding: 4px 1px 3px 1px;
    font-size: 7.8pt;
    font-weight: 620;
}

QToolButton[v3Nav="true"]:hover {
    color: #F2F4F8;
    background: #1B202B;
}

QToolButton[v3Nav="true"]:focus {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #7C9CFF;
}

QToolButton[v3Nav="true"][active="true"] {
    color: #F2F4F8;
    background: #19223A;
    border-color: #36518A;
}

QToolButton[v3Nav="true"][active="true"]:focus {
    border-color: #7C9CFF;
}

QFrame#v3RailDivider {
    background: #2A3140;
    border: none;
    min-height: 1px;
    max-height: 1px;
}

QFrame#v3Workbar {
    background: #0A0C11;
    border: none;
    border-bottom: 1px solid #222836;
}

QLabel#v3PageTitle {
    color: #F2F4F8;
    font-size: 18pt;
    font-weight: 700;
    letter-spacing: -0.55px;
}

QLabel#v3PageHint {
    color: #7E8797;
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
    padding: 8px 13px;
    min-width: 210px;
    text-align: left;
}

QPushButton#v3CommandButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #3B4558;
}

QLabel#v3RuntimeDot {
    color: #7C9CFF;
    font-size: 9pt;
}

QLabel#v3RuntimeText {
    color: #A3AAB7;
    font-size: 9pt;
}

QLabel#v3Pill {
    color: #A3AAB7;
    background: #1B202B;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 4px 9px;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#v3Pill[tone="live"] {
    color: #DFE7FF;
    background: #19243D;
    border-color: #365188;
}

QLabel#v3Pill[tone="accent"] {
    color: #E3E9FF;
    background: #18213A;
    border-color: #31457F;
}

/* --- Chat -------------------------------------------------------------- */

QWidget#v3ChatPage {
    background: #0A0C11;
}

QFrame#v3ChatMeta {
    background: transparent;
    border: none;
    border-bottom: 1px solid #202532;
    border-radius: 0;
}

QLabel#v3MetaLabel,
QLabel#v3Kicker {
    color: #7E8797;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QComboBox#chatSelector,
QComboBox#modelSelector,
QComboBox#settingsModelSelector {
    color: #F2F4F8;
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 7px 30px 7px 11px;
    min-height: 22px;
}

QComboBox#chatSelector:hover,
QComboBox#modelSelector:hover,
QComboBox#settingsModelSelector:hover {
    background: #1B202B;
    border-color: #3B4558;
}

QComboBox QAbstractItemView {
    color: #F2F4F8;
    background: #1B202B;
    border: 1px solid #3B4558;
    border-radius: 8px;
    selection-background-color: #18213A;
    selection-color: #F2F4F8;
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
    background: #141A25;
    border: 1px solid #34405A;
    border-radius: 16px;
}

QFrame#v3Composer:focus-within {
    border-color: #7C9CFF;
}

QPlainTextEdit#promptInput {
    color: #F2F4F8;
    background: transparent;
    border: 0;
    padding: 10px 6px;
    font-size: 10.5pt;
    selection-background-color: #6278C7;
}

QPushButton#sendButton {
    color: #0D1016;
    background: #7C9CFF;
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
    background: #99AFFF;
}

QPushButton#sendButton:disabled {
    color: #626C7D;
    background: #2A3140;
}

QPushButton#newChatButton,
QPushButton#deleteChatButton,
QPushButton#contextToggle,
QPushButton#groundButton {
    color: #A3AAB7;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
    padding: 6px 9px;
}

QPushButton#newChatButton:hover,
QPushButton#deleteChatButton:hover,
QPushButton#contextToggle:hover,
QPushButton#groundButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #2A3140;
}

QPushButton#contextToggle:checked,
QPushButton#groundButton:checked {
    color: #E3E9FF;
    background: #18213A;
    border-color: #31457F;
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
    background: #0A0C11;
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
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 14px;
}

QListWidget#persistentKnowledgeList,
QListWidget#persistentClaimList,
QListWidget#semanticReviewList,
QListWidget#researchJobList,
QListWidget#researchProposalList,
QListWidget#durableJobList,
QListWidget#sourceList {
    color: #F2F4F8;
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
    background: #1B202B;
}

QListWidget::item:selected {
    color: #F2F4F8;
    background: #18213A;
    border: 1px solid #31457F;
}

QPlainTextEdit#persistentKnowledgeDetails,
QPlainTextEdit#persistentClaimDetails,
QPlainTextEdit#semanticReviewDetails,
QPlainTextEdit#researchDetails,
QPlainTextEdit#jobDetails,
QPlainTextEdit#sourceDetails {
    color: #F2F4F8;
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
    border-top: 1px solid #2A3140;
    top: -1px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab {
    color: #7E8797;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 14px;
    margin-right: 4px;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:hover {
    color: #F2F4F8;
}

QTabWidget#v2KnowledgeTabs QTabBar::tab:selected {
    color: #F2F4F8;
    border-bottom-color: #7C9CFF;
}

/* --- Settings ---------------------------------------------------------- */

QFrame#v3ControlRow {
    background: #11151D;
    border: 1px solid #202532;
    border-radius: 12px;
}

QLabel#v3ControlTitle,
QLabel#v2FormLabel,
QLabel#v2PanelTitle,
QLabel#v2SectionTitle {
    color: #F2F4F8;
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
    color: #A3AAB7;
    font-size: 9pt;
}

QWidget#v3ControlHost,
QFrame#v2FormControl {
    background: transparent;
    border: none;
}

QFrame#v3ControlRow:hover {
    background: #141925;
    border-color: #39445A;
}

QFrame#v3RuntimeCard {
    background: #121722;
    border: 1px solid #252C39;
    border-radius: 16px;
}

QLabel#v3RuntimeCardTitle {
    color: #F2F4F8;
    font-size: 12pt;
    font-weight: 700;
}

QLabel#v3RuntimeCardHint,
QWidget#v3SettingsRuntimePanel {
    color: #9099A9;
}

QWidget#v3SettingsPage {
    background: #0A0C11;
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
    color: #7E8797;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.1px;
}

QLabel#inspectorHeading,
QLabel#v3PallasInspectorTitle {
    color: #F2F4F8;
    font-size: 13pt;
    font-weight: 660;
}

QLabel#inspectorBody,
QLabel#v3PallasInspectorBody {
    color: #A3AAB7;
}

/* --- PALLAS living field ---------------------------------------------- */

QFrame#pallasShellWorkspaceHost,
QWidget#pallasShellWorkspace,
QWidget#pallasWorkspace,
QWidget#pallasSemanticField {
    background: #0A0C11;
    border: none;
}

QFrame#v3PallasTopbar {
    background: #0D1016;
    border: 1px solid #202532;
    border-radius: 14px;
}

QLabel#pallasLivingStatus,
QLabel#pallasBreadcrumb,
QLabel#pallasSemanticSelection {
    color: #A3AAB7;
    font-size: 9pt;
}

QPushButton#pallasLensSemanticButton,
QPushButton#pallasLensAgeButton,
QPushButton#pallasLensVitalityButton {
    min-height: 32px;
    padding: 0 12px;
    color: #7E8797;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 9px;
}

QPushButton#pallasLensSemanticButton:hover,
QPushButton#pallasLensAgeButton:hover,
QPushButton#pallasLensVitalityButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #2A3140;
}

QPushButton#pallasLensSemanticButton:checked,
QPushButton#pallasLensAgeButton:checked,
QPushButton#pallasLensVitalityButton:checked {
    color: #E3E9FF;
    background: #18213A;
    border-color: #31457F;
}

/* --- Generic controls -------------------------------------------------- */

QLineEdit,
QTextEdit,
QPlainTextEdit,
QSpinBox,
QDoubleSpinBox,
QTimeEdit {
    color: #F2F4F8;
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: #6278C7;
}

QLineEdit:focus,
QTextEdit:focus,
QPlainTextEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus,
QTimeEdit:focus,
QComboBox:focus {
    border-color: #7C9CFF;
}

QPushButton {
    color: #A3AAB7;
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #3B4558;
}

QPushButton:focus {
    border-color: #7C9CFF;
}

QPushButton:disabled {
    color: #626C7D;
    background: #11151D;
    border-color: #252C39;
}

/* Semantic workspace actions stay legible after legacy object-name refinement. */
QPushButton#researchStartButton,
QPushButton#fileImportButton {
    color: #0D1016;
    background: #7C9CFF;
    border: 1px solid #7C9CFF;
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 680;
}

QPushButton#researchStartButton:hover,
QPushButton#fileImportButton:hover {
    color: #0D1016;
    background: #99AFFF;
    border-color: #99AFFF;
}

QPushButton#researchStartButton:focus,
QPushButton#fileImportButton:focus {
    border-color: #F2F4F8;
}

QPushButton#researchRefreshButton,
QPushButton#researchCancelButton,
QPushButton#fileRefreshButton,
QPushButton#fileProcessButton {
    color: #A3AAB7;
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 10px;
    padding: 7px 10px;
}

QPushButton#researchRefreshButton:hover,
QPushButton#researchCancelButton:hover,
QPushButton#fileRefreshButton:hover,
QPushButton#fileProcessButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #3B4558;
}

QPushButton#researchRefreshButton:focus,
QPushButton#researchCancelButton:focus,
QPushButton#fileRefreshButton:focus,
QPushButton#fileProcessButton:focus {
    border-color: #7C9CFF;
}

QPushButton#researchCancelButton:disabled,
QPushButton#fileProcessButton:disabled {
    color: #687284;
    background: #11151D;
    border-color: #252C39;
}

QPushButton#sendButton:disabled {
    color: #C0CAE6;
    background: #27344F;
    border: 1px solid #40577F;
}

QPushButton#groundButton:disabled {
    color: #8C98B0;
    background: #151D2B;
    border-color: #33405A;
}

QCheckBox {
    color: #F2F4F8;
    spacing: 8px;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #2A3140;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #7C9CFF;
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
    color: #A3AAB7;
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
    background: #0A0C11;
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
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 14px;
}

QFrame#v3ResearchBrief {
    background: #121722;
    border-color: #252C39;
}

QLabel#v3KnowledgeState {
    color: #E3E9FF;
    background: #18213A;
    border: 1px solid #31457F;
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
    color: #98A1B1;
    font-size: 8.8pt;
}

QTabWidget#v3KnowledgeTabs::pane {
    background: #11151D;
    border: 1px solid #252C39;
    border-radius: 14px;
    top: -1px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab {
    color: #7E8797;
    background: transparent;
    border: 0;
    border-bottom: 2px solid transparent;
    padding: 10px 15px;
    margin-right: 4px;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:hover {
    color: #F2F4F8;
}

QTabWidget#v3KnowledgeTabs QTabBar::tab:selected {
    color: #F2F4F8;
    border-bottom-color: #7C9CFF;
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
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 14px;
    padding: 4px;
}

QLabel#v3SectionTitle,
QLabel#v3RuntimeCardTitle {
    color: #F2F4F8;
    font-size: 11pt;
    font-weight: 680;
}

QLabel#v3SettingsIntro {
    color: #A3AAB7;
    font-size: 9.5pt;
}

QWidget#v3SettingsRuntimePanel {
    background: transparent;
    border: none;
}


QFrame#v3KnowledgeSearch {
    background: #121722;
    border: 1px solid #252C39;
    border-radius: 14px;
}

QFrame#v3KnowledgeIdentity {
    background: transparent;
    border: none;
    border-bottom: 1px solid #202532;
}

QLabel#v3WorkspaceLead {
    color: #A3AAB7;
    font-size: 9.2pt;
}

QPushButton[v3PrimaryAction="true"] {
    color: #0D1016;
    background: #7C9CFF;
    border: 1px solid #7C9CFF;
    font-weight: 680;
}

QPushButton[v3PrimaryAction="true"]:hover {
    color: #0D1016;
    background: #99AFFF;
    border-color: #99AFFF;
}

QPushButton[v3PrimaryAction="true"]:focus {
    border-color: #F2F4F8;
}

QPushButton[v3DestructiveAction="true"] {
    color: #D8A3A3;
    background: #151922;
    border-color: #443039;
}

QPushButton[v3DestructiveAction="true"]:hover {
    color: #F2C2C2;
    background: #21171C;
    border-color: #72505C;
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
    color: #F2F4F8;
    background: #1B202B;
}

QListWidget#persistentKnowledgeList::item:selected,
QListWidget#persistentClaimList::item:selected,
QListWidget#semanticReviewList::item:selected,
QListWidget#researchJobList::item:selected,
QListWidget#durableJobList::item:selected,
QListWidget#sourceList::item:selected {
    color: #F2F4F8;
    background: #1E2A42;
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
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 9px;
    padding: 6px 11px;
}

QPushButton#pallasBackButton:hover {
    color: #F2F4F8;
    background: #1B202B;
    border-color: #3B4558;
}

QPushButton#pallasBackButton:focus {
    border-color: #7C9CFF;
}

/* --- Commands, help and local tools ------------------------------------ */

QDialog#commandPalette,
QDialog#helpDialog,
QWidget#helpWorkspace,
QDialog#comfyUiDialog {
    color: #F2F4F8;
    background: #0D1016;
    border: 1px solid #343D4E;
    border-radius: 18px;
}

QFrame#helpBody,
QFrame#helpCapabilityContent {
    background: #0D1016;
    border: none;
}

QFrame#helpSecondaryNavigation {
    background: #0D1016;
    border: none;
    border-right: 1px solid #2A3140;
}

QLabel#helpSecondaryTitle,
QLabel#helpHeadline {
    color: #F2F4F8;
    font-weight: 680;
}

QLineEdit#helpSearch {
    color: #F2F4F8;
    background: #151922;
    border: 1px solid #3B4558;
    border-radius: 12px;
    padding: 10px 12px;
    min-height: 24px;
    selection-background-color: #6278C7;
}

QLineEdit#helpSearch:focus {
    border-color: #7C9CFF;
}

QListWidget#helpSections,
QListWidget#helpCapabilities {
    color: #F2F4F8;
    background: transparent;
    border: none;
}

QListWidget#helpCapabilities::item {
    border: none;
    padding: 0;
}

QFrame#helpCapabilityRow {
    background: #151922;
    border: 1px solid #2A3140;
    border-radius: 12px;
}

QFrame#helpCapabilityRow:hover {
    background: #1B202B;
    border-color: #3B4558;
}

QLabel#helpCapabilityTitle {
    color: #F2F4F8;
}

QLabel#helpCapabilityState {
    color: #7E8797;
    font-size: 8pt;
    font-weight: 650;
}

QLabel#helpCapabilitySummary,
QLabel#helpSummary {
    color: #A3AAB7;
}

QLabel#commandPaletteTitle,
QLabel#helpDialogTitle,
QLabel#comfyUiTitle {
    color: #F2F4F8;
    font-size: 15pt;
    font-weight: 700;
    letter-spacing: -0.35px;
}

QLabel#commandPaletteHint {
    color: #A3AAB7;
    background: #1B202B;
    border: 1px solid #2A3140;
    border-radius: 8px;
    padding: 3px 7px;
    font-size: 8pt;
    font-weight: 650;
}

QLineEdit#commandPaletteQuery {
    color: #F2F4F8;
    background: #151922;
    border: 1px solid #3B4558;
    border-radius: 14px;
    padding: 12px 14px;
    font-size: 11pt;
}

QLineEdit#commandPaletteQuery:focus {
    border-color: #7C9CFF;
}

QListWidget#commandPaletteResults {
    color: #F2F4F8;
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
    background: #1B202B;
}

QListWidget#commandPaletteResults::item:selected {
    color: #F2F4F8;
    background: #18213A;
}

QLabel#commandPaletteFooter,
QLabel#helpDialogIntro {
    color: #7E8797;
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
    background: #0A0C11;
}

QLabel#comfyUiSectionLabel {
    color: #7E8797;
    font-size: 8pt;
    font-weight: 680;
    letter-spacing: 1.15px;
    padding-top: 8px;
}

QLabel#comfyUiStatus[pathenaUiState="success"],
QLabel#comfyUiJobStatus[pathenaUiState="completed"] {
    color: #DFE7FF;
}

QLabel#comfyUiStatus[pathenaUiState="error"],
QLabel#comfyUiJobStatus[pathenaUiState="error"] {
    color: #FF9D96;
}

QLabel#comfyUiResourceStatus,
QLabel#comfyUiQueueReceipt,
QLabel#comfyUiJobStatus {
    color: #A3AAB7;
}

QPushButton#comfyUiQueueWorkflow {
    color: #0D1016;
    background: #7C9CFF;
    border-color: #7C9CFF;
    font-weight: 700;
}

QPushButton#comfyUiQueueWorkflow:hover {
    background: #99AFFF;
    border-color: #99AFFF;
}

QPushButton#comfyUiReleaseVram {
    color: #F0D18A;
    background: #292518;
    border-color: #4D4326;
}

/* --- Editorial empty states ------------------------------------------- */

QFrame#v3EmptyState {
    background: transparent;
    border: none;
}

QLabel#v3EmptyTitle {
    color: #F2F4F8;
    font-size: 16pt;
    font-weight: 700;
    letter-spacing: -0.35px;
}

QLabel#v3EmptyBody {
    color: #98A1B1;
    font-size: 9.5pt;
}
"""
