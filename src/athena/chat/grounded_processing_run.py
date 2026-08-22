"""Validate durable ProcessingRun provenance for one Grounded ContextPackage."""

from __future__ import annotations

import hashlib
import json
import uuid

from athena.chat.send_operation import (
    ChatSendOperationConflictError,
    ChatSendOperationNotFoundError,
    ChatSendOperationRepository,
)
from athena.model.provenance import (
    ModelRunRepository,
    ProcessingRun,
    ProcessingRunNotFoundError,
)
from athena.retrieval.context_package import ContextPackage
from athena.storage.database import SQLiteDatabase

GROUNDED_PROCESSING_RUN_TYPE = "chat.unified_local_context_package"


class GroundedProcessingRunError(RuntimeError):
    """A Grounded provider call is not backed by matching durable model provenance."""


def _canonical_snapshot(package: ContextPackage) -> str:
    return json.dumps(
        package.run_snapshot(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _expected_configuration_hash(package: ContextPackage) -> bytes:
    configuration_json = package.model_signature.context_configuration_json
    if configuration_json is None:
        raise GroundedProcessingRunError(
            "Grounded ContextPackage is missing ProcessingRun configuration provenance."
        )
    return hashlib.sha256(configuration_json.encode("utf-8")).digest()


def _load_bound_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> tuple[ModelRunRepository, ProcessingRun]:
    repository = ModelRunRepository(database)
    try:
        run = repository.load_run(processing_run_id)
    except ProcessingRunNotFoundError as exc:
        raise GroundedProcessingRunError(
            "Grounded generation requires a persisted ProcessingRun."
        ) from exc

    if run.run_type != GROUNDED_PROCESSING_RUN_TYPE:
        raise GroundedProcessingRunError(
            "ProcessingRun type conflicts with the Grounded chat operation."
        )
    if not run.pipeline_version.strip():
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun has an invalid pipeline version."
        )
    if (run.prompt_template_id is None) != (run.prompt_template_version is None):
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun prompt-template provenance is incomplete."
        )
    if run.trigger_actor_id != trigger_actor_id:
        raise GroundedProcessingRunError(
            "ProcessingRun trigger actor conflicts with the Grounded user actor."
        )
    if run.model_signature_id is None:
        raise GroundedProcessingRunError(
            "Grounded generation ProcessingRun is missing ModelSignature provenance."
        )
    if run.model_signature_id != package.model_signature.model_signature_id:
        raise GroundedProcessingRunError(
            "ProcessingRun ModelSignature conflicts with the Grounded ContextPackage."
        )
    if run.input_snapshot_json != _canonical_snapshot(package):
        raise GroundedProcessingRunError(
            "ProcessingRun input snapshot conflicts with the Grounded ContextPackage."
        )
    if run.configuration_hash != _expected_configuration_hash(package):
        raise GroundedProcessingRunError(
            "ProcessingRun configuration conflicts with the Grounded ContextPackage."
        )

    try:
        signature = repository.load_signature(run.model_signature_id)
    except LookupError as exc:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun references a missing ModelSignature."
        ) from exc

    package_signature = package.model_signature
    if (
        signature.provider != package_signature.provider
        or signature.model_identifier != package_signature.model_identifier
        or signature.quantization != package_signature.quantization
        or signature.generation_parameters_json
        != package_signature.generation_parameters_json
        or signature.context_configuration_json
        != package_signature.context_configuration_json
        or signature.signature_hash.hex() != package_signature.signature_hash_hex
    ):
        raise GroundedProcessingRunError(
            "Persisted ModelSignature conflicts with the Grounded ContextPackage."
        )
    return repository, run


def validate_grounded_processing_run_provenance(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> ProcessingRun:
    """Require exact durable Grounded run provenance regardless of lifecycle state."""
    _repository, run = _load_bound_run(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    return run


def validate_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> None:
    """Require one live ProcessingRun exactly bound to its Grounded request."""
    run = validate_grounded_processing_run_provenance(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    if run.status != "running" or run.finished_at_us is not None:
        raise GroundedProcessingRunError(
            "Grounded generation requires a running ProcessingRun."
        )


def bind_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    operation_id: uuid.UUID,
    chat_id: uuid.UUID,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> ProcessingRun:
    """Durably pin the exact live ProcessingRun before provider execution."""
    current_user = package.current_user_ref()
    if current_user.entity_id != operation_id:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun operation identity conflicts with CURRENT-USER."
        )
    run = validate_grounded_processing_run_provenance(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    if run.status != "running" or run.finished_at_us is not None:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun must be running when it is pinned."
        )
    try:
        operation = ChatSendOperationRepository(database).bind_grounded_processing_run(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
        )
    except (ChatSendOperationConflictError, ChatSendOperationNotFoundError) as exc:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun conflicts with durable operation identity."
        ) from exc
    if operation.processing_run_id != processing_run_id:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun binding did not persist the requested identity."
        )
    return run


def _finish_bound_run(
    repository: ModelRunRepository,
    run: ProcessingRun,
    *,
    status: str,
    error_detail: str | None = None,
) -> ProcessingRun:
    if run.status == status and run.finished_at_us is not None:
        return run
    if run.status != "running" or run.finished_at_us is not None:
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun conflicts with the requested terminal state."
        )
    try:
        return repository.finish_run(
            run.processing_run_id,
            status=status,
            error_detail=error_detail,
        )
    except ProcessingRunNotFoundError as exc:
        try:
            recovered = repository.load_run(run.processing_run_id)
        except ProcessingRunNotFoundError as missing_exc:
            raise GroundedProcessingRunError(
                "Grounded ProcessingRun disappeared during terminal finalization."
            ) from missing_exc
        if recovered.status == status and recovered.finished_at_us is not None:
            return recovered
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun could not reach the requested terminal state."
        ) from exc


def complete_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> ProcessingRun:
    """Mark a proven returned Grounded model execution succeeded, idempotently."""
    repository, run = _load_bound_run(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    return _finish_bound_run(repository, run, status="succeeded")


def fail_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
    error_detail: str,
) -> ProcessingRun:
    """Mark a proven Grounded execution failure failed, idempotently."""
    repository, run = _load_bound_run(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    return _finish_bound_run(
        repository,
        run,
        status="failed",
        error_detail=error_detail,
    )


def cancel_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> ProcessingRun:
    """Mark an interrupted Grounded execution cancelled, idempotently."""
    repository, run = _load_bound_run(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    return _finish_bound_run(
        repository,
        run,
        status="cancelled",
        error_detail="KeyboardInterrupt",
    )
