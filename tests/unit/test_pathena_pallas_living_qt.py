from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import delete, isValid

from athena.desktop.pathena_pallas_field import PallasGroundedFieldController
from athena.desktop.pathena_pallas_living_qt import PallasLivingQtController
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticEdge,
    PallasSemanticNode,
)


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


def _node(node_id: str, kind: PallasNodeKind) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=node_id,
        kind=kind,
        entity_type="canonical_claim",
        entity_id=node_id,
        revision_id=f"revision-{node_id}",
        title=node_id.title(),
        summary=f"Grounded semantic context for {node_id}",
        epistemic_status="supported",
        cited=True,
    )


def _snapshot() -> PallasGraphSnapshot:
    focus = _node("focus", PallasNodeKind.FOCUS)
    claim = _node("claim", PallasNodeKind.CLAIM)
    edge = PallasSemanticEdge(focus.node_id, claim.node_id, "cites")
    return PallasGraphSnapshot(
        graph_id="graph:living-qt-test",
        nodes=(focus, claim),
        edges=(edge,),
        focus_id=focus.node_id,
        status="ready",
        status_detail="Two real grounded semantic nodes.",
    )


def _grounded_controller(window: QWidget) -> PallasGroundedFieldController:
    placeholder = QWidget(window)
    placeholder.setObjectName("pallasVisualPlaceholder")
    controller = PallasGroundedFieldController(window, None)
    controller.apply_snapshot(_snapshot())
    return controller


def test_qt_bridge_updates_presentation_without_mutating_semantic_snapshot(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    snapshot = grounded.field.snapshot
    assert snapshot is not None
    original_nodes = snapshot.nodes
    original_edges = snapshot.edges

    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001 - deterministic lifecycle regression
    try:
        living._tick()  # noqa: SLF001 - exercise one exact presentation frame
        qapp.processEvents()

        assert living.engine.tick == 1
        assert grounded.field.snapshot is snapshot
        assert snapshot.nodes == original_nodes
        assert snapshot.edges == original_edges
        assert grounded.field.property("pathenaPallasLiving") is True
        assert grounded.field.property("pathenaPallasLivingRenderer") == "force-ca-v1"
        assert grounded.field.property("pathenaPallasLens") == "semantic"

        living.set_lens("age")
        assert living.lens == "age"
        assert grounded.field.property("pathenaPallasLens") == "age"
        assert grounded.field.snapshot is snapshot
        assert snapshot.nodes == original_nodes
        assert snapshot.edges == original_edges

        living.set_lens("vitality")
        assert living.lens == "vitality"
        assert grounded.field.property("pathenaPallasLens") == "vitality"
        assert snapshot.nodes == original_nodes
        assert snapshot.edges == original_edges
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_moves_real_edge_with_living_node_positions(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001 - deterministic frame ownership
    try:
        living._tick()  # noqa: SLF001 - bind and advance one living frame
        qapp.processEvents()

        binding = living._bindings[id(grounded.field)]  # noqa: SLF001
        assert len(binding.edge_items) == 1
        line_item, source_id, target_id = binding.edge_items[0]
        source = living.engine.position(source_id)
        target = living.engine.position(target_id)
        assert source is not None
        assert target is not None

        line = line_item.line()
        assert line.x1() == pytest.approx(source[0])
        assert line.y1() == pytest.approx(source[1])
        assert line.x2() == pytest.approx(target[0])
        assert line.y2() == pytest.approx(target[1])

        source_item = grounded.field._items[source_id]  # noqa: SLF001
        target_item = grounded.field._items[target_id]  # noqa: SLF001
        assert source_item.x() == pytest.approx(source[0])
        assert source_item.y() == pytest.approx(source[1])
        assert target_item.x() == pytest.approx(target[0])
        assert target_item.y() == pytest.approx(target[1])
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_reduced_motion_keeps_semantic_field_still(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PATHENA_REDUCED_MOTION", "1")
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001 - deterministic reduced-motion regression
    try:
        living._tick()  # noqa: SLF001 - reconcile one stable frame
        qapp.processEvents()

        assert living._reduced_motion is True  # noqa: SLF001
        assert living.engine.tick == 0
        assert grounded.field.property("pathenaPallasLiving") is True
        assert grounded.field.snapshot is not None
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_rejects_unknown_lens(qapp: QApplication) -> None:
    del qapp
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    try:
        with pytest.raises(ValueError, match="Unsupported PALLAS lens"):
            living.set_lens("fabricated-truth")
        assert living.lens == "semantic"
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_stops_and_clears_state_when_primary_field_is_disposed(
    qapp: QApplication,
) -> None:
    del qapp
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    living._tick()  # noqa: SLF001
    assert living.engine.snapshot is not None
    assert living.engine.tick == 1

    living._timer.start()  # noqa: SLF001
    assert living._timer.isActive()  # noqa: SLF001
    delete(grounded.field)
    assert not isValid(grounded.field)

    living._tick()  # noqa: SLF001

    assert not living._timer.isActive()  # noqa: SLF001
    assert living.engine.snapshot is None
    assert living.engine.states == {}
    delete(window)
