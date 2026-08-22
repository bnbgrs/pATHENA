from __future__ import annotations

import hashlib
import json
import uuid

import pytest

from athena.chat.grounded_context_package import (
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatSendMode, build_chat_request_fingerprint
from athena.common.ids import uuid_to_blob
from athena.model.provenance import ModelSignature
from athena.retrieval.context_package import (
    ContextIncludedRef,
    ContextPackageBudget,
    ContextPackageService,
    ContextSection,
    ContextTokenEstimates,
    ExcludedCandidateSummary,
)
from athena.storage.database import SQLiteDatabase


def _fingerprint(chat_id: uuid.UUID):
    return build_chat_request_fingerprint(
        mode=ChatSendMode.GROUNDED,
        chat_id=chat_id,
        content="hello",
        requested_model_id="primary",
        requested_embedding_model_id=None,
        effective_context_limit=4096,
        max_output_tokens=1000,
        temperature=None,
        reasoning_mode="off",
        retrieval_configuration={},
    )


def _stored_package(database: SQLiteDatabase):
    chats = ChatRepository(database)
    user = chats.create_actor(actor_type="user")
    chat_id = chats.create_chat(actor_id=user)
    operation_id = uuid.uuid4()
    message = GroundedUserTurnRepository(database).commit(
        operation_id=operation_id,
        chat_id=chat_id,
        actor_id=user,
        content="hello",
        fingerprint=_fingerprint(chat_id),
    )
    signature = ModelSignature(
        model_signature_id=uuid.uuid4(),
        provider="lm_studio",
        model_identifier="primary",
        model_revision=None,
        quantization=None,
        generation_parameters_json='{"max_output_tokens":1000,"reasoning_mode":"off"}',
        context_configuration_json=None,
        signature_hash=b"s" * 32,
        created_at_us=1,
    )
    package = ContextPackageService.build_from_sections(
        model_signature=signature,
        budget=ContextPackageBudget(
            effective_context_limit=4096,
            context_budget=2800,
            output_reserve=1000,
            safety_margin=200,
        ),
        sections=(
            ContextSection(
                name="current_user",
                role="user",
                content="hello",
                included_ref_ids=("CURRENT-USER",),
            ),
        ),
        included_refs=(
            ContextIncludedRef(
                ref_id="CURRENT-USER",
                entity_type="chat_message",
                entity_id=operation_id,
                revision_id=message.revision_id,
            ),
        ),
        excluded_candidate_summary=ExcludedCandidateSummary(
            retrieval_candidate_count=0,
            retrieval_included_count=0,
            retrieval_excluded_count=0,
            memory_candidate_count=0,
            memory_included_count=0,
            memory_excluded_count=0,
            conversation_candidate_count=0,
            conversation_included_count=0,
            conversation_excluded_count=0,
        ),
        token_estimates=ContextTokenEstimates(
            conversation_tokens=0,
            current_user_tokens=10,
            system_tokens=0,
            context_tokens=0,
            estimated_input_tokens=10,
            estimated_total_tokens=1010,
        ),
        snapshot_commit_seq=1,
    )
    repository = GroundedContextPackageRepository(database)
    repository.store(operation_id=operation_id, chat_id=chat_id, package=package)
    return repository, operation_id


def _tamper_payload(database: SQLiteDatabase, operation_id: uuid.UUID, mutate) -> None:
    row = database.connection.execute(
        "SELECT payload_json FROM grounded_context_packages WHERE operation_id = ?",
        (uuid_to_blob(operation_id),),
    ).fetchone()
    assert row is not None
    payload = json.loads(str(row["payload_json"]))
    mutate(payload)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    with database.write_transaction() as connection:
        connection.execute(
            """
            UPDATE grounded_context_packages
            SET payload_json = ?, payload_sha256 = ?
            WHERE operation_id = ?
            """,
            (encoded, digest, uuid_to_blob(operation_id)),
        )


def test_context_package_load_normalizes_invalid_uuid_to_schema_error(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        repository, operation_id = _stored_package(database)
        _tamper_payload(
            database,
            operation_id,
            lambda payload: payload.__setitem__("request_id", "not-a-uuid"),
        )
        with pytest.raises(GroundedContextPackageSchemaError, match="valid UUID"):
            repository.load(operation_id)
    finally:
        database.stop()


def test_context_package_load_normalizes_generation_contract_corruption(tmp_path) -> None:
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    try:
        repository, operation_id = _stored_package(database)
        _tamper_payload(
            database,
            operation_id,
            lambda payload: payload["model_signature"].__setitem__(
                "generation_parameters_json",
                "not-json",
            ),
        )
        with pytest.raises(
            GroundedContextPackageSchemaError,
            match="model-input contract",
        ):
            repository.load(operation_id)
    finally:
        database.stop()
