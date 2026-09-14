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
    """Keep one in-memory baseline and emit a delta for each later observation."""

    def __init__(self) -> None:
        self._previous: PallasGraphSnapshot | None = None

    @property
    def has_baseline(self) -> bool:
        return self._previous is not None

    def reset(self) -> None:
        self._previous = None

    def observe(self, snapshot: PallasGraphSnapshot) -> PallasSnapshotDelta | None:
        previous = self._previous
        self._previous = snapshot
        if previous is None:
            return None
        return compare_pallas_snapshots(previous, snapshot)


def compare_pallas_snapshots(
    before: PallasGraphSnapshot,
    after: PallasGraphSnapshot,
) -> PallasSnapshotDelta:
    """Compare exact snapshot facts without creating new semantic relationships."""
    before_nodes = _node_index(before)
    after_nodes = _node_index(after)
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

    before_edges = _edge_set(before)
    after_edges = _edge_set(after)
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
