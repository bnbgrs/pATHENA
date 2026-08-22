"""Durable pre-provider replay checkpoint for Unified Local chat."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.grounded_context_package import GroundedContextPackageRepository
from athena.chat.send_operation import ChatSendOperationMode, ChatSendOperationRepository
from athena.chat.unified_replay import (
    UnifiedReplayProjection,
    UnifiedReplayProjectionError,
    load_unified_replay_projection,
)
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

UNIFIED_REPLAY_INPUT_EXTENSION_VERSION = 1


class UnifiedReplayInputConflictError(RuntimeError):
    """The requested replay checkpoint conflicts with durable operation state."""


class UnifiedReplayInputSchemaError(RuntimeError):
    """The Unified replay checkpoint journal is missing or corrupted."""


@dataclass(frozen=True, slots=True)
class UnifiedReplayInputRecord:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    processing_run_id: uuid.UUID
    context_package_request_id: uuid.UUID
    payload_json: str
    payload_sha256: str
    projection: UnifiedReplayProjection
    created_at_us: int


_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "processing_run_id",
    "context_package_request_id",
    "payload_json",
    "payload_sha256",
    "extension_schema_version",
    "created_at_us",
)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS unified_grounded_replay_inputs (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    processing_run_id BLOB(16) NOT NULL CHECK(length(processing_run_id) = 16),
    context_package_request_id BLOB(16) NOT NULL CHECK(length(context_package_request_id) = 16),
    payload_json TEXT NOT NULL CHECK(length(payload_json) > 1),
    payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256) = 64),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE,
    FOREIGN KEY(processing_run_id)
        REFERENCES processing_runs(processing_run_id) ON DELETE RESTRICT
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _encode_projection(projection: Mapping[str, Any]) -> tuple[str, str]:
    payload_json = json.dumps(
        {"unified_replay_projection": dict(projection)},
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload_json, hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _decode_projection(
    *,
    payload_json: str,
    payload_sha256: str,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    database: SQLiteDatabase,
) -> tuple[dict[str, Any], UnifiedReplayProjection, uuid.UUID]:
    actual_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    if actual_hash != payload_sha256:
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint payload hash does not match its journal row."
        )
    try:
        raw = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint payload is invalid JSON."
        ) from exc
    if not isinstance(raw, dict):
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint payload must be a JSON object."
        )
    root = cast(dict[str, Any], raw)
    projection_raw = root.get("unified_replay_projection")
    if not isinstance(projection_raw, dict):
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint is missing its replay projection."
        )
    projection_payload = cast(dict[str, Any], projection_raw)

    context_record = GroundedContextPackageRepository(database).load(operation_id)
    if context_record is None or context_record.chat_id != chat_id:
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint is missing its durable ContextPackage."
        )
    package = context_record.package
    try:
        projection = load_unified_replay_projection(
            receipt_payload_json=payload_json,
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            context_package=package,
            provider_id=package.model_signature.provider,
            model_id=package.model_signature.model_identifier,
        )
    except UnifiedReplayProjectionError as exc:
        raise UnifiedReplayInputSchemaError(
            "Unified replay checkpoint conflicts with its durable ContextPackage."
        ) from exc
    return projection_payload, projection, package.request_id


class UnifiedReplayInputRepository:
    """Persist exact Unified replay inputs before provider ambiguity is claimed."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.operations = ChatSendOperationRepository(database)
        self.context_packages = GroundedContextPackageRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_CREATE_SQL)
        row = self.database.connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = 'unified_grounded_replay_inputs'
            """
        ).fetchone()
        if (
            row is None
            or row["sql"] is None
            or _normalized_schema_sql(str(row["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
        ):
            raise UnifiedReplayInputSchemaError(
                "unified_grounded_replay_inputs has an incompatible extension definition."
            )
        columns = self.database.connection.execute(
            "PRAGMA table_info(unified_grounded_replay_inputs)"
        ).fetchall()
        if tuple(str(item["name"]) for item in columns) != _REQUIRED_COLUMNS:
            raise UnifiedReplayInputSchemaError(
                "unified_grounded_replay_inputs has an incompatible extension layout."
            )

    def store(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        projection: Mapping[str, Any],
    ) -> UnifiedReplayInputRecord:
        operation = self.operations.load(operation_id)
        context_record = self.context_packages.load(operation_id)
        if (
            operation is None
            or operation.chat_id != chat_id
            or operation.mode is not ChatSendOperationMode.GROUNDED
            or operation.processing_run_id != processing_run_id
            or context_record is None
            or context_record.chat_id != chat_id
        ):
            raise UnifiedReplayInputConflictError(
                "Unified replay checkpoint requires the matching pinned Grounded operation."
            )
        payload_json, payload_sha256 = _encode_projection(projection)
        try:
            _, decoded, request_id = _decode_projection(
                payload_json=payload_json,
                payload_sha256=payload_sha256,
                operation_id=operation_id,
                chat_id=chat_id,
                processing_run_id=processing_run_id,
                database=self.database,
            )
        except UnifiedReplayInputSchemaError as exc:
            raise UnifiedReplayInputConflictError(
                "Unified replay checkpoint violates its durable replay contract."
            ) from exc
        if request_id != context_record.package.request_id:
            raise UnifiedReplayInputConflictError(
                "Unified replay checkpoint ContextPackage identity changed during validation."
            )

        with self.database.write_transaction() as connection:
            existing = connection.execute(
                """
                SELECT chat_id, processing_run_id, context_package_request_id,
                       payload_json, payload_sha256, created_at_us
                FROM unified_grounded_replay_inputs
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                if (
                    uuid_from_blob(bytes(existing["chat_id"])) == chat_id
                    and uuid_from_blob(bytes(existing["processing_run_id"]))
                    == processing_run_id
                    and uuid_from_blob(bytes(existing["context_package_request_id"]))
                    == request_id
                    and str(existing["payload_json"]) == payload_json
                    and str(existing["payload_sha256"]) == payload_sha256
                ):
                    return UnifiedReplayInputRecord(
                        operation_id=operation_id,
                        chat_id=chat_id,
                        processing_run_id=processing_run_id,
                        context_package_request_id=request_id,
                        payload_json=payload_json,
                        payload_sha256=payload_sha256,
                        projection=decoded,
                        created_at_us=int(existing["created_at_us"]),
                    )
                raise UnifiedReplayInputConflictError(
                    "Unified operation already owns a different replay checkpoint."
                )

            provider_attempt_table = connection.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = 'grounded_provider_attempts'
                """
            ).fetchone()
            if provider_attempt_table is not None:
                provider_attempt = connection.execute(
                    "SELECT 1 FROM grounded_provider_attempts WHERE operation_id = ?",
                    (uuid_to_blob(operation_id),),
                ).fetchone()
                if provider_attempt is not None:
                    raise UnifiedReplayInputConflictError(
                        "Unified replay checkpoint must be persisted before provider execution begins."
                    )

            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO unified_grounded_replay_inputs (
                    operation_id, chat_id, processing_run_id,
                    context_package_request_id, payload_json, payload_sha256,
                    extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    uuid_to_blob(processing_run_id),
                    uuid_to_blob(request_id),
                    payload_json,
                    payload_sha256,
                    UNIFIED_REPLAY_INPUT_EXTENSION_VERSION,
                    created_at_us,
                ),
            )
        return UnifiedReplayInputRecord(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            context_package_request_id=request_id,
            payload_json=payload_json,
            payload_sha256=payload_sha256,
            projection=decoded,
            created_at_us=created_at_us,
        )

    def load(self, operation_id: uuid.UUID) -> UnifiedReplayInputRecord | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, processing_run_id,
                   context_package_request_id, payload_json, payload_sha256,
                   extension_schema_version, created_at_us
            FROM unified_grounded_replay_inputs
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        if int(row["extension_schema_version"]) != UNIFIED_REPLAY_INPUT_EXTENSION_VERSION:
            raise UnifiedReplayInputSchemaError(
                "Unified replay checkpoint has an unsupported extension version."
            )
        stored_operation_id = uuid_from_blob(bytes(row["operation_id"]))
        chat_id = uuid_from_blob(bytes(row["chat_id"]))
        processing_run_id = uuid_from_blob(bytes(row["processing_run_id"]))
        request_id = uuid_from_blob(bytes(row["context_package_request_id"]))
        if stored_operation_id != operation_id:
            raise UnifiedReplayInputSchemaError(
                "Unified replay checkpoint operation identity is corrupted."
            )

        operation = self.operations.load(operation_id)
        if (
            operation is None
            or operation.chat_id != chat_id
            or operation.mode is not ChatSendOperationMode.GROUNDED
            or operation.processing_run_id != processing_run_id
        ):
            raise UnifiedReplayInputSchemaError(
                "Unified replay checkpoint no longer matches its Grounded operation."
            )
        payload_json = str(row["payload_json"])
        payload_sha256 = str(row["payload_sha256"])
        _, projection, decoded_request_id = _decode_projection(
            payload_json=payload_json,
            payload_sha256=payload_sha256,
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            database=self.database,
        )
        if decoded_request_id != request_id:
            raise UnifiedReplayInputSchemaError(
                "Unified replay checkpoint ContextPackage request identity is corrupted."
            )
        return UnifiedReplayInputRecord(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            context_package_request_id=request_id,
            payload_json=payload_json,
            payload_sha256=payload_sha256,
            projection=projection,
            created_at_us=int(row["created_at_us"]),
        )
