"""High-level durable state machine for one Grounded chat send operation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import (
    GroundedSendCompletionRepository,
    GroundedSendReceipt,
)
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedReconciliationStatus,
    GroundedSendReconciler,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
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


class GroundedSendCoordinator:
    """Coordinate crash-safe start, assistant commit, completion and replay."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.reconciler = GroundedSendReconciler(database)
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
