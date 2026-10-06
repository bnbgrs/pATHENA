"""Read-only provenance backlinks for canonical Knowledge."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.storage.database import SQLiteDatabase


class KnowledgeBacklinkNotFoundError(LookupError):
    """Raised when the requested active Knowledge identity does not exist."""


@dataclass(frozen=True, slots=True)
class KnowledgeBacklink:
    knowledge_id: uuid.UUID
    revision_id: uuid.UUID
    revision_no: int
    knowledge_kind: str
    epistemic_status: str
    title: str | None
    body: str
    shared_input_count: int


class KnowledgeBacklinkService:
    """Suggest related Knowledge using exact shared persisted provenance inputs."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def related(
        self,
        knowledge_id: uuid.UUID,
        *,
        limit: int = 8,
    ) -> tuple[KnowledgeBacklink, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("Knowledge backlink limit must be an integer.")
        if not 1 <= limit <= 50:
            raise ValueError("Knowledge backlink limit must be between 1 and 50.")

        exists = self.database.connection.execute(
            """
            SELECT 1
            FROM knowledge_units AS k
            JOIN entity_registry AS e ON e.entity_id = k.knowledge_id
            WHERE k.knowledge_id = ?
              AND e.lifecycle_state = 'active'
            """,
            (uuid_to_blob(knowledge_id),),
        ).fetchone()
        if exists is None:
            raise KnowledgeBacklinkNotFoundError(str(knowledge_id))

        rows = self.database.connection.execute(
            """
            WITH target_inputs AS (
                SELECT pi.input_entity_id, pi.input_revision_id
                FROM entity_heads AS th
                JOIN revisions AS tr
                  ON tr.revision_id = th.current_revision_id
                JOIN provenance_inputs AS pi
                  ON pi.provenance_id = tr.provenance_id
                WHERE th.entity_id = ?
            ),
            matches AS (
                SELECT
                    r.entity_id AS knowledge_id,
                    r.revision_id,
                    r.revision_no,
                    kr.knowledge_kind,
                    kr.epistemic_status,
                    kr.title,
                    kr.body,
                    COUNT(*) AS shared_input_count
                FROM knowledge_units AS k
                JOIN entity_registry AS e
                  ON e.entity_id = k.knowledge_id
                JOIN entity_heads AS h
                  ON h.entity_id = k.knowledge_id
                JOIN revisions AS r
                  ON r.revision_id = h.current_revision_id
                JOIN knowledge_unit_revisions AS kr
                  ON kr.revision_id = r.revision_id
                JOIN provenance_inputs AS pi
                  ON pi.provenance_id = r.provenance_id
                JOIN target_inputs AS ti
                  ON ti.input_entity_id = pi.input_entity_id
                 AND (
                      ti.input_revision_id = pi.input_revision_id
                      OR (
                          ti.input_revision_id IS NULL
                          AND pi.input_revision_id IS NULL
                      )
                 )
                WHERE e.lifecycle_state = 'active'
                  AND k.knowledge_id != ?
                GROUP BY
                    r.entity_id,
                    r.revision_id,
                    r.revision_no,
                    kr.knowledge_kind,
                    kr.epistemic_status,
                    kr.title,
                    kr.body
            )
            SELECT *
            FROM matches
            ORDER BY shared_input_count DESC, revision_no DESC, knowledge_id ASC
            LIMIT ?
            """,
            (uuid_to_blob(knowledge_id), uuid_to_blob(knowledge_id), limit),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> KnowledgeBacklink:
        return KnowledgeBacklink(
            knowledge_id=uuid_from_blob(bytes(row["knowledge_id"])),
            revision_id=uuid_from_blob(bytes(row["revision_id"])),
            revision_no=int(row["revision_no"]),
            knowledge_kind=str(row["knowledge_kind"]),
            epistemic_status=str(row["epistemic_status"]),
            title=str(row["title"]) if row["title"] is not None else None,
            body=str(row["body"]),
            shared_input_count=int(row["shared_input_count"]),
        )
