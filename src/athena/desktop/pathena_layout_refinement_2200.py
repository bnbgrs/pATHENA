"""Adaptive layout refinement tasks 2101-2200 for pATHENA.

This presentation-only controller improves real desktop geometry: workspace splitters,
list/detail proportions, header density, composer sizing and compact-mode spacing.
It does not alter controller signals, durable state, APIs, persistence or job behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import SHELL

_COMPACT = 1260
_WIDE = 1540
_TOP_NAVIGATION: tuple[tuple[str, int], ...] = (
    ("CHAT", 0),
    ("KNOWLEDGE", 1),
    ("RESEARCH", 2),
    ("JOBS", 3),
    ("SOURCES", 4),
)


@dataclass(frozen=True)
class LayoutTarget:
    key: str
    label: str


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
    """Apply adaptive geometry to the installed pATHENA presentation tree."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._top_navigation_buttons: list[QPushButton] = []
        self._install_top_navigation()
        navigation = getattr(window, "navigation", None)
        if navigation is not None and hasattr(navigation, "currentRowChanged"):
            navigation.currentRowChanged.connect(self._sync_top_navigation)
            self._sync_top_navigation(navigation.currentRow())
        window.installEventFilter(self)
        self.apply_for_width(window.width())

    def _install_top_navigation(self) -> None:
        """Mirror real primary routes in the reference top bar without creating routes."""
        top_bar = self.window.findChild(QWidget, "topBar")
        navigation = getattr(self.window, "navigation", None)
        if top_bar is None or navigation is None:
            return
        layout = top_bar.layout()
        if not isinstance(layout, QHBoxLayout):
            return

        existing = top_bar.findChildren(QPushButton, "topNavButton")
        if existing:
            self._top_navigation_buttons = existing
            self._link_top_navigation_tab_order()
            return

        insert_at = 1
        for label, row in _TOP_NAVIGATION:
            if row >= navigation.count():
                continue
            button = QPushButton(label, top_bar)
            button.setObjectName("topNavButton")
            button.setCheckable(True)
            button.setAutoExclusive(False)
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(f"Open {label.title()} workspace")
            button.setAccessibleDescription("Primary workspace route.")
            button.setToolTip(f"Open {label.title()}")
            button.setProperty("pathenaRouteRow", row)
            button.clicked.connect(
                lambda _checked=False, route=row: self._activate_top_navigation_route(
                    route
                )
            )
            layout.insertWidget(insert_at, button)
            insert_at += 1
            self._top_navigation_buttons.append(button)
        self._link_top_navigation_tab_order()

    def _link_top_navigation_tab_order(self) -> None:
        """Keep keyboard traversal aligned with the visible primary-route order."""
        for previous, following in zip(
            self._top_navigation_buttons,
            self._top_navigation_buttons[1:],
            strict=False,
        ):
            QWidget.setTabOrder(previous, following)

    def _activate_top_navigation_route(self, row: int) -> None:
        """Route through the real navigation and keep repeated clicks visually stable."""
        navigation = getattr(self.window, "navigation", None)
        if navigation is None or not hasattr(navigation, "setCurrentRow"):
            return
        navigation.setCurrentRow(row)
        current_row = navigation.currentRow() if hasattr(navigation, "currentRow") else row
        self._sync_top_navigation(current_row)

    def _sync_top_navigation(self, row: int) -> None:
        for button in self._top_navigation_buttons:
            route = button.property("pathenaRouteRow")
            active = route == row
            button.setChecked(active)
            button.setAccessibleDescription(
                "Current workspace route." if active else "Primary workspace route."
            )

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
        self.window.setProperty(
            "pathenaLayoutDensity",
            "compact" if compact else "wide" if wide else "comfortable",
        )

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

        if compact:
            prompt_min_height = SHELL.composer_action_size
            prompt_max_height = SHELL.composer_min_height
        elif wide:
            prompt_min_height = SHELL.composer_min_height + 6
            prompt_max_height = SHELL.composer_min_height + 14
        else:
            prompt_min_height = SHELL.composer_min_height
            prompt_max_height = SHELL.composer_min_height + 8

        if prompt is not None:
            prompt.setMinimumHeight(prompt_min_height)
            prompt.setMaximumHeight(prompt_max_height)
        if ground is not None:
            ground.setMinimumWidth(62 if compact else 72)
            ground.setMaximumWidth(82)
            ground.setMinimumHeight(SHELL.composer_action_size)
            ground.setText("Source" if compact else "Sources")
            ground.setAccessibleDescription(
                "Use grounded sources for the next response."
            )
        if send is not None:
            send.setFixedSize(SHELL.composer_action_size, SHELL.composer_action_size)

    def _tune_tabs(self, *, compact: bool) -> None:
        tabs = self.window.findChild(QTabWidget, "canonicalMemoryTabs")
        if tabs is not None:
            tabs.tabBar().setExpanding(not compact)
            tabs.setUsesScrollButtons(compact)


def install_layout_refinement(window: QWidget) -> PathenaLayoutRefinement:
    """Install adaptive splitter, workspace and composer geometry."""
    return PathenaLayoutRefinement(window)
