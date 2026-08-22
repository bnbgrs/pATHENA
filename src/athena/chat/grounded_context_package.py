"""Durable exact ContextPackage journal for crash-safe Grounded retries."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any, cast

from athena.chat.send_operation import ChatSendOperationMode, ChatSendOperationRepository
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextModelSignature,
    ContextPackage,
    ContextPackageBudget,
    ContextPackageError,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase

GROUNDED_CONTEXT_PACKAGE_EXTENSION_VERSION = 1


class GroundedContextPackageConflictError(RuntimeError):
    """The durable ContextPackage conflicts with existing operation identity."""


class GroundedContextPackageSchemaError(RuntimeError):
    """The Grounded ContextPackage journal is missing or corrupted."""


@dataclass(frozen=True, slots=True)
class GroundedContextPackageRecord:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    package: ContextPackage
    payload_sha256: str
    created_at_us: int


_REQUIRED_COLUMNS = (
    "operation_id",
    "chat_id",
    "payload_json",
    "payload_sha256",
    "extension_schema_version",
    "created_at_us",
)

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_context_packages (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    payload_json TEXT NOT NULL CHECK(length(payload_json) > 1),
    payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256) = 64),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES chat_send_operations(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _encode_package(package: ContextPackage) -> tuple[str, str]:
    payload: dict[str, Any] = {
        "format_version": 1,
        "request_id": str(package.request_id),
        "model_signature": {
            "model_signature_id": str(package.model_signature.model_signature_id),
            "provider": package.model_signature.provider,
            "model_identifier": package.model_signature.model_identifier,
            "quantization": package.model_signature.quantization,
            "generation_parameters_json": package.model_signature.generation_parameters_json,
            "context_configuration_json": package.model_signature.context_configuration_json,
            "signature_hash_hex": package.model_signature.signature_hash_hex,
        },
        "budget": {
            "effective_context_limit": package.budget.effective_context_limit,
            "context_budget": package.budget.context_budget,
            "output_reserve": package.budget.output_reserve,
            "safety_margin": package.budget.safety_margin,
        },
        "sections": [
            {
                "name": item.name,
                "role": item.role,
                "content": item.content,
                "included_ref_ids": list(item.included_ref_ids),
            }
            for item in package.sections
        ],
        "included_refs": [
            {
                "ref_id": item.ref_id,
                "entity_type": item.entity_type,
                "entity_id": str(item.entity_id),
                "revision_id": None if item.revision_id is None else str(item.revision_id),
            }
            for item in package.included_refs
        ],
        "excluded_candidate_summary": {
            "retrieval_candidate_count": package.excluded_candidate_summary.retrieval_candidate_count,
            "retrieval_included_count": package.excluded_candidate_summary.retrieval_included_count,
            "retrieval_excluded_count": package.excluded_candidate_summary.retrieval_excluded_count,
            "memory_candidate_count": package.excluded_candidate_summary.memory_candidate_count,
            "memory_included_count": package.excluded_candidate_summary.memory_included_count,
            "memory_excluded_count": package.excluded_candidate_summary.memory_excluded_count,
            "conversation_candidate_count": package.excluded_candidate_summary.conversation_candidate_count,
            "conversation_included_count": package.excluded_candidate_summary.conversation_included_count,
            "conversation_excluded_count": package.excluded_candidate_summary.conversation_excluded_count,
        },
        "token_estimates": {
            "conversation_tokens": package.token_estimates.conversation_tokens,
            "current_user_tokens": package.token_estimates.current_user_tokens,
            "system_tokens": package.token_estimates.system_tokens,
            "context_tokens": package.token_estimates.context_tokens,
            "estimated_input_tokens": package.token_estimates.estimated_input_tokens,
            "estimated_total_tokens": package.token_estimates.estimated_total_tokens,
        },
        "snapshot_commit_seq": package.snapshot_commit_seq,
        "structured_schema_id": package.structured_schema_id,
        "structured_schema_json": package.structured_schema_json,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return encoded, hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GroundedContextPackageSchemaError(f"{label} must be a JSON object.")
    return cast(dict[str, Any], value)


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GroundedContextPackageSchemaError(f"{label} must be a JSON array.")
    return value


def _required_str(mapping: dict[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value:
        raise GroundedContextPackageSchemaError(f"{key} must be a non-empty string.")
    return value


def _optional_str(mapping: dict[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise GroundedContextPackageSchemaError(f"{key} must be a string or null.")
    return value


def _required_int(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise GroundedContextPackageSchemaError(f"{key} must be an integer.")
    return value


def _parse_uuid(value: str, label: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError as exc:
        raise GroundedContextPackageSchemaError(
            f"{label} must be a valid UUID string."
        ) from exc


def _decode_package(payload_json: str, expected_sha256: str) -> ContextPackage:
    digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    if digest != expected_sha256:
        raise GroundedContextPackageSchemaError(
            "Persisted Grounded ContextPackage failed checksum verification."
        )
    try:
        raw = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise GroundedContextPackageSchemaError(
            "Persisted Grounded ContextPackage is invalid JSON."
        ) from exc
    root = _object(raw, "ContextPackage payload")
    if root.get("format_version") != 1:
        raise GroundedContextPackageSchemaError(
            "Unsupported Grounded ContextPackage payload version."
        )

    signature = _object(root.get("model_signature"), "model_signature")
    budget = _object(root.get("budget"), "budget")
    excluded = _object(
        root.get("excluded_candidate_summary"),
        "excluded_candidate_summary",
    )
    tokens = _object(root.get("token_estimates"), "token_estimates")

    sections: list[ContextSection] = []
    for raw_section in _list(root.get("sections"), "sections"):
        item = _object(raw_section, "section")
        role = _required_str(item, "role")
        if role not in {"system", "user", "assistant"}:
            raise GroundedContextPackageSchemaError("Invalid ContextPackage section role.")
        included_ref_ids = tuple(
            _required_str({"value": value}, "value")
            for value in _list(item.get("included_ref_ids"), "included_ref_ids")
        )
        sections.append(
            ContextSection(
                name=_required_str(item, "name"),
                role=cast(Any, role),
                content=_required_str(item, "content"),
                included_ref_ids=included_ref_ids,
            )
        )

    refs: list[ContextIncludedRef] = []
    for raw_ref in _list(root.get("included_refs"), "included_refs"):
        item = _object(raw_ref, "included_ref")
        revision_value = item.get("revision_id")
        if revision_value is not None and not isinstance(revision_value, str):
            raise GroundedContextPackageSchemaError(
                "included_ref revision_id must be a UUID string or null."
            )
        refs.append(
            ContextIncludedRef(
                ref_id=_required_str(item, "ref_id"),
                entity_type=_required_str(item, "entity_type"),
                entity_id=_parse_uuid(_required_str(item, "entity_id"), "entity_id"),
                revision_id=(
                    None
                    if revision_value is None
                    else _parse_uuid(revision_value, "revision_id")
                ),
            )
        )

    return ContextPackage(
        request_id=_parse_uuid(_required_str(root, "request_id"), "request_id"),
        model_signature=ContextModelSignature(
            model_signature_id=_parse_uuid(
                _required_str(signature, "model_signature_id"),
                "model_signature_id",
            ),
            provider=_required_str(signature, "provider"),
            model_identifier=_required_str(signature, "model_identifier"),
            quantization=_optional_str(signature, "quantization"),
            generation_parameters_json=_required_str(
                signature,
                "generation_parameters_json",
            ),
            context_configuration_json=_optional_str(
                signature,
                "context_configuration_json",
            ),
            signature_hash_hex=_required_str(signature, "signature_hash_hex"),
        ),
        budget=ContextPackageBudget(
            effective_context_limit=_required_int(budget, "effective_context_limit"),
            context_budget=_required_int(budget, "context_budget"),
            output_reserve=_required_int(budget, "output_reserve"),
            safety_margin=_required_int(budget, "safety_margin"),
        ),
        sections=tuple(sections),
        included_refs=tuple(refs),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=_required_int(excluded, "retrieval_candidate_count"),
            retrieval_included_count=_required_int(excluded, "retrieval_included_count"),
            retrieval_excluded_count=_required_int(excluded, "retrieval_excluded_count"),
            memory_candidate_count=_required_int(excluded, "memory_candidate_count"),
            memory_included_count=_required_int(excluded, "memory_included_count"),
            memory_excluded_count=_required_int(excluded, "memory_excluded_count"),
            conversation_candidate_count=_required_int(excluded, "conversation_candidate_count"),
            conversation_included_count=_required_int(excluded, "conversation_included_count"),
            conversation_excluded_count=_required_int(excluded, "conversation_excluded_count"),
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=_required_int(tokens, "conversation_tokens"),
            current_user_tokens=_required_int(tokens, "current_user_tokens"),
            system_tokens=_required_int(tokens, "system_tokens"),
            context_tokens=_required_int(tokens, "context_tokens"),
            estimated_input_tokens=_required_int(tokens, "estimated_input_tokens"),
            estimated_total_tokens=_required_int(tokens, "estimated_total_tokens"),
        ),
        snapshot_commit_seq=_required_int(root, "snapshot_commit_seq"),
        structured_schema_id=_optional_str(root, "structured_schema_id"),
        structured_schema_json=_optional_str(root, "structured_schema_json"),
    )


class GroundedContextPackageRepository:
    """Persist and reload the exact provider-facing package for one operation."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.operations = ChatSendOperationRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_CREATE_SQL)
        row = self.database.connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'grounded_context_packages'"
        ).fetchone()
        if (
            row is None
            or row["sql"] is None
            or _normalized_schema_sql(str(row["sql"]))
            != _normalized_schema_sql(_CREATE_SQL)
        ):
            raise GroundedContextPackageSchemaError(
                "grounded_context_packages has an incompatible extension definition."
            )
        columns = self.database.connection.execute(
            "PRAGMA table_info(grounded_context_packages)"
        ).fetchall()
        if tuple(str(item["name"]) for item in columns) != _REQUIRED_COLUMNS:
            raise GroundedContextPackageSchemaError(
                "grounded_context_packages has an incompatible extension layout."
            )

    def store(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        package: ContextPackage,
    ) -> GroundedContextPackageRecord:
        operation = self.operations.load(operation_id)
        if (
            operation is None
            or operation.chat_id != chat_id
            or operation.mode is not ChatSendOperationMode.GROUNDED
        ):
            raise GroundedContextPackageConflictError(
                "ContextPackage requires the matching Grounded send operation."
            )
        current_ref = package.current_user_ref()
        if current_ref.entity_id != operation_id:
            raise GroundedContextPackageConflictError(
                "ContextPackage CURRENT-USER identity must equal operation_id."
            )
        payload_json, payload_sha256 = _encode_package(package)
        with self.database.write_transaction() as connection:
            existing = connection.execute(
                """
                SELECT chat_id, payload_json, payload_sha256, created_at_us
                FROM grounded_context_packages WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                if (
                    uuid_from_blob(bytes(existing["chat_id"])) == chat_id
                    and str(existing["payload_json"]) == payload_json
                    and str(existing["payload_sha256"]) == payload_sha256
                ):
                    return GroundedContextPackageRecord(
                        operation_id=operation_id,
                        chat_id=chat_id,
                        package=package,
                        payload_sha256=payload_sha256,
                        created_at_us=int(existing["created_at_us"]),
                    )
                raise GroundedContextPackageConflictError(
                    "Grounded operation already owns a different ContextPackage."
                )
            provider_attempt = connection.execute(
                "SELECT 1 FROM grounded_provider_attempts WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if provider_attempt is not None:
                raise GroundedContextPackageConflictError(
                    "ContextPackage must be persisted before provider execution begins."
                )
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_context_packages (
                    operation_id, chat_id, payload_json, payload_sha256,
                    extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    payload_json,
                    payload_sha256,
                    GROUNDED_CONTEXT_PACKAGE_EXTENSION_VERSION,
                    created_at_us,
                ),
            )
        return GroundedContextPackageRecord(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
            payload_sha256=payload_sha256,
            created_at_us=created_at_us,
        )

    def load(self, operation_id: uuid.UUID) -> GroundedContextPackageRecord | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, chat_id, payload_json, payload_sha256, created_at_us
            FROM grounded_context_packages WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        payload_json = str(row["payload_json"])
        payload_sha256 = str(row["payload_sha256"])
        package = _decode_package(payload_json, payload_sha256)
        operation = self.operations.load(operation_id)
        chat_id = uuid_from_blob(bytes(row["chat_id"]))
        try:
            current_ref = package.current_user_ref()
            package.generation_controls()
            package.generation_temperature()
            package.structured_schema()
        except ContextPackageError as exc:
            raise GroundedContextPackageSchemaError(
                "Persisted ContextPackage violates its model-input contract."
            ) from exc
        if (
            operation is None
            or operation.chat_id != chat_id
            or operation.mode is not ChatSendOperationMode.GROUNDED
            or current_ref.entity_id != operation_id
        ):
            raise GroundedContextPackageSchemaError(
                "Persisted ContextPackage no longer matches its Grounded operation."
            )
        return GroundedContextPackageRecord(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
            payload_sha256=payload_sha256,
            created_at_us=int(row["created_at_us"]),
        )
