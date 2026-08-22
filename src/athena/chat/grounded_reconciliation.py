"""Crash-safe reconciliation projection for durable Grounded send operations."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from athena.chat.grounded_completion import (
    GroundedSendCompletionCorruptionError,
    GroundedSendCompletionRepository,
    GroundedSendReceipt,
)
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_operation import (
    ChatSendOperationMatch,
    ChatSendOperationMode,
    ChatSendOperationRepository,
    ChatSendOperationState,
)
from athena.storage.database import SQLiteDatabase


class GroundedReconciliationState(str, Enum):
    ABSENT = "absent"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class GroundedReconciliationStatus:
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    state: GroundedReconciliationState
    receipt: GroundedSendReceipt | None


class GroundedSendReconciler:
    """Project durable operation/receipt state without performing generation."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.operations = ChatSendOperationRepository(database)
        self.completions = GroundedSendCompletionRepository(database)

    def inspect(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> GroundedReconciliationStatus:
        match = self.operations.match_request(
            operation_id=operation_id,
            chat_id=chat_id,
            mode=ChatSendOperationMode.GROUNDED,
            fingerprint=fingerprint,
        )
        if match is ChatSendOperationMatch.ABSENT:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.ABSENT,
            )
        if match is ChatSendOperationMatch.CONFLICT:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
            )

        operation = self.operations.load(operation_id)
        if operation is None:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
            )
        try:
            receipt = self.completions.load(operation_id)
        except GroundedSendCompletionCorruptionError:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
            )

        if operation.state is ChatSendOperationState.COMPLETE:
            if (
                receipt is None
                or operation.processing_run_id is None
                or operation.receipt_payload_sha256 is None
                or receipt.chat_id != chat_id
                or receipt.processing_run_id != operation.processing_run_id
                or receipt.payload_sha256 != operation.receipt_payload_sha256
            ):
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedReconciliationState.CONFLICT,
                )
            return GroundedReconciliationStatus(
                operation_id=operation_id,
                chat_id=chat_id,
                state=GroundedReconciliationState.COMPLETE,
                receipt=receipt,
            )

        if receipt is not None:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
            )

        return self._status(
            operation_id,
            chat_id,
            GroundedReconciliationState.INCOMPLETE,
        )

    @staticmethod
    def _status(
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        state: GroundedReconciliationState,
    ) -> GroundedReconciliationStatus:
        return GroundedReconciliationStatus(
            operation_id=operation_id,
            chat_id=chat_id,
            state=state,
            receipt=None,
        )