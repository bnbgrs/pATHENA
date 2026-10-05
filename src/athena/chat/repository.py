"""Transactional persistence for standard archived chats."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid

from athena.chat.models import (
    ChatForkOrigin,
    ChatMessage,
    ChatSummary,
    ChatThread,
    MessageType,
)
from athena.chat.send_identity import (
    SendOperationState,
    SendOperationStatus,
    assistant_message_id_for_operation,
    user_message_id_for_operation,
)
from athena.common.ids import new_uuid7, uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase


class ChatNotFoundError(LookupError):
    """Raised when a requested chat does not exist."""


class ActorNotFoundError(LookupError):
    """Raised when a requested actor does not exist or is inactive."""


class ChatMessageNotFoundError(LookupError):
    """Raised when a requested message is not part of the requested chat."""


class ChatRevisionConflictError(RuntimeError):
    """Raised when a chat mutation targets a stale message revision."""


class UnsupportedMessageEditError(ValueError):
    """Raised when an immutable chat-message edit is not permitted."""


class UnsupportedChatForkError(ValueError):
    """Raised when a chat cannot be forked without weakening protection semantics."""


class UnsupportedArchiveModeError(ValueError):
    """Raised when this persistent repository cannot safely handle a mode."""


class ChatRepository:
    """Minimal v1 chat repository used by Vertical Slice 1.

    Only ``standard`` chats are accepted here. ``temporary`` requires TTL and
    lifecycle machinery; ``do_not_store`` must not route its full payload into
    persistent storage. Those modes are introduced by their dedicated slices.
    """

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database

    def find_active_actor(
        self,
        *,
        actor_type: str,
        display_name: str | None = None,
    ) -> uuid.UUID | None:
        row = self.database.connection.execute(
            """
            SELECT actor_id
            FROM actors
            WHERE actor_type = ?
              AND display_name IS ?
              AND active = 1
            ORDER BY created_at_us ASC, actor_id ASC
            LIMIT 1
            """,
            (actor_type, display_name),
        ).fetchone()
        if row is None:
            return None
        return uuid_from_blob(bytes(row["actor_id"]))

    def ensure_actor(
        self,
        *,
        actor_type: str,
        display_name: str | None = None,
    ) -> uuid.UUID:
        """Return one active actor identity, creating it atomically if absent.

        Lookup and insertion share one BEGIN IMMEDIATE transaction so concurrent
        writers cannot both persist the same logical actor identity.
        """
        with self.database.write_transaction() as connection:
            row = connection.execute(
                """
                SELECT actor_id
                FROM actors
                WHERE actor_type = ?
                  AND display_name IS ?
                  AND active = 1
                ORDER BY created_at_us ASC, actor_id ASC
                LIMIT 1
                """,
                (actor_type, display_name),
            ).fetchone()
            if row is not None:
                return uuid_from_blob(bytes(row["actor_id"]))

            actor_id = new_uuid7()
            connection.execute(
                """
                INSERT INTO actors (
                    actor_id, actor_type, display_name, plugin_id, created_at_us, active
                ) VALUES (?, ?, ?, NULL, ?, 1)
                """,
                (
                    uuid_to_blob(actor_id),
                    actor_type,
                    display_name,
                    utc_now_us(),
                ),
            )
            return actor_id

    def create_actor(self, *, actor_type: str, display_name: str | None = None) -> uuid.UUID:
        actor_id = new_uuid7()
        created_at_us = utc_now_us()

        with self.database.write_transaction() as connection:
            connection.execute(
                """
                INSERT INTO actors (
                    actor_id, actor_type, display_name, plugin_id, created_at_us, active
                ) VALUES (?, ?, ?, NULL, ?, 1)
                """,
                (uuid_to_blob(actor_id), actor_type, display_name, created_at_us),
            )

        return actor_id

    def create_chat(
        self,
        *,
        actor_id: uuid.UUID,
        archive_mode: str = "standard",
        chat_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        if archive_mode != "standard":
            raise UnsupportedArchiveModeError(
                "Vertical Slice 1 persists only standard chats. Temporary and "
                "do_not_store modes require their dedicated lifecycle paths."
            )

        resolved_chat_id = (
            chat_id
            if chat_id is not None
            else new_uuid7()
        )

        with self.database.write_transaction() as connection:
            self._require_active_actor(
                connection,
                actor_id,
            )

            if chat_id is not None:
                existing = connection.execute(
                    """
                    SELECT 1
                    FROM chats
                    WHERE chat_id = ?
                    """,
                    (
                        uuid_to_blob(
                            resolved_chat_id
                        ),
                    ),
                ).fetchone()

                if existing is not None:
                    self._require_standard_chat(
                        connection,
                        resolved_chat_id,
                    )
                    return resolved_chat_id

            commit_id = new_uuid7()
            provenance_id = new_uuid7()
            created_at_us = utc_now_us()

            commit_seq = self._insert_commit(
                connection,
                commit_id=commit_id,
                actor_id=actor_id,
                operation_type="chat.create",
                committed_at_us=created_at_us,
            )

            self._insert_entity(
                connection,
                entity_id=resolved_chat_id,
                entity_type="chat",
                actor_id=actor_id,
                created_at_us=created_at_us,
                commit_seq=commit_seq,
            )

            connection.execute(
                """
                INSERT INTO chats (
                    chat_id,
                    started_at_us,
                    ended_at_us,
                    archive_mode,
                    lifecycle_state,
                    protection_scope_id
                ) VALUES (?, ?, NULL, ?, 'active', NULL)
                """,
                (
                    uuid_to_blob(
                        resolved_chat_id
                    ),
                    created_at_us,
                    archive_mode,
                ),
            )

            self._insert_provenance(
                connection,
                provenance_id=provenance_id,
                entity_id=resolved_chat_id,
                revision_id=None,
                operation="chat.create",
                actor_id=actor_id,
                created_at_us=created_at_us,
            )

            connection.execute(
                """
                INSERT INTO commit_changes (
                    commit_seq,
                    entity_id,
                    revision_id,
                    change_type
                ) VALUES (?, ?, NULL, 'create')
                """,
                (
                    commit_seq,
                    uuid_to_blob(
                        resolved_chat_id
                    ),
                ),
            )

        return resolved_chat_id

    def fork_chat_from_message(
        self,
        *,
        chat_id: uuid.UUID,
        source_message_id: uuid.UUID,
        source_revision_id: uuid.UUID,
        actor_id: uuid.UUID,
    ) -> uuid.UUID:
        """Create an independent standard chat through one exact source revision.

        The fork is a real persisted branch: history through the selected message
        is copied into new immutable message entities, while provenance_inputs
        points both the new chat and every copied message at the exact source
        entity/revision they derive from.
        """
        fork_chat_id = new_uuid7()
        chat_provenance_id = new_uuid7()
        chat_commit_id = new_uuid7()
        forked_at_us = utc_now_us()

        with self.database.write_transaction() as connection:
            self._require_active_actor(connection, actor_id)
            self._require_standard_chat(connection, chat_id)

            fork_point = connection.execute(
                """
                SELECT
                    m.sequence_no,
                    h.current_revision_id AS revision_id,
                    c.protection_scope_id AS chat_protection_scope_id,
                    ce.protection_scope_id AS entity_protection_scope_id
                FROM chat_messages AS m
                JOIN entity_heads AS h
                  ON h.entity_id = m.message_id
                JOIN chats AS c
                  ON c.chat_id = m.chat_id
                JOIN entity_registry AS ce
                  ON ce.entity_id = c.chat_id
                WHERE m.chat_id = ?
                  AND m.message_id = ?
                """,
                (
                    uuid_to_blob(chat_id),
                    uuid_to_blob(source_message_id),
                ),
            ).fetchone()
            if fork_point is None:
                raise ChatMessageNotFoundError(str(source_message_id))

            current_fork_revision_id = uuid_from_blob(
                bytes(fork_point["revision_id"])
            )
            if current_fork_revision_id != source_revision_id:
                raise ChatRevisionConflictError(
                    "The requested fork point revision is no longer current."
                )

            if (
                fork_point["chat_protection_scope_id"] is not None
                or fork_point["entity_protection_scope_id"] is not None
            ):
                raise UnsupportedChatForkError(
                    "Protected chats require protection-scope-aware fork semantics."
                )

            fork_sequence = int(fork_point["sequence_no"])

            source_rows = connection.execute(
                """
                SELECT
                    m.message_id,
                    m.sequence_no,
                    m.message_type,
                    m.actor_id,
                    r.revision_id,
                    r.payload_hash,
                    mr.content,
                    mr.content_format,
                    mr.protected_payload_id,
                    me.protection_scope_id AS entity_protection_scope_id
                FROM chat_messages AS m
                JOIN entity_heads AS h
                  ON h.entity_id = m.message_id
                JOIN revisions AS r
                  ON r.revision_id = h.current_revision_id
                JOIN chat_message_revisions AS mr
                  ON mr.revision_id = r.revision_id
                JOIN entity_registry AS me
                  ON me.entity_id = m.message_id
                WHERE m.chat_id = ?
                  AND m.sequence_no <= ?
                ORDER BY m.sequence_no ASC
                """,
                (uuid_to_blob(chat_id), fork_sequence),
            ).fetchall()

            if any(
                row["protected_payload_id"] is not None
                or row["entity_protection_scope_id"] is not None
                for row in source_rows
            ):
                raise UnsupportedChatForkError(
                    "Protected message revisions require protection-scope-aware fork semantics."
                )

            chat_commit_seq = self._insert_commit(
                connection,
                commit_id=chat_commit_id,
                actor_id=actor_id,
                operation_type="chat.fork",
                committed_at_us=forked_at_us,
            )
            self._insert_entity(
                connection,
                entity_id=fork_chat_id,
                entity_type="chat",
                actor_id=actor_id,
                created_at_us=forked_at_us,
                commit_seq=chat_commit_seq,
            )
            connection.execute(
                """
                INSERT INTO chats (
                    chat_id,
                    started_at_us,
                    ended_at_us,
                    archive_mode,
                    lifecycle_state,
                    protection_scope_id
                ) VALUES (?, ?, NULL, 'standard', 'active', NULL)
                """,
                (uuid_to_blob(fork_chat_id), forked_at_us),
            )
            self._insert_provenance(
                connection,
                provenance_id=chat_provenance_id,
                entity_id=fork_chat_id,
                revision_id=None,
                operation="chat.fork",
                actor_id=actor_id,
                created_at_us=forked_at_us,
            )
            self._insert_provenance_input(
                connection,
                provenance_id=chat_provenance_id,
                input_entity_id=source_message_id,
                input_revision_id=source_revision_id,
                input_role="fork_point",
                ordinal=0,
            )
            connection.execute(
                """
                INSERT INTO commit_changes (
                    commit_seq, entity_id, revision_id, change_type
                ) VALUES (?, ?, NULL, 'create')
                """,
                (chat_commit_seq, uuid_to_blob(fork_chat_id)),
            )

            for row in source_rows:
                source_id = uuid_from_blob(bytes(row["message_id"]))
                source_revision_id = uuid_from_blob(bytes(row["revision_id"]))
                message_actor_blob = row["actor_id"]
                message_actor_id = (
                    uuid_from_blob(bytes(message_actor_blob))
                    if message_actor_blob is not None
                    else None
                )
                content = str(row["content"]) if row["content"] is not None else None
                content_format = (
                    str(row["content_format"])
                    if row["content_format"] is not None
                    else None
                )

                forked_message_id = new_uuid7()
                forked_revision_id = new_uuid7()
                message_provenance_id = new_uuid7()
                self._insert_entity(
                    connection,
                    entity_id=forked_message_id,
                    entity_type="chat_message",
                    actor_id=actor_id,
                    created_at_us=forked_at_us,
                    commit_seq=chat_commit_seq,
                )
                self._insert_provenance(
                    connection,
                    provenance_id=message_provenance_id,
                    entity_id=forked_message_id,
                    revision_id=forked_revision_id,
                    operation="chat_message.fork",
                    actor_id=actor_id,
                    created_at_us=forked_at_us,
                )
                self._insert_provenance_input(
                    connection,
                    provenance_id=message_provenance_id,
                    input_entity_id=source_id,
                    input_revision_id=source_revision_id,
                    input_role="fork_source",
                    ordinal=0,
                )
                connection.execute(
                    """
                    INSERT INTO revisions (
                        revision_id,
                        entity_id,
                        revision_no,
                        parent_revision_id,
                        created_at_us,
                        created_by_actor_id,
                        provenance_id,
                        schema_version,
                        payload_hash,
                        change_kind,
                        commit_id
                    ) VALUES (?, ?, 1, NULL, ?, ?, ?, 1, ?, 'create', ?)
                    """,
                    (
                        uuid_to_blob(forked_revision_id),
                        uuid_to_blob(forked_message_id),
                        forked_at_us,
                        uuid_to_blob(actor_id),
                        uuid_to_blob(message_provenance_id),
                        bytes(row["payload_hash"]),
                        uuid_to_blob(chat_commit_id),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO entity_heads (
                        entity_id, current_revision_id, current_revision_no
                    ) VALUES (?, ?, 1)
                    """,
                    (
                        uuid_to_blob(forked_message_id),
                        uuid_to_blob(forked_revision_id),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO chat_messages (
                        message_id, chat_id, sequence_no, message_type, actor_id
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        uuid_to_blob(forked_message_id),
                        uuid_to_blob(fork_chat_id),
                        int(row["sequence_no"]),
                        str(row["message_type"]),
                        (
                            uuid_to_blob(message_actor_id)
                            if message_actor_id is not None
                            else None
                        ),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO chat_message_revisions (
                        revision_id, content, content_format, protected_payload_id
                    ) VALUES (?, ?, ?, NULL)
                    """,
                    (
                        uuid_to_blob(forked_revision_id),
                        content,
                        content_format,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO commit_changes (
                        commit_seq, entity_id, revision_id, change_type
                    ) VALUES (?, ?, ?, 'create')
                    """,
                    (
                        chat_commit_seq,
                        uuid_to_blob(forked_message_id),
                        uuid_to_blob(forked_revision_id),
                    ),
                )

        return fork_chat_id

    def edit_user_message(
        self,
        *,
        chat_id: uuid.UUID,
        message_id: uuid.UUID,
        expected_revision_id: uuid.UUID,
        actor_id: uuid.UUID,
        content: str,
        content_format: str = "text/plain",
    ) -> ChatMessage:
        """Create a new immutable revision for one user-authored message."""
        revision_id = new_uuid7()
        provenance_id = new_uuid7()
        commit_id = new_uuid7()
        created_at_us = utc_now_us()
        payload_hash = _message_payload_hash(content, content_format)
        if any(not isinstance(source_id, uuid.UUID) for source_id in source_ids):
            raise TypeError("Chat message source IDs must be UUIDs.")
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("Chat message source IDs must be unique.")

        with self.database.write_transaction() as connection:
            self._require_active_actor(connection, actor_id)
            self._require_standard_chat(connection, chat_id)

            row = connection.execute(
                """
                SELECT
                    m.sequence_no,
                    m.message_type,
                    m.actor_id,
                    h.current_revision_id,
                    h.current_revision_no,
                    c.protection_scope_id AS chat_protection_scope_id,
                    e.protection_scope_id AS message_protection_scope_id,
                    mr.protected_payload_id
                FROM chat_messages AS m
                JOIN entity_heads AS h
                  ON h.entity_id = m.message_id
                JOIN chats AS c
                  ON c.chat_id = m.chat_id
                JOIN entity_registry AS e
                  ON e.entity_id = m.message_id
                JOIN chat_message_revisions AS mr
                  ON mr.revision_id = h.current_revision_id
                WHERE m.chat_id = ?
                  AND m.message_id = ?
                """,
                (
                    uuid_to_blob(chat_id),
                    uuid_to_blob(message_id),
                ),
            ).fetchone()
            if row is None:
                raise ChatMessageNotFoundError(str(message_id))
            current_revision_id = uuid_from_blob(
                bytes(row["current_revision_id"])
            )
            if current_revision_id != expected_revision_id:
                raise ChatRevisionConflictError(
                    "The user message changed before this edit was applied."
                )

            if str(row["message_type"]) != MessageType.USER.value:
                raise UnsupportedMessageEditError(
                    "Only user-authored chat messages can be edited."
                )
            if (
                row["chat_protection_scope_id"] is not None
                or row["message_protection_scope_id"] is not None
                or row["protected_payload_id"] is not None
            ):
                raise UnsupportedMessageEditError(
                    "Protected messages require protection-scope-aware edit semantics."
                )

            message_actor_blob = row["actor_id"]
            if message_actor_blob is None:
                raise UnsupportedMessageEditError(
                    "A user message without an actor cannot be edited."
                )
            message_actor_id = uuid_from_blob(bytes(message_actor_blob))
            if message_actor_id != actor_id:
                raise UnsupportedMessageEditError(
                    "A user message can only be edited by its original actor."
                )

            parent_revision_id = current_revision_id
            revision_no = int(row["current_revision_no"]) + 1

            commit_seq = self._insert_commit(
                connection,
                commit_id=commit_id,
                actor_id=actor_id,
                operation_type="chat_message.edit",
                committed_at_us=created_at_us,
            )
            self._insert_provenance(
                connection,
                provenance_id=provenance_id,
                entity_id=message_id,
                revision_id=revision_id,
                operation="chat_message.edit",
                actor_id=actor_id,
                created_at_us=created_at_us,
            )
            self._insert_provenance_input(
                connection,
                provenance_id=provenance_id,
                input_entity_id=message_id,
                input_revision_id=parent_revision_id,
                input_role="prior_revision",
                ordinal=0,
            )
            connection.execute(
                """
                INSERT INTO revisions (
                    revision_id,
                    entity_id,
                    revision_no,
                    parent_revision_id,
                    created_at_us,
                    created_by_actor_id,
                    provenance_id,
                    schema_version,
                    payload_hash,
                    change_kind,
                    commit_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 'update', ?)
                """,
                (
                    uuid_to_blob(revision_id),
                    uuid_to_blob(message_id),
                    revision_no,
                    uuid_to_blob(parent_revision_id),
                    created_at_us,
                    uuid_to_blob(actor_id),
                    uuid_to_blob(provenance_id),
                    payload_hash,
                    uuid_to_blob(commit_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO chat_message_revisions (
                    revision_id, content, content_format, protected_payload_id
                ) VALUES (?, ?, ?, NULL)
                """,
                (
                    uuid_to_blob(revision_id),
                    content,
                    content_format,
                ),
            )
            connection.execute(
                """
                UPDATE entity_heads
                SET current_revision_id = ?,
                    current_revision_no = ?
                WHERE entity_id = ?
                """,
                (
                    uuid_to_blob(revision_id),
                    revision_no,
                    uuid_to_blob(message_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO commit_changes (
                    commit_seq, entity_id, revision_id, change_type
                ) VALUES (?, ?, ?, 'update')
                """,
                (
                    commit_seq,
                    uuid_to_blob(message_id),
                    uuid_to_blob(revision_id),
                ),
            )

        return ChatMessage(
            message_id=message_id,
            chat_id=chat_id,
            sequence_no=int(row["sequence_no"]),
            message_type=MessageType.USER,
            actor_id=actor_id,
            created_at_us=created_at_us,
            revision_id=revision_id,
            content=content,
            content_format=content_format,
        )

    def append_message(
        self,
        *,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        message_type: MessageType,
        content: str,
        content_format: str = "text/plain",
        message_id: uuid.UUID | None = None,
        source_ids: tuple[uuid.UUID, ...] = (),
    ) -> ChatMessage:
        resolved_message_id = (
            message_id
            if message_id is not None
            else new_uuid7()
        )
        revision_id = new_uuid7()
        provenance_id = new_uuid7()
        commit_id = new_uuid7()
        created_at_us = utc_now_us()
        payload_hash = _message_payload_hash(content, content_format)

        with self.database.write_transaction() as connection:
            self._require_active_actor(connection, actor_id)
            self._require_standard_chat(connection, chat_id)

            next_sequence = int(
                connection.execute(
                    """
                    SELECT COALESCE(MAX(sequence_no), 0) + 1
                    FROM chat_messages
                    WHERE chat_id = ?
                    """,
                    (uuid_to_blob(chat_id),),
                ).fetchone()[0]
            )

            commit_seq = self._insert_commit(
                connection,
                commit_id=commit_id,
                actor_id=actor_id,
                operation_type="chat_message.create",
                committed_at_us=created_at_us,
            )
            self._insert_entity(
                connection,
                entity_id=resolved_message_id,
                entity_type="chat_message",
                actor_id=actor_id,
                created_at_us=created_at_us,
                commit_seq=commit_seq,
            )
            self._insert_provenance(
                connection,
                provenance_id=provenance_id,
                entity_id=resolved_message_id,
                revision_id=revision_id,
                operation="chat_message.create",
                actor_id=actor_id,
                created_at_us=created_at_us,
            )
            for ordinal, source_id in enumerate(source_ids):
                source_row = connection.execute(
                    """
                    SELECT entity_type, lifecycle_state
                    FROM entity_registry
                    WHERE entity_id = ?
                    """,
                    (uuid_to_blob(source_id),),
                ).fetchone()
                if (
                    source_row is None
                    or str(source_row["entity_type"]) != "source"
                    or str(source_row["lifecycle_state"]) != "active"
                ):
                    raise ValueError(
                        "Chat image attachment must reference an active Source entity."
                    )
                self._insert_provenance_input(
                    connection,
                    provenance_id=provenance_id,
                    input_entity_id=source_id,
                    input_revision_id=None,
                    input_role="attachment",
                    ordinal=ordinal,
                )
            connection.execute(
                """
                INSERT INTO revisions (
                    revision_id,
                    entity_id,
                    revision_no,
                    parent_revision_id,
                    created_at_us,
                    created_by_actor_id,
                    provenance_id,
                    schema_version,
                    payload_hash,
                    change_kind,
                    commit_id
                ) VALUES (?, ?, 1, NULL, ?, ?, ?, 1, ?, 'create', ?)
                """,
                (
                    uuid_to_blob(revision_id),
                    uuid_to_blob(resolved_message_id),
                    created_at_us,
                    uuid_to_blob(actor_id),
                    uuid_to_blob(provenance_id),
                    payload_hash,
                    uuid_to_blob(commit_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO entity_heads (
                    entity_id, current_revision_id, current_revision_no
                ) VALUES (?, ?, 1)
                """,
                (uuid_to_blob(resolved_message_id), uuid_to_blob(revision_id)),
            )
            connection.execute(
                """
                INSERT INTO chat_messages (
                    message_id, chat_id, sequence_no, message_type, actor_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(resolved_message_id),
                    uuid_to_blob(chat_id),
                    next_sequence,
                    message_type.value,
                    uuid_to_blob(actor_id),
                ),
            )
            connection.execute(
                """
                INSERT INTO chat_message_revisions (
                    revision_id, content, content_format, protected_payload_id
                ) VALUES (?, ?, ?, NULL)
                """,
                (uuid_to_blob(revision_id), content, content_format),
            )
            connection.execute(
                """
                INSERT INTO commit_changes (
                    commit_seq, entity_id, revision_id, change_type
                ) VALUES (?, ?, ?, 'create')
                """,
                (commit_seq, uuid_to_blob(resolved_message_id), uuid_to_blob(revision_id)),
            )

        return ChatMessage(
            message_id=resolved_message_id,
            chat_id=chat_id,
            sequence_no=next_sequence,
            message_type=message_type,
            actor_id=actor_id,
            created_at_us=created_at_us,
            revision_id=revision_id,
            content=content,
            content_format=content_format,
            source_ids=source_ids,
        )

    def inspect_send_operation(
        self,
        *,
        chat_id: uuid.UUID,
        operation_id: uuid.UUID,
        expected_content: str,
    ) -> SendOperationStatus:
        """Inspect durable send state without performing a mutation."""
        connection = self.database.connection
        self._require_standard_chat(
            connection,
            chat_id,
        )

        user_message_id = (
            user_message_id_for_operation(
                operation_id
            )
        )
        assistant_message_id = (
            assistant_message_id_for_operation(
                operation_id
            )
        )

        rows = connection.execute(
            """
            SELECT
                m.message_id,
                m.chat_id,
                m.sequence_no,
                m.message_type,
                m.actor_id,
                r.created_at_us,
                r.revision_id,
                r.provenance_id,
                mr.content,
                mr.content_format
            FROM chat_messages AS m
            JOIN entity_heads AS h
              ON h.entity_id = m.message_id
            JOIN revisions AS r
              ON r.revision_id = h.current_revision_id
            JOIN chat_message_revisions AS mr
              ON mr.revision_id = r.revision_id
            WHERE m.message_id IN (?, ?)
            """,
            (
                uuid_to_blob(
                    user_message_id
                ),
                uuid_to_blob(
                    assistant_message_id
                ),
            ),
        ).fetchall()

        messages = {
            message.message_id: message
            for message in (
                self._message_from_row(row)
                for row in rows
            )
        }

        user_message = messages.get(
            user_message_id
        )
        assistant_message = messages.get(
            assistant_message_id
        )

        if (
            user_message is None
            and assistant_message is None
        ):
            state = SendOperationState.ABSENT
        elif user_message is None:
            state = SendOperationState.CONFLICT
        elif (
            user_message.chat_id != chat_id
            or user_message.message_type
            is not MessageType.USER
            or user_message.content
            != expected_content
        ):
            state = SendOperationState.CONFLICT
        elif assistant_message is None:
            state = SendOperationState.INCOMPLETE
        elif (
            assistant_message.chat_id != chat_id
            or assistant_message.message_type
            is not MessageType.ASSISTANT
            or assistant_message.sequence_no
            != user_message.sequence_no + 1
        ):
            state = SendOperationState.CONFLICT
        else:
            state = SendOperationState.COMPLETE

        return SendOperationStatus(
            chat_id=chat_id,
            operation_id=operation_id,
            user_message_id=user_message_id,
            assistant_message_id=(
                assistant_message_id
            ),
            state=state,
        )

    def set_chat_pinned(
        self,
        *,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        pinned: bool,
    ) -> None:
        """Persist one local-user conversation favorite without touching Knowledge."""
        if not isinstance(pinned, bool):
            raise TypeError("Chat pinned state must be bool.")

        with self.database.write_transaction() as connection:
            self._require_standard_chat(connection, chat_id)
            connection.execute(
                """
                INSERT INTO chat_preferences (
                    chat_id,
                    pinned,
                    updated_at_us,
                    updated_by_actor_id
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    pinned = excluded.pinned,
                    updated_at_us = excluded.updated_at_us,
                    updated_by_actor_id = excluded.updated_by_actor_id
                """,
                (
                    uuid_to_blob(chat_id),
                    1 if pinned else 0,
                    utc_now_us(),
                    uuid_to_blob(actor_id),
                ),
            )

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummary, ...]:
        if limit < 1 or limit > 500:
            raise ValueError("Chat list limit must be between 1 and 500.")
        if offset < 0:
            raise ValueError("Chat list offset must be zero or greater.")

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
            WHERE c.lifecycle_state != 'deleted'
            GROUP BY
                c.chat_id,
                c.started_at_us,
                c.ended_at_us,
                c.archive_mode,
                c.lifecycle_state,
                p.pinned
            ORDER BY COALESCE(p.pinned, 0) DESC,
                     c.started_at_us DESC,
                     c.chat_id DESC
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

    def get_fork_origin(self, chat_id: uuid.UUID) -> ChatForkOrigin | None:
        """Return the exact persisted fork point for a branched chat."""
        self._require_standard_chat(self.database.connection, chat_id)
        rows = self.database.connection.execute(
            """
            SELECT
                i.input_entity_id,
                i.input_revision_id
            FROM provenance_records AS p
            JOIN provenance_inputs AS i
              ON i.provenance_id = p.provenance_id
            WHERE p.subject_entity_id = ?
              AND p.subject_revision_id IS NULL
              AND p.operation = 'chat.fork'
              AND i.input_role = 'fork_point'
              AND i.ordinal = 0
            ORDER BY p.created_at_us ASC, p.provenance_id ASC
            """,
            (uuid_to_blob(chat_id),),
        ).fetchall()
        if not rows:
            return None
        if len(rows) != 1:
            raise RuntimeError("A forked chat must have exactly one canonical fork point.")

        revision_blob = rows[0]["input_revision_id"]
        if revision_blob is None:
            raise RuntimeError("A forked chat is missing its source revision identity.")

        return ChatForkOrigin(
            chat_id=chat_id,
            source_message_id=uuid_from_blob(bytes(rows[0]["input_entity_id"])),
            source_revision_id=uuid_from_blob(bytes(revision_blob)),
        )

    def load_chat(self, chat_id: uuid.UUID) -> ChatThread:
        connection = self.database.connection
        chat_row = connection.execute(
            """
            SELECT chat_id, started_at_us, ended_at_us, archive_mode, lifecycle_state
            FROM chats
            WHERE chat_id = ?
              AND lifecycle_state != 'deleted'
            """,
            (uuid_to_blob(chat_id),),
        ).fetchone()
        if chat_row is None:
            raise ChatNotFoundError(str(chat_id))

        message_rows = connection.execute(
            """
            SELECT
                m.message_id,
                m.chat_id,
                m.sequence_no,
                m.message_type,
                m.actor_id,
                r.created_at_us,
                r.revision_id,
                mr.content,
                mr.content_format
            FROM chat_messages AS m
            JOIN entity_heads AS h
              ON h.entity_id = m.message_id
            JOIN revisions AS r
              ON r.revision_id = h.current_revision_id
            JOIN chat_message_revisions AS mr
              ON mr.revision_id = r.revision_id
            WHERE m.chat_id = ?
            ORDER BY m.sequence_no ASC
            """,
            (uuid_to_blob(chat_id),),
        ).fetchall()

        messages = tuple(
            self._message_from_row(
                row,
                source_ids=self._attachment_source_ids(
                    connection,
                    uuid_from_blob(bytes(row["provenance_id"])),
                ),
            )
            for row in message_rows
        )
        return ChatThread(
            chat_id=uuid_from_blob(bytes(chat_row["chat_id"])),
            started_at_us=int(chat_row["started_at_us"]),
            ended_at_us=(
                int(chat_row["ended_at_us"])
                if chat_row["ended_at_us"] is not None
                else None
            ),
            archive_mode=str(chat_row["archive_mode"]),
            lifecycle_state=str(chat_row["lifecycle_state"]),
            messages=messages,
        )

    @staticmethod
    def _message_from_row(
        row: sqlite3.Row,
        *,
        source_ids: tuple[uuid.UUID, ...] = (),
    ) -> ChatMessage:
        actor_blob = row["actor_id"]
        return ChatMessage(
            message_id=uuid_from_blob(bytes(row["message_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            sequence_no=int(row["sequence_no"]),
            message_type=MessageType(str(row["message_type"])),
            actor_id=uuid_from_blob(bytes(actor_blob)) if actor_blob is not None else None,
            created_at_us=int(row["created_at_us"]),
            revision_id=uuid_from_blob(bytes(row["revision_id"])),
            content=str(row["content"]) if row["content"] is not None else None,
            content_format=(
                str(row["content_format"])
                if row["content_format"] is not None
                else None
            ),
            source_ids=source_ids,
        )

    @staticmethod
    def _attachment_source_ids(
        connection: sqlite3.Connection,
        provenance_id: uuid.UUID,
    ) -> tuple[uuid.UUID, ...]:
        rows = connection.execute(
            """
            SELECT i.input_entity_id
            FROM provenance_inputs AS i
            JOIN entity_registry AS e
              ON e.entity_id = i.input_entity_id
            WHERE i.provenance_id = ?
              AND i.input_role = 'attachment'
              AND i.input_revision_id IS NULL
              AND e.entity_type = 'source'
            ORDER BY i.ordinal ASC, i.input_entity_id ASC
            """,
            (uuid_to_blob(provenance_id),),
        ).fetchall()
        return tuple(
            uuid_from_blob(bytes(row["input_entity_id"]))
            for row in rows
        )

    @staticmethod
    def _require_active_actor(connection: sqlite3.Connection, actor_id: uuid.UUID) -> None:
        row = connection.execute(
            "SELECT active FROM actors WHERE actor_id = ?",
            (uuid_to_blob(actor_id),),
        ).fetchone()
        if row is None or int(row["active"]) != 1:
            raise ActorNotFoundError(str(actor_id))

    @staticmethod
    def _require_standard_chat(connection: sqlite3.Connection, chat_id: uuid.UUID) -> None:
        row = connection.execute(
            "SELECT archive_mode, lifecycle_state "
            "FROM chats WHERE chat_id = ?",
            (uuid_to_blob(chat_id),),
        ).fetchone()
        if row is None:
            raise ChatNotFoundError(str(chat_id))
        if str(row["lifecycle_state"]) == "deleted":
            raise ChatNotFoundError(str(chat_id))
        if str(row["archive_mode"]) != "standard":
            raise UnsupportedArchiveModeError(
                "This repository path only accepts standard archived chats."
            )

    @staticmethod
    def _insert_commit(
        connection: sqlite3.Connection,
        *,
        commit_id: uuid.UUID,
        actor_id: uuid.UUID,
        operation_type: str,
        committed_at_us: int,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO commit_records (
                commit_id, committed_at_us, actor_id, operation_type, reason
            ) VALUES (?, ?, ?, ?, NULL)
            """,
            (
                uuid_to_blob(commit_id),
                committed_at_us,
                uuid_to_blob(actor_id),
                operation_type,
            ),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("SQLite did not return a commit sequence.")
        return int(cursor.lastrowid)

    @staticmethod
    def _insert_entity(
        connection: sqlite3.Connection,
        *,
        entity_id: uuid.UUID,
        entity_type: str,
        actor_id: uuid.UUID,
        created_at_us: int,
        commit_seq: int,
    ) -> None:
        entity_blob = uuid_to_blob(entity_id)
        actor_blob = uuid_to_blob(actor_id)
        connection.execute(
            """
            INSERT INTO entity_registry (
                entity_id,
                entity_type,
                domain,
                created_at_us,
                created_by_actor_id,
                lifecycle_state,
                protection_scope_id,
                schema_version
            ) VALUES (?, ?, 'raw_archive', ?, ?, 'active', NULL, 1)
            """,
            (entity_blob, entity_type, created_at_us, actor_blob),
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
            ) VALUES (?, ?, NULL, 'active', NULL, ?, NULL)
            """,
            (entity_blob, commit_seq, actor_blob),
        )

    @staticmethod
    def _insert_provenance_input(
        connection: sqlite3.Connection,
        *,
        provenance_id: uuid.UUID,
        input_entity_id: uuid.UUID,
        input_revision_id: uuid.UUID | None,
        input_role: str,
        ordinal: int,
    ) -> None:
        connection.execute(
            """
            INSERT INTO provenance_inputs (
                provenance_id,
                input_entity_id,
                input_revision_id,
                input_role,
                ordinal
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                uuid_to_blob(provenance_id),
                uuid_to_blob(input_entity_id),
                (
                    uuid_to_blob(input_revision_id)
                    if input_revision_id is not None
                    else None
                ),
                input_role,
                ordinal,
            ),
        )

    @staticmethod
    def _insert_provenance(
        connection: sqlite3.Connection,
        *,
        provenance_id: uuid.UUID,
        entity_id: uuid.UUID,
        revision_id: uuid.UUID | None,
        operation: str,
        actor_id: uuid.UUID,
        created_at_us: int,
    ) -> None:
        connection.execute(
            """
            INSERT INTO provenance_records (
                provenance_id,
                subject_entity_id,
                subject_revision_id,
                operation,
                actor_id,
                created_at_us,
                model_signature_id,
                processing_run_id,
                reason,
                protection_scope_id
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)
            """,
            (
                uuid_to_blob(provenance_id),
                uuid_to_blob(entity_id),
                uuid_to_blob(revision_id) if revision_id is not None else None,
                operation,
                uuid_to_blob(actor_id),
                created_at_us,
            ),
        )


def _message_payload_hash(content: str, content_format: str) -> bytes:
    # For this payload shape (string-only fields), Python's sorted compact JSON
    # encoding is the RFC 8785 canonical representation. A general JCS encoder
    # will be introduced before payloads can contain numeric/object extensions.
    canonical_payload = json.dumps(
        {"content": content, "content_format": content_format},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical_payload).digest()
