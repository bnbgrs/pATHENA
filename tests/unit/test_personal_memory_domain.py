from __future__ import annotations

from athena.memory.domain import ExplicitPersistenceDomain, route_explicit_persistence_domain
from athena.memory.models import MemoryKind


def test_project_or_world_content_routes_to_knowledge_not_personal_memory() -> None:
    routing = route_explicit_persistence_domain(
        "Merke dir, dass dieses Projekt FastAPI, SQLite und einen lokalen Worker verwendet."
    )

    assert routing is not None
    assert routing.domain is ExplicitPersistenceDomain.KNOWLEDGE
    assert routing.personal_memory_intent is None


def test_collaboration_preference_routes_to_personal_memory() -> None:
    routing = route_explicit_persistence_domain(
        "Merke dir, dass du bitte immer kurz antworten sollst."
    )

    assert routing is not None
    assert routing.domain is ExplicitPersistenceDomain.PERSONAL_MEMORY
    assert routing.personal_memory_intent is not None
    assert routing.personal_memory_intent.memory_kind is MemoryKind.DETAIL_PREFERENCE
    assert routing.personal_memory_intent.memory_content == "du bitte immer kurz antworten sollst."


def test_non_persistence_text_has_no_domain_routing_side_effect() -> None:
    assert route_explicit_persistence_domain("Dieses Projekt verwendet FastAPI und SQLite.") is None
