from __future__ import annotations

import uuid

import pytest

from athena.api.knowledge_read import KnowledgeReadApiService
from athena.api.knowledge_read_composition import (
    attach_knowledge_read_api,
    build_knowledge_read_api,
)
from athena.knowledge.models import (
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
    ProvenanceInputRef,
)

KNOWLEDGE_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")


class _KnowledgeSourceStub:
    def __init__(self) -> None:
        self.loaded: list[uuid.UUID] = []
        self.histories: list[uuid.UUID] = []

    def load(self, knowledge_id: uuid.UUID) -> KnowledgeUnitSnapshot:
        self.loaded.append(knowledge_id)
        raise LookupError("explanation source reached")

    def provenance_inputs(
        self,
        provenance_id: uuid.UUID,
    ) -> tuple[ProvenanceInputRef, ...]:
        raise AssertionError(
            f"load failure must stop before provenance inputs for {provenance_id}"
        )

    def history(self, knowledge_id: uuid.UUID) -> tuple[KnowledgeUnitRevision, ...]:
        self.histories.append(knowledge_id)
        raise LookupError("history source reached")


class _FacadeStub:
    def __init__(self) -> None:
        self.attached: KnowledgeReadApiService | None = None

    def attach_knowledge_read(self, service: KnowledgeReadApiService) -> None:
        if self.attached is not None:
            raise RuntimeError("Knowledge read service already attached.")
        self.attached = service


def test_builder_routes_both_views_through_same_canonical_source() -> None:
    source = _KnowledgeSourceStub()
    service = build_knowledge_read_api(knowledge=source)

    with pytest.raises(LookupError, match="explanation source reached"):
        service.why_known(str(KNOWLEDGE_ID))
    with pytest.raises(LookupError, match="history source reached"):
        service.revision_history(str(KNOWLEDGE_ID))

    assert source.loaded == [KNOWLEDGE_ID]
    assert source.histories == [KNOWLEDGE_ID]


def test_builder_preserves_fail_closed_identity_validation() -> None:
    source = _KnowledgeSourceStub()
    service = build_knowledge_read_api(knowledge=source)

    with pytest.raises(ValueError):
        service.why_known("not-a-uuid")
    with pytest.raises(ValueError):
        service.revision_history("not-a-uuid")

    assert source.loaded == []
    assert source.histories == []


def test_attach_helper_returns_exact_service_attached_to_facade() -> None:
    source = _KnowledgeSourceStub()
    facade = _FacadeStub()

    service = attach_knowledge_read_api(facade=facade, knowledge=source)

    assert facade.attached is service
    with pytest.raises(LookupError, match="explanation source reached"):
        service.why_known(str(KNOWLEDGE_ID))
    assert source.loaded == [KNOWLEDGE_ID]


def test_attach_helper_preserves_single_attach_failure() -> None:
    source = _KnowledgeSourceStub()
    facade = _FacadeStub()

    first = attach_knowledge_read_api(facade=facade, knowledge=source)

    with pytest.raises(RuntimeError, match="already attached"):
        attach_knowledge_read_api(facade=facade, knowledge=source)

    assert facade.attached is first
