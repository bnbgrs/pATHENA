from __future__ import annotations

import math

from athena.desktop.pathena_pallas_living import (
    PallasLivingConfig,
    PallasLivingEngine,
    age_glyph,
    semantic_similarity,
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
    kind: PallasNodeKind = PallasNodeKind.KNOWLEDGE,
    title: str = "Node",
    summary: str = "grounded semantic context",
    cited: bool = True,
) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=node_id,
        kind=kind,
        entity_type="canonical_claim",
        entity_id=node_id,
        revision_id=f"revision-{node_id}",
        title=title,
        summary=summary,
        epistemic_status="supported",
        cited=cited,
    )


def _snapshot(
    nodes: tuple[PallasSemanticNode, ...],
    edges: tuple[PallasSemanticEdge, ...] = (),
    *,
    focus_id: str | None = None,
) -> PallasGraphSnapshot:
    return PallasGraphSnapshot(
        graph_id="test-graph",
        nodes=nodes,
        edges=edges,
        focus_id=focus_id,
        status="ready",
        status_detail="test graph",
    )


def _distance(engine: PallasLivingEngine, left: str, right: str) -> float:
    left_pos = engine.position(left)
    right_pos = engine.position(right)
    assert left_pos is not None and right_pos is not None
    return math.dist(left_pos, right_pos)


def test_living_engine_is_deterministic_for_fixed_steps() -> None:
    nodes = (
        _node("focus", kind=PallasNodeKind.FOCUS),
        _node("a", title="Solar storage", summary="battery solar storage"),
        _node("b", title="Solar battery", summary="solar battery evidence"),
    )
    graph = _snapshot(
        nodes,
        (
            PallasSemanticEdge("focus", "a", "cites"),
            PallasSemanticEdge("focus", "b", "cites"),
        ),
        focus_id="focus",
    )
    seeds = {"focus": (0.0, 0.0), "a": (-120.0, 20.0), "b": (120.0, 20.0)}
    first = PallasLivingEngine()
    second = PallasLivingEngine()
    first.reconcile(graph, seeds)
    second.reconcile(graph, seeds)

    for _ in range(90):
        first.step()
        second.step()

    assert first.tick == second.tick == 90
    for node in nodes:
        assert first.position(node.node_id) == second.position(node.node_id)
        left = first.states[node.node_id]
        right = second.states[node.node_id]
        assert left.vitality == right.vitality
        assert left.age_seconds == right.age_seconds


def test_semantic_similarity_attracts_without_adding_graph_edges() -> None:
    left = _node("a", title="solar battery", summary="home solar battery storage")
    right = _node("b", title="battery storage", summary="solar storage battery system")
    graph = _snapshot((left, right))
    config = PallasLivingConfig(
        semantic_threshold=0.1,
        semantic_attraction=30.0,
        global_repulsion=0.0,
        edge_spring=0.0,
        center_pull=0.0,
        focus_pull=0.0,
        temporal_drift=0.0,
    )
    engine = PallasLivingEngine(config)
    engine.reconcile(graph, {"a": (-140.0, 0.0), "b": (140.0, 0.0)})
    before = _distance(engine, "a", "b")
    edges_before = graph.edges

    for _ in range(60):
        engine.step()

    assert semantic_similarity(left, right) > config.semantic_threshold
    assert _distance(engine, "a", "b") < before
    assert graph.edges == edges_before == ()


def test_explicit_contradiction_edge_repels_more_strongly() -> None:
    left = _node("left")
    right = _node("right")
    config = PallasLivingConfig(
        semantic_attraction=0.0,
        semantic_threshold=1.0,
        global_repulsion=400.0,
        contradiction_repulsion=8000.0,
        edge_spring=0.0,
        center_pull=0.0,
        focus_pull=0.0,
        temporal_drift=0.0,
    )
    ordinary = PallasLivingEngine(config)
    conflict = PallasLivingEngine(config)
    seeds = {"left": (-40.0, 0.0), "right": (40.0, 0.0)}
    ordinary.reconcile(_snapshot((left, right)), seeds)
    conflict.reconcile(
        _snapshot((left, right), (PallasSemanticEdge("left", "right", "contradicts"),)),
        seeds,
    )

    for _ in range(30):
        ordinary.step()
        conflict.step()

    assert _distance(conflict, "left", "right") > _distance(ordinary, "left", "right")


def test_runtime_age_uses_documented_progression() -> None:
    glyphs = [age_glyph(age, 80.0) for age in (0, 10, 20, 30, 40, 50, 60, 70, 80)]
    assert glyphs == ["·", ":", "+", "o", "O", "░", "▒", "▓", "█"]


def test_reconcile_preserves_age_and_reobservation_survival_pulse() -> None:
    node = _node("a")
    engine = PallasLivingEngine()
    engine.reconcile(_snapshot((node,)), {"a": (10.0, 20.0)})
    for _ in range(10):
        engine.step()
    age_before = engine.states["a"].age_seconds
    engine.states["a"].vitality = 0.4

    second = _node("b")
    engine.reconcile(_snapshot((node, second)), {"b": (30.0, 40.0)})

    assert engine.states["a"].age_seconds == age_before
    assert abs(engine.states["a"].vitality - 0.48) < 1e-9
    assert engine.position("b") == (30.0, 40.0)


def test_cellular_vitality_diffuses_only_across_real_edges() -> None:
    left = _node("left", cited=True)
    right = _node("right", cited=False)
    isolated = _node("isolated", cited=False)
    graph = _snapshot(
        (left, right, isolated),
        (PallasSemanticEdge("left", "right", "cites"),),
    )
    engine = PallasLivingEngine(
        PallasLivingConfig(
            semantic_attraction=0.0,
            global_repulsion=0.0,
            edge_spring=0.0,
            center_pull=0.0,
            focus_pull=0.0,
            temporal_drift=0.0,
            vitality_diffusion=1.5,
        )
    )
    engine.reconcile(graph, {"left": (-20, 0), "right": (20, 0), "isolated": (0, 80)})
    engine.states["left"].vitality = 1.0
    engine.states["right"].vitality = 0.1
    engine.states["isolated"].vitality = 0.1

    engine.step(0.1)

    assert engine.states["right"].vitality > engine.states["isolated"].vitality
    assert graph.edges == (PallasSemanticEdge("left", "right", "cites"),)
