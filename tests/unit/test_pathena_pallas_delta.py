from __future__ import annotations

import pytest

from athena.desktop.pathena_pallas_delta import (
    PallasActivityTracker,
    compare_pallas_snapshots,
)
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticEdge,
    PallasSemanticNode,
)


def _node(
    node_id: str,
    *,
    revision_id: str | None = None,
    entity_id: str | None = None,
    cited: bool = True,
    summary: str = "grounded fact",
) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=node_id,
        kind=PallasNodeKind.KNOWLEDGE,
        entity_type="canonical_claim",
        entity_id=entity_id or node_id,
        revision_id=revision_id,
        title=f"Node {node_id}",
        summary=summary,
        epistemic_status="supported",
        cited=cited,
        confidence=0.9,
    )


def _snapshot(
    graph_id: str,
    nodes: tuple[PallasSemanticNode, ...],
    edges: tuple[PallasSemanticEdge, ...] = (),
    *,
    focus_id: str | None = None,
    status: str = "ready",
    detail: str = "ready",
) -> PallasGraphSnapshot:
    return PallasGraphSnapshot(
        graph_id=graph_id,
        nodes=nodes,
        edges=edges,
        focus_id=focus_id,
        status=status,
        status_detail=detail,
    )


def test_delta_reports_added_removed_updated_and_edge_changes() -> None:
    before = _snapshot(
        "before",
        (_node("a", revision_id="r1"), _node("b", revision_id="r1")),
        (PallasSemanticEdge("a", "b", "supports"),),
        focus_id="a",
    )
    after = _snapshot(
        "after",
        (
            _node("a", revision_id="r2", summary="revised fact"),
            _node("c", revision_id="r1"),
        ),
        (PallasSemanticEdge("a", "c", "supports"),),
        focus_id="c",
    )

    delta = compare_pallas_snapshots(before, after)

    assert delta.added_node_ids == ("c",)
    assert delta.removed_node_ids == ("b",)
    assert delta.updated_node_ids == ("a",)
    assert delta.revision_changed_node_ids == ("a",)
    assert delta.changed_node_ids == ("a", "b", "c")
    assert delta.removed_edges == (("a", "b", "supports"),)
    assert delta.added_edges == (("a", "c", "supports"),)
    assert delta.focus_changed is True
    assert delta.is_empty is False


def test_delta_is_empty_for_semantically_identical_snapshot() -> None:
    node = _node("a", revision_id="r1")
    before = _snapshot("run-1", (node,))
    after = _snapshot("run-2", (node,))

    delta = compare_pallas_snapshots(before, after)

    assert delta.before_graph_id == "run-1"
    assert delta.after_graph_id == "run-2"
    assert delta.changed_node_ids == ()
    assert delta.is_empty is True


def test_delta_tracks_status_detail_without_inventing_node_change() -> None:
    node = _node("a")
    before = _snapshot("before", (node,), detail="one grounded item")
    after = _snapshot("after", (node,), detail="one grounded item, refreshed")

    delta = compare_pallas_snapshots(before, after)

    assert delta.changed_node_ids == ()
    assert delta.status_changed is True
    assert delta.is_empty is False


def test_delta_rejects_stable_node_id_rebound_to_different_entity() -> None:
    before = _snapshot("before", (_node("a", entity_id="entity-1"),))
    after = _snapshot("after", (_node("a", entity_id="entity-2"),))

    with pytest.raises(ValueError, match="node identity changed"):
        compare_pallas_snapshots(before, after)


def test_delta_rejects_duplicate_nodes_and_edges() -> None:
    node = _node("a")
    duplicate_nodes = _snapshot("bad", (node, node))
    clean = _snapshot("clean", (node,))
    with pytest.raises(ValueError, match="duplicate PALLAS node"):
        compare_pallas_snapshots(duplicate_nodes, clean)

    edge = PallasSemanticEdge("a", "a", "references")
    duplicate_edges = _snapshot("bad-edges", (node,), (edge, edge))
    with pytest.raises(ValueError, match="duplicate PALLAS edge"):
        compare_pallas_snapshots(duplicate_edges, clean)


def test_delta_rejects_dangling_edge_and_focus_references() -> None:
    node = _node("a")
    clean = _snapshot("clean", (node,))
    dangling_edge = _snapshot(
        "dangling-edge",
        (node,),
        (PallasSemanticEdge("a", "missing", "supports"),),
    )
    with pytest.raises(ValueError, match="edge references a missing node"):
        compare_pallas_snapshots(clean, dangling_edge)

    dangling_focus = _snapshot("dangling-focus", (node,), focus_id="missing")
    with pytest.raises(ValueError, match="focus ID references a missing node"):
        compare_pallas_snapshots(clean, dangling_focus)


def test_activity_tracker_uses_first_snapshot_as_baseline_and_can_reset() -> None:
    tracker = PallasActivityTracker()
    first = _snapshot("first", (_node("a"),))
    second = _snapshot("second", (_node("a"), _node("b")))

    assert tracker.has_baseline is False
    assert tracker.observe(first) is None
    assert tracker.has_baseline is True

    delta = tracker.observe(second)
    assert delta is not None
    assert delta.added_node_ids == ("b",)

    tracker.reset()
    assert tracker.has_baseline is False
    assert tracker.observe(second) is None


def test_activity_tracker_rejects_invalid_initial_baseline() -> None:
    tracker = PallasActivityTracker()
    invalid = _snapshot("invalid", (_node("a"),), focus_id="missing")

    with pytest.raises(ValueError, match="focus ID references a missing node"):
        tracker.observe(invalid)

    assert tracker.has_baseline is False


def test_activity_tracker_keeps_last_valid_baseline_after_rejected_update() -> None:
    tracker = PallasActivityTracker()
    first = _snapshot("first", (_node("a", entity_id="entity-1"),))
    invalid = _snapshot("invalid", (_node("a", entity_id="entity-2"),))
    later = _snapshot(
        "later",
        (
            _node("a", entity_id="entity-1"),
            _node("b", entity_id="entity-3"),
        ),
    )

    assert tracker.observe(first) is None
    with pytest.raises(ValueError, match="node identity changed"):
        tracker.observe(invalid)

    delta = tracker.observe(later)
    assert delta is not None
    assert delta.before_graph_id == "first"
    assert delta.after_graph_id == "later"
    assert delta.added_node_ids == ("b",)
