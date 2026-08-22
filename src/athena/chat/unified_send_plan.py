"""Durable pre-user execution plan for Unified Local grounded chat."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified_replay import (
    UnifiedReplayProjection,
    UnifiedReplayProjectionError,
    _decode_evidence_selection,
    _decode_memory_context,
    _decode_model,
    _decode_source_context,
    _encode_evidence_selection,
    _encode_memory_context,
    _encode_model,
    _encode_source_context,
)
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.model.domain import ModelInfo
from athena.model.provenance import ModelRunRepository
from athena.retrieval.context import ContextBundle
from athena.retrieval.evidence import MemoryEvidenceSelection
from athena.retrieval.source_context import SourceContextBundle
from athena.storage.database import SQLiteDatabase

UNIFIED_SEND_PLAN_VERSION = 1


class UnifiedSendPlanConflictError(RuntimeError):
    """A requested Unified send plan conflicts with already durable state."""


class UnifiedSendPlanSchemaError(RuntimeError):
    """The Unified send-plan journal is missing, malformed, or corrupted."""


@dataclass(frozen=True, slots=True)
class UnifiedSendPlanRecord:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    fingerprint: ChatRequestFingerprint
    user_actor_id: uuid.UUID
    retrieval_snapshot_commit_seq: int
    model_signature_id: uuid.UUID
    retrieval_query_override: str | None
    projection: UnifiedReplayProjection
    payload_json: str
    payload_sha256: str
    created_at_us: int


_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "request_fingerprint_sha256",
    "model_signature_id",
    "payload_json",
    "payload_sha256",
    "extension_schema_version",
    "created_at_us",
)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS unified_grounded_send_plans (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    request_fingerprint_sha256 TEXT NOT NULL CHECK(length(request_fingerprint_sha256) = 64),
    model_signature_id BLOB(16) NOT NULL CHECK(length(model_signature_id) = 16),
    payload_json TEXT NOT NULL CHECK(length(payload_json) > 1),
    payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256) = 64),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE,
    FOREIGN KEY(model_signature_id)
        REFERENCES model_signatures(model_signature_id) ON DELETE RESTRICT
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _canonical_payload(
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    fingerprint: ChatRequestFingerprint,
    user_actor_id: uuid.UUID,
    retrieval_snapshot_commit_seq: int,
    model_signature_id: uuid.UUID,
    retrieval_query_override: str | None,
    primary_model: ModelInfo,
    embedding_model: ModelInfo | None,
    memory_context: ContextBundle,
    source_context: SourceContextBundle,
    evidence_selection: MemoryEvidenceSelection,
) -> tuple[str, str]:
    payload = {
        "version": UNIFIED_SEND_PLAN_VERSION,
        "operation_id": str(operation_id),
        "chat_id": str(chat_id),
        "request_fingerprint": {
            "payload_json": fingerprint.payload_json,
            "payload_sha256": fingerprint.payload_sha256,
            "format_version": fingerprint.format_version,
        },
        "user_actor_id": str(user_actor_id),
        "retrieval_snapshot_commit_seq": retrieval_snapshot_commit_seq,
        "model_signature_id": str(model_signature_id),
        "retrieval_query_override": retrieval_query_override,
        "primary_model": _encode_model(primary_model),
        "embedding_model": (
            None if embedding_model is None else _encode_model(embedding_model)
        ),
        "memory_context": _encode_memory_context(memory_context),
        "source_context": _encode_source_context(source_context),
        "evidence_selection": _encode_evidence_selection(evidence_selection),
    }
    payload_json = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return payload_json, hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _uuid_field(raw: dict[str, Any], key: str) -> uuid.UUID:
    value = raw.get(key)
    if not isinstance(value, str):
        raise UnifiedSendPlanSchemaError(f"Unified send plan field {key!r} is not a UUID.")
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise UnifiedSendPlanSchemaError(
            f"Unified send plan field {key!r} is not a UUID."
        ) from exc


def _decode_payload(
    *,
    payload_json: str,
    payload_sha256: str,
    expected_operation_id: uuid.UUID,
    expected_chat_id: uuid.UUID,
    expected_fingerprint_sha256: str,
    expected_model_signature_id: uuid.UUID,
    model_runs: ModelRunRepository,
) -> tuple[
    ChatRequestFingerprint,
    uuid.UUID,
    int,
    str | None,
    UnifiedReplayProjection,
]:
    actual_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    if actual_hash != payload_sha256:
        raise UnifiedSendPlanSchemaError(
            "Unified send plan payload hash does not match its journal row."
        )
    try:
        decoded = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise UnifiedSendPlanSchemaError("Unified send plan payload is invalid JSON.") from exc
    if not isinstance(decoded, dict):
        raise UnifiedSendPlanSchemaError("Unified send plan payload must be an object.")
    raw = cast(dict[str, Any], decoded)
    if raw.get("version") != UNIFIED_SEND_PLAN_VERSION:
        raise UnifiedSendPlanSchemaError("Unified send plan version is unsupported.")
    if _uuid_field(raw, "operation_id") != expected_operation_id:
        raise UnifiedSendPlanSchemaError("Unified send plan operation identity is corrupted.")
    if _uuid_field(raw, "chat_id") != expected_chat_id:
        raise UnifiedSendPlanSchemaError("Unified send plan chat identity is corrupted.")
    if _uuid_field(raw, "model_signature_id") != expected_model_signature_id:
        raise UnifiedSendPlanSchemaError("Unified send plan ModelSignature identity is corrupted.")

    fingerprint_raw = raw.get("request_fingerprint")
    if not isinstance(fingerprint_raw, dict):
        raise UnifiedSendPlanSchemaError("Unified send plan fingerprint is missing.")
    fingerprint_map = cast(dict[str, Any], fingerprint_raw)
    fingerprint_payload = fingerprint_map.get("payload_json")
    fingerprint_sha = fingerprint_map.get("payload_sha256")
    fingerprint_version = fingerprint_map.get("format_version")
    if (
        not isinstance(fingerprint_payload, str)
        or not isinstance(fingerprint_sha, str)
        or isinstance(fingerprint_version, bool)
        or not isinstance(fingerprint_version, int)
        or hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
        != fingerprint_sha
        or fingerprint_sha != expected_fingerprint_sha256
    ):
        raise UnifiedSendPlanSchemaError("Unified send plan request fingerprint is corrupted.")
    fingerprint = ChatRequestFingerprint(
        payload_json=fingerprint_payload,
        payload_sha256=fingerprint_sha,
        format_version=fingerprint_version,
    )

    user_actor_id = _uuid_field(raw, "user_actor_id")
    snapshot_seq = raw.get("retrieval_snapshot_commit_seq")
    if isinstance(snapshot_seq, bool) or not isinstance(snapshot_seq, int) or snapshot_seq < 0:
        raise UnifiedSendPlanSchemaError("Unified send plan snapshot sequence is invalid.")
    retrieval_query_override = raw.get("retrieval_query_override")
    if retrieval_query_override is not None and (
        not isinstance(retrieval_query_override, str) or not retrieval_query_override
    ):
        raise UnifiedSendPlanSchemaError("Unified send plan retrieval override is invalid.")

    try:
        primary_raw = raw.get("primary_model")
        memory_raw = raw.get("memory_context")
        source_raw = raw.get("source_context")
        evidence_raw = raw.get("evidence_selection")
        if not all(
            isinstance(value, dict)
            for value in (primary_raw, memory_raw, source_raw, evidence_raw)
        ):
            raise UnifiedReplayProjectionError("Unified send plan projection is incomplete.")
        primary_model = _decode_model(cast(dict[str, Any], primary_raw))
        embedding_raw = raw.get("embedding_model")
        embedding_model = (
            None
            if embedding_raw is None
            else _decode_model(cast(dict[str, Any], embedding_raw))
        )
        memory_context = _decode_memory_context(cast(dict[str, Any], memory_raw))
        source_context = _decode_source_context(cast(dict[str, Any], source_raw))
        evidence_selection = _decode_evidence_selection(cast(dict[str, Any], evidence_raw))
    except (TypeError, UnifiedReplayProjectionError) as exc:
        raise UnifiedSendPlanSchemaError("Unified send plan replay projection is invalid.") from exc

    signature = model_runs.load_signature(expected_model_signature_id)
    if (
        signature.provider != primary_model.provider
        or signature.model_identifier != primary_model.backend_model_id
        or signature.quantization != primary_model.quantization
    ):
        raise UnifiedSendPlanSchemaError(
            "Unified send plan primary model conflicts with its ModelSignature."
        )
    try:
        configuration = json.loads(signature.context_configuration_json or "{}")
    except json.JSONDecodeError as exc:
        raise UnifiedSendPlanSchemaError(
            "Unified send plan ModelSignature configuration is invalid JSON."
        ) from exc
    if not isinstance(configuration, dict):
        raise UnifiedSendPlanSchemaError(
            "Unified send plan ModelSignature configuration is not an object."
        )
    configured_embedding = configuration.get("embedding_model_id")
    actual_embedding = (
        None if embedding_model is None else embedding_model.backend_model_id
    )
    if configured_embedding != actual_embedding:
        raise UnifiedSendPlanSchemaError(
            "Unified send plan embedding model conflicts with its ModelSignature."
        )
    if configuration.get("evidence_policy_id") != evidence_selection.policy_id:
        raise UnifiedSendPlanSchemaError(
            "Unified send plan evidence policy conflicts with its ModelSignature."
        )
    result_keys = {
        (item.entity_type, item.entity_id, item.revision_id)
        for item in evidence_selection.results
    }
    memory_keys = {
        (item.entity_type, item.entity_id, item.revision_id)
        for item in memory_context.items
    }
    if not memory_keys.issubset(result_keys):
        raise UnifiedSendPlanSchemaError(
            "Unified send plan Memory context escapes its evidence selection."
        )
    context_ids = tuple(item.context_id for item in memory_context.items) + tuple(
        item.context_id for item in source_context.items
    )
    if len(context_ids) != len(set(context_ids)):
        raise UnifiedSendPlanSchemaError(
            "Unified send plan context identities are not unique."
        )

    return (
        fingerprint,
        user_actor_id,
        snapshot_seq,
        cast(str | None, retrieval_query_override),
        UnifiedReplayProjection(
            primary_model=primary_model,
            embedding_model=embedding_model,
            memory_context=memory_context,
            source_context=source_context,
            evidence_selection=evidence_selection,
        ),
    )


class UnifiedSendPlanRepository:
    """Persist frozen Unified retrieval state before the durable user mutation."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.model_runs = ModelRunRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_CREATE_SQL)
        row = self.database.connection.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type = 'table' AND name = 'unified_grounded_send_plans'
            """
        ).fetchone()
        if (
            row is None
            or row["sql"] is None
            or _normalized_schema_sql(str(row["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
        ):
            raise UnifiedSendPlanSchemaError(
                "unified_grounded_send_plans has an incompatible extension definition."
            )
        columns = self.database.connection.execute(
            "PRAGMA table_info(unified_grounded_send_plans)"
        ).fetchall()
        if tuple(str(item["name"]) for item in columns) != _REQUIRED_COLUMNS:
            raise UnifiedSendPlanSchemaError(
                "unified_grounded_send_plans has an incompatible extension layout."
            )

    def store(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
        user_actor_id: uuid.UUID,
        retrieval_snapshot_commit_seq: int,
        model_signature_id: uuid.UUID,
        retrieval_query_override: str | None,
        primary_model: ModelInfo,
        embedding_model: ModelInfo | None,
        memory_context: ContextBundle,
        source_context: SourceContextBundle,
        evidence_selection: MemoryEvidenceSelection,
    ) -> UnifiedSendPlanRecord:
        if retrieval_snapshot_commit_seq < 0:
            raise ValueError("Unified send-plan snapshot sequence must not be negative.")
        actor = self.database.connection.execute(
            "SELECT active FROM actors WHERE actor_id = ?",
            (uuid_to_blob(user_actor_id),),
        ).fetchone()
        if actor is None or int(actor["active"]) != 1:
            raise UnifiedSendPlanConflictError(
                "Unified send plan requires its active trigger actor."
            )
        chat = self.database.connection.execute(
            "SELECT 1 FROM chats WHERE chat_id = ?",
            (uuid_to_blob(chat_id),),
        ).fetchone()
        if chat is None:
            raise UnifiedSendPlanConflictError("Unified send plan requires its chat.")
        self.model_runs.load_signature(model_signature_id)
        payload_json, payload_sha256 = _canonical_payload(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
            user_actor_id=user_actor_id,
            retrieval_snapshot_commit_seq=retrieval_snapshot_commit_seq,
            model_signature_id=model_signature_id,
            retrieval_query_override=retrieval_query_override,
            primary_model=primary_model,
            embedding_model=embedding_model,
            memory_context=memory_context,
            source_context=source_context,
            evidence_selection=evidence_selection,
        )
        _decode_payload(
            payload_json=payload_json,
            payload_sha256=payload_sha256,
            expected_operation_id=operation_id,
            expected_chat_id=chat_id,
            expected_fingerprint_sha256=fingerprint.payload_sha256,
            expected_model_signature_id=model_signature_id,
            model_runs=self.model_runs,
        )

        with self.database.write_transaction() as connection:
            operation = connection.execute(
                "SELECT 1 FROM chat_send_operations WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if operation is not None:
                raise UnifiedSendPlanConflictError(
                    "Unified send plan must be persisted before the user operation."
                )
            existing = connection.execute(
                """
                SELECT chat_id, request_fingerprint_sha256, model_signature_id,
                       payload_json, payload_sha256, created_at_us
                FROM unified_grounded_send_plans
                WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                if (
                    uuid_from_blob(bytes(existing["chat_id"])) == chat_id
                    and str(existing["request_fingerprint_sha256"])
                    == fingerprint.payload_sha256
                    and uuid_from_blob(bytes(existing["model_signature_id"]))
                    == model_signature_id
                    and str(existing["payload_json"]) == payload_json
                    and str(existing["payload_sha256"]) == payload_sha256
                ):
                    return self.load(operation_id, fingerprint=fingerprint)  # type: ignore[return-value]
                raise UnifiedSendPlanConflictError(
                    "Unified operation already owns a different pre-user send plan."
                )
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO unified_grounded_send_plans (
                    operation_id, chat_id, request_fingerprint_sha256,
                    model_signature_id, payload_json, payload_sha256,
                    extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    fingerprint.payload_sha256,
                    uuid_to_blob(model_signature_id),
                    payload_json,
                    payload_sha256,
                    UNIFIED_SEND_PLAN_VERSION,
                    created_at_us,
                ),
            )

        record = self.load(operation_id, fingerprint=fingerprint)
        if record is None:
            raise UnifiedSendPlanSchemaError("Unified send plan disappeared after insert.")
        return record

    def load(
        self,
        operation_id: uuid.UUID,
        *,
        fingerprint: ChatRequestFingerprint | None = None,
    ) -> UnifiedSendPlanRecord | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, request_fingerprint_sha256,
                   model_signature_id, payload_json, payload_sha256,
                   extension_schema_version, created_at_us
            FROM unified_grounded_send_plans
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        if int(row["extension_schema_version"]) != UNIFIED_SEND_PLAN_VERSION:
            raise UnifiedSendPlanSchemaError("Unified send plan extension version is unsupported.")
        stored_operation = uuid_from_blob(bytes(row["operation_id"]))
        if stored_operation != operation_id:
            raise UnifiedSendPlanSchemaError("Unified send plan row identity is corrupted.")
        chat_id = uuid_from_blob(bytes(row["chat_id"]))
        model_signature_id = uuid_from_blob(bytes(row["model_signature_id"]))
        fingerprint_sha = str(row["request_fingerprint_sha256"])
        if fingerprint is not None and fingerprint.payload_sha256 != fingerprint_sha:
            raise UnifiedSendPlanConflictError(
                "Unified retry request conflicts with its durable pre-user send plan."
            )
        (
            decoded_fingerprint,
            user_actor_id,
            snapshot_seq,
            retrieval_query_override,
            projection,
        ) = _decode_payload(
            payload_json=str(row["payload_json"]),
            payload_sha256=str(row["payload_sha256"]),
            expected_operation_id=operation_id,
            expected_chat_id=chat_id,
            expected_fingerprint_sha256=fingerprint_sha,
            expected_model_signature_id=model_signature_id,
            model_runs=self.model_runs,
        )
        return UnifiedSendPlanRecord(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=decoded_fingerprint,
            user_actor_id=user_actor_id,
            retrieval_snapshot_commit_seq=snapshot_seq,
            model_signature_id=model_signature_id,
            retrieval_query_override=retrieval_query_override,
            projection=projection,
            payload_json=str(row["payload_json"]),
            payload_sha256=str(row["payload_sha256"]),
            created_at_us=int(row["created_at_us"]),
        )
