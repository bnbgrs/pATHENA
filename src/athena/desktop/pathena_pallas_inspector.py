"""Shared Context Inspector binding for renderer-owned PALLAS selections.

The design-system layer deliberately treats the selection payload structurally.
Core owns the semantic model and renderer; this module only projects an emitted
selection into the existing, shared inspector and restores the previous screen
context when that selection is cleared.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QWidget

from athena.desktop.window import MetricRow


@dataclass(frozen=True, slots=True)
class _InspectorSnapshot:
    object_id: str
    heading: str
    mode: str
    provenance: str
    message_count_visible: bool
    panel_visible: bool
    details_visible: bool
    details_checked: bool


def _text(value: object | None) -> str:
    return str(value).strip() if value is not None else ""


def _kind_value(value: object | None) -> str:
    raw = getattr(value, "value", value)
    return _text(raw).upper()


class PallasContextInspectorController(QObject):
    """Project real PALLAS selections into the shared read-only inspector."""

    def __init__(self, window: QWidget, selection_source: object) -> None:
        super().__init__(window)
        self._window = window
        self._selection_source = selection_source
        self._selection_signal: Any = getattr(selection_source, "selection_changed", None)
        self._snapshot: _InspectorSnapshot | None = None
        self._disposed = False

        self._panel = window.findChild(QFrame, "inspector")
        self._object_id = window.findChild(QLabel, "objectId")
        self._heading = window.findChild(QLabel, "inspectorHeading")
        candidate_mode = getattr(window, "inspector_mode", None)
        self._mode = candidate_mode if isinstance(candidate_mode, MetricRow) else None
        candidate_count = getattr(window, "inspector_message_count", None)
        self._message_count = candidate_count if isinstance(candidate_count, MetricRow) else None
        self._provenance = window.findChild(QLabel, "inspectorBody")
        self._details = window.findChild(QPushButton, "detailsToggle")

        missing = tuple(
            name
            for name, widget in (
                ("inspector", self._panel),
                ("objectId", self._object_id),
                ("inspectorHeading", self._heading),
                ("inspectorBody", self._provenance),
            )
            if widget is None
        )
        if missing:
            raise RuntimeError(
                "PALLAS Context Inspector requires shared widgets: " + ", ".join(missing)
            )
        if self._selection_signal is None or not callable(
            getattr(self._selection_signal, "connect", None)
        ):
            raise TypeError("selection_source must expose selection_changed.connect")

        assert self._panel is not None
        self._panel.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._panel.setAccessibleName("PALLAS Context Inspector")
        self._panel.setAccessibleDescription(
            "Read-only details for the selected real PALLAS semantic object."
        )
        self._panel.setProperty("pathenaPallasInspectorSlot", True)
        self._selection_signal.connect(self.set_selection)
        window.destroyed.connect(self.dispose)

    @Slot(object)
    def set_selection(self, selection: object | None) -> None:
        """Show one validated structural selection, or restore prior context."""
        if self._disposed:
            return
        if selection is None:
            self.clear_selection()
            return

        graph_id = _text(getattr(selection, "graph_id", None))
        node = getattr(selection, "node", None)
        node_id = _text(getattr(node, "node_id", None))
        title = _text(getattr(node, "title", None))
        kind = _kind_value(getattr(node, "kind", None))
        if not graph_id or node is None or not node_id or not title or not kind:
            self.clear_selection()
            return

        self._capture_previous_context()
        glyph = _text(getattr(node, "glyph", None))
        entity_type = _text(getattr(node, "entity_type", None))
        entity_id = _text(getattr(node, "entity_id", None))
        revision_id = _text(getattr(node, "revision_id", None))
        summary = _text(getattr(node, "summary", None))
        epistemic = _text(getattr(node, "epistemic_status", None))
        confidence = getattr(node, "confidence", None)
        cited = bool(getattr(node, "cited", False))

        assert self._object_id is not None
        assert self._heading is not None
        assert self._provenance is not None
        assert self._panel is not None
        self._object_id.setText(f"PALLAS / {kind} / {node_id}")
        self._heading.setText(f"{glyph} {title}".strip())
        if self._mode is not None:
            self._mode.set_value(kind)
        if self._message_count is not None:
            self._message_count.hide()

        provenance = [
            summary or "No summary is attached to this semantic object.",
            "",
            f"Entity: {entity_type or '—'} / {entity_id or '—'}",
            f"Revision: {revision_id or '—'}",
            f"Graph: {graph_id}",
            f"Grounding: {'cited evidence' if cited else 'context only'}",
        ]
        if epistemic:
            provenance.append(f"Epistemic state: {epistemic}")
        if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            provenance.append(f"Confidence: {confidence:.2f}")
        self._provenance.setText("\n".join(provenance))
        self._provenance.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self._panel.setProperty("pathenaPallasSelectionId", node_id)
        self._panel.setProperty("pathenaPallasGraphId", graph_id)
        self._panel.setVisible(True)
        if self._details is not None:
            self._details.setVisible(True)
            self._details.setChecked(True)

    @Slot()
    def clear_selection(self) -> None:
        """Clear PALLAS state without erasing another screen's inspector state."""
        snapshot = self._snapshot
        if snapshot is None:
            return
        assert self._object_id is not None
        assert self._heading is not None
        assert self._provenance is not None
        assert self._panel is not None
        self._object_id.setText(snapshot.object_id)
        self._heading.setText(snapshot.heading)
        if self._mode is not None:
            self._mode.set_value(snapshot.mode)
        if self._message_count is not None:
            self._message_count.setVisible(snapshot.message_count_visible)
        self._provenance.setText(snapshot.provenance)
        self._panel.setProperty("pathenaPallasSelectionId", None)
        self._panel.setProperty("pathenaPallasGraphId", None)
        if self._details is not None:
            self._details.setVisible(snapshot.details_visible)
            self._details.setChecked(snapshot.details_checked)
        self._panel.setVisible(snapshot.panel_visible)
        self._snapshot = None

    def _capture_previous_context(self) -> None:
        if self._snapshot is not None:
            return
        assert self._object_id is not None
        assert self._heading is not None
        assert self._provenance is not None
        assert self._panel is not None
        details_visible = self._details.isVisible() if self._details is not None else False
        details_checked = self._details.isChecked() if self._details is not None else False
        mode = self._mode.value_label.text() if self._mode is not None else ""
        self._snapshot = _InspectorSnapshot(
            object_id=self._object_id.text(),
            heading=self._heading.text(),
            mode=mode,
            provenance=self._provenance.text(),
            message_count_visible=(
                self._message_count.isVisible() if self._message_count is not None else False
            ),
            panel_visible=self._panel.isVisible(),
            details_visible=details_visible,
            details_checked=details_checked,
        )

    @Slot()
    def dispose(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        try:
            self._selection_signal.disconnect(self.set_selection)
        except (RuntimeError, TypeError):
            pass
        self._snapshot = None


def install_pallas_context_inspector(
    window: QWidget,
    selection_source: object,
) -> PallasContextInspectorController:
    """Install the one shared PALLAS Inspector binding for ``window``."""
    existing = getattr(window, "_pathena_pallas_inspector_controller", None)
    if isinstance(existing, PallasContextInspectorController):
        existing.dispose()
        existing.deleteLater()
    controller = PallasContextInspectorController(window, selection_source)
    window.__dict__["_pathena_pallas_inspector_controller"] = controller
    return controller
