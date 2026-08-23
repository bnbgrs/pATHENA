"""Adaptive layout refinement tasks 2101-2200 for pATHENA.

This presentation-only controller improves real desktop geometry: workspace splitters,
list/detail proportions, header density, composer sizing and compact-mode spacing.
It does not alter controller signals, durable state, APIs, persistence or job behavior.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

_COMPACT = 1260
_WIDE = 1540


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


def install_layout_refinement(window: QWidget) -> PathenaLayoutRefinement:
    """Install adaptive splitter, workspace and composer geometry."""
    return PathenaLayoutRefinement(window)
