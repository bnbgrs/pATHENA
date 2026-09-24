"""Qt bridge for the provenance-safe PALLAS living simulation.

This controller wraps the existing semantic renderer. It moves already-rendered
nodes and edges and annotates runtime age/vitality; graph membership stays owned
by the grounded Core response.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, QTimer, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsSimpleTextItem,
)
from shiboken6 import isValid

from athena.desktop.pathena_pallas_field import (
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


@dataclass(slots=True)
class _FieldBinding:
    field: PallasSemanticField
    graph_id: str
    item_token: tuple[int, ...]
    edge_items: tuple[tuple[QGraphicsLineItem, str, str], ...]
    age_items: dict[str, QGraphicsSimpleTextItem]


class PallasLivingQtController(QObject):
    """Share one 30 FPS living state across compact and full PALLAS views."""

    diagnostics_changed = Signal(object)

    def __init__(
        self,
        grounded_controller: PallasGroundedFieldController,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent or grounded_controller)
        self._grounded_controller = grounded_controller
        self._engine = PallasLivingEngine()
        self._graph_id: str | None = None
        self._lens = "semantic"
        self._bindings: dict[int, _FieldBinding] = {}
        self._reduced_motion = os.environ.get(
            "PATHENA_REDUCED_MOTION", ""
        ).casefold() in {"1", "true", "yes", "on"}
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.TimerType.PreciseTimer)
        self._timer.setInterval(
            250 if self._reduced_motion else round(1000 / self._engine.config.fps)
        )
        self._timer.timeout.connect(self._tick)
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
        for binding in tuple(self._bindings.values()):
            if isValid(binding.field):
                binding.field.setProperty("pathenaPallasLens", normalized)
                self._apply_binding(binding)

    def stop(self) -> None:
        self._timer.stop()
        self._bindings.clear()
        self._engine.clear()
        self._graph_id = None

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
            self._graph_id = None
            return

        if snapshot.graph_id != self._graph_id:
            seeds = {
                item.node_id: (item.x, item.y)
                for item in deterministic_layout(snapshot)
            }
            self._engine.reconcile(snapshot, seeds)
            self._graph_id = snapshot.graph_id
            self._bindings.clear()

        fields = self._live_fields()
        live_ids = {id(current) for current in fields}
        for stale_id in tuple(self._bindings):
            if stale_id not in live_ids:
                del self._bindings[stale_id]
        for current in fields:
            self._ensure_binding(current, snapshot)

        if not self._reduced_motion:
            self._engine.step()
        for binding in tuple(self._bindings.values()):
            if isValid(binding.field):
                self._apply_binding(binding)
        diagnostics: dict[str, object] = {
            key: value for key, value in self._engine.diagnostics().items()
        }
        diagnostics["fps_target"] = 0 if self._reduced_motion else int(self._engine.config.fps)
        diagnostics["motion"] = "reduced" if self._reduced_motion else "living"
        diagnostics["lens"] = self._lens
        self.diagnostics_changed.emit(diagnostics)

    def _live_fields(self) -> tuple[PallasSemanticField, ...]:
        return tuple(
            field
            for field in self._grounded_controller._live_fields()  # noqa: SLF001
            if isValid(field) and field.snapshot is not None
        )

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
            0 if self._reduced_motion else int(self._engine.config.fps),
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
        mapped: list[tuple[QGraphicsLineItem, str, str]] = []
        for edge in snapshot.edges:
            source = seeds.get(edge.source_id)
            target = seeds.get(edge.target_id)
            if source is None or target is None:
                continue
            line = _nearest_seed_line(available, source, target)
            if line is None:
                continue
            available.remove(line)
            conflict = edge.relation.casefold() in _CONFLICT_REL
            line.setPen(
                QPen(
                    _CONFLICT if conflict else _BORDER,
                    1.25 if conflict else 1.0,
                )
            )
            mapped.append((line, edge.source_id, edge.target_id))

        ages: dict[str, QGraphicsSimpleTextItem] = {}
        nodes = {node.node_id: node for node in snapshot.nodes}
        for node_id, node_item in items.items():
            node = nodes.get(node_id)
            if node is None:
                continue
            _set_main_glyph(node_item, node, _display_glyph(node))
            age_item = _age_child(node_item)
            if age_item is None:
                age_item = QGraphicsSimpleTextItem("·", node_item)
                age_item.setData(_AGE_MARKER_KEY, _AGE_MARKER_VALUE)
                age_item.setBrush(QBrush(_MUTED))
                font = QFont("Segoe UI Symbol")
                font.setPixelSize(8)
                age_item.setFont(font)
                bounds = node_item.boundingRect()
                age_item.setPos(bounds.right() - 1, bounds.bottom() - 8)
                age_item.setZValue(4.0)
            ages[node_id] = age_item
        return _FieldBinding(
            field,
            snapshot.graph_id,
            token,
            tuple(mapped),
            ages,
        )

    def _apply_binding(self, binding: _FieldBinding) -> None:
        snapshot = binding.field.snapshot
        if snapshot is None:
            return
        items = binding.field._items  # noqa: SLF001
        nodes = {node.node_id: node for node in snapshot.nodes}
        for node_id, item in items.items():
            position = self._engine.position(node_id)
            state = self._engine.states.get(node_id)
            node = nodes.get(node_id)
            if position is None or state is None or node is None:
                continue
            item.setPos(position[0], position[1])
            age = self._engine.age_glyph(node_id)
            age_item = binding.age_items.get(node_id)
            if self._lens == "age":
                _set_main_glyph(item, node, age)
                if age_item is not None:
                    age_item.setText(_display_glyph(node))
                item.setOpacity(0.92)
            else:
                _set_main_glyph(item, node, _display_glyph(node))
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
            item.setScale(
                0.86 + 0.18 * state.vitality
                if self._lens == "vitality"
                else 1.0
            )
            if age_item is not None:
                age_item.setToolTip(
                    f"runtime age {state.age_seconds:.1f}s · "
                    f"vitality {state.vitality:.0%}"
                )

        for line, source_id, target_id in binding.edge_items:
            source = self._engine.position(source_id)
            target = self._engine.position(target_id)
            if source is not None and target is not None:
                line.setLine(source[0], source[1], target[0], target[1])


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


def _set_main_glyph(
    item: QGraphicsItem,
    node: PallasSemanticNode,
    glyph: str,
) -> None:
    candidates = {node.glyph, _display_glyph(node), *tuple("·:+oO░▒▓█")}
    for child in item.childItems():
        if not isinstance(child, QGraphicsSimpleTextItem):
            continue
        if (
            child.data(_AGE_MARKER_KEY) == _AGE_MARKER_VALUE
            or child.text() not in candidates
        ):
            continue
        child.setText(glyph)
        bounds = child.boundingRect()
        child.setPos(-bounds.width() / 2, -bounds.height() / 2)
        return


def _display_glyph(node: PallasSemanticNode) -> str:
    """Preserve the canonical semantic glyph owned by the grounded node."""
    return node.glyph
