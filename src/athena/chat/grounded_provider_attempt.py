"""Durable provider-call boundary and result journal for Grounded sends."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import cast

from athena.chat.grounded_context_package import (
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run,
)
from athena.chat.grounded_provider_result_contract import (
    GroundedProviderResultContractError,
    validate_provider_result_contract,
)
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.common.time import utc_now_us
from athena.storage.database import SQLiteDatabase

GROUNDED_PROVIDER_ATTEMPT_EXTENSION_VERSION = 1
GROUNDED_PROVIDER_RESULT_EXTENSION_VERSION = 1
GROUNDED_PROVIDER_RESULT_IDENTITY_EXTENSION_VERSION = 1


class GroundedProviderAttemptConflictError(RuntimeError):
    """The provider boundary conflicts with existing durable operation state."""


class GroundedProviderAttemptSchemaError(RuntimeError):
    """A provider-boundary extension table is missing or incompatible."""


@dataclass(frozen=True, slots=True)
class GroundedProviderAttempt:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    started_at_us: int


@dataclass(frozen=True, slots=True)
class GroundedProviderResult:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    processing_run_id: uuid.UUID
    assistant_content: str
    receipt_payload_json: str
    receipt_payload_sha256: str
    created_at_us: int


@dataclass(frozen=True, slots=True)
class GroundedProviderResultIdentity:
    operation_id: uuid.UUID
    provider_id: str
    model_id: str


_ATTEMPT_COLUMNS = (
    "operation_id",
    "chat_id",
    "extension_schema_version",
    "started_at_us",
)
_RESULT_COLUMNS = (
    "operation_id",
    "chat_id",
    "processing_run_id",
    "assistant_content",
    "receipt_payload_json",
    "receipt_payload_sha256",
    "extension_schema_version",
    "created_at_us",
)
_RESULT_IDENTITY_COLUMNS = (
    "operation_id",
    "provider_id",
    "model_id",
    "extension_schema_version",
)

_ATTEMPT_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_provider_attempts (
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

_RESULT_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_provider_results (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    chat_id BLOB(16) NOT NULL CHECK(length(chat_id) = 16),
    processing_run_id BLOB(16) NOT NULL CHECK(length(processing_run_id) = 16),
    assistant_content TEXT NOT NULL CHECK(length(trim(assistant_content)) > 0),
    receipt_payload_json TEXT NOT NULL CHECK(length(receipt_payload_json) > 1),
    receipt_payload_sha256 TEXT NOT NULL CHECK(length(receipt_payload_sha256) = 64),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    created_at_us INTEGER NOT NULL CHECK(created_at_us >= 0),
    FOREIGN KEY(operation_id)
        REFERENCES grounded_provider_attempts(operation_id) ON DELETE CASCADE,
    FOREIGN KEY(chat_id)
        REFERENCES chats(chat_id) ON DELETE CASCADE
) WITHOUT ROWID
"""

_RESULT_IDENTITY_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS grounded_provider_result_identities (
    operation_id BLOB(16) PRIMARY KEY NOT NULL CHECK(length(operation_id) = 16),
    provider_id TEXT NOT NULL CHECK(length(trim(provider_id)) > 0),
    model_id TEXT NOT NULL CHECK(length(trim(model_id)) > 0),
    extension_schema_version INTEGER NOT NULL CHECK(extension_schema_version = 1),
    FOREIGN KEY(operation_id)
        REFERENCES grounded_provider_results(operation_id) ON DELETE CASCADE
) WITHOUT ROWID
"""


def _normalized_schema_sql(sql: str) -> str:
    normalized = " ".join(sql.split())
    return normalized.replace("CREATE TABLE IF NOT EXISTS ", "CREATE TABLE ", 1)


def _canonical_receipt_payload(payload_json: str) -> tuple[str, str]:
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Provider result receipt payload must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Provider result receipt payload must be a JSON object.")
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return canonical, digest


class GroundedProviderAttemptRepository:
    """Persist the irreversible provider boundary and returned result durably."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        ChatSendOperationRepository(database)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.database.write_transaction() as connection:
            connection.execute(_ATTEMPT_CREATE_SQL)
            connection.execute(_RESULT_CREATE_SQL)
            connection.execute(_RESULT_IDENTITY_CREATE_SQL)
        self._verify_table(
            "grounded_provider_attempts",
            _ATTEMPT_CREATE_SQL,
            _ATTEMPT_COLUMNS,
        )
        self._verify_table(
            "grounded_provider_results",
            _RESULT_CREATE_SQL,
            _RESULT_COLUMNS,
        )
        self._verify_table(
            "grounded_provider_result_identities",
            _RESULT_IDENTITY_CREATE_SQL,
            _RESULT_IDENTITY_COLUMNS,
        )

    def _verify_table(
        self,
        table: str,
        expected_sql: str,
        expected_columns: tuple[str, ...],
    ) -> None:
        connection = self.database.connection
        schema = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        if (
            schema is None
            or schema["sql"] is None
            or _normalized_schema_sql(str(schema["sql"]))
            != _normalized_schema_sql(expected_sql)
        ):
            raise GroundedProviderAttemptSchemaError(
                f"{table} has an incompatible extension definition."
            )
        columns = connection.execute(f"PRAGMA table_info({table})").fetchall()
        if tuple(str(row["name"]) for row in columns) != expected_columns:
            raise GroundedProviderAttemptSchemaError(
                f"{table} has an incompatible extension layout."
            )

    def load(self, operation_id: uuid.UUID) -> GroundedProviderAttempt | None:
        row = self.database.connection.execute(
            """
            SELECT a.operation_id, a.chat_id, a.started_at_us,
                   o.chat_id AS operation_chat_id, o.mode AS operation_mode
            FROM grounded_provider_attempts AS a
            LEFT JOIN chat_send_operations AS o ON o.operation_id = a.operation_id
            WHERE a.operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        if (
            row["operation_chat_id"] is None
            or uuid_from_blob(bytes(row["chat_id"]))
            != uuid_from_blob(bytes(row["operation_chat_id"]))
            or str(row["operation_mode"]) != "grounded"
        ):
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider attempt no longer matches its Grounded operation."
            )
        return GroundedProviderAttempt(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            started_at_us=int(row["started_at_us"]),
        )

    def load_result(self, operation_id: uuid.UUID) -> GroundedProviderResult | None:
        row = self.database.connection.execute(
            """
            SELECT r.operation_id, r.chat_id, r.processing_run_id,
                   r.assistant_content, r.receipt_payload_json,
                   r.receipt_payload_sha256, r.created_at_us,
                   a.chat_id AS attempt_chat_id,
                   o.chat_id AS operation_chat_id, o.mode AS operation_mode,
                   o.processing_run_id AS operation_processing_run_id
            FROM grounded_provider_results AS r
            LEFT JOIN grounded_provider_attempts AS a ON a.operation_id = r.operation_id
            LEFT JOIN chat_send_operations AS o ON o.operation_id = r.operation_id
            WHERE r.operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        if (
            row["attempt_chat_id"] is None
            or row["operation_chat_id"] is None
            or uuid_from_blob(bytes(row["chat_id"]))
            != uuid_from_blob(bytes(row["attempt_chat_id"]))
            or uuid_from_blob(bytes(row["chat_id"]))
            != uuid_from_blob(bytes(row["operation_chat_id"]))
            or str(row["operation_mode"]) != "grounded"
            or (
                row["operation_processing_run_id"] is not None
                and uuid_from_blob(bytes(row["operation_processing_run_id"]))
                != uuid_from_blob(bytes(row["processing_run_id"]))
            )
        ):
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider result no longer matches its Grounded operation."
            )
        return self._result_from_row(row)

    def load_result_identity(
        self,
        operation_id: uuid.UUID,
    ) -> GroundedProviderResultIdentity | None:
        row = self.database.connection.execute(
            """
            SELECT operation_id, provider_id, model_id
            FROM grounded_provider_result_identities
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if row is None:
            return None
        provider_id = str(row["provider_id"])
        model_id = str(row["model_id"])
        if not provider_id.strip() or not model_id.strip():
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider-result identity is blank."
            )
        return GroundedProviderResultIdentity(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            provider_id=provider_id,
            model_id=model_id,
        )

    def mark_started(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> GroundedProviderAttempt:
        return self._mark_started(
            operation_id=operation_id,
            chat_id=chat_id,
            allow_existing=True,
            require_pinned_context=False,
        )

    def claim_started(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> GroundedProviderAttempt:
        """Claim exclusive ownership of the irreversible provider boundary."""
        return self._mark_started(
            operation_id=operation_id,
            chat_id=chat_id,
            allow_existing=False,
            require_pinned_context=True,
        )

    def _mark_started(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        allow_existing: bool,
        require_pinned_context: bool,
    ) -> GroundedProviderAttempt:
        with self.database.write_transaction() as connection:
            operation = self._require_grounded_operation(connection, operation_id, chat_id)
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
                if not allow_existing:
                    raise GroundedProviderAttemptConflictError(
                        "Provider attempt marker has already been claimed."
                    )
                return attempt
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise GroundedProviderAttemptConflictError(
                    "Provider attempt may start only from user_committed state."
                )
            if require_pinned_context:
                if operation["processing_run_id"] is None:
                    raise GroundedProviderAttemptConflictError(
                        "Provider attempt claim requires a pinned Grounded ProcessingRun."
                    )
                self._require_pinned_context_before_claim_in_transaction(
                    connection,
                    operation_id=operation_id,
                    chat_id=chat_id,
                )
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
        stored = self.load(operation_id)
        if stored is None:
            raise RuntimeError("Provider attempt marker disappeared after commit.")
        return stored

    @staticmethod
    def _require_pinned_context_before_claim_in_transaction(
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> None:
        context_table = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'grounded_context_packages'
            """
        ).fetchone()
        if context_table is None:
            raise GroundedProviderAttemptConflictError(
                "Provider attempt claim requires a durable ContextPackage."
            )
        context = connection.execute(
            """
            SELECT chat_id, payload_json, payload_sha256
            FROM grounded_context_packages
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if context is None:
            raise GroundedProviderAttemptConflictError(
                "Provider attempt claim requires a durable ContextPackage."
            )
        if uuid_from_blob(bytes(context["chat_id"])) != chat_id:
            raise GroundedProviderAttemptConflictError(
                "Pinned ContextPackage chat identity conflicts with provider attempt."
            )
        payload_json = str(context["payload_json"])
        expected_sha256 = str(context["payload_sha256"])
        actual_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        if actual_sha256 != expected_sha256:
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage failed checksum verification before provider claim."
            )

    def store_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        assistant_content: str,
        receipt_payload_json: str,
        provider_id: str | None = None,
        model_id: str | None = None,
    ) -> GroundedProviderResult:
        validate_provider_result_contract(
            assistant_content=assistant_content,
            receipt_payload_json=receipt_payload_json,
        )
        if (provider_id is None) != (model_id is None):
            raise ValueError(
                "Provider result identity requires both provider_id and model_id."
            )
        if provider_id is not None and not provider_id.strip():
            raise ValueError("Provider result provider_id must not be blank.")
        if model_id is not None and not model_id.strip():
            raise ValueError("Provider result model_id must not be blank.")
        canonical, digest = _canonical_receipt_payload(receipt_payload_json)

        context_record = None
        context_table = self.database.connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'grounded_context_packages'
            """
        ).fetchone()
        if context_table is not None:
            try:
                context_record = GroundedContextPackageRepository(self.database).load(
                    operation_id
                )
            except GroundedContextPackageSchemaError as exc:
                raise GroundedProviderAttemptSchemaError(
                    "Pinned ContextPackage is unreadable before provider-result commit."
                ) from exc

        with self.database.write_transaction() as connection:
            operation = self._require_grounded_operation(connection, operation_id, chat_id)
            attempt = connection.execute(
                "SELECT chat_id FROM grounded_provider_attempts WHERE operation_id = ?",
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if attempt is None or uuid_from_blob(bytes(attempt["chat_id"])) != chat_id:
                raise GroundedProviderAttemptConflictError(
                    "Provider result requires the matching durable attempt marker."
                )
            existing = connection.execute(
                """
                SELECT operation_id, chat_id, processing_run_id,
                       assistant_content, receipt_payload_json,
                       receipt_payload_sha256, created_at_us
                FROM grounded_provider_results WHERE operation_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if existing is not None:
                result = self._result_from_row(existing)
                if not (
                    result.chat_id == chat_id
                    and result.processing_run_id == processing_run_id
                    and result.assistant_content == assistant_content
                    and result.receipt_payload_json == canonical
                    and result.receipt_payload_sha256 == digest
                ):
                    raise GroundedProviderAttemptConflictError(
                        "Provider result conflicts with the already recorded result."
                    )
                self._match_or_store_identity_in_transaction(
                    connection,
                    operation_id=operation_id,
                    provider_id=provider_id,
                    model_id=model_id,
                    allow_store=False,
                )
                return result
            if str(operation["state"]) != ChatSendOperationState.USER_COMMITTED.value:
                raise GroundedProviderAttemptConflictError(
                    "A new provider result may be recorded only before assistant commit."
                )
            if (
                operation["processing_run_id"] is not None
                and uuid_from_blob(bytes(operation["processing_run_id"]))
                != processing_run_id
            ):
                raise GroundedProviderAttemptConflictError(
                    "Provider result conflicts with the pinned Grounded ProcessingRun."
                )
            if context_record is not None:
                if operation["processing_run_id"] is None:
                    raise GroundedProviderAttemptConflictError(
                        "Provider result requires the pinned Grounded ProcessingRun."
                    )
                current_context = connection.execute(
                    """
                    SELECT chat_id, payload_sha256
                    FROM grounded_context_packages
                    WHERE operation_id = ?
                    """,
                    (uuid_to_blob(operation_id),),
                ).fetchone()
                if (
                    current_context is None
                    or uuid_from_blob(bytes(current_context["chat_id"])) != chat_id
                    or context_record.chat_id != chat_id
                    or str(current_context["payload_sha256"])
                    != context_record.payload_sha256
                ):
                    raise GroundedProviderAttemptSchemaError(
                        "Pinned ContextPackage changed before provider-result commit."
                    )
                user = connection.execute(
                    """
                    SELECT chat_id, actor_id, message_type
                    FROM chat_messages
                    WHERE message_id = ?
                    """,
                    (uuid_to_blob(operation_id),),
                ).fetchone()
                if (
                    user is None
                    or uuid_from_blob(bytes(user["chat_id"])) != chat_id
                    or str(user["message_type"]) != "user"
                ):
                    raise GroundedProviderAttemptConflictError(
                        "Provider result is missing its durable Grounded trigger user."
                    )
                try:
                    validate_grounded_processing_run(
                        self.database,
                        processing_run_id=processing_run_id,
                        package=context_record.package,
                        trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
                    )
                except GroundedProcessingRunError as exc:
                    raise GroundedProviderAttemptConflictError(
                        "Provider result ProcessingRun conflicts with the pinned ContextPackage."
                    ) from exc
            self._require_pinned_context_identity_in_transaction(
                connection,
                operation_id=operation_id,
                provider_id=provider_id,
                model_id=model_id,
            )
            created_at_us = utc_now_us()
            connection.execute(
                """
                INSERT INTO grounded_provider_results (
                    operation_id, chat_id, processing_run_id,
                    assistant_content, receipt_payload_json,
                    receipt_payload_sha256, extension_schema_version, created_at_us
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid_to_blob(operation_id),
                    uuid_to_blob(chat_id),
                    uuid_to_blob(processing_run_id),
                    assistant_content,
                    canonical,
                    digest,
                    GROUNDED_PROVIDER_RESULT_EXTENSION_VERSION,
                    created_at_us,
                ),
            )
            self._match_or_store_identity_in_transaction(
                connection,
                operation_id=operation_id,
                provider_id=provider_id,
                model_id=model_id,
                allow_store=True,
            )
        stored = self.load_result(operation_id)
        if stored is None:
            raise RuntimeError("Provider result disappeared after commit.")
        return stored

    @staticmethod
    def _require_pinned_context_identity_in_transaction(
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        provider_id: str | None,
        model_id: str | None,
    ) -> None:
        context_table = connection.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = 'grounded_context_packages'
            """
        ).fetchone()
        if context_table is None:
            return
        context = connection.execute(
            """
            SELECT payload_json, payload_sha256
            FROM grounded_context_packages
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if context is None:
            return
        payload_json = str(context["payload_json"])
        expected_sha256 = str(context["payload_sha256"])
        actual_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        if actual_sha256 != expected_sha256:
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage failed checksum verification before provider-result commit."
            )
        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage is invalid JSON before provider-result commit."
            ) from exc
        if not isinstance(payload, dict):
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage payload is not an object."
            )
        signature = payload.get("model_signature")
        if not isinstance(signature, dict):
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage is missing its model signature."
            )
        pinned_provider = signature.get("provider")
        pinned_model = signature.get("model_identifier")
        if (
            not isinstance(pinned_provider, str)
            or not pinned_provider.strip()
            or not isinstance(pinned_model, str)
            or not pinned_model.strip()
        ):
            raise GroundedProviderAttemptSchemaError(
                "Pinned ContextPackage has an invalid model identity."
            )
        if provider_id is None or model_id is None:
            raise GroundedProviderAttemptConflictError(
                "Provider result identity is required by the pinned ContextPackage model."
            )
        if provider_id != pinned_provider or model_id != pinned_model:
            raise GroundedProviderAttemptConflictError(
                "Provider result identity conflicts with the pinned ContextPackage model."
            )

    @staticmethod
    def _match_or_store_identity_in_transaction(
        connection: sqlite3.Connection,
        *,
        operation_id: uuid.UUID,
        provider_id: str | None,
        model_id: str | None,
        allow_store: bool,
    ) -> None:
        existing = connection.execute(
            """
            SELECT provider_id, model_id
            FROM grounded_provider_result_identities
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if provider_id is None or model_id is None:
            if existing is not None:
                raise GroundedProviderAttemptConflictError(
                    "Provider result identity already exists and cannot be omitted."
                )
            return
        if existing is not None:
            if (
                str(existing["provider_id"]) == provider_id
                and str(existing["model_id"]) == model_id
            ):
                return
            raise GroundedProviderAttemptConflictError(
                "Provider result identity conflicts with the recorded model identity."
            )
        if not allow_store:
            raise GroundedProviderAttemptConflictError(
                "Provider result identity cannot be added after the result was recorded."
            )
        connection.execute(
            """
            INSERT INTO grounded_provider_result_identities (
                operation_id, provider_id, model_id, extension_schema_version
            ) VALUES (?, ?, ?, ?)
            """,
            (
                uuid_to_blob(operation_id),
                provider_id,
                model_id,
                GROUNDED_PROVIDER_RESULT_IDENTITY_EXTENSION_VERSION,
            ),
        )

    @staticmethod
    def _require_grounded_operation(
        connection: sqlite3.Connection,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
    ) -> sqlite3.Row:
        operation = connection.execute(
            """
            SELECT chat_id, mode, state, processing_run_id
            FROM chat_send_operations
            WHERE operation_id = ?
            """,
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if operation is None:
            raise GroundedProviderAttemptConflictError(
                "Provider boundary requires an existing send operation."
            )
        if uuid_from_blob(bytes(operation["chat_id"])) != chat_id:
            raise GroundedProviderAttemptConflictError(
                "Provider boundary chat identity conflicts with send operation."
            )
        if str(operation["mode"]) != "grounded":
            raise GroundedProviderAttemptConflictError(
                "Provider boundary marker is Grounded-only."
            )
        return cast(sqlite3.Row, operation)

    @staticmethod
    def _result_from_row(row: sqlite3.Row) -> GroundedProviderResult:
        result = GroundedProviderResult(
            operation_id=uuid_from_blob(bytes(row["operation_id"])),
            chat_id=uuid_from_blob(bytes(row["chat_id"])),
            processing_run_id=uuid_from_blob(bytes(row["processing_run_id"])),
            assistant_content=str(row["assistant_content"]),
            receipt_payload_json=str(row["receipt_payload_json"]),
            receipt_payload_sha256=str(row["receipt_payload_sha256"]),
            created_at_us=int(row["created_at_us"]),
        )
        try:
            canonical, digest = _canonical_receipt_payload(result.receipt_payload_json)
            validate_provider_result_contract(
                assistant_content=result.assistant_content,
                receipt_payload_json=result.receipt_payload_json,
            )
        except (ValueError, GroundedProviderResultContractError) as exc:
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider result violates its durable receipt contract."
            ) from exc
        if canonical != result.receipt_payload_json or digest != result.receipt_payload_sha256:
            raise GroundedProviderAttemptSchemaError(
                "Persisted provider result failed checksum verification."
            )
        return result
