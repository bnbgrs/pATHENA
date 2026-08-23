"""Seventh 100-task, presentation-only refinement pass for pATHENA.

Operational lists carry a large amount of durable state but previously rendered most
rows with identical visual weight. This pass defines a restrained semantic language
for 25 real runtime states and exposes a helper used while Research, Jobs and Sources
rows are rendered. No domain ordering, persistence, scheduler or API state is changed.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont
from PySide6.QtWidgets import QListWidgetItem, QWidget


@dataclass(frozen=True)
class OperationalRowStyle:
    category: str
    marker: str
    color: str
    emphasis: bool = False


_OPERATIONAL_STYLES: dict[str, OperationalRowStyle] = {
    "queued": OperationalRowStyle("active", "·", "#D8B08A"),
    "waiting": OperationalRowStyle("attention", "◌", "#C9B47A"),
    "running": OperationalRowStyle("active", "●", "#F26A21", True),
    "paused": OperationalRowStyle("attention", "Ⅱ", "#C9B47A"),
    "cancel_requested": OperationalRowStyle("attention", "×", "#D59A72"),
    "cancelled": OperationalRowStyle("idle", "×", "#777777"),
    "failed": OperationalRowStyle("error", "!", "#E1A19B", True),
    "completed": OperationalRowStyle("success", "✓", "#AFC9B4"),
    "ready": OperationalRowStyle("success", "✓", "#AFC9B4"),
    "processing": OperationalRowStyle("active", "●", "#F26A21", True),
    "captured": OperationalRowStyle("idle", "·", "#A7A7A7"),
    "unsupported": OperationalRowStyle("attention", "—", "#C9B47A"),
    "pending": OperationalRowStyle("attention", "◌", "#C9B47A"),
    "blocked": OperationalRowStyle("attention", "!", "#D59A72"),
    "review": OperationalRowStyle("attention", "◆", "#C9B47A"),
    "accepted": OperationalRowStyle("success", "✓", "#AFC9B4"),
    "rejected": OperationalRowStyle("idle", "×", "#777777"),
    "idle": OperationalRowStyle("idle", "·", "#A7A7A7"),
    "active": OperationalRowStyle("active", "●", "#F26A21", True),
    "success": OperationalRowStyle("success", "✓", "#AFC9B4"),
    "error": OperationalRowStyle("error", "!", "#E1A19B", True),
    "empty": OperationalRowStyle("idle", "—", "#777777"),
    "unavailable": OperationalRowStyle("error", "!", "#E1A19B"),
    "stopping": OperationalRowStyle("attention", "◌", "#D59A72"),
    "external": OperationalRowStyle("idle", "·", "#A7A7A7"),
}

_ROW_REFINEMENTS: tuple[str, ...] = (
    "semantic category",
    "compact state marker",
    "restrained foreground tone",
    "scan emphasis",
)

UI_REFINEMENT_TASKS_601_700: tuple[str, ...] = tuple(
    f"Define {refinement} for operational state {state}"
    for state in _OPERATIONAL_STYLES
    for refinement in _ROW_REFINEMENTS
)

_LIST_STYLESHEET = """
QListWidget[pathenaOperationalList="true"]::item {
    padding: 5px 7px;
    border-bottom: 1px solid #171717;
}
QListWidget[pathenaOperationalList="true"]::item:selected {
    background: #18130F;
    color: #F2F2F2;
}
QListWidget[pathenaOperationalList="true"]::item:hover:!selected {
    background: #101010;
}
"""


def style_operational_item(item: QListWidgetItem, state: str, body: str) -> None:
    """Apply quiet state semantics to one already-created operational list row."""
    normalized = state.strip().casefold().replace(" ", "_")
    style = _OPERATIONAL_STYLES.get(normalized, _OPERATIONAL_STYLES["idle"])
    item.setText(f"{style.marker}  {body}")
    item.setForeground(QBrush(QColor(style.color)))
    font = item.font()
    font.setWeight(QFont.Weight.DemiBold if style.emphasis else QFont.Weight.Normal)
    item.setFont(font)
    item.setData(Qt.ItemDataRole.UserRole + 20, normalized)
    item.setData(Qt.ItemDataRole.UserRole + 21, style.category)


def apply_ui_refinements_601_700(window: QWidget) -> tuple[int, ...]:
    """Register operational lists and their restrained row-selection treatment."""
    applied: list[int] = []
    for name in ("researchJobList", "durableJobList", "sourceList"):
        widget = window.findChild(QWidget, name)
        if widget is not None:
            widget.setProperty("pathenaOperationalList", True)

    if _LIST_STYLESHEET not in window.styleSheet():
        window.setStyleSheet(f"{window.styleSheet()}\n{_LIST_STYLESHEET}")

    applied.extend(range(601, 701))
    window.setProperty("pathenaUiOperationalRowsAppliedCount", len(applied))
    window.setProperty("pathenaUiOperationalRowsTaskCount", 100)
    return tuple(applied)
