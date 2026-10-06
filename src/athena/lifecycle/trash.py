"""Reversible canonical trash/restore lifecycle for supported entities."""

from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from athena.chat.models import ChatSummary
from athena.chat.service import ChatService
from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


class LifecycleTrashError(RuntimeError):
    """Base error for reversible lifecycle transitions."""


class LifecycleTrashNotFoundError(LookupError):
    """Requested canonical entity does not exist."""


class LifecycleTrashUnsupportedError(LifecycleTrashError):
    """Entity type has no reversible trash contract."""


class LifecycleTrashStateError(LifecycleTrashError):
    """Entity is not in the state required for the requested transition."""


@dataclass(frozen=True, slots=True)
class LifecycleTransitionResult:
    entity_id: uuid.UUID
    entity_type: str
    lifecycle_state: str
    commit_id: uuid.UUID
    affected_entity_ids: tuple[uuid.UUID, ...]


class LifecycleTrashService:
    """Durably trash and restore standard chats without creating deletion tombstones."""

    def __init__(self, *, database: SQLiteDatabase, chat: ChatService) -> None:
        self.database = database
        self.chat = chat

    def trash_chat(self, chat_id: uuid.UUID) -> LifecycleTransitionResult:
        return self._transition_chat(chat_id, from_state="active", to_state="trashed")

    def restore_chat(self, chat_id: uuid.UUID) -> LifecycleTransitionResult:
        return self._transition_chat(chat_id, from_state="trashed", to_state="active")

    def list_trashed_chats(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[ChatSummary, ...]:
        if limit < 1 or limit > 500:
            raise ValueError("Trash list limit must be between 1 and 500.")
        if offset < 0:
            raise ValueError("Trash list offset must be zero or greater.")
        rows = self.database.connection.execute(
            """
            SELECT
                c.chat_id,
                c.started_at_us,
                c.ended_at_us,
                c.archive_mode,
                c.lifecycle_state,
                COALESCE(p.pinned, 0) AS pinned,
                COUNT(m.message_id) AS message_count
            FROM chats AS c
            LEFT JOIN chat_messages AS m
              ON m.chat_id = c.chat_id
            LEFT JOIN chat_preferences AS p
              ON p.chat_id = c.chat_id
            WHERE c.lifecycle_state = 'trashed'
            GROUP BY
                c.chat_id,
                c.started_at_us,
                c.ended_at_us,
                c.archive_mode,
                c.lifecycle_state,
                p.pinned
            ORDER BY c.started_at_us DESC, c.chat_id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return tuple(
            ChatSummary(
                chat_id=uuid_from_blob(bytes(row["chat_id"])),
                started_at_us=int(row["started_at_us"]),
                ended_at_us=(
                    int(row["ended_at_us"]) if row["ended_at_us"] is not None else None
                ),
                archive_mode=str(row["archive_mode"]),
                lifecycle_state=str(row["lifecycle_state"]),
                message_count=int(row["message_count"]),
                pinned=bool(int(row["pinned"])),
            )
            for row in rows
        )

    def _transition_chat(
        self,
        chat_id: uuid.UUID,
        *,
        from_state: str,
        to_state: str,
    ) -> LifecycleTransitionResult:
        actor_id = self.chat.ensure_local_user()
        transitioned_at_us = utc_now_us()
        commit_id = new_uuid7()
        operation = "trash" if to_state == "trashed" else "restore"
        reason = (
            "explicit user trash transition"
            if to_state == "trashed"
            else "explicit user restore transition"
        )

        with self.database.write_transaction() as connection:
            chat_row = connection.execute(
                """
                SELECT
                    c.archive_mode,
                    c.lifecycle_state,
                    e.entity_type,
                    e.protection_scope_id
                FROM chats AS c
                JOIN entity_registry AS e
                  ON e.entity_id = c.chat_id
                WHERE c.chat_id = ?
                """,
                (uuid_to_blob(chat_id),),
            ).fetchone()
            if chat_row is None:
                raise LifecycleTrashNotFoundError(str(chat_id))
            if str(chat_row["entity_type"]) != "chat":
                raise LifecycleTrashUnsupportedError("Trash target is not a chat.")
            if str(chat_row["archive_mode"]) != "standard":
                raise LifecycleTrashUnsupportedError(
                    "Only standard archived chats have a reversible trash contract."
                )
            if chat_row["protection_scope_id"] is not None:
                raise LifecycleTrashUnsupportedError(
                    "Protected chats require protection-scope-aware trash semantics."
                )
            current_state = str(chat_row["lifecycle_state"])
            if current_state != from_state:
                raise LifecycleTrashStateError(
                    f"Chat lifecycle state is {current_state!r}; expected {from_state!r}."
                )

            cursor = connection.execute(
                """
                INSERT INTO commit_records (
                    commit_id,
                    committed_at_us,
                    actor_id,
                    operation_type,
                    reason
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(commit_id),
                    transitioned_at_us,
                    uuid_to_blob(actor_id),
                    f"lifecycle.{operation}.chat",
                    reason,
                ),
            )
            if cursor.lastrowid is None:
                raise LifecycleTrashError(
                    "SQLite did not return a lifecycle transition commit sequence."
                )
            commit_seq = int(cursor.lastrowid)

            affected: list[uuid.UUID] = [chat_id]
            child_rows = connection.execute(
                """
                SELECT m.message_id, e.lifecycle_state, e.protection_scope_id
                FROM chat_messages AS m
                JOIN entity_registry AS e
                  ON e.entity_id = m.message_id
                WHERE m.chat_id = ?
                ORDER BY m.sequence_no ASC, m.message_id ASC
                """,
                (uuid_to_blob(chat_id),),
            ).fetchall()

            for row in child_rows:
                child_state = str(row["lifecycle_state"])
                if row["protection_scope_id"] is not None:
                    raise LifecycleTrashUnsupportedError(
                        "Protected chat messages require protection-scope-aware trash semantics."
                    )
                if to_state == "trashed" and child_state == "active":
                    child_id = uuid_from_blob(bytes(row["message_id"]))
                    self._transition_entity(
                        connection,
                        entity_id=child_id,
                        actor_id=actor_id,
                        commit_seq=commit_seq,
                        from_state="active",
                        to_state="trashed",
                        reason=reason,
                    )
                    affected.append(child_id)
                elif to_state == "active" and child_state == "trashed":
                    child_id = uuid_from_blob(bytes(row["message_id"]))
                    self._transition_entity(
                        connection,
                        entity_id=child_id,
                        actor_id=actor_id,
                        commit_seq=commit_seq,
                        from_state="trashed",
                        to_state="active",
                        reason=reason,
                    )
                    affected.append(child_id)

            self._transition_entity(
                connection,
                entity_id=chat_id,
                actor_id=actor_id,
                commit_seq=commit_seq,
                from_state=from_state,
                to_state=to_state,
                reason=reason,
            )

            updated = connection.execute(
                """
                UPDATE chats
                SET lifecycle_state = ?
                WHERE chat_id = ?
                  AND lifecycle_state = ?
                """,
                (to_state, uuid_to_blob(chat_id), from_state),
            )
            if updated.rowcount != 1:
                raise LifecycleTrashError(
                    "Canonical chat lifecycle row changed during transition."
                )

            for affected_id in affected:
                connection.execute(
                    """
                    INSERT INTO commit_changes (
                        commit_seq,
                        entity_id,
                        revision_id,
                        change_type
                    ) VALUES (?, ?, NULL, ?)
                    """,
                    (
                        commit_seq,
                        uuid_to_blob(affected_id),
                        "trashed" if to_state == "trashed" else "restored",
                    ),
                )

        return LifecycleTransitionResult(
            entity_id=chat_id,
            entity_type="chat",
            lifecycle_state=to_state,
            commit_id=commit_id,
            affected_entity_ids=tuple(affected),
        )

    @staticmethod
    def _transition_entity(
        connection: sqlite3.Connection,
        *,
        entity_id: uuid.UUID,
        actor_id: uuid.UUID,
        commit_seq: int,
        from_state: str,
        to_state: str,
        reason: str,
    ) -> None:
        entity_blob = uuid_to_blob(entity_id)
        row = connection.execute(
            """
            SELECT lifecycle_state, protection_scope_id
            FROM entity_registry
            WHERE entity_id = ?
            """,
            (entity_blob,),
        ).fetchone()
        if row is None:
            raise LifecycleTrashNotFoundError(str(entity_id))
        if str(row["lifecycle_state"]) != from_state:
            raise LifecycleTrashStateError(
                f"Entity lifecycle state changed; expected {from_state!r}."
            )

        closed = connection.execute(
            """
            UPDATE entity_state_history
            SET valid_to_commit_seq = ?
            WHERE entity_id = ?
              AND valid_to_commit_seq IS NULL
            """,
            (commit_seq, entity_blob),
        )
        if closed.rowcount != 1:
            raise LifecycleTrashError(
                "Entity has ambiguous open lifecycle history."
            )

        protection_scope = (
            bytes(row["protection_scope_id"])
            if row["protection_scope_id"] is not None
            else None
        )
        connection.execute(
            """
            INSERT INTO entity_state_history (
                entity_id,
                valid_from_commit_seq,
                valid_to_commit_seq,
                lifecycle_state,
                protection_scope_id,
                changed_by_actor_id,
                reason
            ) VALUES (?, ?, NULL, ?, ?, ?, ?)
            """,
            (
                entity_blob,
                commit_seq,
                to_state,
                protection_scope,
                uuid_to_blob(actor_id),
                reason,
            ),
        )

        updated = connection.execute(
            """
            UPDATE entity_registry
            SET lifecycle_state = ?
            WHERE entity_id = ?
              AND lifecycle_state = ?
            """,
            (to_state, entity_blob, from_state),
        )
        if updated.rowcount != 1:
            raise LifecycleTrashError(
                "Entity registry lifecycle transition failed."
            )
