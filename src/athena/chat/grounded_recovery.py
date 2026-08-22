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
from athena.chat.grounded_provider_attempt import (
    GroundedProviderAttemptRepository,
    GroundedProviderAttemptSchemaError,
    GroundedProviderResult,
    GroundedProviderResultIdentity,
)
from athena.chat.grounded_provider_result_contract import (
    GroundedProviderResultContractError,
    validate_provider_result_contract,
)
from athena.chat.grounded_reconciliation import (
    GroundedReconciliationState,
    GroundedSendReconciler,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.chat.service import ChatService
from athena.common.ids import uuid_to_blob
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
    provider_result: GroundedProviderResult | None = None
    provider_identity: GroundedProviderResultIdentity | None = None


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
        self.chat = ChatService(self.chats)

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
            receipt = base.receipt
            if receipt is None:
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            try:
                result, identity = self._load_provider_state(operation_id)
            except GroundedProviderAttemptSchemaError:
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            if (
                result is None
                or result.chat_id != chat_id
                or result.processing_run_id != receipt.processing_run_id
                or result.receipt_payload_json != receipt.payload_json
                or result.receipt_payload_sha256 != receipt.payload_sha256
            ):
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            try:
                validate_provider_result_contract(
                    assistant_content=result.assistant_content,
                    receipt_payload_json=result.receipt_payload_json,
                )
            except GroundedProviderResultContractError:
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            if not self._assistant_matches_result(
                operation_id=operation_id,
                chat_id=chat_id,
                result=result,
                identity=identity,
            ):
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            return GroundedRecoveryStatus(
                operation_id=operation_id,
                chat_id=chat_id,
                state=GroundedRecoveryState.COMPLETE,
                receipt=receipt,
                provider_result=result,
                provider_identity=identity,
            )

        operation = self.operations.load(operation_id)
        if operation is None:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        try:
            result, identity = self._load_provider_state(operation_id)
        except GroundedProviderAttemptSchemaError:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        if result is not None:
            try:
                validate_provider_result_contract(
                    assistant_content=result.assistant_content,
                    receipt_payload_json=result.receipt_payload_json,
                )
            except GroundedProviderResultContractError:
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
        if operation.state is ChatSendOperationState.ASSISTANT_COMMITTED:
            if result is not None and not self._assistant_matches_result(
                operation_id=operation_id,
                chat_id=chat_id,
                result=result,
                identity=identity,
            ):
                return self._status(
                    operation_id,
                    chat_id,
                    GroundedRecoveryState.CONFLICT,
                )
            state = (
                GroundedRecoveryState.FINALIZATION_REQUIRED
                if result is not None
                else GroundedRecoveryState.AMBIGUOUS
            )
            return self._status(
                operation_id,
                chat_id,
                state,
                provider_result=result,
                provider_identity=identity,
            )
        if operation.state is not ChatSendOperationState.USER_COMMITTED:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        if result is not None:
            return self._status(
                operation_id,
                chat_id,
                GroundedRecoveryState.RESULT_AVAILABLE,
                provider_result=result,
                provider_identity=identity,
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
        fingerprint: ChatRequestFingerprint,
        actor_id: uuid.UUID | None = None,
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
        try:
            result, identity = self._load_provider_state(operation_id)
        except GroundedProviderAttemptSchemaError as exc:
            raise GroundedRecoveryConflictError(
                "Recorded provider result journal is corrupted."
            ) from exc
        if result is None or result.chat_id != chat_id:
            raise GroundedRecoveryConflictError(
                "Recorded provider result is missing or belongs to another chat."
            )
        try:
            validate_provider_result_contract(
                assistant_content=result.assistant_content,
                receipt_payload_json=result.receipt_payload_json,
            )
        except GroundedProviderResultContractError as exc:
            raise GroundedRecoveryConflictError(
                "Recorded provider result violates its durable receipt contract."
            ) from exc

        if identity is None:
            if actor_id is None:
                raise GroundedRecoveryConflictError(
                    "Legacy provider result is missing model identity for autonomous recovery."
                )
            resolved_actor_id = actor_id
        else:
            resolved_actor_id = self.chat.ensure_primary_model(
                provider_id=identity.provider_id,
                model_id=identity.model_id,
            )
            if actor_id is not None and actor_id != resolved_actor_id:
                raise GroundedRecoveryConflictError(
                    "Requested recovery actor conflicts with durable provider model identity."
                )

        operation = self.operations.load(operation_id)
        if operation is None:
            raise GroundedRecoveryConflictError("Grounded send operation disappeared.")
        if operation.state is ChatSendOperationState.USER_COMMITTED:
            self.assistant_turns.commit(
                operation_id=operation_id,
                chat_id=chat_id,
                actor_id=resolved_actor_id,
                content=result.assistant_content,
            )
        elif operation.state is ChatSendOperationState.ASSISTANT_COMMITTED:
            assistant_id = assistant_message_id_for_operation(operation_id)
            thread = self.chats.load_chat(chat_id)
            assistant = next(
                (message for message in thread.messages if message.message_id == assistant_id),
                None,
            )
            if (
                assistant is None
                or assistant.content != result.assistant_content
                or assistant.actor_id != resolved_actor_id
            ):
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

    def _load_provider_state(
        self,
        operation_id: uuid.UUID,
    ) -> tuple[GroundedProviderResult | None, GroundedProviderResultIdentity | None]:
        result = self.provider_attempts.load_result(operation_id)
        identity = (
            None
            if result is None
            else self.provider_attempts.load_result_identity(operation_id)
        )
        return result, identity

    def _assistant_matches_result(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        result: GroundedProviderResult,
        identity: GroundedProviderResultIdentity | None,
    ) -> bool:
        assistant_id = assistant_message_id_for_operation(operation_id)
        thread = self.chats.load_chat(chat_id)
        assistant = next(
            (message for message in thread.messages if message.message_id == assistant_id),
            None,
        )
        if assistant is None or assistant.content != result.assistant_content:
            return False
        if identity is None:
            return True

        actor = self.database.connection.execute(
            """
            SELECT actor_type, display_name
            FROM actors
            WHERE actor_id = ?
            """,
            (uuid_to_blob(assistant.actor_id),),
        ).fetchone()
        return (
            actor is not None
            and str(actor["actor_type"]) == "primary_model"
            and str(actor["display_name"])
            == f"{identity.provider_id}:{identity.model_id}"
        )

    @staticmethod
    def _status(
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        state: GroundedRecoveryState,
        *,
        provider_result: GroundedProviderResult | None = None,
        provider_identity: GroundedProviderResultIdentity | None = None,
    ) -> GroundedRecoveryStatus:
        return GroundedRecoveryStatus(
            operation_id=operation_id,
            chat_id=chat_id,
            state=state,
            receipt=None,
            provider_result=provider_result,
            provider_identity=provider_identity,
        )