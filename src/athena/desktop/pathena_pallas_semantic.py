"""Deterministic PALLAS graph input derived from real desktop contracts.

PALLAS must never invent semantic content.  This adapter therefore accepts the
already validated ``GroundedChatResponse`` returned by Core and preserves its
entity IDs, revision IDs, evidence text, epistemic state, and cited/context
distinction.  Layout seeds are deterministic presentation input; they do not
claim domain relationships beyond the response's grounding membership.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from athena.api.contracts import (
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundedMemoryResponse,
)


class PallasNodeKind(StrEnum):
    """Semantic glyph classes supported by the first interactive PALLAS slice."""

    SOURCE = "source"
    CLAIM = "claim"
    KNOWLEDGE = "knowledge"
    HYPOTHESIS = "hypothesis"
    MEMORY = "memory"
    FOCUS = "focus"
    CONFLICT = "conflict"
    UNCERTAIN = "uncertain"


PALLAS_GLYPHS: dict[PallasNodeKind, str] = {
    PallasNodeKind.SOURCE: "△",
    PallasNodeKind.CLAIM: "◆",
    PallasNodeKind.KNOWLEDGE: "■",
    PallasNodeKind.HYPOTHESIS: "◇",
    PallasNodeKind.MEMORY: "●",
    PallasNodeKind.FOCUS: "◉",
    PallasNodeKind.CONFLICT: "×",
    PallasNodeKind.UNCERTAIN: "≈",
}


@dataclass(frozen=True, slots=True)
class PallasSemanticNode:
    """One renderer-neutral node backed by a persisted or response entity."""

    node_id: str
    kind: PallasNodeKind
    entity_type: str
    entity_id: str
    revision_id: str | None
    title: str
    summary: str
    epistemic_status: str | None
    cited: bool
    confidence: float | None = None

    @property
    def glyph(self) -> str:
        return PALLAS_GLYPHS[self.kind]


@dataclass(frozen=True, slots=True)
class PallasSemanticEdge:
    """A relationship explicitly justified by grounded response membership."""

    source_id: str
    target_id: str
    relation: str


@dataclass(frozen=True, slots=True)
class PallasGraphSnapshot:
    """Immutable graph snapshot safe to share between miniature and full views."""

    graph_id: str
    nodes: tuple[PallasSemanticNode, ...]
    edges: tuple[PallasSemanticEdge, ...]
    focus_id: str | None
    status: str
    status_detail: str

    def node(self, node_id: str) -> PallasSemanticNode | None:
        return next((node for node in self.nodes if node.node_id == node_id), None)


@dataclass(frozen=True, slots=True)
class PallasLayoutNode:
    """Deterministic seed position for one semantic node."""

    node_id: str
    x: float
    y: float


def graph_from_grounded_response(response: GroundedChatResponse) -> PallasGraphSnapshot:
    """Adapt one validated grounded response without fabricating graph content."""
    graph_id = f"grounded-run:{response.processing_run_id}"
    semantic_items = len(response.evidence) + len(response.personal_memory)
    if semantic_items == 0:
        return PallasGraphSnapshot(
            graph_id=graph_id,
            nodes=(),
            edges=(),
            focus_id=None,
            status="empty",
            status_detail="This grounded run returned no evidence or personal memory.",
        )

    focus_id = f"focus:{response.processing_run_id}"
    focus = PallasSemanticNode(
        node_id=focus_id,
        kind=PallasNodeKind.FOCUS,
        entity_type="grounded_processing_run",
        entity_id=response.processing_run_id,
        revision_id=None,
        title="Grounded response",
        summary=response.assistant_text,
        epistemic_status=None,
        cited=True,
    )

    evidence_nodes = tuple(
        _node_from_evidence(item)
        for item in sorted(
            response.evidence,
            key=lambda item: (_evidence_node_id(item), item.context_id),
        )
    )
    memory_nodes = tuple(
        _node_from_memory(item)
        for item in sorted(response.personal_memory, key=lambda item: item.memory_id)
    )
    nodes = _deduplicate_nodes((focus, *evidence_nodes, *memory_nodes))
    edges = tuple(
        PallasSemanticEdge(
            source_id=focus_id,
            target_id=node.node_id,
            relation=(
                "uses_personal_memory"
                if node.kind is PallasNodeKind.MEMORY
                else "cites"
                if node.cited
                else "includes_context"
            ),
        )
        for node in nodes
        if node.node_id != focus_id
    )
    return PallasGraphSnapshot(
        graph_id=graph_id,
        nodes=nodes,
        edges=edges,
        focus_id=focus_id,
        status="ready",
        status_detail=(
            f"{len(nodes) - 1} real semantic items from grounded run "
            f"{response.processing_run_id}."
        ),
    )


def deterministic_layout(snapshot: PallasGraphSnapshot) -> tuple[PallasLayoutNode, ...]:
    """Return stable renderer seeds independent of input ordering and wall time."""
    if not snapshot.nodes:
        return ()

    positions: list[PallasLayoutNode] = []
    if snapshot.focus_id is not None:
        positions.append(PallasLayoutNode(snapshot.focus_id, 0.0, 0.0))

    grouped: dict[PallasNodeKind, list[PallasSemanticNode]] = {}
    for node in sorted(snapshot.nodes, key=lambda item: item.node_id):
        if node.node_id == snapshot.focus_id:
            continue
        grouped.setdefault(node.kind, []).append(node)

    lane_angles = {
        PallasNodeKind.SOURCE: math.radians(190),
        PallasNodeKind.CLAIM: math.radians(245),
        PallasNodeKind.KNOWLEDGE: math.radians(55),
        PallasNodeKind.HYPOTHESIS: math.radians(5),
        PallasNodeKind.MEMORY: math.radians(105),
        PallasNodeKind.CONFLICT: math.radians(145),
        PallasNodeKind.UNCERTAIN: math.radians(325),
        PallasNodeKind.FOCUS: 0.0,
    }
    for kind in PallasNodeKind:
        lane = grouped.get(kind, [])
        for index, node in enumerate(lane):
            centered = index - (len(lane) - 1) / 2
            angle = lane_angles[kind] + centered * math.radians(13)
            ring = 118.0 + 34.0 * (index // 5)
            positions.append(
                PallasLayoutNode(
                    node_id=node.node_id,
                    x=round(math.cos(angle) * ring, 4),
                    y=round(math.sin(angle) * ring, 4),
                )
            )

    return tuple(sorted(positions, key=lambda item: item.node_id))


def _evidence_node_id(item: GroundedEvidenceResponse) -> str:
    return f"{item.entity_type}:{item.entity_id}"


def _node_from_evidence(item: GroundedEvidenceResponse) -> PallasSemanticNode:
    title = item.title or item.source_name or item.entity_type.replace("_", " ").title()
    return PallasSemanticNode(
        node_id=_evidence_node_id(item),
        kind=_kind_for_evidence(item),
        entity_type=item.entity_type,
        entity_id=item.entity_id,
        revision_id=item.revision_id,
        title=title,
        summary=item.text,
        epistemic_status=item.epistemic_status,
        cited=item.cited,
    )


def _node_from_memory(item: GroundedMemoryResponse) -> PallasSemanticNode:
    return PallasSemanticNode(
        node_id=f"memory:{item.memory_id}",
        kind=PallasNodeKind.MEMORY,
        entity_type="personal_memory",
        entity_id=item.memory_id,
        revision_id=item.revision_id,
        title=item.memory_kind.replace("_", " ").title(),
        summary=item.content,
        epistemic_status=None,
        cited=False,
    )


def _kind_for_evidence(item: GroundedEvidenceResponse) -> PallasNodeKind:
    status = (item.epistemic_status or "").casefold()
    if any(marker in status for marker in ("conflict", "contradict")):
        return PallasNodeKind.CONFLICT
    if any(marker in status for marker in ("uncertain", "unknown", "contested")):
        return PallasNodeKind.UNCERTAIN

    entity_type = item.entity_type.casefold()
    if item.evidence_class == "source" or "source" in entity_type:
        return PallasNodeKind.SOURCE
    if "claim" in entity_type:
        return PallasNodeKind.CLAIM
    if "hypothesis" in entity_type or status == "hypothesis":
        return PallasNodeKind.HYPOTHESIS
    if item.evidence_class == "research" or "research" in entity_type:
        return PallasNodeKind.HYPOTHESIS
    return PallasNodeKind.KNOWLEDGE


def _deduplicate_nodes(
    nodes: tuple[PallasSemanticNode, ...],
) -> tuple[PallasSemanticNode, ...]:
    """Collapse repeated context references to one stable real entity node."""
    unique: dict[str, PallasSemanticNode] = {}
    for node in nodes:
        existing = unique.get(node.node_id)
        if existing is None:
            unique[node.node_id] = node
            continue
        if (
            existing.entity_type != node.entity_type
            or existing.entity_id != node.entity_id
            or existing.revision_id != node.revision_id
        ):
            raise ValueError(f"PALLAS node ID collision for {node.node_id!r}.")
        if node.cited and not existing.cited:
            unique[node.node_id] = PallasSemanticNode(
                node_id=existing.node_id,
                kind=existing.kind,
                entity_type=existing.entity_type,
                entity_id=existing.entity_id,
                revision_id=existing.revision_id,
                title=existing.title,
                summary=existing.summary,
                epistemic_status=existing.epistemic_status,
                cited=True,
                confidence=existing.confidence,
            )
    return tuple(sorted(unique.values(), key=lambda item: item.node_id))
