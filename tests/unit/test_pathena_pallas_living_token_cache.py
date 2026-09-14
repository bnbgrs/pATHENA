from __future__ import annotations

import athena.desktop.pathena_pallas_living as living_module
from athena.desktop.pathena_pallas_living import PallasLivingEngine
from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticNode,
)


def _node(node_id: str, title: str) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=node_id,
        kind=PallasNodeKind.KNOWLEDGE,
        entity_type="knowledge_unit",
        entity_id=node_id,
        revision_id=f"revision-{node_id}",
        title=title,
        summary="semantic cache regression context",
        epistemic_status="accepted",
        cited=True,
    )


def _snapshot(left: PallasSemanticNode, right: PallasSemanticNode) -> PallasGraphSnapshot:
    return PallasGraphSnapshot(
        graph_id="token-cache-graph",
        nodes=(left, right),
        edges=(),
        focus_id=left.node_id,
        status="ready",
        status_detail="semantic token cache regression",
    )


def test_living_ticks_reuse_tokens_built_during_reconcile(monkeypatch) -> None:
    original = living_module._tokens  # noqa: SLF001
    calls: list[str] = []

    def counted(node: PallasSemanticNode) -> frozenset[str]:
        calls.append(node.node_id)
        return original(node)

    monkeypatch.setattr(living_module, "_tokens", counted)
    left = _node("left", "solar battery")
    right = _node("right", "battery storage")
    engine = PallasLivingEngine()

    engine.reconcile(
        _snapshot(left, right),
        {"left": (-80.0, 0.0), "right": (80.0, 0.0)},
    )
    assert calls == ["left", "right"]

    calls.clear()
    for _ in range(30):
        engine.step()

    assert calls == []


def test_reconcile_refreshes_cached_tokens_after_snapshot_change(monkeypatch) -> None:
    original = living_module._tokens  # noqa: SLF001
    calls: list[str] = []

    def counted(node: PallasSemanticNode) -> frozenset[str]:
        calls.append(node.node_id)
        return original(node)

    monkeypatch.setattr(living_module, "_tokens", counted)
    engine = PallasLivingEngine()
    left = _node("left", "solar battery")
    right = _node("right", "battery storage")
    engine.reconcile(_snapshot(left, right))

    calls.clear()
    refreshed_right = _node("right", "wind storage")
    engine.reconcile(_snapshot(left, refreshed_right))

    assert calls == ["left", "right"]
