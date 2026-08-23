"""Typed evidence roles for memory-augmented chat retrieval."""

from __future__ import annotations

import uuid
from collections import Counter
from dataclasses import dataclass
from enum import Enum

from athena.common.ids import uuid_to_blob
from athena.knowledge.models import EpistemicStatus
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType
from athena.storage.database import SQLiteDatabase

MEMORY_EVIDENCE_POLICY_ID = "typed-provenance-v1"
_CHAT_MESSAGE_TYPES = frozenset({"user", "assistant", "tool_result", "system_event"})


class EvidenceClass(str, Enum):
    """Epistemic role of one retrieved item in a grounded answer."""

    CANONICAL = "canonical"
    USER_STATEMENT = "user_statement"
    CONVERSATION_RECORD = "conversation_record"
    SOURCE = "source"
    RESEARCH = "research"
    NEWS = "news"


class MemoryEvidencePolicyError(RuntimeError):
    """Raised when evidence cannot be classified without guessing."""


@dataclass(frozen=True, slots=True)
class MemoryEvidenceClassification:
    """Typed provenance for one retrieved hybrid result."""

    entity_id: uuid.UUID
    revision_id: uuid.UUID
    entity_type: SearchEntityType
    evidence_class: EvidenceClass
    message_type: str | None
    epistemic_status: EpistemicStatus | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.entity_id, uuid.UUID):
            raise TypeError("Evidence entity_id must be a UUID.")
        if not isinstance(self.revision_id, uuid.UUID):
            raise TypeError("Evidence revision_id must be a UUID.")
        if not isinstance(self.entity_type, SearchEntityType):
            raise TypeError("Evidence entity_type must be a SearchEntityType.")
        if not isinstance(self.evidence_class, EvidenceClass):
            raise TypeError("Evidence evidence_class must be an EvidenceClass.")
        if self.message_type is not None:
            if not isinstance(self.message_type, str):
                raise TypeError("Evidence message_type must be text or None.")
            if self.message_type not in _CHAT_MESSAGE_TYPES:
                raise ValueError("Evidence message_type is unsupported.")
        if self.epistemic_status is not None and not isinstance(
            self.epistemic_status,
            EpistemicStatus,
        ):
            raise TypeError("Evidence epistemic_status must be EpistemicStatus or None.")

        if self.evidence_class is EvidenceClass.CANONICAL:
            if self.entity_type not in {SearchEntityType.KNOWLEDGE, SearchEntityType.CLAIM}:
                raise ValueError("Canonical evidence requires Knowledge or Claim entity type.")
            if self.message_type is not None or self.epistemic_status is None:
                raise ValueError(
                    "Canonical evidence requires epistemic status and no message_type."
                )
        elif self.evidence_class is EvidenceClass.USER_STATEMENT:
            if self.entity_type is not SearchEntityType.CHAT_MESSAGE or self.message_type != "user":
                raise ValueError("User-statement evidence requires a user chat message.")
            if self.epistemic_status is not None:
                raise ValueError("User-statement evidence must not carry epistemic status.")
        elif self.evidence_class is EvidenceClass.CONVERSATION_RECORD:
            if self.entity_type is not SearchEntityType.CHAT_MESSAGE:
                raise ValueError("Conversation-record evidence requires a chat message.")
            if self.message_type not in {"assistant", "tool_result", "system_event"}:
                raise ValueError("Conversation-record evidence requires a non-user chat message.")
            if self.epistemic_status is not None:
                raise ValueError("Conversation-record evidence must not carry epistemic status.")


@dataclass(frozen=True, slots=True)
class MemoryEvidenceSelection:
    """Retrieved results plus deterministic epistemic-role classification."""

    policy_id: str
    results: tuple[HybridSearchResult, ...]
    classifications: tuple[MemoryEvidenceClassification, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.policy_id, str) or not self.policy_id.strip():
            raise ValueError("Evidence policy_id must be non-empty text.")
        if not isinstance(self.results, tuple) or not all(
            isinstance(item, HybridSearchResult) for item in self.results
        ):
            raise TypeError("Evidence results must be a tuple of HybridSearchResult values.")
        if not isinstance(self.classifications, tuple) or not all(
            isinstance(item, MemoryEvidenceClassification) for item in self.classifications
        ):
            raise TypeError(
                "Evidence classifications must be a tuple of MemoryEvidenceClassification values."
            )
        result_keys = {
            (item.entity_type, item.entity_id, item.revision_id)
            for item in self.results
        }
        classification_keys = {
            (item.entity_type, item.entity_id, item.revision_id)
            for item in self.classifications
        }
        if len(result_keys) != len(self.results):
            raise ValueError("Evidence results contain duplicate entity revisions.")
        if len(classification_keys) != len(self.classifications):
            raise ValueError("Evidence classifications contain duplicate entity revisions.")
        if result_keys != classification_keys:
            raise ValueError("Evidence classifications must exactly cover retrieval results.")

    def classification_for(
        self,
        *,
        entity_type: SearchEntityType,
        entity_id: uuid.UUID,
        revision_id: uuid.UUID,
    ) -> MemoryEvidenceClassification:
        if not isinstance(entity_type, SearchEntityType):
            raise TypeError("entity_type must be a SearchEntityType.")
        if not isinstance(entity_id, uuid.UUID):
            raise TypeError("entity_id must be a UUID.")
        if not isinstance(revision_id, uuid.UUID):
            raise TypeError("revision_id must be a UUID.")
        for item in self.classifications:
            if (
                item.entity_type is entity_type
                and item.entity_id == entity_id
                and item.revision_id == revision_id
            ):
                return item
        raise MemoryEvidencePolicyError(
            "Context item has no evidence classification: "
            f"{entity_type.value}:{entity_id}:{revision_id}"
        )

    @property
    def counts(self) -> tuple[tuple[EvidenceClass, int], ...]:
        counts = Counter(item.evidence_class for item in self.classifications)
        return tuple(sorted(counts.items(), key=lambda item: item[0].value))


class MemoryEvidencePolicy:
    """Classify retrieval without converting raw conversation into knowledge.

    Knowledge and Claims are canonical semantic evidence. A raw user message is
    direct evidence of what the user said or self-reported, but it is not
    independent verification of an arbitrary world fact. Other chat messages
    remain conversation records: useful for continuity and recap, but not an
    independent factual authority.
    """

    def __init__(self, database: SQLiteDatabase) -> None:
        if not isinstance(database, SQLiteDatabase):
            raise TypeError("database must be a SQLiteDatabase.")
        self.database = database

    def classify(
        self,
        results: tuple[HybridSearchResult, ...],
    ) -> MemoryEvidenceSelection:
        if not isinstance(results, tuple) or not all(
            isinstance(item, HybridSearchResult) for item in results
        ):
            raise TypeError("results must be a tuple of HybridSearchResult values.")
        classifications = tuple(self._classify_one(result) for result in results)
        return MemoryEvidenceSelection(
            policy_id=MEMORY_EVIDENCE_POLICY_ID,
            results=results,
            classifications=classifications,
        )

    def _canonical_epistemic_status(
        self,
        result: HybridSearchResult,
    ) -> EpistemicStatus:
        if result.entity_type is SearchEntityType.KNOWLEDGE:
            row = self.database.connection.execute(
                """
                SELECT kr.epistemic_status
                FROM knowledge_units AS k
                JOIN entity_registry AS e
                  ON e.entity_id = k.knowledge_id
                JOIN entity_heads AS h
                  ON h.entity_id = k.knowledge_id
                JOIN knowledge_unit_revisions AS kr
                  ON kr.revision_id = h.current_revision_id
                WHERE k.knowledge_id = ?
                  AND h.current_revision_id = ?
                  AND e.lifecycle_state = 'active'
                """,
                (
                    uuid_to_blob(result.entity_id),
                    uuid_to_blob(result.revision_id),
                ),
            ).fetchone()
        elif result.entity_type is SearchEntityType.CLAIM:
            row = self.database.connection.execute(
                """
                SELECT cr.epistemic_status
                FROM claims AS c
                JOIN entity_registry AS e
                  ON e.entity_id = c.claim_id
                JOIN entity_heads AS h
                  ON h.entity_id = c.claim_id
                JOIN claim_revisions AS cr
                  ON cr.revision_id = h.current_revision_id
                WHERE c.claim_id = ?
                  AND h.current_revision_id = ?
                  AND e.lifecycle_state = 'active'
                """,
                (
                    uuid_to_blob(result.entity_id),
                    uuid_to_blob(result.revision_id),
                ),
            ).fetchone()
        else:
            raise MemoryEvidencePolicyError(
                "Canonical epistemic status requires Knowledge or Claim."
            )

        if row is None:
            raise MemoryEvidencePolicyError(
                "Retrieved canonical evidence is not the active current revision: "
                f"{result.entity_type.value}:{result.entity_id}:{result.revision_id}"
            )

        try:
            return EpistemicStatus(str(row["epistemic_status"]))
        except ValueError as exc:
            raise MemoryEvidencePolicyError(
                "Retrieved canonical evidence has an unsupported epistemic status."
            ) from exc

    def _classify_one(
        self,
        result: HybridSearchResult,
    ) -> MemoryEvidenceClassification:
        if result.entity_type in {SearchEntityType.KNOWLEDGE, SearchEntityType.CLAIM}:
            return MemoryEvidenceClassification(
                entity_id=result.entity_id,
                revision_id=result.revision_id,
                entity_type=result.entity_type,
                evidence_class=EvidenceClass.CANONICAL,
                message_type=None,
                epistemic_status=self._canonical_epistemic_status(result),
            )

        if result.entity_type is not SearchEntityType.CHAT_MESSAGE:
            raise MemoryEvidencePolicyError(
                f"Unsupported memory evidence entity type: {result.entity_type.value}"
            )

        row = self.database.connection.execute(
            """
            SELECT m.message_type
            FROM chat_messages AS m
            JOIN chats AS ch
              ON ch.chat_id = m.chat_id
            JOIN entity_registry AS e
              ON e.entity_id = m.message_id
            JOIN entity_heads AS h
              ON h.entity_id = m.message_id
            JOIN chat_message_revisions AS mr
              ON mr.revision_id = h.current_revision_id
            WHERE m.message_id = ?
              AND h.current_revision_id = ?
              AND e.lifecycle_state = 'active'
              AND ch.lifecycle_state = 'active'
              AND ch.archive_mode = 'standard'
            """,
            (
                uuid_to_blob(result.entity_id),
                uuid_to_blob(result.revision_id),
            ),
        ).fetchone()
        if row is None:
            raise MemoryEvidencePolicyError(
                "Retrieved chat evidence is not the active current searchable revision: "
                f"{result.entity_id}:{result.revision_id}"
            )

        message_type = str(row["message_type"])
        if message_type not in _CHAT_MESSAGE_TYPES:
            raise MemoryEvidencePolicyError(
                "Retrieved chat message has an unsupported message type."
            )

        evidence_class = (
            EvidenceClass.USER_STATEMENT
            if message_type == "user"
            else EvidenceClass.CONVERSATION_RECORD
        )
        return MemoryEvidenceClassification(
            entity_id=result.entity_id,
            revision_id=result.revision_id,
            entity_type=result.entity_type,
            evidence_class=evidence_class,
            message_type=message_type,
            epistemic_status=None,
        )
