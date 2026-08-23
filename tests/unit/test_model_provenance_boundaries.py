from __future__ import annotations

import uuid

import pytest

from athena.model.provenance import ModelSignature, ProcessingRun


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def test_model_signature_rejects_invalid_hash() -> None:
    with pytest.raises(ValueError, match="32-byte SHA-256"):
        ModelSignature(
            model_signature_id=_uuid(),
            provider="lm_studio",
            model_identifier="model",
            model_revision=None,
            quantization=None,
            generation_parameters_json="{}",
            context_configuration_json=None,
            signature_hash=b"short",
            created_at_us=1,
        )


def test_model_signature_rejects_bool_timestamp() -> None:
    with pytest.raises(TypeError, match="created_at_us must be an integer"):
        ModelSignature(
            model_signature_id=_uuid(),
            provider="lm_studio",
            model_identifier="model",
            model_revision=None,
            quantization=None,
            generation_parameters_json="{}",
            context_configuration_json=None,
            signature_hash=b"x" * 32,
            created_at_us=True,
        )


def _run(**overrides: object) -> ProcessingRun:
    values: dict[str, object] = {
        "processing_run_id": _uuid(),
        "run_type": "source_analysis",
        "started_at_us": 10,
        "finished_at_us": None,
        "status": "running",
        "trigger_actor_id": _uuid(),
        "pipeline_version": "v1",
        "input_snapshot_json": "{}",
        "configuration_hash": b"c" * 32,
        "model_signature_id": None,
        "prompt_template_id": None,
        "prompt_template_version": None,
        "error_detail": None,
    }
    values.update(overrides)
    return ProcessingRun(**values)  # type: ignore[arg-type]


def test_processing_run_rejects_finished_timestamp_while_running() -> None:
    with pytest.raises(ValueError, match="must not have finished_at_us"):
        _run(finished_at_us=11)


def test_processing_run_requires_finished_timestamp_for_terminal_status() -> None:
    with pytest.raises(ValueError, match="requires finished_at_us"):
        _run(status="succeeded")


def test_processing_run_rejects_timestamp_regression() -> None:
    with pytest.raises(ValueError, match="precedes started_at_us"):
        _run(status="failed", finished_at_us=9)


def test_processing_run_rejects_unknown_status() -> None:
    with pytest.raises(ValueError, match="status is invalid"):
        _run(status="unknown")


def test_processing_run_rejects_bool_timestamp() -> None:
    with pytest.raises(TypeError, match="started_at_us must be an integer"):
        _run(started_at_us=True)


def test_processing_run_accepts_terminal_state_with_monotonic_timestamp() -> None:
    run = _run(status="cancelled", finished_at_us=10)
    assert run.status == "cancelled"
    assert run.finished_at_us == 10
