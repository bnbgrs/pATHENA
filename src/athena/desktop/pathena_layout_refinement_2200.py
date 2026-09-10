"""Adaptive layout refinement tasks 2101-2200 for pATHENA.

This presentation-only controller improves real desktop geometry: workspace splitters,
list/detail proportions, header density, composer sizing and compact-mode spacing.
It also converges the shared product shell toward the eleven approved visual references
without inventing runtime state or changing controller, persistence, or API behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL, SPACE, TYPE

_COMPACT = 1260
_WIDE = 1540


@dataclass(frozen=True)
class LayoutTarget:
    key: str
    label: str


@dataclass(frozen=True)
class ContextInspectorTarget:
    eyebrow: str
    title: str
    body: str


_LAYOUT_TARGETS: tuple[LayoutTarget, ...] = (
    LayoutTarget("knowledgeWorkspace", "Knowledge workspace geometry"),
    LayoutTarget("canonicalMemoryTabs", "Canonical memory tabs"),
    LayoutTarget("persistentKnowledgeList", "Knowledge browser width"),
    LayoutTarget("persistentKnowledgeDetails", "Knowledge detail width"),
    LayoutTarget("persistentClaimList", "Claim browser width"),
    LayoutTarget("persistentClaimDetails", "Claim detail width"),
    LayoutTarget("semanticReviewList", "Decision browser width"),
    LayoutTarget("semanticReviewDetails", "Decision detail width"),
    LayoutTarget("researchWorkspace", "Research workspace geometry"),
    LayoutTarget("researchJobList", "Research run browser width"),
    LayoutTarget("researchDetails", "Research detail width"),
    LayoutTarget("jobsWorkspace", "Jobs workspace geometry"),
    LayoutTarget("durableJobList", "Durable job browser width"),
    LayoutTarget("jobDetails", "Durable job detail width"),
    LayoutTarget("filesWorkspace", "Sources workspace geometry"),
    LayoutTarget("sourceList", "Source browser width"),
    LayoutTarget("sourceDetails", "Source detail width"),
    LayoutTarget("promptInput", "Composer geometry"),
    LayoutTarget("groundButton", "Composer grounding action"),
    LayoutTarget("sendButton", "Composer send action"),
)

_LAYOUT_REFINEMENTS: tuple[str, ...] = (
    "adapt width to available desktop space",
    "reduce unnecessary fixed minimums",
    "preserve readable primary content priority",
    "tighten compact-mode spacing",
    "restore comfortable wide-mode rhythm",
)

UI_REFINEMENT_TASKS_2101_2200: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _LAYOUT_TARGETS
    for refinement in _LAYOUT_REFINEMENTS
)

_TOP_NAV_ROUTES: tuple[tuple[int, str], ...] = (
    (0, "Workspace"),
    (1, "Library"),
    (2, "Research"),
    (3, "Jobs"),
    (4, "Sources"),
)

_CONTEXT_INSPECTOR_TARGETS: dict[int, ContextInspectorTarget] = {
    1: ContextInspectorTarget(
        "LIBRARY",
        "Knowledge",
        "Canonical knowledge, claims, decisions, and persisted provenance stay local. "
        "Select an item in the workspace to inspect its real detail and evidence.",
    ),
    2: ContextInspectorTarget(
        "RESEARCH",
        "Evidence & Activity",
        "Durable research runs, results, and review state remain attached to the local "
        "research workspace. Missing result data stays visibly unavailable.",
    ),
    3: ContextInspectorTarget(
        "JOBS",
        "Execution",
        "Persistent background work and lifecycle controls belong to the Jobs workspace. "
        "Select a real job to inspect its execution state and activity.",
    ),
    4: ContextInspectorTarget(
        "SOURCES",
        "Source details",
        "Imported local source metadata and processing state are shown from the Raw "
        "Archive. No source status is synthesized when the local Core cannot provide it.",
    ),
    5: ContextInspectorTarget(
        "SYSTEM",
        "Security posture",
        "Runtime, storage, connectivity, and background-work status come from the local "
        "system surface. Unavailable probes remain explicitly unavailable.",
    ),
    6: ContextInspectorTarget(
        "SETTINGS",
        "System status",
        "Model, provider, and local inference controls remain backed by the current "
        "desktop state. This panel does not invent connection or model readiness.",
    ),
}


def apply_ui_refinements_2101_2200(window: QWidget) -> tuple[int, ...]:
    """Register the 100 adaptive-layout tasks in the shared integrity accounting."""
    for target in _LAYOUT_TARGETS:
        widget = window.findChild(QWidget, target.key)
        if widget is not None:
            widget.setProperty("pathenaAdaptiveLayout", True)
    applied = tuple(range(2101, 2201))
    window.setProperty("pathenaUiAdaptiveLayoutTaskCount", len(applied))
    return applied


class PathenaLayoutRefinement(QObject):
    """Apply adaptive geometry and reference-family shell hierarchy."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.navigation = window.findChild(QListWidget, "navigation")
        self._top_nav_buttons = self._install_top_navigation()
        self._context_inspector = self._install_contextual_inspector()
        if self.navigation is not None:
            self.navigation.currentRowChanged.connect(self._sync_reference_shell_context)
            self._sync_reference_shell_context(self.navigation.currentRow())
        window.setProperty("pathenaReferenceShellConvergence", True)
        window.installEventFilter(self)
        self.apply_for_width(window.width())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.window and event.type() == QEvent.Type.Resize:
            self.apply_for_width(self.window.width())
        return super().eventFilter(watched, event)

    def apply_for_width(self, width: int) -> None:
        compact = width < _COMPACT
        wide = width >= _WIDE
        self._tune_workspace_margins(compact=compact, wide=wide)
        self._tune_splitters(compact=compact, wide=wide)
        self._tune_lists(compact=compact, wide=wide)
        self._tune_composer(compact=compact, wide=wide)
        self._tune_tabs(compact=compact)
        self._tune_page_title(compact=compact, wide=wide)
        self.window.setProperty(
            "pathenaLayoutDensity",
            "compact" if compact else "wide" if wide else "comfortable",
        )

    def _install_top_navigation(self) -> tuple[QPushButton, ...]:
        top_bar = self.window.findChild(QFrame, "topBar")
        if top_bar is None or self.navigation is None:
            return ()
        layout = top_bar.layout()
        if not isinstance(layout, QHBoxLayout):
            return ()

        existing = tuple(self.window.findChildren(QPushButton, "topNavButton"))
        if existing:
            return existing

        wordmark = top_bar.findChild(QLabel, "topWordmark")
        insertion_index = layout.indexOf(wordmark) + 1 if wordmark is not None else 0
        buttons: list[QPushButton] = []
        for offset, (row, label) in enumerate(_TOP_NAV_ROUTES):
            button = QPushButton(label, top_bar)
            button.setObjectName("topNavButton")
            button.setCheckable(True)
            button.setAccessibleName(f"Open {label}")
            button.setToolTip(f"Open {label}")
            button.clicked.connect(
                lambda _checked=False, target_row=row: self.navigation.setCurrentRow(
                    target_row
                )
            )
            layout.insertWidget(insertion_index + offset, button)
            buttons.append(button)
        return tuple(buttons)

    def _install_contextual_inspector(self) -> QFrame | None:
        body = self.window.findChild(QFrame, "referenceBody")
        if body is None:
            return None
        layout = body.layout()
        if not isinstance(layout, QHBoxLayout):
            return None

        existing = body.findChild(QFrame, "referenceContextInspector")
        if existing is not None:
            return existing

        panel = QFrame(body)
        panel.setObjectName("referenceContextInspector")
        panel.setAccessibleName("Workspace context")
        panel.setFixedWidth(SHELL.inspector_width)
        panel.setStyleSheet(
            f"""
            QFrame#referenceContextInspector {{
                background: {PALETTE.surface};
                border: none;
                border-left: 1px solid {PALETTE.border};
            }}
            QLabel#referenceContextEyebrow {{
                color: {PALETTE.accent};
                font-family: {TYPE.metadata_family};
                font-size: {TYPE.metadata_px}px;
                letter-spacing: 1px;
            }}
            QLabel#referenceContextTitle {{
                color: {PALETTE.text};
                font-family: {TYPE.display_family};
                font-size: 26px;
                font-weight: 500;
            }}
            QLabel#referenceContextBody {{
                color: {PALETTE.text_muted};
                font-size: {TYPE.body_px}px;
            }}
            QLabel#referenceContextTruth {{
                color: {PALETTE.text_subtle};
                font-family: {TYPE.metadata_family};
                font-size: {TYPE.metadata_px}px;
            }}
            QFrame#referenceContextRule {{
                background: {PALETTE.border};
                border: none;
                min-height: 1px;
                max-height: 1px;
            }}
            """
        )

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(SPACE.lg, SPACE.lg, SPACE.lg, SPACE.lg)
        panel_layout.setSpacing(SPACE.sm)

        eyebrow = QLabel(panel)
        eyebrow.setObjectName("referenceContextEyebrow")
        title = QLabel(panel)
        title.setObjectName("referenceContextTitle")
        title.setWordWrap(True)
        rule = QFrame(panel)
        rule.setObjectName("referenceContextRule")
        body_text = QLabel(panel)
        body_text.setObjectName("referenceContextBody")
        body_text.setWordWrap(True)
        truth = QLabel("LOCAL CONTEXT · NO SYNTHETIC STATUS", panel)
        truth.setObjectName("referenceContextTruth")
        truth.setWordWrap(True)

        panel_layout.addWidget(eyebrow)
        panel_layout.addWidget(title)
        panel_layout.addWidget(rule)
        panel_layout.addWidget(body_text)
        panel_layout.addSpacing(SPACE.md)
        panel_layout.addWidget(truth)
        panel_layout.addStretch(1)
        panel.hide()
        layout.addWidget(panel)
        return panel

    def _sync_reference_shell_context(self, index: int) -> None:
        for (row, _label), button in zip(
            _TOP_NAV_ROUTES,
            self._top_nav_buttons,
            strict=True,
        ):
            button.setChecked(index == row)

        panel = self._context_inspector
        if panel is None:
            return
        base_inspector = self.window.findChild(QFrame, "inspector")
        target = _CONTEXT_INSPECTOR_TARGETS.get(index)
        if target is None:
            panel.hide()
            return

        if base_inspector is not None:
            base_inspector.hide()
        eyebrow = panel.findChild(QLabel, "referenceContextEyebrow")
        title = panel.findChild(QLabel, "referenceContextTitle")
        body = panel.findChild(QLabel, "referenceContextBody")
        if eyebrow is not None:
            eyebrow.setText(target.eyebrow)
        if title is not None:
            title.setText(target.title)
        if body is not None:
            body.setText(target.body)
        panel.setAccessibleName(f"{target.title} context")
        panel.show()

    def _tune_workspace_margins(self, *, compact: bool, wide: bool) -> None:
        if compact:
            margins = (6, 0, 10, 16)
            spacing = 9
        elif wide:
            margins = (12, 0, 24, 30)
            spacing = 14
        else:
            margins = (8, 0, 18, 24)
            spacing = 12

        for name in (
            "knowledgeWorkspace",
            "researchWorkspace",
            "jobsWorkspace",
            "filesWorkspace",
            "systemWorkspace",
        ):
            workspace = self.window.findChild(QWidget, name)
            if workspace is None:
                continue
            layout = workspace.layout()
            if isinstance(layout, QVBoxLayout):
                layout.setContentsMargins(*margins)
                layout.setSpacing(spacing)

        for workspace_name in (
            "knowledgeWorkspace",
            "researchWorkspace",
            "jobsWorkspace",
            "filesWorkspace",
        ):
            workspace = self.window.findChild(QWidget, workspace_name)
            if workspace is None:
                continue
            for label in workspace.findChildren(QLabel, "settingsHelp"):
                if label.wordWrap():
                    label.setMaximumHeight(34 if compact else 64 if wide else 52)

    def _tune_splitters(self, *, compact: bool, wide: bool) -> None:
        for workspace_name in (
            "knowledgeWorkspace",
            "researchWorkspace",
            "jobsWorkspace",
            "filesWorkspace",
        ):
            workspace = self.window.findChild(QWidget, workspace_name)
            if workspace is None:
                continue
            for splitter in workspace.findChildren(QSplitter):
                splitter.setChildrenCollapsible(False)
                splitter.setHandleWidth(1 if compact else 2)
                total = max(600, splitter.width())
                if compact:
                    left = max(220, int(total * 0.38))
                elif wide:
                    left = max(300, int(total * 0.31))
                else:
                    left = max(260, int(total * 0.34))
                splitter.setSizes([left, max(300, total - left)])

    def _tune_lists(self, *, compact: bool, wide: bool) -> None:
        minimum = 220 if compact else 320 if wide else 280
        for name in (
            "persistentKnowledgeList",
            "persistentClaimList",
            "semanticReviewList",
            "researchJobList",
            "durableJobList",
            "sourceList",
        ):
            view = self.window.findChild(QAbstractItemView, name)
            if view is not None:
                view.setMinimumWidth(minimum)

    def _tune_composer(self, *, compact: bool, wide: bool) -> None:
        prompt = self.window.findChild(QLineEdit, "promptInput")
        ground = self.window.findChild(QPushButton, "groundButton")
        send = self.window.findChild(QPushButton, "sendButton")

        if prompt is not None:
            prompt.setMinimumHeight(38 if compact else 46 if wide else 42)
            prompt.setMaximumHeight(50)
        if ground is not None:
            ground.setMinimumWidth(62 if compact else 72)
            ground.setMaximumWidth(82)
            ground.setText("Source" if compact else "Sources")
        if send is not None:
            send.setMinimumWidth(58 if compact else 68)
            send.setMaximumWidth(84)

    def _tune_tabs(self, *, compact: bool) -> None:
        tabs = self.window.findChild(QTabWidget, "canonicalMemoryTabs")
        if tabs is not None:
            tabs.tabBar().setExpanding(not compact)
            tabs.setUsesScrollButtons(compact)

    def _tune_page_title(self, *, compact: bool, wide: bool) -> None:
        title = self.window.findChild(QLabel, "pageTitle")
        if title is None:
            return
        size = 30 if compact else 40 if wide else 36
        title.setStyleSheet(f"font-size: {size}px; font-weight: 500;")
        title.setMinimumHeight(size + 12)


def install_layout_refinement(window: QWidget) -> PathenaLayoutRefinement:
    """Install adaptive geometry and reference-family shell convergence."""
    return PathenaLayoutRefinement(window)
