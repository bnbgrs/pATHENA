"""Actionable recovery for interrupted Grounded send operations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.chat.grounded_assistant_turn import GroundedAssistantTurnRepository
from athena.chat.grounded_completion import (
    GroundedSendCompletionRepository,
    GroundedSendReceipt,
)
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.storage.database import SQLiteDatabase


class GroundedRecoveryState(str, Enum):
    ABSENT = "absent"
    RESUMABLE = "resumable"
    AMBIGUOUS = "ambiguous"
    RESULT_AVAILABLE = "result_available"
    FINALIZATION_REQUIRED = "finalization_required"
    COMPLETE = "complete"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class GroundedRecoveryStatus:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    state: GroundedRecoveryState
    receipt: GroundedSendReceipt | None


class GroundedRecoveryConflictError(RuntimeError):
    """Durable recovery state cannot be finalized without risking divergence."""


class GroundedSendRecovery:
    """Decide and execute safe recovery without repeating a completed provider call."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.operations = ChatSendOperationRepository(database)
        self.reconciler = GroundedSendReconciler(database)
        self.provider_attempts = GroundedProviderAttemptRepository(database)
        self.assistant_turns = GroundedAssistantTurnRepository(database)
        self.completions = GroundedSendCompletionRepository(database)
        self.chats = ChatRepository(database)

    def inspect(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedRecoveryStatus:
        base = self.reconciler.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if base.state is GroundedReconciliationState.ABSENT:
            return self._status(operation_id, chat_id, GroundedRecoveryState.ABSENT)
        if base.state is GroundedReconciliationState.CONFLICT:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        if base.state is GroundedReconciliationState.COMPLETE:
            return GroundedRecoveryStatus(
                operation_id=operation_id,
                chat_id=chat_id,
                state=GroundedRecoveryState.COMPLETE,
                receipt=base.receipt,
            )

        operation = self.operations.load(operation_id)
        if operation is None:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        result = self.provider_attempts.load_result(operation_id)
        if operation.state is ChatSendOperationState.ASSISTANT_COMMITTED:
            state = (
                GroundedRecoveryState.FINALIZATION_REQUIRED
                if result is not None
                else GroundedRecoveryState.AMBIGUOUS
            )
            return self._status(operation_id, chat_id, state)
        if operation.state is not ChatSendOperationState.USER_COMMITTED:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        if result is not None:
            return self._status(
                operation_id,
                chat_id,
                GroundedRecoveryState.RESULT_AVAILABLE,
            )
        attempt = self.provider_attempts.load(operation_id)
        state = (
            GroundedRecoveryState.RESUMABLE
            if attempt is None
            else GroundedRecoveryState.AMBIGUOUS
        )
        return self._status(operation_id, chat_id, state)

    def finalize_recorded_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        actor_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedSendReceipt:
        status = self.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if status.state is GroundedRecoveryState.COMPLETE:
            if status.receipt is None:
                raise GroundedRecoveryConflictError(
                    "Completed recovery state is missing its durable receipt."
                )
            return status.receipt
        if status.state not in {
            GroundedRecoveryState.RESULT_AVAILABLE,
            GroundedRecoveryState.FINALIZATION_REQUIRED,
        }:
            raise GroundedRecoveryConflictError(
                f"Grounded provider result cannot finalize from {status.state.value}."
            )
        result = self.provider_attempts.load_result(operation_id)
        if result is None or result.chat_id != chat_id:
            raise GroundedRecoveryConflictError(
                "Recorded provider result is missing or belongs to another chat."
            )

        operation = self.operations.load(operation_id)
        if operation is None:
            raise GroundedRecoveryConflictError("Grounded send operation disappeared.")
        if operation.state is ChatSendOperationState.USER_COMMITTED:
            self.assistant_turns.commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=actor_id,
                content=result.assistant_content,
            )
        elif operation.state is ChatSendOperationState.ASSISTANT_COMMITTED:
            assistant_id = assistant_message_id_for_operation(operation_id)
            thread = self.chats.load_chat(chat_id)
            assistant = next(
                (message for message in thread.messages if message.message_id == assistant_id),
                None,
            )
            if assistant is None or assistant.content != result.assistant_content:
                raise GroundedRecoveryConflictError(
                    "Persisted assistant turn conflicts with recorded provider result."
                )
        else:
            raise GroundedRecoveryConflictError(
                "Grounded result finalization found an unexpected operation state."
            )

        return self.completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result.processing_run_id,
            payload_json=result.receipt_payload_json,
        )

    @staticmethod
    def _status(
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        state: GroundedRecoveryState,
    ) -> GroundedRecoveryStatus:
        return GroundedRecoveryStatus(
            operation_id=operation_id,
            chat_id=chat_id,
            state=state,
            receipt=None,
        )
