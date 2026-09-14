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
        self.tick = 0

    def clear(self) -> None:
        self.snapshot = None
        self.states.clear()
        self._semantic_tokens.clear()
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
        self._semantic_tokens = {
            node.node_id: _tokens(node) for node in snapshot.nodes
        }
        self.snapshot = snapshot
        if not had_state:
            self.tick = 0

    def step(self, dt: float | None = None) -> None:
        graph = self.snapshot
        if graph is None or not graph.nodes:
            return
        c = self.config
        dt = 1.0 / c.fps if dt is None else min(max(float(dt), 1 / 240), 0.1)
        nodes = tuple(sorted(graph.nodes, key=lambda item: item.node_id))
        by_id = {node.node_id: node for node in nodes}
        force: dict[str, list[float]] = {
            node.node_id: [0.0, 0.0] for node in nodes
        }
        neighbors: dict[str, set[str]] = {
            node.node_id: set() for node in nodes
        }
        conflict_pairs: set[frozenset[str]] = set()

        for edge in graph.edges:
            if edge.source_id not in by_id or edge.target_id not in by_id:
                continue
            neighbors[edge.source_id].add(edge.target_id)
            neighbors[edge.target_id].add(edge.source_id)
            if edge.relation.casefold() in _CONFLICT_REL:
                conflict_pairs.add(frozenset((edge.source_id, edge.target_id)))
            self._pair_force(edge.source_id, edge.target_id, force, spring=True)

        for index, left in enumerate(nodes):
            for right in nodes[index + 1 :]:
                pair = frozenset((left.node_id, right.node_id))
                ratio = (
                    c.contradiction_repulsion / max(c.global_repulsion, 1e-9)
                    if pair in conflict_pairs
                    else 1.0
                )
                self._pair_force(left.node_id, right.node_id, force, repulsion=ratio)
                similarity = _token_similarity(
                    self._semantic_tokens.get(left.node_id, frozenset()),
                    self._semantic_tokens.get(right.node_id, frozenset()),
                )
                if similarity >= c.semantic_threshold:
                    self._pair_force(
                        left.node_id,
                        right.node_id,
                        force,
                        attraction=similarity,
                    )

        conflict_ids = {
            node.node_id for node in nodes if node.kind is PallasNodeKind.CONFLICT
        }
        for conflict_id in conflict_ids:
            for node in nodes:
                pair = frozenset((conflict_id, node.node_id))
                if node.node_id != conflict_id and pair not in conflict_pairs:
                    self._pair_force(conflict_id, node.node_id, force, repulsion=1.55)

        previous = {
            node_id: state.vitality for node_id, state in self.states.items()
        }
        active = {node_id: state.active for node_id, state in self.states.items()}
        damping = c.damping ** (dt * c.fps)
        for node in nodes:
            state = self.states[node.node_id]
            pull = c.focus_pull if node.node_id == graph.focus_id else c.center_pull
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
            target += 0.14 if node.node_id == graph.focus_id else 0.0
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
            if node.node_id == graph.focus_id:
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

    def diagnostics(self) -> dict[str, float | int]:
        values = tuple(self.states.values())
        mean_vitality = (
            0.0
            if not values
            else sum(state.vitality for state in values) / len(values)
        )
        return {
            "nodes": len(values),
            "active": sum(state.active for state in values),
            "mean_vitality": mean_vitality,
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
