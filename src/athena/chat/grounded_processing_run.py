"""Validate durable ProcessingRun provenance for one Grounded ContextPackage."""

from __future__ import annotations

import hashlib
import json
import uuid

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


def validate_grounded_processing_run(
    database: SQLiteDatabase,
    *,
    processing_run_id: uuid.UUID,
    package: ContextPackage,
    trigger_actor_id: uuid.UUID,
) -> None:
    """Require one live ProcessingRun exactly bound to its Grounded request."""
    _repository, run = _load_bound_run(
        database,
        processing_run_id=processing_run_id,
        package=package,
        trigger_actor_id=trigger_actor_id,
    )
    if run.status != "running" or run.finished_at_us is not None:
        raise GroundedProcessingRunError(
            "Grounded generation requires a running ProcessingRun."
        )


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
    if run.status == "succeeded" and run.finished_at_us is not None:
        return run
    if run.status != "running" or run.finished_at_us is not None:
        raise GroundedProcessingRunError(
            "Grounded provider result conflicts with the ProcessingRun terminal state."
        )
    try:
        return repository.finish_run(processing_run_id, status="succeeded")
    except ProcessingRunNotFoundError as exc:
        recovered = repository.load_run(processing_run_id)
        if recovered.status == "succeeded" and recovered.finished_at_us is not None:
            return recovered
        raise GroundedProcessingRunError(
            "Grounded ProcessingRun could not be finalized as succeeded."
        ) from exc
