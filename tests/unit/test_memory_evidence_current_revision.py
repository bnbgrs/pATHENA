from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest

from athena.retrieval.evidence import (
    EvidenceClass,
    MemoryEvidencePolicy,
    MemoryEvidencePolicyError,
)
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType


class _Cursor:
    def __init__(self, row: dict[str, object] | None) -> None:
        self._row = row

    def fetchone(self) -> dict[str, object] | None:
        return self._row


class _Connection:
    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row
        self.sql = ""
        self.parameters: tuple[bytes, bytes] | None = None

    def execute(
        self,
        sql: str,
        parameters: tuple[bytes, bytes],
    ) -> _Cursor:
        self.sql = " ".join(sql.split())
        self.parameters = parameters
        return _Cursor(self.row)


@dataclass
class _Database:
    connection: _Connection


def _result() -> HybridSearchResult:
    return HybridSearchResult(
        entity_id=uuid.uuid4(),
        revision_id=uuid.uuid4(),
        entity_type=SearchEntityType.CHAT_MESSAGE,
        title="Chat message",
        text="hello",
        score=0.2,
        lexical_score=0.1,
        semantic_score=0.1,
        authority_score=0.68,
        contradiction_count=0,
        duplicate_count=0,
    )


def _policy(row: dict[str, object] | None) -> tuple[MemoryEvidencePolicy, _Connection]:
    connection = _Connection(row)
    policy = object.__new__(MemoryEvidencePolicy)
    policy.database = _Database(connection)  # type: ignore[assignment]
    return policy, connection


def test_chat_evidence_requires_current_revision_and_searchable_chat() -> None:
    result = _result()
    policy, connection = _policy({"message_type": "user"})

    classification = policy._classify_one(result)

    assert classification.evidence_class is EvidenceClass.USER_STATEMENT
    assert connection.parameters == (result.entity_id.bytes, result.revision_id.bytes)
    assert "h.current_revision_id = ?" in connection.sql
    assert "e.lifecycle_state = 'active'" in connection.sql
    assert "ch.lifecycle_state = 'active'" in connection.sql
    assert "ch.archive_mode = 'standard'" in connection.sql


def test_stale_or_nonsearchable_chat_evidence_fails_closed() -> None:
    result = _result()
    policy, _connection = _policy(None)

    with pytest.raises(
        MemoryEvidencePolicyError,
        match="not the active current searchable revision",
    ):
        policy._classify_one(result)
