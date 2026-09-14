"""Deterministic change detection between immutable PALLAS graph snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasSemanticEdge,
    PallasSemanticNode,
)

EdgeKey = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class PallasSnapshotDelta:
    """Exact structural differences between two PALLAS snapshots."""

    before_graph_id: str
    after_graph_id: str
    added_node_ids: tuple[str, ...]
    removed_node_ids: tuple[str, ...]
    updated_node_ids: tuple[str, ...]
    revision_changed_node_ids: tuple[str, ...]
    added_edges: tuple[EdgeKey, ...]
    removed_edges: tuple[EdgeKey, ...]
    before_focus_id: str | None
    after_focus_id: str | None
    before_status: str
    after_status: str
    before_status_detail: str
    after_status_detail: str

    @property
    def changed_node_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    *self.added_node_ids,
                    *self.removed_node_ids,
                    *self.updated_node_ids,
                }
            )
        )

    @property
    def focus_changed(self) -> bool:
        return self.before_focus_id != self.after_focus_id

    @property
    def status_changed(self) -> bool:
        return (
            self.before_status != self.after_status
            or self.before_status_detail != self.after_status_detail
        )

    @property
    def is_empty(self) -> bool:
        return not (
            self.changed_node_ids
            or self.added_edges
            or self.removed_edges
            or self.focus_changed
            or self.status_changed
        )


class PallasActivityTracker:
    """Keep one valid baseline and emit a delta for each later observation."""

    def __init__(self) -> None:
        self._previous: PallasGraphSnapshot | None = None
        self._identity_history: dict[str, tuple[str, str]] = {}

    @property
    def has_baseline(self) -> bool:
        return self._previous is not None

    def reset(self) -> None:
        self._previous = None
        self._identity_history.clear()

    def observe(self, snapshot: PallasGraphSnapshot) -> PallasSnapshotDelta | None:
        snapshot_nodes, _snapshot_edges = _validate_snapshot(snapshot)
        for node_id, node in snapshot_nodes.items():
            identity = (node.entity_type, node.entity_id)
            previous_identity = self._identity_history.get(node_id)
            if previous_identity is not None and previous_identity != identity:
                raise ValueError(f"PALLAS node identity changed for {node_id!r}")

        previous = self._previous
        delta = (
            None
            if previous is None
            else compare_pallas_snapshots(previous, snapshot)
        )

        # Identity history advances only after the complete observation is valid.
        # A removed node intentionally remains registered for this tracker epoch.
        for node_id, node in snapshot_nodes.items():
            self._identity_history.setdefault(
                node_id,
                (node.entity_type, node.entity_id),
            )
        self._previous = snapshot
        return delta


def compare_pallas_snapshots(
    before: PallasGraphSnapshot,
    after: PallasGraphSnapshot,
) -> PallasSnapshotDelta:
    """Compare exact snapshot facts without creating new semantic relationships."""
    before_nodes, before_edges = _validate_snapshot(before)
    after_nodes, after_edges = _validate_snapshot(after)
    before_ids = set(before_nodes)
    after_ids = set(after_nodes)

    added = tuple(sorted(after_ids - before_ids))
    removed = tuple(sorted(before_ids - after_ids))
    updated: list[str] = []
    revision_changed: list[str] = []

    for node_id in sorted(before_ids & after_ids):
        old = before_nodes[node_id]
        new = after_nodes[node_id]
        _require_same_entity(old, new)
        if old != new:
            updated.append(node_id)
        if old.revision_id != new.revision_id:
            revision_changed.append(node_id)

    return PallasSnapshotDelta(
        before_graph_id=before.graph_id,
        after_graph_id=after.graph_id,
        added_node_ids=added,
        removed_node_ids=removed,
        updated_node_ids=tuple(updated),
        revision_changed_node_ids=tuple(revision_changed),
        added_edges=tuple(sorted(after_edges - before_edges)),
        removed_edges=tuple(sorted(before_edges - after_edges)),
        before_focus_id=before.focus_id,
        after_focus_id=after.focus_id,
        before_status=before.status,
        after_status=after.status,
        before_status_detail=before.status_detail,
        after_status_detail=after.status_detail,
    )


def _validate_snapshot(
    snapshot: PallasGraphSnapshot,
) -> tuple[dict[str, PallasSemanticNode], set[EdgeKey]]:
    nodes = _node_index(snapshot)
    node_ids = set(nodes)
    edges = _edge_set(snapshot)
    for source_id, target_id, _relation in edges:
        if source_id not in node_ids or target_id not in node_ids:
            raise ValueError("PALLAS edge references a missing node")
    if snapshot.focus_id is not None and snapshot.focus_id not in node_ids:
        raise ValueError("PALLAS focus ID references a missing node")
    return nodes, edges


def _node_index(snapshot: PallasGraphSnapshot) -> dict[str, PallasSemanticNode]:
    result: dict[str, PallasSemanticNode] = {}
    for node in snapshot.nodes:
        if node.node_id in result:
            raise ValueError(f"duplicate PALLAS node ID {node.node_id!r}")
        result[node.node_id] = node
    return result


def _edge_set(snapshot: PallasGraphSnapshot) -> set[EdgeKey]:
    result: set[EdgeKey] = set()
    for edge in snapshot.edges:
        key = _edge_key(edge)
        if key in result:
            raise ValueError(f"duplicate PALLAS edge {key!r}")
        result.add(key)
    return result


def _edge_key(edge: PallasSemanticEdge) -> EdgeKey:
    return edge.source_id, edge.target_id, edge.relation


def _require_same_entity(
    before: PallasSemanticNode,
    after: PallasSemanticNode,
) -> None:
    if before.entity_type == after.entity_type and before.entity_id == after.entity_id:
        return
    raise ValueError(f"PALLAS node identity changed for {before.node_id!r}")
