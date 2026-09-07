"""Deterministic domain routing for explicit persistence commands."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.memory.explicit_command import (
    ExplicitMemoryIntent,
    is_explicit_persistence_command,
    parse_explicit_personal_memory_command,
)
from athena.memory.models import MemoryScopeKind


class ExplicitPersistenceDomain(str, Enum):
    """Canonical domain selected for one explicit persistence command."""

    PERSONAL_MEMORY = "personal_memory"
    KNOWLEDGE = "knowledge"


@dataclass(frozen=True, slots=True)
class ExplicitPersistenceRouting:
    """Side-effect-free routing decision for one explicit persistence command."""

    domain: ExplicitPersistenceDomain
    personal_memory_intent: ExplicitMemoryIntent | None


def route_explicit_persistence_domain(
    content: str,
    *,
    scope_kind: MemoryScopeKind | None = None,
    scope_entity_id: uuid.UUID | None = None,
) -> ExplicitPersistenceRouting | None:
    """Route explicit persistence to Personal Memory only for user preferences.

    Explicit persistence text that is not a collaboration preference belongs to
    Knowledge rather than Personal Memory. Ordinary non-persistence text produces
    no routing decision. This function performs no persistence and synthesizes no
    provenance or entity identity.
    """
    if not is_explicit_persistence_command(content):
        return None

    intent = parse_explicit_personal_memory_command(
        content,
        scope_kind=scope_kind,
        scope_entity_id=scope_entity_id,
    )
    if intent is None:
        return ExplicitPersistenceRouting(
            domain=ExplicitPersistenceDomain.KNOWLEDGE,
            personal_memory_intent=None,
        )
    return ExplicitPersistenceRouting(
        domain=ExplicitPersistenceDomain.PERSONAL_MEMORY,
        personal_memory_intent=intent,
    )
