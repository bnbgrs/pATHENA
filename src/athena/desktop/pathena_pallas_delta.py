"""Deterministic PALLAS snapshot comparison helpers."""

from __future__ import annotations

from dataclasses import dataclass

from athena.desktop.pathena_pallas_semantic import PallasGraphSnapshot


@dataclass(frozen=True, slots=True)
class PallasSnapshotDelta:
    before_graph_id: str
    after_graph_id: str
    changed_node_ids: tuple[str, ...]


def compare_pallas_snapshots(before: PallasGraphSnapshot, after: PallasGraphSnapshot) -> PallasSnapshotDelta:
    before_nodes = {node.node_id: node for node in before.nodes}
    after_nodes = {node.node_id: node for node in after.nodes}
    changed = tuple(sorted(node_id for node_id in set(before_nodes) | set(after_nodes) if before_nodes.get(node_id) != after_nodes.get(node_id)))
    return PallasSnapshotDelta(before.graph_id, after.graph_id, changed)
