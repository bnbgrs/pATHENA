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
from athena.chat.grounded_context_package import (
    GroundedContextPackageRepository,
    GroundedContextPackageSchemaError,
)
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    complete_grounded_processing_run,
    validate_grounded_processing_run_provenance,
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
from athena.chat.grounded_request_context import (
    GroundedRequestContextBindingError,
    validate_grounded_request_context_binding,
)
from athena.chat.repository import ChatRepository
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.send_identity import assistant_message_id_for_operation
from athena.chat.send_operation import ChatSendOperationRepository, ChatSendOperationState
from athena.chat.service import ChatService
from athena.common.ids import uuid_from_blob, uuid_to_blob
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
        self.context_packages = GroundedContextPackageRepository(database)
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

        try:
            context_record = self.context_packages.load(operation_id)
        except GroundedContextPackageSchemaError:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
        if context_record is not None:
            if context_record.chat_id != chat_id:
                return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
            try:
                validate_grounded_request_context_binding(
                    package=context_record.package,
                    fingerprint=fingerprint,
                )
            except GroundedRequestContextBindingError:
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
                result, identity = self._load_provider_state(
                    operation_id,
                    require_succeeded_run=True,
                )
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
        if (
            result is not None
            and operation.processing_run_id is not None
            and result.processing_run_id != operation.processing_run_id
        ):
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
        try:
            attempt = self.provider_attempts.load(operation_id)
        except GroundedProviderAttemptSchemaError:
            return self._status(operation_id, chat_id, GroundedRecoveryState.CONFLICT)
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

        try:
            context_record = self.context_packages.load(operation_id)
        except GroundedContextPackageSchemaError as exc:
            raise GroundedRecoveryConflictError(
                "Grounded recovery found a corrupted pinned ContextPackage."
            ) from exc
        if context_record is not None:
            if context_record.chat_id != chat_id:
                raise GroundedRecoveryConflictError(
                    "Pinned ContextPackage chat conflicts with Grounded recovery."
                )
            user = self.database.connection.execute(
                """
                SELECT chat_id, actor_id, message_type
                FROM chat_messages
                WHERE message_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if (
                user is None
                or uuid_from_blob(bytes(user["chat_id"])) != chat_id
                or str(user["message_type"]) != "user"
            ):
                raise GroundedRecoveryConflictError(
                    "Pinned ContextPackage is missing its durable Grounded trigger user."
                )
            try:
                complete_grounded_processing_run(
                    self.database,
                    processing_run_id=result.processing_run_id,
                    package=context_record.package,
                    trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
                )
            except GroundedProcessingRunError as exc:
                raise GroundedRecoveryConflictError(
                    "Recorded provider result conflicts with its durable ProcessingRun."
                ) from exc

        return self.completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=result.processing_run_id,
            payload_json=result.receipt_payload_json,
        )

    def _load_provider_state(
        self,
        operation_id: uuid.UUID,
        *,
        require_succeeded_run: bool = False,
    ) -> tuple[GroundedProviderResult | None, GroundedProviderResultIdentity | None]:
        result = self.provider_attempts.load_result(operation_id)
        if result is None:
            return None, None
        identity = self.provider_attempts.load_result_identity(operation_id)
        try:
            context_record = self.context_packages.load(operation_id)
        except GroundedContextPackageSchemaError as exc:
            raise GroundedProviderAttemptSchemaError(
                "Provider identity cannot be verified against a corrupted ContextPackage."
            ) from exc
        if context_record is not None:
            if identity is None:
                raise GroundedProviderAttemptSchemaError(
                    "Pinned ContextPackage requires durable provider result identity."
                )
            signature = context_record.package.model_signature
            if (
                identity.provider_id != signature.provider
                or identity.model_id != signature.model_identifier
            ):
                raise GroundedProviderAttemptSchemaError(
                    "Persisted provider identity conflicts with the pinned ContextPackage model."
                )
            user = self.database.connection.execute(
                """
                SELECT chat_id, actor_id, message_type
                FROM chat_messages
                WHERE message_id = ?
                """,
                (uuid_to_blob(operation_id),),
            ).fetchone()
            if (
                user is None
                or user["actor_id"] is None
                or uuid_from_blob(bytes(user["chat_id"])) != context_record.chat_id
                or str(user["message_type"]) != "user"
            ):
                raise GroundedProviderAttemptSchemaError(
                    "Pinned ContextPackage is missing its durable Grounded trigger user."
                )
            try:
                run = validate_grounded_processing_run_provenance(
                    self.database,
                    processing_run_id=result.processing_run_id,
                    package=context_record.package,
                    trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
                )
            except GroundedProcessingRunError as exc:
                raise GroundedProviderAttemptSchemaError(
                    "Persisted provider result conflicts with its pinned ProcessingRun provenance."
                ) from exc
            if run.status not in {"running", "succeeded"}:
                raise GroundedProviderAttemptSchemaError(
                    "Persisted provider result conflicts with its ProcessingRun lifecycle."
                )
            if run.status == "running" and run.finished_at_us is not None:
                raise GroundedProviderAttemptSchemaError(
                    "Running provider ProcessingRun has an impossible finish timestamp."
                )
            if run.status == "succeeded" and run.finished_at_us is None:
                raise GroundedProviderAttemptSchemaError(
                    "Succeeded provider ProcessingRun is missing its finish timestamp."
                )
            if require_succeeded_run and run.status != "succeeded":
                raise GroundedProviderAttemptSchemaError(
                    "Completed Grounded send requires a succeeded ProcessingRun."
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
