"""High-level durable state machine for one Grounded chat send operation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_context_package import (
    GroundedContextPackageRecord,
    GroundedContextPackageRepository,
)
from athena.chat.grounded_completion import (
    GroundedSendCompletionRepository,
    GroundedSendReceipt,
)
from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttempt,
    GroundedProviderAttemptConflictError,
    GroundedProviderAttemptRepository,
    GroundedProviderResult,
)
from athena.chat.grounded_provider_result_contract import validate_provider_result_contract
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedReconciliationStatus,
    GroundedSendReconciler,
)
from athena.chat.grounded_recovery import (
    GroundedRecoveryState,
    GroundedRecoveryStatus,
    GroundedSendRecovery,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.retrieval.context_package import ContextPackage
from athena.storage.database import SQLiteDatabase


@dataclass(frozen=True, slots=True)
class GroundedSendStart:
    user_message: ChatMessage
    status: GroundedReconciliationStatus


class GroundedSendStateError(RuntimeError):
    """A caller attempted execution when reconciliation requires another action."""

    def __init__(self, status: GroundedReconciliationStatus) -> None:
        self.status = status
        super().__init__(
            f"Grounded send operation {status.operation_id} is {status.state.value}; "
            "only absent operations may start execution."
        )


class GroundedProviderBoundaryError(RuntimeError):
    """The provider boundary is unsafe for the current durable recovery state."""

    def __init__(self, status: GroundedRecoveryStatus) -> None:
        self.status = status
        super().__init__(
            f"Grounded send operation {status.operation_id} is {status.state.value}; "
            "only resumable operations may begin a provider attempt."
        )


class GroundedProviderResultError(RuntimeError):
    """A provider result cannot be journaled from the current recovery state."""

    def __init__(self, status: GroundedRecoveryStatus) -> None:
        self.status = status
        super().__init__(
            f"Grounded send operation {status.operation_id} is {status.state.value}; "
            "only ambiguous operations may record a first provider result."
        )


class GroundedSendCoordinator:
    """Coordinate crash-safe start, assistant commit, completion and replay."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.reconciler = GroundedSendReconciler(database)
        self.context_packages = GroundedContextPackageRepository(database)
        self.recovery = GroundedSendRecovery(database)
        self.provider_attempts = GroundedProviderAttemptRepository(database)
        self.user_turns = GroundedUserTurnRepository(database)
        self.assistant_turns = GroundedAssistantTurnRepository(database)
        self.completions = GroundedSendCompletionRepository(database)

    def reconcile(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedReconciliationStatus:
        return self.reconciler.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

    def recover(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedRecoveryStatus:
        return self.recovery.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )

    def store_context_package(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        package: ContextPackage,
    ) -> GroundedContextPackageRecord:
        return self.context_packages.store(
            operation_id=operation_id,
            chat_id=chat_id,
            package=package,
        )

    def load_context_package(
        self,
        operation_id: uuid.UUID,
    ) -> GroundedContextPackageRecord | None:
        return self.context_packages.load(operation_id)

    def begin_provider_attempt(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedProviderAttempt:
        before = self.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if before.state is not GroundedRecoveryState.RESUMABLE:
            raise GroundedProviderBoundaryError(before)
        try:
            attempt = self.provider_attempts.mark_started(
                operation_id=operation_id,
                chat_id=chat_id,
            )
        except GroundedProviderAttemptConflictError as exc:
            after_conflict = self.recover(
                operation_id=operation_id,
                chat_id=chat_id,
                fingerprint=fingerprint,
            )
            if after_conflict.state is not GroundedRecoveryState.RESUMABLE:
                raise GroundedProviderBoundaryError(after_conflict) from exc
            raise
        after = self.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if after.state is not GroundedRecoveryState.AMBIGUOUS:
            raise RuntimeError(
                "Grounded provider attempt did not become durably ambiguous."
            )
        return attempt

    def record_provider_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
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
        before = self.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if before.state is not GroundedRecoveryState.AMBIGUOUS:
            raise GroundedProviderResultError(before)
        result = self.provider_attempts.store_result(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            assistant_content=assistant_content,
            receipt_payload_json=receipt_payload_json,
            provider_id=provider_id,
            model_id=model_id,
        )
        after = self.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if after.state is not GroundedRecoveryState.RESULT_AVAILABLE:
            raise RuntimeError(
                "Grounded provider result did not become durably recoverable."
            )
        return result

    def finalize_recorded_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
        actor_id: uuid.UUID | None = None,
    ) -> GroundedSendReceipt:
        return self.recovery.finalize_recorded_result(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            fingerprint=fingerprint,
        )

    def start(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        content: str,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedSendStart:
        before = self.reconcile(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if before.state is not GroundedReconciliationState.ABSENT:
            raise GroundedSendStateError(before)
        user_message = self.user_turns.commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content=content,
            fingerprint=fingerprint,
        )
        after = self.reconcile(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if after.state is not GroundedReconciliationState.INCOMPLETE:
            raise RuntimeError("Grounded send start did not become durably incomplete.")
        return GroundedSendStart(user_message=user_message, status=after)

    def commit_assistant(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        content: str,
    ) -> ChatMessage:
        return self.assistant_turns.commit(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=actor_id,
            content=content,
        )

    def complete(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        processing_run_id: uuid.UUID,
        payload_json: str,
    ) -> GroundedSendReceipt:
        return self.completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            payload_json=payload_json,
        )
