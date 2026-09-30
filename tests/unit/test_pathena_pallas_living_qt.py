from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QWidget
from shiboken6 import delete, isValid

from athena.desktop.pathena_pallas_field import PallasGroundedFieldController
from athena.desktop.pathena_pallas_living_qt import (
    PallasLivingQtController,
    _cadence_interval_ms,
)
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


def _updated_snapshot_same_graph_id() -> PallasGraphSnapshot:
    focus = _node("focus", PallasNodeKind.FOCUS)
    claim = _node("claim", PallasNodeKind.CLAIM)
    knowledge = _node("knowledge", PallasNodeKind.KNOWLEDGE)
    return PallasGraphSnapshot(
        graph_id="graph:living-qt-test",
        nodes=(focus, claim, knowledge),
        edges=(
            PallasSemanticEdge(focus.node_id, claim.node_id, "cites"),
            PallasSemanticEdge(focus.node_id, knowledge.node_id, "includes_context"),
        ),
        focus_id=focus.node_id,
        status="ready",
        status_detail="Three real grounded semantic nodes.",
    )


def test_qt_bridge_reconciles_snapshot_changes_even_when_graph_id_is_stable(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    try:
        living._tick()  # noqa: SLF001
        original = living.engine.snapshot
        assert original is not None
        assert set(living.engine.states) == {"focus", "claim"}

        updated = _updated_snapshot_same_graph_id()
        assert updated.graph_id == original.graph_id
        grounded.apply_snapshot(updated)
        living._tick()  # noqa: SLF001
        qapp.processEvents()

        assert living.engine.snapshot == updated
        assert set(living.engine.states) == {"focus", "claim", "knowledge"}
        assert grounded.field.snapshot == updated
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_publishes_structural_activity_delta(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    diagnostics: list[object] = []
    living.diagnostics_changed.connect(diagnostics.append)
    try:
        living._tick()  # noqa: SLF001
        first = diagnostics[-1]
        assert isinstance(first, dict)
        assert first["delta_added"] == 0

        grounded.apply_snapshot(_updated_snapshot_same_graph_id())
        living._tick()  # noqa: SLF001
        qapp.processEvents()

        latest = diagnostics[-1]
        assert isinstance(latest, dict)
        assert latest["delta_added"] == 1
        assert latest["delta_removed"] == 0
        assert latest["delta_updated"] == 0
        assert latest["delta_revisions"] == 0
        assert latest["delta_edges"] == 1
        assert latest["focus_changed"] is False

        updated = _updated_snapshot_same_graph_id()
        focus, claim, knowledge = updated.nodes
        revised_claim = PallasSemanticNode(
            node_id=claim.node_id,
            kind=claim.kind,
            entity_type=claim.entity_type,
            entity_id=claim.entity_id,
            revision_id="revision-claim-2",
            title=claim.title,
            summary=claim.summary,
            epistemic_status=claim.epistemic_status,
            cited=claim.cited,
        )
        revised = PallasGraphSnapshot(
            graph_id=updated.graph_id,
            nodes=(focus, revised_claim, knowledge),
            edges=updated.edges,
            focus_id=updated.focus_id,
            status=updated.status,
            status_detail=updated.status_detail,
        )
        grounded.apply_snapshot(revised)
        living._tick()  # noqa: SLF001
        qapp.processEvents()

        revision_delta = diagnostics[-1]
        assert isinstance(revision_delta, dict)
        assert revision_delta["delta_added"] == 0
        assert revision_delta["delta_removed"] == 0
        assert revision_delta["delta_updated"] == 1
        assert revision_delta["delta_revisions"] == 1
        assert revision_delta["delta_edges"] == 0

        living._delta_pulse_remaining = 0.0  # noqa: SLF001
        living._tick()  # noqa: SLF001
        expired = diagnostics[-1]
        assert isinstance(expired, dict)
        assert expired["delta_added"] == 0
        assert expired["delta_removed"] == 0
        assert expired["delta_updated"] == 0
        assert expired["delta_revisions"] == 0
        assert expired["delta_edges"] == 0
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_tracks_real_selection_as_visual_focus(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    try:
        living._tick()  # noqa: SLF001
        snapshot = living.engine.snapshot
        assert snapshot is not None

        assert grounded.field.focus_node("claim")
        qapp.processEvents()

        assert living.engine.visual_focus_id == "claim"
        assert living.engine.snapshot is snapshot
        assert snapshot.focus_id == "focus"

        grounded.field.clear_selection()
        qapp.processEvents()
        assert living.engine.visual_focus_id is None
    finally:
        living.stop()
        delete(window)


def test_qt_bridge_rejects_invalid_snapshot_without_crashing_timer_path(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    workspace = grounded.create_workspace(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    diagnostics: list[object] = []
    living.diagnostics_changed.connect(diagnostics.append)
    try:
        living._tick()  # noqa: SLF001
        assert living.engine.snapshot is not None

        focus = _node("focus", PallasNodeKind.FOCUS)
        claim = _node("claim", PallasNodeKind.CLAIM)
        invalid = PallasGraphSnapshot(
            graph_id="graph:living-qt-invalid",
            nodes=(focus, claim),
            edges=(PallasSemanticEdge("focus", "missing", "cites"),),
            focus_id="focus",
            status="ready",
            status_detail="Invalid graph for regression coverage.",
        )
        grounded.apply_snapshot(invalid)
        living._tick()  # noqa: SLF001
        qapp.processEvents()

        latest = diagnostics[-1]
        assert isinstance(latest, dict)
        assert "missing node" in str(latest["validation_error"])
        assert living.engine.snapshot is None
        assert "missing node" in str(
            grounded.field.property("pathenaPallasLivingError")
        )
        assert "missing node" in str(
            workspace.field.property("pathenaPallasLivingError")
        )

        empty = PallasGraphSnapshot(
            graph_id="graph:living-qt-empty",
            nodes=(),
            edges=(),
            focus_id=None,
            status="empty",
            status_detail="No current grounded context.",
        )
        grounded.apply_snapshot(empty)
        living._tick()  # noqa: SLF001

        assert grounded.field.property("pathenaPallasLivingError") == ""
        assert workspace.field.property("pathenaPallasLivingError") == ""
    finally:
        living.stop()
        delete(window)


def test_vitality_marker_geometry_tracks_dynamic_text_width(
    qapp: QApplication,
) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    try:
        living._tick()  # noqa: SLF001
        binding = living._bindings[id(grounded.field)]  # noqa: SLF001
        marker = binding.age_items["claim"]
        item = grounded.field._items["claim"]  # noqa: SLF001

        living.set_lens("vitality")
        qapp.processEvents()

        assert marker.text().endswith("%")
        assert marker.pos().x() == pytest.approx(
            -marker.boundingRect().width() / 2
        )
        assert marker.pos().y() == pytest.approx(
            item.boundingRect().bottom() + 2
        )

        living.set_lens("age")
        qapp.processEvents()

        assert marker.text() == "◆"
        assert marker.pos().x() == pytest.approx(
            -marker.boundingRect().width() / 2
        )
        assert marker.pos().y() == pytest.approx(
            item.boundingRect().bottom() + 2
        )
        assert "field age" in marker.toolTip()
    finally:
        living.stop()
        delete(window)

def test_cadence_scales_down_without_changing_graph_facts() -> None:
    assert _cadence_interval_ms(full_visible=True, visible=True, nodes=20) == 33
    assert _cadence_interval_ms(full_visible=True, visible=True, nodes=120) == 42
    assert _cadence_interval_ms(full_visible=True, visible=True, nodes=240) == 56
    assert _cadence_interval_ms(full_visible=True, visible=True, nodes=500) == 83
    assert _cadence_interval_ms(full_visible=False, visible=True, nodes=20) == 67
    assert _cadence_interval_ms(full_visible=False, visible=True, nodes=220) == 100
    assert _cadence_interval_ms(full_visible=False, visible=True, nodes=500) == 167
    assert _cadence_interval_ms(full_visible=False, visible=False, nodes=500) == 250


def test_stop_disconnects_selection_focus_lifecycle(qapp: QApplication) -> None:
    window = QWidget()
    grounded = _grounded_controller(window)
    living = PallasLivingQtController(grounded)
    living._timer.stop()  # noqa: SLF001
    try:
        living._tick()  # noqa: SLF001
        assert grounded.field.focus_node("claim")
        qapp.processEvents()
        assert living.engine.visual_focus_id == "claim"

        living.stop()
        assert living._selection_connected is False  # noqa: SLF001
        assert living.engine.visual_focus_id is None

        grounded.field.clear_selection()
        grounded.field.focus_node("focus")
        qapp.processEvents()

        assert living.engine.visual_focus_id is None
        living.stop()
    finally:
        delete(window)

