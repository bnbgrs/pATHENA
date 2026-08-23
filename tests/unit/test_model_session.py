from __future__ import annotations

import uuid

import pytest

from athena.model.session import (
    ModelSession,
    ModelSessionState,
    ModelSessionStateError,
)


def _session() -> ModelSession:
    return ModelSession(
        request_id=uuid.uuid4(),
        model_signature_id=uuid.uuid4(),
        context_budget=4096,
        output_reserve=512,
    )


def test_model_session_streams_and_completes() -> None:
    session = _session()

    session.begin_streaming()
    session.record_delta()
    session.record_delta()
    session.complete()

    assert session.state is ModelSessionState.COMPLETED
    assert session.emitted_delta_count == 2
    assert session.terminal
    assert session.request_key == str(session.request_id)


def test_cancel_before_streaming_never_requires_provider_cancel() -> None:
    session = _session()

    provider_work_may_be_active = session.request_cancel()

    assert not provider_work_may_be_active
    assert session.state is ModelSessionState.CANCELLED
    assert session.cancel_requested
    with pytest.raises(ModelSessionStateError, match="created state"):
        session.begin_streaming()


def test_cancel_during_streaming_requires_provider_cancel_and_discards_late_delta() -> None:
    session = _session()
    session.begin_streaming()

    provider_work_may_be_active = session.request_cancel()

    assert provider_work_may_be_active
    assert session.state is ModelSessionState.STREAMING
    with pytest.raises(ModelSessionStateError, match="discard provider deltas"):
        session.record_delta()


def test_late_completion_after_cancel_becomes_cancelled() -> None:
    session = _session()
    session.begin_streaming()
    assert session.request_cancel()

    with pytest.raises(ModelSessionStateError, match="discard late provider completion"):
        session.complete()

    assert session.state is ModelSessionState.CANCELLED
    assert session.terminal


def test_provider_failure_after_cancel_is_classified_cancelled() -> None:
    session = _session()
    session.begin_streaming()
    session.request_cancel()

    session.fail()

    assert session.state is ModelSessionState.CANCELLED


def test_provider_failure_without_cancel_is_failed() -> None:
    session = _session()
    session.begin_streaming()

    session.fail()

    assert session.state is ModelSessionState.FAILED
    assert session.terminal


@pytest.mark.parametrize("field", ["request_id", "model_signature_id"])
def test_model_session_requires_uuid_identity(field: str) -> None:
    values: dict[str, object] = {
        "request_id": uuid.uuid4(),
        "model_signature_id": uuid.uuid4(),
        "context_budget": 100,
        "output_reserve": 10,
    }
    values[field] = "not-a-uuid"

    with pytest.raises(TypeError, match="must be a UUID"):
        ModelSession(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["context_budget", "output_reserve"])
@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "10", None])
def test_model_session_rejects_invalid_positive_budget(
    field: str,
    value: object,
) -> None:
    values: dict[str, object] = {
        "request_id": uuid.uuid4(),
        "model_signature_id": uuid.uuid4(),
        "context_budget": 100,
        "output_reserve": 10,
    }
    values[field] = value

    with pytest.raises((TypeError, ValueError)):
        ModelSession(**values)  # type: ignore[arg-type]


def test_model_session_rejects_delta_before_streaming() -> None:
    with pytest.raises(ModelSessionStateError, match="only while streaming"):
        _session().record_delta()


def test_completed_session_ignores_new_cancel_request() -> None:
    session = _session()
    session.begin_streaming()
    session.complete()

    assert not session.request_cancel()
    assert session.state is ModelSessionState.COMPLETED
