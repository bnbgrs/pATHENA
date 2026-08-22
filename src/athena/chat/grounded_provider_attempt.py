"""Durable marker for the irreversible provider-call boundary of a Grounded send."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PROVIDER_ATTEMPT_EXTENSION_VERSION = 1


class GroundedProviderAttemptConflictError(RuntimeError):
    """The provider boundary cannot be marked for the current operation state."""


@dataclass(frozen=True, slots=True)
class GroundedProviderAttempt:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    started_at_us: int


_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "extension_schema_version",
    "started_at_us",
)

_CREATE_SQL = """
CREATE TABLE grounded_provider_attempts (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    started_at_us INTEGER NOT NULL CHECK(started_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


class GroundedProviderAttemptRepository:
    """Persist exactly one marker immediately before the first provider call."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        ChatSendOperationRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        row = self.database.connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'grounded_provider_attempts'"
        ).fetchone()
        if row is None:
            with self.database.write_transaction() as connection:
                connection.execute(_CREATE_SQL)
        columns = self.database.connection.execute(
            "PRAGMA table_info(grounded_provider_attempts)"
        ).fetchall()
        if tuple(str(row["name"]) for row in columns) != _REQUIRED_COLUMNS:
            raise GroundedProviderAttemptConflictError(
                "grounded_provider_attempts has an incompatible extension layout."
            )

    def load(self, operation_id: uuid.UUID) -> GroundedProviderAttempt | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, started_at_us
            FROM grounded_provider_attempts
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        return GroundedProviderAttempt(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            started_at_us=int(row["started_at_us"]),
        )

    def mark_started(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> GroundedProviderAttempt:
        with self.database.write_transaction() as connection:
            operation = connection.execute(
                "SELECT chat_id, mode, state FROM chat_send_operations WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if operation is None:
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt requires an existing send operation."
                )
            if uuid_from_blob(bytes(operation["chat_id"])) != chat_id:
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt chat identity conflicts with send operation."
                )
            if str(operation["mode"]) != "grounded":
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt marker is Grounded-only."
                )
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt may start only from user_committed state."
                )

            existing = connection.execute(
                """
                SELECT operation_id, chat_id, started_at_us
                FROM grounded_provider_attempts WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                attempt = GroundedProviderAttempt(
                    operation_id=uuid_from_blob(bytes(existing["operation_id"])),
                    chat_id=uuid_from_blob(bytes(existing["chat_id"])),
                    started_at_us=int(existing["started_at_us"]),
                )
                if attempt.chat_id != chat_id:
                    raise GroundedProviderAttemptConflictError(
                        "Provider attempt marker belongs to another chat."
                    )
                return attempt

            started_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_provider_attempts (
                    operation_id, chat_id, extension_schema_version, started_at_us
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    GROUNDED_PROVIDER_ATTEMPT_EXTENSION_VERSION,
                    started_at_us,
                ),
            )
        stored_attempt = self.load(operation_id)
        if stored_attempt is None:
            raise RuntimeError("Provider attempt marker disappeared after commit.")
        return stored_attempt
