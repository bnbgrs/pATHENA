"""Actionable recovery classification for interrupted Grounded send operations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.chat.grounded_completion import GroundedSendReceipt
from athena.chat.grounded_provider_attempt import GroundedProviderAttemptRepository
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.storage.database import SQLiteDatabase


class GroundedRecoveryState(str, Enum):
    ABSENT = "absent"
    RESUMABLE = "resumable"
    AMBIGUOUS = "ambiguous"
    FINALIZATION_REQUIRED = "finalization_required"
    COMPLETE = "complete"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class GroundedRecoveryStatus:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    state: GroundedRecoveryState
    receipt: GroundedSendReceipt | None


class GroundedSendRecovery:
    """Decide whether interrupted work may resume, must reconcile, or can replay."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.operations = ChatSendOperationRepository(database)
        self.reconciler = GroundedSendReconciler(database)
        self.provider_attempts = GroundedProviderAttemptRepository(database)

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
        if operation.state is ChatSendOperationState.ASSISTANT_COMMITTED:
            return self._status(
                operation_id,
                chat_id,
                GroundedRecoveryState.FINALIZATION_REQUIRED,
            )
        if operation.state is not ChatSendOperationState.USER_COMMITTED:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        attempt = self.provider_attempts.load(operation_id)
        state = (
            GroundedRecoveryState.RESUMABLE
            if attempt is None
            else GroundedRecoveryState.AMBIGUOUS
        )
        return self._status(operation_id, chat_id, state)

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
