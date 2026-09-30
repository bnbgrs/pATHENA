"""Qt bridge for the provenance-safe PALLAS living simulation.

This controller wraps the existing semantic renderer. It moves already-rendered
nodes and edges and annotates runtime age/vitality; graph membership stays owned
by the grounded Core response.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsSimpleTextItem,
)
from shiboken6 import isValid

from athena.desktop.pathena_pallas_delta import (
    PallasActivityTracker,
    PallasSnapshotDelta,
)
from athena.desktop.pathena_pallas_field import (
    PALLAS_EDGE_RELATION_DATA_KEY,
    PALLAS_EDGE_SOURCE_DATA_KEY,
    PALLAS_EDGE_TARGET_DATA_KEY,
    PallasGroundedFieldController,
    PallasSemanticField,
)
from athena.desktop.pathena_pallas_living import PallasLivingEngine
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasSemanticNode,
    deterministic_layout,
)
from athena.desktop.pathena_v3_theme import (
    V3_BORDER,
    V3_DANGER,
    V3_TEXT_DIM,
)

_AGE_MARKER_KEY = 7391
_AGE_MARKER_VALUE = "pallas-living-age"
_MUTED = QColor(V3_TEXT_DIM)
_CONFLICT = QColor(V3_DANGER)
_BORDER = QColor(V3_BORDER)
_LENSES = frozenset({"semantic", "age", "vitality"})
_CONFLICT_REL = frozenset(
    {"conflict", "conflicts", "contradicts", "contradiction", "opposes"}
)


def _cadence_interval_ms(*, full_visible: bool, visible: bool, nodes: int) -> int:
    """Choose presentation cadence without dropping semantic graph facts."""
    if not visible:
        return 250
    if full_visible:
        fps = 30 if nodes <= 96 else 24 if nodes <= 180 else 18 if nodes <= 320 else 12
    else:
        fps = 15 if nodes <= 140 else 10 if nodes <= 320 else 6
    return round(1000 / fps)


@dataclass(slots=True)
class _FieldBinding:
    field: PallasSemanticField
    graph_id: str
    item_token: tuple[int, ...]
    edge_items: tuple[tuple[QGraphicsLineItem, str, str], ...]
    age_items: dict[str, QGraphicsSimpleTextItem]
    nodes: dict[str, PallasSemanticNode]
    glyph_items: dict[str, QGraphicsSimpleTextItem]


class PallasLivingQtController(QObject):
    """Share one adaptive living state across compact and full PALLAS views."""

    diagnostics_changed = Signal(object)

    def __init__(
        self,
        grounded_controller: PallasGroundedFieldController,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or grounded_controller)
        self._grounded_controller = grounded_controller
        self._engine = PallasLivingEngine()
        self._snapshot: PallasGraphSnapshot | None = None
        self._rejected_snapshot: PallasGraphSnapshot | None = None
        self._validation_error = ""
        self._activity = PallasActivityTracker()
        self._last_delta: PallasSnapshotDelta | None = None
        self._delta_pulse_seconds = 4.0
        self._delta_pulse_remaining = 0.0
        self._lens = "semantic"
        self._bindings: dict[int, _FieldBinding] = {}
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._active_interval_ms = round(1000 / self._engine.config.fps)
        self._compact_interval_ms = round(1000 / 15)
        self._idle_interval_ms = 250
        self._timer.setInterval(self._compact_interval_ms)
        self._timer.timeout.connect(self._tick)
        grounded_controller.selection_changed.connect(self._apply_selection_focus)
        self._selection_connected = True
        self._stopped = False
        self._apply_selection_focus(
            getattr(grounded_controller, "_selection", None)  # noqa: SLF001
        )
        self._timer.start()

    @property
    def engine(self) -> PallasLivingEngine:
        return self._engine

    @property
    def lens(self) -> str:
        return self._lens

    def set_lens(self, lens: str) -> None:
        normalized = lens.casefold().strip()
        if normalized not in _LENSES:
            raise ValueError(f"Unsupported PALLAS lens: {lens!r}")
        self._lens = normalized
        for field in self._mounted_fields():
            field.setProperty("pathenaPallasLens", normalized)
        for binding_id, binding in tuple(self._bindings.items()):
            if not self._binding_is_current(binding):
                self._bindings.pop(binding_id, None)
                continue
            self._apply_binding(binding)

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._timer.stop()
        if self._selection_connected:
            try:
                self._grounded_controller.selection_changed.disconnect(
                    self._apply_selection_focus
                )
            except (RuntimeError, TypeError):
                pass
            self._selection_connected = False
        self._bindings.clear()
        self._engine.clear()
        self._snapshot = None
        self._rejected_snapshot = None
        self._validation_error = ""
        self._activity.reset()
        self._last_delta = None
        self._delta_pulse_remaining = 0.0

    @Slot(object)
    def _apply_selection_focus(self, selection: object | None) -> None:
        node = getattr(selection, "node", None)
        node_id = str(getattr(node, "node_id", "") or "")
        self._engine.set_visual_focus(node_id or None)

    @Slot()
    def _tick(self) -> None:
        field = self._grounded_controller.field
        if not isValid(field):
            self.stop()
            return
        snapshot = field.snapshot
        if snapshot is None or snapshot.status != "ready" or not snapshot.nodes:
            self._bindings.clear()
            self._engine.clear()
            self._snapshot = None
            self._rejected_snapshot = None
            self._validation_error = ""
            for current in self._mounted_fields():
                current.setProperty("pathenaPallasLivingError", "")
            if self._timer.interval() != self._idle_interval_ms:
                self._timer.setInterval(self._idle_interval_ms)
            field_state = str(field.property("pathenaUiState") or "empty")
            self.diagnostics_changed.emit(
                {
                    "nodes": 0,
                    "active": 0,
                    "fps_target": round(1000 / self._idle_interval_ms),
                    "cadence_mode": "background",
                    "lens": self._lens,
                    "field_state": field_state,
                    "validation_error": "",
                }
            )
            return

        if snapshot == self._rejected_snapshot:
            for current in self._mounted_fields():
                current.setProperty("pathenaPallasLivingError", self._validation_error)
            self.diagnostics_changed.emit(
                {
                    "nodes": len(snapshot.nodes),
                    "active": 0,
                    "lens": self._lens,
                    "field_state": "ready",
                    "validation_error": self._validation_error,
                }
            )
            return

        if snapshot != self._snapshot:
            seeds = {
                item.node_id: (item.x, item.y)
                for item in deterministic_layout(snapshot)
            }
            try:
                self._last_delta = self._activity.observe(snapshot)
                self._delta_pulse_remaining = (
                    self._delta_pulse_seconds
                    if self._last_delta is not None and not self._last_delta.is_empty
                    else 0.0
                )
            except ValueError as exc:
                self._bindings.clear()
                self._engine.clear()
                self._snapshot = None
                self._rejected_snapshot = snapshot
                self._validation_error = str(exc)
                for current in self._mounted_fields():
                    current.setProperty(
                        "pathenaPallasLivingError",
                        self._validation_error,
                    )
                self.diagnostics_changed.emit(
                    {
                        "nodes": len(snapshot.nodes),
                        "active": 0,
                        "lens": self._lens,
                        "field_state": "ready",
                        "validation_error": self._validation_error,
                    }
                )
                return
            self._engine.reconcile(snapshot, seeds)
            selection = getattr(self._grounded_controller, "_selection", None)
            self._apply_selection_focus(selection)
            self._snapshot = snapshot
            self._rejected_snapshot = None
            self._validation_error = ""
            for current in self._mounted_fields():
                current.setProperty("pathenaPallasLivingError", "")
            self._bindings.clear()

        fields = self._live_fields()
        current_target_fps = round(1000 / max(self._timer.interval(), 1))
        for current in fields:
            current.setProperty("pathenaPallasLiving", True)
            current.setProperty("pathenaPallasLivingRenderer", "force-ca-v1")
            current.setProperty("pathenaPallasLens", self._lens)
            current.setProperty("pathenaPallasTargetFps", current_target_fps)

        visible = tuple(current for current in fields if current.isVisible())
        render_fields = (
            visible
            if visible
            else fields
            if not self._grounded_controller.window.isVisible()
            else ()
        )
        full_visible = any(
            current.property("pathenaPallasMode") == "full"
            for current in visible
        )
        target_interval = _cadence_interval_ms(
            full_visible=full_visible,
            visible=bool(visible),
            nodes=len(snapshot.nodes),
        )
        if self._timer.interval() != target_interval:
            self._timer.setInterval(target_interval)
        current_target_fps = round(1000 / max(target_interval, 1))
        for current in fields:
            current.setProperty("pathenaPallasTargetFps", current_target_fps)
        rendered_ids = {id(current) for current in render_fields}
        for stale_id in tuple(self._bindings):
            if stale_id not in rendered_ids:
                del self._bindings[stale_id]
        for current in render_fields:
            self._ensure_binding(current, snapshot)

        self._engine.step(target_interval / 1000.0)
        for binding_id, binding in tuple(self._bindings.items()):
            if not self._binding_is_current(binding):
                self._bindings.pop(binding_id, None)
                continue
            self._apply_binding(binding)
        diagnostics: dict[str, object] = {
            key: value for key, value in self._engine.diagnostics().items()
        }
        diagnostics["fps_target"] = current_target_fps
        diagnostics["rendered_fields"] = len(render_fields)
        diagnostics["cadence_mode"] = (
            "full" if full_visible else "compact" if visible else "background"
        )
        diagnostics["lens"] = self._lens
        diagnostics["field_state"] = "ready"
        delta = (
            self._last_delta
            if self._delta_pulse_remaining > 0.0
            else None
        )
        diagnostics["delta_added"] = 0 if delta is None else len(delta.added_node_ids)
        diagnostics["delta_removed"] = 0 if delta is None else len(delta.removed_node_ids)
        diagnostics["delta_updated"] = 0 if delta is None else len(delta.updated_node_ids)
        diagnostics["delta_revisions"] = (
            0 if delta is None else len(delta.revision_changed_node_ids)
        )
        diagnostics["delta_edges"] = (
            0
            if delta is None
            else len(delta.added_edges) + len(delta.removed_edges)
        )
        diagnostics["focus_changed"] = False if delta is None else delta.focus_changed
        diagnostics["validation_error"] = ""
        self.diagnostics_changed.emit(diagnostics)
        self._delta_pulse_remaining = max(
            0.0,
            self._delta_pulse_remaining - target_interval / 1000.0,
        )

    def _mounted_fields(self) -> tuple[PallasSemanticField, ...]:
        return tuple(
            field
            for field in self._grounded_controller._live_fields()  # noqa: SLF001
            if isValid(field)
        )

    def _live_fields(self) -> tuple[PallasSemanticField, ...]:
        return tuple(
            field
            for field in self._mounted_fields()
            if field.snapshot is not None
        )

    def _binding_is_current(self, binding: _FieldBinding) -> bool:
        field = binding.field
        if not isValid(field):
            return False
        snapshot = field.snapshot
        if snapshot is None or snapshot.graph_id != binding.graph_id:
            return False
        current_token = tuple(
            sorted(id(item) for item in field._items.values())  # noqa: SLF001
        )
        return current_token == binding.item_token

    def _ensure_binding(
        self,
        field: PallasSemanticField,
        snapshot: PallasGraphSnapshot,
    ) -> None:
        items = field._items  # noqa: SLF001
        token = tuple(sorted(id(item) for item in items.values()))
        current = self._bindings.get(id(field))
        if (
            current is not None
            and current.graph_id == snapshot.graph_id
            and current.item_token == token
        ):
            return
        self._bindings[id(field)] = self._bind_field(field, snapshot, token)
        field.setProperty("pathenaPallasLiving", True)
        field.setProperty("pathenaPallasLivingRenderer", "force-ca-v1")
        field.setProperty(
            "pathenaPallasTargetFps",
            round(1000 / max(self._timer.interval(), 1)),
        )
        field.setProperty("pathenaPallasLens", self._lens)

    def _bind_field(
        self,
        field: PallasSemanticField,
        snapshot: PallasGraphSnapshot,
        token: tuple[int, ...],
    ) -> _FieldBinding:
        items = field._items  # noqa: SLF001
        seeds = {
            item.node_id: (item.x, item.y)
            for item in deterministic_layout(snapshot)
        }
        available = [
            item
            for item in field.scene.items()
            if isinstance(item, QGraphicsLineItem) and item.parentItem() is None
        ]
        tagged: dict[tuple[str, str, str], list[QGraphicsLineItem]] = {}
        fallback: list[QGraphicsLineItem] = []
        for line_item in available:
            source_id = line_item.data(PALLAS_EDGE_SOURCE_DATA_KEY)
            target_id = line_item.data(PALLAS_EDGE_TARGET_DATA_KEY)
            relation = line_item.data(PALLAS_EDGE_RELATION_DATA_KEY)
            if all(isinstance(value, str) and value for value in (source_id, target_id, relation)):
                tagged.setdefault((source_id, target_id, relation), []).append(line_item)
            else:
                fallback.append(line_item)

        mapped: list[tuple[QGraphicsLineItem, str, str]] = []
        for edge in snapshot.edges:
            key = (edge.source_id, edge.target_id, edge.relation)
            tagged_matches = tagged.get(key, [])
            line = tagged_matches.pop(0) if tagged_matches else None
            if line is None:
                source = seeds.get(edge.source_id)
                target = seeds.get(edge.target_id)
                if source is None or target is None:
                    continue
                line = _nearest_seed_line(fallback, source, target)
                if line is None:
                    continue
                fallback.remove(line)
            conflict = edge.relation.casefold() in _CONFLICT_REL
            line.setPen(
                QPen(
                    _CONFLICT if conflict else _BORDER,
                    1.25 if conflict else 1.0,
                )
            )
            mapped.append((line, edge.source_id, edge.target_id))

        ages: dict[str, QGraphicsSimpleTextItem] = {}
        glyphs: dict[str, QGraphicsSimpleTextItem] = {}
        nodes = {node.node_id: node for node in snapshot.nodes}
        for node_id, node_item in items.items():
            node = nodes.get(node_id)
            if node is None:
                continue
            glyph_item = _main_glyph_child(node_item, node)
            if glyph_item is not None:
                glyphs[node_id] = glyph_item
                _set_glyph_text(glyph_item, _display_glyph(node))
            age_item = _age_child(node_item)
            if age_item is None:
                age_item = QGraphicsSimpleTextItem("·", node_item)
                age_item.setData(_AGE_MARKER_KEY, _AGE_MARKER_VALUE)
                age_item.setBrush(QBrush(_MUTED))
                font = QFont("Segoe UI Symbol")
                font.setPixelSize(8)
                age_item.setFont(font)
                _position_age_marker(node_item, age_item)
                age_item.setZValue(4.0)
            ages[node_id] = age_item
        return _FieldBinding(
            field=field,
            graph_id=snapshot.graph_id,
            item_token=token,
            edge_items=tuple(mapped),
            age_items=ages,
            nodes=nodes,
            glyph_items=glyphs,
        )

    def _apply_binding(self, binding: _FieldBinding) -> None:
        snapshot = binding.field.snapshot
        if snapshot is None:
            return
        items = binding.field._items  # noqa: SLF001
        nodes = binding.nodes
        for node_id, item in items.items():
            position = self._engine.position(node_id)
            state = self._engine.states.get(node_id)
            node = nodes.get(node_id)
            if position is None or state is None or node is None:
                continue
            item.setPos(position[0], position[1])
            age = self._engine.age_glyph(node_id)
            age_item = binding.age_items.get(node_id)
            glyph_item = binding.glyph_items.get(node_id)
            if self._lens == "age":
                _set_glyph_text(glyph_item, age)
                if age_item is not None:
                    age_item.setText(_display_glyph(node))
                item.setOpacity(0.92)
            else:
                _set_glyph_text(glyph_item, _display_glyph(node))
                if age_item is not None:
                    marker = (
                        f"{state.vitality:.0%}"
                        if self._lens == "vitality"
                        else age
                    )
                    age_item.setText(marker)
                item.setOpacity(
                    0.38 + 0.62 * state.vitality
                    if self._lens == "vitality"
                    else 1.0
                )
            if age_item is not None:
                _position_age_marker(item, age_item)
                age_item.setToolTip(
                    f"field age {state.age_seconds:.1f}s · "
                    f"vitality {state.vitality:.0%}"
                )

        for line, source_id, target_id in binding.edge_items:
            source = self._engine.position(source_id)
            target = self._engine.position(target_id)
            if source is not None and target is not None:
                line.setLine(source[0], source[1], target[0], target[1])

        if self._engine.tick % 8 == 0:
            binding.field.expand_scene_to_items()


def _nearest_seed_line(
    lines: list[QGraphicsLineItem],
    source: tuple[float, float],
    target: tuple[float, float],
) -> QGraphicsLineItem | None:
    best: tuple[float, QGraphicsLineItem] | None = None
    for item in lines:
        line = item.line()
        direct = (
            abs(line.x1() - source[0])
            + abs(line.y1() - source[1])
            + abs(line.x2() - target[0])
            + abs(line.y2() - target[1])
        )
        reverse = (
            abs(line.x2() - source[0])
            + abs(line.y2() - source[1])
            + abs(line.x1() - target[0])
            + abs(line.y1() - target[1])
        )
        score = min(direct, reverse)
        if best is None or score < best[0]:
            best = (score, item)
    return None if best is None else best[1]


def _position_age_marker(
    item: QGraphicsItem,
    marker: QGraphicsSimpleTextItem,
) -> None:
    parent_bounds = item.boundingRect()
    marker_bounds = marker.boundingRect()
    marker.setPos(
        -marker_bounds.width() / 2,
        parent_bounds.bottom() + 2,
    )


def _age_child(item: QGraphicsItem) -> QGraphicsSimpleTextItem | None:
    return next(
        (
            child
            for child in item.childItems()
            if isinstance(child, QGraphicsSimpleTextItem)
            and child.data(_AGE_MARKER_KEY) == _AGE_MARKER_VALUE
        ),
        None,
    )


def _main_glyph_child(
    item: QGraphicsItem,
    node: PallasSemanticNode,
) -> QGraphicsSimpleTextItem | None:
    candidates = {node.glyph, _display_glyph(node), *tuple("·:+oO░▒▓█")}
    return next(
        (
            child
            for child in item.childItems()
            if isinstance(child, QGraphicsSimpleTextItem)
            and child.data(_AGE_MARKER_KEY) != _AGE_MARKER_VALUE
            and child.text() in candidates
        ),
        None,
    )


def _set_glyph_text(
    item: QGraphicsSimpleTextItem | None,
    glyph: str,
) -> None:
    if item is None or item.text() == glyph:
        return
    item.setText(glyph)
    bounds = item.boundingRect()
    item.setPos(-bounds.width() / 2, -bounds.height() / 2)


def _display_glyph(node: PallasSemanticNode) -> str:
    """Preserve the canonical semantic glyph owned by the grounded node."""
    return node.glyph
