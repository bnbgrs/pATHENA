"""Provenance-safe living layout for PALLAS.

This module changes presentation state only. It never mutates semantic graph
membership or invents provenance edges.
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Mapping

from athena.desktop.pathena_pallas_semantic import (
    PallasGraphSnapshot,
    PallasNodeKind,
    PallasSemanticNode,
)

_TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)
_AGE = ("·", ":", "+", "o", "O", "░", "▒", "▓", "█")
_CONFLICT_REL = frozenset(
    {"conflict", "conflicts", "contradicts", "contradiction", "opposes"}
)


@dataclass(frozen=True, slots=True)
class PallasLivingConfig:
    fps: float = 30.0
    semantic_threshold: float = 0.24
    semantic_attraction: float = 18.0
    global_repulsion: float = 1450.0
    contradiction_repulsion: float = 4200.0
    edge_spring: float = 8.0
    edge_rest_length: float = 128.0
    focus_pull: float = 5.5
    center_pull: float = 0.9
    temporal_drift: float = 2.4
    damping: float = 0.87
    max_speed: float = 92.0
    min_distance: float = 22.0
    world_radius: float = 420.0
    vitality_diffusion: float = 0.55
    vitality_relaxation: float = 0.75
    vitality_decay: float = 0.018
    active_threshold: float = 0.18
    aging_horizon_seconds: float = 300.0


@dataclass(slots=True)
class PallasLivingNodeState:
    node_id: str
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    age_seconds: float = 0.0
    vitality: float = 1.0
    active: bool = True


class PallasLivingEngine:
    """Deterministic forces plus CA-style birth/survive/diffuse/decay."""

    def __init__(self, config: PallasLivingConfig | None = None) -> None:
        self.config = config or PallasLivingConfig()
        self.snapshot: PallasGraphSnapshot | None = None
        self.states: dict[str, PallasLivingNodeState] = {}
        self._semantic_tokens: dict[str, frozenset[str]] = {}
        self._node_order: tuple[PallasSemanticNode, ...] = ()
        self._node_by_id: dict[str, PallasSemanticNode] = {}
        self._neighbors: dict[str, frozenset[str]] = {}
        self._conflict_pairs: frozenset[frozenset[str]] = frozenset()
        self._spring_pairs: tuple[tuple[str, str], ...] = ()
        self._repulsion_pairs: tuple[tuple[str, str, float], ...] = ()
        self._conflict_repulsion_pairs: tuple[tuple[str, str], ...] = ()
        self._semantic_pairs: tuple[tuple[str, str, float], ...] = ()
        self.visual_focus_id: str | None = None
        self.tick = 0

    def clear(self) -> None:
        self.snapshot = None
        self.states.clear()
        self._semantic_tokens.clear()
        self._node_order = ()
        self._node_by_id.clear()
        self._neighbors.clear()
        self._conflict_pairs = frozenset()
        self._spring_pairs = ()
        self._repulsion_pairs = ()
        self._conflict_repulsion_pairs = ()
        self._semantic_pairs = ()
        self.visual_focus_id = None
        self.tick = 0

    def reconcile(
        self,
        snapshot: PallasGraphSnapshot,
        seed_positions: Mapping[str, tuple[float, float]] | None = None,
    ) -> None:
        seeds = seed_positions or {}
        ids = {node.node_id for node in snapshot.nodes}
        self.states = {
            node_id: state
            for node_id, state in self.states.items()
            if node_id in ids
        }
        had_state = bool(self.states)
        for node in sorted(snapshot.nodes, key=lambda item: item.node_id):
            state = self.states.get(node.node_id)
            if state is not None:
                state.vitality = min(1.0, state.vitality + 0.08)
                state.active = True
                continue
            x, y = seeds.get(node.node_id, _stable_seed(node.node_id))
            self.states[node.node_id] = PallasLivingNodeState(
                node.node_id,
                float(x),
                float(y),
                vitality=1.0 if node.node_id == snapshot.focus_id else 0.82,
            )
        self._node_order = tuple(sorted(snapshot.nodes, key=lambda item: item.node_id))
        self._node_by_id = {node.node_id: node for node in self._node_order}
        self._semantic_tokens = {
            node.node_id: _tokens(node) for node in self._node_order
        }

        neighbor_sets: dict[str, set[str]] = {
            node.node_id: set() for node in self._node_order
        }
        conflict_pairs: set[frozenset[str]] = set()
        spring_pairs: list[tuple[str, str]] = []
        for edge in snapshot.edges:
            if (
                edge.source_id not in self._node_by_id
                or edge.target_id not in self._node_by_id
            ):
                continue
            neighbor_sets[edge.source_id].add(edge.target_id)
            neighbor_sets[edge.target_id].add(edge.source_id)
            spring_pairs.append((edge.source_id, edge.target_id))
            if edge.relation.casefold() in _CONFLICT_REL:
                conflict_pairs.add(frozenset((edge.source_id, edge.target_id)))
        self._neighbors = {
            node_id: frozenset(linked) for node_id, linked in neighbor_sets.items()
        }
        self._conflict_pairs = frozenset(conflict_pairs)
        self._spring_pairs = tuple(spring_pairs)

        semantic_pairs: list[tuple[str, str, float]] = []
        repulsion_pairs: list[tuple[str, str, float]] = []
        conflict_repulsion_pairs: list[tuple[str, str]] = []
        contradiction_ratio = (
            self.config.contradiction_repulsion
            / max(self.config.global_repulsion, 1e-9)
        )
        for index, left in enumerate(self._node_order):
            left_tokens = self._semantic_tokens.get(left.node_id, frozenset())
            for right in self._node_order[index + 1 :]:
                pair = frozenset((left.node_id, right.node_id))
                repulsion_pairs.append(
                    (
                        left.node_id,
                        right.node_id,
                        contradiction_ratio if pair in conflict_pairs else 1.0,
                    )
                )
                if (
                    pair not in conflict_pairs
                    and (
                        left.kind is PallasNodeKind.CONFLICT
                        or right.kind is PallasNodeKind.CONFLICT
                    )
                ):
                    conflict_repulsion_pairs.append(
                        (left.node_id, right.node_id)
                    )
                similarity = _token_similarity(
                    left_tokens,
                    self._semantic_tokens.get(right.node_id, frozenset()),
                )
                if similarity >= self.config.semantic_threshold:
                    semantic_pairs.append((left.node_id, right.node_id, similarity))
        self._repulsion_pairs = tuple(repulsion_pairs)
        self._conflict_repulsion_pairs = tuple(conflict_repulsion_pairs)
        self._semantic_pairs = tuple(semantic_pairs)
        if self.visual_focus_id not in ids:
            self.visual_focus_id = None

        self.snapshot = snapshot
        if not had_state:
            self.tick = 0

    def set_visual_focus(self, node_id: str | None) -> None:
        """Bias presentation toward a selected real node without changing graph facts."""
        self.visual_focus_id = node_id

    def step(self, dt: float | None = None) -> None:
        graph = self.snapshot
        if graph is None or not graph.nodes:
            return
        c = self.config
        dt = 1.0 / c.fps if dt is None else min(max(float(dt), 1 / 240), 0.1)
        nodes = self._node_order
        force: dict[str, list[float]] = {
            node.node_id: [0.0, 0.0] for node in nodes
        }
        neighbors = self._neighbors

        for left_id, right_id in self._spring_pairs:
            self._pair_force(left_id, right_id, force, spring=True)

        for left_id, right_id, ratio in self._repulsion_pairs:
            self._pair_force(left_id, right_id, force, repulsion=ratio)

        for left_id, right_id, similarity in self._semantic_pairs:
            self._pair_force(
                left_id,
                right_id,
                force,
                attraction=similarity,
            )

        for left_id, right_id in self._conflict_repulsion_pairs:
            self._pair_force(left_id, right_id, force, repulsion=1.55)

        previous = {
            node_id: state.vitality for node_id, state in self.states.items()
        }
        active = {node_id: state.active for node_id, state in self.states.items()}
        presentation_focus = (
            self.visual_focus_id
            if self.visual_focus_id in self.states
            else graph.focus_id
        )
        damping = c.damping ** (dt * c.fps)
        for node in nodes:
            state = self.states[node.node_id]
            pull = (
                c.focus_pull
                if node.node_id == presentation_focus
                else c.center_pull
            )
            phase = _phase(node.node_id)
            temporal = state.age_seconds * 0.13 + self.tick * 0.021
            force[node.node_id][0] += (
                -state.x * pull / 100
                + math.sin(phase + temporal) * c.temporal_drift
            )
            force[node.node_id][1] += (
                -state.y * pull / 100
                + math.cos(phase * 0.71 + temporal) * c.temporal_drift
            )

            linked = neighbors[node.node_id]
            alive = sum(1 for other in linked if active.get(other, False))
            if state.active:
                target = 0.72 if 1 <= alive <= 5 else 0.42
            else:
                target = 0.62 if alive >= 2 else 0.08
            target += 0.12 if node.cited else 0.0
            target += 0.14 if node.node_id == presentation_focus else 0.0
            if node.confidence is not None:
                target += 0.10 * max(0.0, min(1.0, node.confidence))
            if linked:
                mean = sum(previous[other] for other in linked) / len(linked)
                diffusion = (mean - previous[node.node_id]) * c.vitality_diffusion
            else:
                diffusion = 0.0
            age_factor = 1 + min(
                state.age_seconds / max(c.aging_horizon_seconds, 1), 2
            ) * 0.25
            delta = (
                (min(target, 1.0) - previous[node.node_id]) * c.vitality_relaxation
                + diffusion
                - c.vitality_decay * age_factor
            ) * dt
            state.vitality = min(
                1.0,
                max(0.03, previous[node.node_id] + delta),
            )
            state.active = state.vitality >= c.active_threshold
            state.age_seconds += dt

            fx, fy = force[node.node_id]
            state.vx = (state.vx + fx * dt) * damping
            state.vy = (state.vy + fy * dt) * damping
            speed = math.hypot(state.vx, state.vy)
            if speed > c.max_speed:
                scale = c.max_speed / speed
                state.vx *= scale
                state.vy *= scale
            if node.node_id == presentation_focus:
                state.vx *= 0.72
                state.vy *= 0.72
            state.x += state.vx * dt
            state.y += state.vy * dt
            radius = math.hypot(state.x, state.y)
            if radius > c.world_radius:
                scale = c.world_radius / radius
                state.x *= scale
                state.y *= scale
                state.vx *= -0.25
                state.vy *= -0.25
        self.tick += 1

    def _pair_force(
        self,
        left_id: str,
        right_id: str,
        force: dict[str, list[float]],
        *,
        spring: bool = False,
        repulsion: float = 0.0,
        attraction: float = 0.0,
    ) -> None:
        c = self.config
        left, right = self.states[left_id], self.states[right_id]
        dx, dy = right.x - left.x, right.y - left.y
        distance = math.hypot(dx, dy)
        if distance < 1e-6:
            phase = _phase(left_id + "|" + right_id)
            dx, dy, distance = math.cos(phase), math.sin(phase), 1.0
        ux, uy = dx / distance, dy / distance
        magnitude = 0.0
        if spring:
            magnitude += (
                c.edge_spring
                * (distance - c.edge_rest_length)
                / max(c.edge_rest_length, 1)
            )
        if attraction:
            magnitude += c.semantic_attraction * attraction
        if repulsion:
            bounded = max(distance, c.min_distance)
            magnitude -= c.global_repulsion * repulsion / (bounded * bounded)
        fx, fy = magnitude * ux, magnitude * uy
        force[left_id][0] += fx
        force[left_id][1] += fy
        force[right_id][0] -= fx
        force[right_id][1] -= fy

    def position(self, node_id: str) -> tuple[float, float] | None:
        state = self.states.get(node_id)
        return None if state is None else (state.x, state.y)

    def age_glyph(self, node_id: str) -> str:
        state = self.states.get(node_id)
        age = 0.0 if state is None else state.age_seconds
        return age_glyph(age, self.config.aging_horizon_seconds)

    def diagnostics(self) -> dict[str, float | int | str]:
        values = tuple(self.states.values())
        mean_vitality = (
            0.0
            if not values
            else sum(state.vitality for state in values) / len(values)
        )
        speeds = tuple(math.hypot(state.vx, state.vy) for state in values)
        return {
            "nodes": len(values),
            "active": sum(state.active for state in values),
            "mean_vitality": mean_vitality,
            "mean_speed": 0.0 if not speeds else sum(speeds) / len(speeds),
            "max_speed": 0.0 if not speeds else max(speeds),
            "semantic_pairs": len(self._semantic_pairs),
            "spring_pairs": len(self._spring_pairs),
            "repulsion_pairs": len(self._repulsion_pairs),
            "conflict_repulsion_pairs": len(self._conflict_repulsion_pairs),
            "edges": 0 if self.snapshot is None else len(self.snapshot.edges),
            "visual_focus": self.visual_focus_id or "",
            "tick": self.tick,
        }


def semantic_similarity(left: PallasSemanticNode, right: PallasSemanticNode) -> float:
    return _token_similarity(_tokens(left), _tokens(right))


def age_glyph(age_seconds: float, horizon_seconds: float = 300.0) -> str:
    progress = min(
        max(float(age_seconds) / max(float(horizon_seconds), 1e-6), 0.0),
        1.0,
    )
    return _AGE[min(int(progress * len(_AGE)), len(_AGE) - 1)]


def _token_similarity(left: frozenset[str], right: frozenset[str]) -> float:
    return 0.0 if not left or not right else len(left & right) / len(left | right)


def _tokens(node: PallasSemanticNode) -> frozenset[str]:
    text = f"{node.title} {node.summary}".casefold()
    return frozenset(
        token for token in _TOKEN_RE.findall(text) if len(token) > 2
    )


def _phase(value: str) -> float:
    digest = hashlib.sha256(value.encode()).digest()
    return int.from_bytes(digest[:8], "big") / (2**64 - 1) * math.tau


def _stable_seed(value: str) -> tuple[float, float]:
    digest = hashlib.sha256(value.encode()).digest()
    phase = _phase(value)
    radius = 90 + int.from_bytes(digest[:2], "big") / 65535 * 120
    return math.cos(phase) * radius, math.sin(phase) * radius
