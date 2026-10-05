from __future__ import annotations

import importlib
import uuid
from types import SimpleNamespace
from typing import Any

import pytest

from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedRecoveryStatus
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified import (
    UnifiedGroundedRecoveryRequiredError,
    UnifiedLocalChatService,
)


unified_module = importlib.import_module("athena.chat.unified")

_CHAT_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
_OPERATION_ID = uuid.UUID("22222222-2222-4222-8222-222222222222")
_RUN_ID = uuid.UUID("33333333-3333-4333-8333-333333333333")
_FINGERPRINT = ChatRequestFingerprint(
    payload_json='{"persisted":true}',
    payload_sha256="a" * 64,
    format_version=1,
)


class _PlanRepository:
    def __init__(self, _database: object, *, present: bool = True) -> None:
        self.present = present

    def load(self, operation_id: uuid.UUID) -> Any:
        assert operation_id == _OPERATION_ID
        if not self.present:
            return None
        return SimpleNamespace(
            operation_id=_OPERATION_ID,
            chat_id=_CHAT_ID,
            fingerprint=_FINGERPRINT,
            retrieval_query_override="persisted query",
        )


class _Coordinator:
    def __init__(self, _database: object, *, state: GroundedRecoveryState) -> None:
        self.state = state
        self.finalize_calls = 0

    def recover(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedRecoveryStatus:
        assert operation_id == _OPERATION_ID
        assert chat_id == _CHAT_ID
        assert fingerprint is _FINGERPRINT
        return GroundedRecoveryStatus(
            operation_id=operation_id,
            chat_id=chat_id,
            state=self.state,
            receipt=None,
            processing_run_id=_RUN_ID,
        )

    def finalize_recorded_result(self, **kwargs: object) -> None:
        del kwargs
        self.finalize_calls += 1


class _ServiceDouble:
    def __init__(self) -> None:
        self.model_runs = SimpleNamespace(database=object())
        self.resume_calls: list[dict[str, object]] = []

    def _resume_from_checkpoint(self, **kwargs: object) -> str:
        self.resume_calls.append(dict(kwargs))
        return "continued"

    def _replay_complete(self, *, status: GroundedRecoveryStatus) -> str:
        return f"complete:{status.state.value}"


def test_continue_operation_uses_only_persisted_recovery_inputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _ServiceDouble()
    coordinator = _Coordinator(
        service.model_runs.database,
        state=GroundedRecoveryState.RESUMABLE,
    )
    monkeypatch.setattr(
        unified_module,
        "UnifiedSendPlanRepository",
        lambda database: _PlanRepository(database),
    )
    monkeypatch.setattr(
        unified_module,
        "GroundedSendCoordinator",
        lambda database: coordinator,
    )

    result = UnifiedLocalChatService.continue_operation(
        service,  # type: ignore[arg-type]
        chat_id=_CHAT_ID,
        operation_id=_OPERATION_ID,
    )

    assert result == "continued"
    assert len(service.resume_calls) == 1
    call = service.resume_calls[0]
    assert call["fingerprint"] is _FINGERPRINT
    assert call["retrieval_query_override"] == "persisted query"
    assert call["on_delta"] is None
    assert call["cancel_requested"] is None
    status = call["status"]
    assert isinstance(status, GroundedRecoveryStatus)
    assert status.state is GroundedRecoveryState.RESUMABLE


def test_continue_operation_refuses_ambiguous_provider_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _ServiceDouble()
    coordinator = _Coordinator(
        service.model_runs.database,
        state=GroundedRecoveryState.AMBIGUOUS,
    )
    monkeypatch.setattr(
        unified_module,
        "UnifiedSendPlanRepository",
        lambda database: _PlanRepository(database),
    )
    monkeypatch.setattr(
        unified_module,
        "GroundedSendCoordinator",
        lambda database: coordinator,
    )

    with pytest.raises(UnifiedGroundedRecoveryRequiredError) as exc_info:
        UnifiedLocalChatService.continue_operation(
            service,  # type: ignore[arg-type]
            chat_id=_CHAT_ID,
            operation_id=_OPERATION_ID,
        )

    assert exc_info.value.status.state is GroundedRecoveryState.AMBIGUOUS
    assert service.resume_calls == []


def test_inspect_recovery_reports_absent_without_recreating_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _ServiceDouble()
    monkeypatch.setattr(
        unified_module,
        "UnifiedSendPlanRepository",
        lambda database: _PlanRepository(database, present=False),
    )

    status = UnifiedLocalChatService.inspect_operation_recovery(
        service,  # type: ignore[arg-type]
        chat_id=_CHAT_ID,
        operation_id=_OPERATION_ID,
    )

    assert status.state is GroundedRecoveryState.ABSENT
    assert status.operation_id == _OPERATION_ID
    assert status.chat_id == _CHAT_ID
