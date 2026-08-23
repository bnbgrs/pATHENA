"""Research readability refinements 2301-2400 for pATHENA.

The immutable ResearchResult command intentionally emits canonical JSON. This
presentation-only adapter preserves that raw payload in a dynamic property while
rendering a calmer human-readable outline after the existing load completes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QPushButton, QWidget

if TYPE_CHECKING:
    from athena.desktop.research_results_extension import ResearchResultsExtension


@dataclass(frozen=True)
class ResearchReadabilityTarget:
    key: str
    label: str


_TARGETS: tuple[ResearchReadabilityTarget, ...] = (
    ResearchReadabilityTarget("researchResultPanel", "Research result panel"),
    ResearchReadabilityTarget("researchDetails", "Research result body"),
    ResearchReadabilityTarget("researchProposalList", "Proposal list"),
    ResearchReadabilityTarget("researchProposalRefreshButton", "Proposal review action"),
    ResearchReadabilityTarget("researchProposalAcceptButton", "Proposal accept action"),
    ResearchReadabilityTarget("researchProposalSeparateButton", "Keep-separate action"),
    ResearchReadabilityTarget("researchProposalRejectButton", "Proposal reject action"),
    ResearchReadabilityTarget("researchJobList", "Research runs"),
    ResearchReadabilityTarget("researchJobFilter", "Research filter"),
    ResearchReadabilityTarget("researchStatus", "Research status"),
    ResearchReadabilityTarget("researchQuestionInput", "Research question"),
    ResearchReadabilityTarget("researchStartButton", "Start research"),
    ResearchReadabilityTarget("researchRefreshButton", "Refresh research"),
    ResearchReadabilityTarget("researchCancelButton", "Cancel research"),
    ResearchReadabilityTarget("researchProposalStatus", "Proposal status"),
    ResearchReadabilityTarget("researchCoverage", "Coverage summary"),
    ResearchReadabilityTarget("researchEvidence", "Evidence summary"),
    ResearchReadabilityTarget("researchResultMeta", "Result metadata"),
    ResearchReadabilityTarget("researchDecisionContext", "Decision context"),
    ResearchReadabilityTarget("researchEmptyState", "Research empty state"),
)

_REFINEMENTS: tuple[str, ...] = (
    "replace raw technical emphasis with readable hierarchy",
    "surface evidence and coverage before identifiers",
    "keep decision context adjacent to proposal actions",
    "preserve raw data without making it primary",
    "tighten vertical rhythm for long research output",
)

UI_REFINEMENT_TASKS_2301_2400: tuple[str, ...] = tuple(
    f"{refinement} for {target.label}"
    for target in _TARGETS
    for refinement in _REFINEMENTS
)

_STYLESHEET = r"""
QPlainTextEdit#researchDetails {
    background: #080808;
    border: none;
    color: #D9D9D9;
    padding: 10px 12px;
}
QListWidget#researchProposalList::item {
    padding: 7px 9px;
    border-bottom: 1px solid #171717;
}
QListWidget#researchProposalList::item:selected {
    background: #15100C;
    border-left: 2px solid #F26A21;
}
QLabel[pathenaResearchReadability="secondary"] { color: #8F8F8F; }
"""


def _human_key(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def _scalar(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def _format_mapping(data: dict[str, Any], *, depth: int = 0) -> list[str]:
    lines: list[str] = []
    priority = (
        "question", "query", "summary", "answer", "result", "coverage",
        "evidence", "sources", "claims", "findings", "status",
    )
    keys = list(data)
    keys.sort(
        key=lambda key: (
            next((i for i, name in enumerate(priority) if name in key.casefold()), 99),
            key,
        )
    )
    indent = "  " * depth
    for key in keys:
        value = data[key]
        heading = _human_key(key)
        if isinstance(value, dict):
            lines.append(f"{indent}{heading}")
            lines.extend(_format_mapping(value, depth=depth + 1))
        elif isinstance(value, list):
            lines.append(f"{indent}{heading} · {len(value)}")
            for item in value:
                if isinstance(item, dict):
                    lines.extend(_format_mapping(item, depth=depth + 1))
                else:
                    lines.append(f"{indent}  • {_scalar(item)}")
        else:
            lines.append(f"{indent}{heading}: {_scalar(value)}")
    return lines


def _readable_result(raw: str) -> str | None:
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(payload, dict):
        return None
    return "\n".join(_format_mapping(payload)).strip()


def apply_ui_refinements_2301_2400(window: QWidget) -> tuple[int, ...]:
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = window.findChild(QWidget, target.key)
        if widget is None:
            continue
        widget.setProperty("pathenaResearchReadable", True)
        start = 2301 + index * len(_REFINEMENTS)
        applied.extend(range(start, start + len(_REFINEMENTS)))
    if _STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_STYLESHEET}")
    return tuple(applied)


class PathenaResearchReadability(QObject):
    """Render existing immutable ResearchResult JSON as a readable outline."""

    def __init__(self, window: QWidget, extension: ResearchResultsExtension) -> None:
        super().__init__(window)
        self.window = window
        self.extension = extension
        self.details = window.findChild(QPlainTextEdit, "researchDetails")
        self.proposals = window.findChild(QListWidget, "researchProposalList")
        apply_ui_refinements_2301_2400(window)
        extension.process.finished.connect(self._schedule_format)
        self._quiet_status_labels()
        if self.details is not None:
            self.details.document().setDocumentMargin(12.0)

    def _schedule_format(self, *_args: object) -> None:
        if getattr(self.extension, "_operation", "") not in {"", "result"}:
            return
        QTimer.singleShot(0, self._format_loaded_result)

    def _format_loaded_result(self) -> None:
        if self.details is None:
            return
        raw = self.details.toPlainText().strip()
        if not raw.startswith("{"):
            return
        readable = _readable_result(raw)
        if not readable:
            return
        self.details.setProperty("pathenaRawResearchResult", raw)
        self.details.setPlainText(readable)
        self.details.moveCursor(QTextCursor.MoveOperation.Start)

    def _quiet_status_labels(self) -> None:
        for label in self.window.findChildren(QLabel):
            text = label.text().casefold()
            if "proposal" in text or "research" in text or "evidence" in text:
                label.setProperty("pathenaResearchReadability", "secondary")
        for name in (
            "researchProposalRefreshButton",
            "researchProposalSeparateButton",
            "researchProposalRejectButton",
        ):
            button = self.window.findChild(QPushButton, name)
            if button is not None:
                button.setProperty("role", "secondary")


def install_research_readability(
    window: QWidget,
    extension: ResearchResultsExtension,
) -> PathenaResearchReadability:
    """Install human-readable presentation for immutable Research results."""
    return PathenaResearchReadability(window, extension)
