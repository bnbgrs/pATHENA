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
from athena.chat.grounded_processing_run import (
    GroundedProcessingRunError,
    validate_grounded_processing_run,
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
from athena.chat.grounded_request_context import (
    GroundedRequestContextBindingError,
    validate_grounded_request_context_binding,
)
from athena.chat.grounded_snapshot import (
    GroundedSnapshotBindingError,
    validate_grounded_snapshot_current,
    validate_grounded_snapshot_identity,
)
from athena.chat.grounded_turn import GroundedUserTurnRepository
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.common.ids import uuid_from_blob, uuid_to_blob
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


class GroundedProviderContextError(RuntimeError):
    """The provider boundary is missing or conflicts with its exact ContextPackage."""


class GroundedProviderResultError(RuntimeError):
    """A provider result cannot be journaled from the current recovery state."""

    def __init__(self, status: GroundedRecoveryStatus) -> None:
        self.status = status
        super().__init__(
            f"Grounded send operation {status.operation_id} is {status.state.value}; "
            "only ambiguous operations may record a first provider result."
        )


class GroundedProviderIdentityError(RuntimeError):
    """Provider result identity conflicts with the pinned ContextPackage model."""


class GroundedProviderRunError(RuntimeError):
    """Provider result provenance conflicts with its durable ProcessingRun."""


class GroundedAssistantCommitError(RuntimeError):
    """An assistant turn conflicts with the recorded durable provider result."""


class GroundedCompletionCommitError(RuntimeError):
    """Completion conflicts with the recorded durable provider result."""


class GroundedSendCoordinator:
    """Coordinate crash-safe start, assistant commit, completion and replay."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
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
        try:
            validate_grounded_snapshot_current(
                self.database,
                package=package,
                operation_id=operation_id,
            )
        except GroundedSnapshotBindingError as exc:
            raise GroundedProviderContextError(
                "Grounded ContextPackage does not own the current canonical snapshot."
            ) from exc
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
        context_package = self.context_packages.load(operation_id)
        if context_package is None or context_package.chat_id != chat_id:
            raise GroundedProviderContextError(
                "Grounded provider attempt requires the exact durable ContextPackage."
            )
        before = self.recover(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if before.state is not GroundedRecoveryState.RESUMABLE:
            raise GroundedProviderBoundaryError(before)
        try:
            validate_grounded_request_context_binding(
                package=context_package.package,
                fingerprint=fingerprint,
            )
            validate_grounded_snapshot_current(
                self.database,
                package=context_package.package,
                operation_id=operation_id,
            )
        except (GroundedRequestContextBindingError, GroundedSnapshotBindingError) as exc:
            raise GroundedProviderContextError(
                "Grounded provider attempt conflicts with its durable ContextPackage."
            ) from exc
        try:
            attempt = self.provider_attempts.claim_started(
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
        context_record = self.context_packages.load(operation_id)
        if context_record is None or context_record.chat_id != chat_id:
            raise GroundedProviderContextError(
                "Grounded provider result requires the exact durable ContextPackage."
            )
        try:
            validate_grounded_request_context_binding(
                package=context_record.package,
                fingerprint=fingerprint,
            )
            validate_grounded_snapshot_identity(
                self.database,
                package=context_record.package,
                operation_id=operation_id,
            )
        except (GroundedRequestContextBindingError, GroundedSnapshotBindingError) as exc:
            raise GroundedProviderContextError(
                "Grounded provider result conflicts with its durable ContextPackage."
            ) from exc
        if provider_id is not None and model_id is not None:
            signature = context_record.package.model_signature
            if (
                provider_id != signature.provider
                or model_id != signature.model_identifier
            ):
                raise GroundedProviderIdentityError(
                    "Provider result identity conflicts with the pinned ContextPackage model."
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
            raise GroundedProviderRunError(
                "Grounded provider result is missing its durable trigger user."
            )
        try:
            validate_grounded_processing_run(
                self.database,
                processing_run_id=processing_run_id,
                package=context_record.package,
                trigger_actor_id=uuid_from_blob(bytes(user["actor_id"])),
            )
        except GroundedProcessingRunError as exc:
            raise GroundedProviderRunError(
                "Grounded provider result conflicts with its durable ProcessingRun."
            ) from exc
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
        result = self.provider_attempts.load_result(operation_id)
        if (
            result is None
            or result.chat_id != chat_id
            or result.assistant_content != content
        ):
            raise GroundedAssistantCommitError(
                "Grounded assistant commit requires the matching durable provider result."
            )
        identity = self.provider_attempts.load_result_identity(operation_id)
        context_record = self.context_packages.load(operation_id)
        if context_record is not None:
            if context_record.chat_id != chat_id or identity is None:
                raise GroundedAssistantCommitError(
                    "Pinned ContextPackage requires durable provider identity before assistant commit."
                )
            signature = context_record.package.model_signature
            if (
                identity.provider_id != signature.provider
                or identity.model_id != signature.model_identifier
            ):
                raise GroundedAssistantCommitError(
                    "Durable provider identity conflicts with pinned ContextPackage before assistant commit."
                )
        if identity is not None:
            actor = self.database.connection.execute(
                """
                SELECT actor_type, display_name
                FROM actors
                WHERE actor_id = ?
                """,
                (uuid_to_blob(actor_id),),
            ).fetchone()
            if (
                actor is None
                or str(actor["actor_type"]) != "primary_model"
                or str(actor["display_name"])
                != f"{identity.provider_id}:{identity.model_id}"
            ):
                raise GroundedAssistantCommitError(
                    "Grounded assistant actor conflicts with durable provider identity."
                )
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
        result = self.provider_attempts.load_result(operation_id)
        if (
            result is None
            or result.chat_id != chat_id
            or result.processing_run_id != processing_run_id
            or result.receipt_payload_json != payload_json
        ):
            raise GroundedCompletionCommitError(
                "Grounded completion requires the exact durable provider result."
            )
        return self.completions.complete(
            operation_id=operation_id,
            chat_id=chat_id,
            processing_run_id=processing_run_id,
            payload_json=payload_json,
        )
