"""Overflow-safe provenance scanning for the secondary Inspector surfaces.

Grounded provenance can contain long source names, context identifiers and excerpts.
The Inspector already owns a responsive fixed width, so its internal labels must yield
to that width rather than expanding the secondary pane. This presentation-only pass
adds shrink-safe size policy, wrapping and selectable text to existing surfaces. It
never truncates provenance data or changes evidence relationships.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget


@dataclass(frozen=True)
class InspectorScanTarget:
    object_name: str
    label: str
    wrap: bool


_TARGETS: tuple[InspectorScanTarget, ...] = (
    InspectorScanTarget("inspectorBody", "Inspector provenance", True),
    InspectorScanTarget("inspectorHeading", "Inspector heading", True),
    InspectorScanTarget("objectId", "Inspector object identity", True),
    InspectorScanTarget("chainState", "Evidence chain summary", True),
)


def _harden_label(label: QLabel, target: InspectorScanTarget) -> None:
    label.setMinimumWidth(0)
    policy = label.sizePolicy()
    policy.setHorizontalPolicy(QSizePolicy.Policy.Ignored)
    policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
    label.setSizePolicy(policy)
    if target.wrap:
        label.setWordWrap(True)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setTextInteractionFlags(
        label.textInteractionFlags()
        | Qt.TextInteractionFlag.TextSelectableByMouse
        | Qt.TextInteractionFlag.TextSelectableByKeyboard
    )
    label.setProperty("pathenaInspectorShrinkSafe", True)
    label.setProperty("pathenaInspectorFullTextPreserved", True)
    label.setProperty("pathenaInspectorWrapEnabled", target.wrap)
    label.setProperty("pathenaInspectorScanRole", target.label.casefold())
    label.setAccessibleDescription(
        f"{target.label}. Full text is preserved and wraps within the current Inspector width."
    )


def apply_inspector_scanability(window: QWidget) -> tuple[QLabel, ...]:
    """Apply overflow-safe presentation to existing Inspector/evidence labels."""
    applied: list[QLabel] = []
    for target in _TARGETS:
        label = window.findChild(QLabel, target.object_name)
        if label is None:
            continue
        _harden_label(label, target)
        applied.append(label)

    inspector = window.findChild(QWidget, "inspector")
    if inspector is not None:
        inspector.setProperty("pathenaInspectorOverflowProtected", True)
        inspector.setProperty("pathenaInspectorProvenanceFullText", True)

    evidence = window.findChild(QWidget, "evidenceChain")
    if evidence is not None:
        evidence.setProperty("pathenaEvidenceChainOverflowProtected", True)

    window.setProperty("pathenaInspectorScanabilityManaged", True)
    window.setProperty("pathenaInspectorScanabilityTargetCount", len(applied))
    return tuple(applied)
