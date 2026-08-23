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
    ChatSendOperationSchemaError,
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

    def __post_init__(self) -> None:
        if not isinstance(self.operation_id, uuid.UUID):
            raise TypeError("Grounded reconciliation operation_id must be a UUID.")
        if not isinstance(self.chat_id, uuid.UUID):
            raise TypeError("Grounded reconciliation chat_id must be a UUID.")
        if not isinstance(self.state, GroundedReconciliationState):
            raise TypeError("Grounded reconciliation state must be a GroundedReconciliationState.")
        if self.receipt is not None and not isinstance(self.receipt, GroundedSendReceipt):
            raise TypeError("Grounded reconciliation receipt must be a GroundedSendReceipt or None.")
        if self.state is GroundedReconciliationState.COMPLETE:
            if self.receipt is None:
                raise ValueError("Complete Grounded reconciliation requires a durable receipt.")
            if self.receipt.operation_id != self.operation_id:
                raise ValueError("Grounded reconciliation receipt belongs to another operation.")
            if self.receipt.chat_id != self.chat_id:
                raise ValueError("Grounded reconciliation receipt belongs to another chat.")
            return
        if self.receipt is not None:
            raise ValueError("Non-complete Grounded reconciliation must not expose a receipt.")


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
        if not isinstance(operation_id, uuid.UUID):
            raise TypeError("operation_id must be a UUID.")
        if not isinstance(chat_id, uuid.UUID):
            raise TypeError("chat_id must be a UUID.")
        if not isinstance(fingerprint, ChatRequestFingerprint):
            raise TypeError("fingerprint must be a ChatRequestFingerprint.")
        try:
            match = self.operations.match_request(
                operation_id=operation_id,
                chat_id=chat_id,
                mode=ChatSendOperationMode.GROUNDED,
                fingerprint=fingerprint,
            )
        except ChatSendOperationSchemaError:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
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

        try:
            operation = self.operations.load(operation_id)
        except ChatSendOperationSchemaError:
            return self._status(
                operation_id,
                chat_id,
                GroundedReconciliationState.CONFLICT,
            )
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
