"""Recovery classification for Unified sends frozen before the user commit."""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass

from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified_send_plan import (
    UnifiedSendPlanConflictError,
    UnifiedSendPlanRecord,
    UnifiedSendPlanRepository,
)
from athena.common.ids import uuid_from_blob, uuid_to_blob
from athena.retrieval.context_package import ContextPackageService
from athena.storage.database import SQLiteDatabase


class UnifiedPreUserRecoveryState(str, enum.Enum):
    """Durable state of a Unified operation before provider execution."""

    ABSENT = "absent"
    READY = "ready"
    CONSUMED = "consumed"
    CONFLICT = "conflict"


@dataclass(frozen=True, slots=True)
class UnifiedPreUserRecoveryStatus:
    state: UnifiedPreUserRecoveryState
    operation_id: uuid.UUID
    chat_id: uuid.UUID
    plan: UnifiedSendPlanRecord | None = None
    reason: str | None = None


class UnifiedPreUserRecoveryInspector:
    """Classify a pre-user send plan without replaying mutable retrieval."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.plans = UnifiedSendPlanRepository(database)
        self.context_packages = ContextPackageService(database)

    def inspect(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        fingerprint: ChatRequestFingerprint,
    ) -> UnifiedPreUserRecoveryStatus:
        try:
            plan = self.plans.load(operation_id, fingerprint=fingerprint)
        except UnifiedSendPlanConflictError as exc:
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.CONFLICT,
                operation_id=operation_id,
                chat_id=chat_id,
                reason=str(exc),
            )
        if plan is None:
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.ABSENT,
                operation_id=operation_id,
                chat_id=chat_id,
            )
        if plan.chat_id != chat_id:
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.CONFLICT,
                operation_id=operation_id,
                chat_id=chat_id,
                plan=plan,
                reason="Unified pre-user plan belongs to a different chat.",
            )

        actor = self.database.connection.execute(
            "SELECT active FROM actors WHERE actor_id = ?",
            (uuid_to_blob(plan.user_actor_id),),
        ).fetchone()
        if actor is None or int(actor["active"]) != 1:
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.CONFLICT,
                operation_id=operation_id,
                chat_id=chat_id,
                plan=plan,
                reason="Unified pre-user plan trigger actor is no longer active.",
            )

        operation = self.database.connection.execute(
            "SELECT chat_id FROM chat_send_operations WHERE operation_id = ?",
            (uuid_to_blob(operation_id),),
        ).fetchone()
        if operation is not None:
            operation_chat_id = uuid_from_blob(bytes(operation["chat_id"]))
            if operation_chat_id != chat_id:
                return UnifiedPreUserRecoveryStatus(
                    state=UnifiedPreUserRecoveryState.CONFLICT,
                    operation_id=operation_id,
                    chat_id=chat_id,
                    plan=plan,
                    reason="Unified durable operation belongs to a different chat.",
                )
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.CONSUMED,
                operation_id=operation_id,
                chat_id=chat_id,
                plan=plan,
            )

        current_commit_seq = self.context_packages.current_commit_seq()
        if current_commit_seq != plan.retrieval_snapshot_commit_seq:
            return UnifiedPreUserRecoveryStatus(
                state=UnifiedPreUserRecoveryState.CONFLICT,
                operation_id=operation_id,
                chat_id=chat_id,
                plan=plan,
                reason=(
                    "Canonical state changed after the Unified pre-user plan was frozen: "
                    f"expected commit_seq={plan.retrieval_snapshot_commit_seq}, "
                    f"current={current_commit_seq}."
                ),
            )
        return UnifiedPreUserRecoveryStatus(
            state=UnifiedPreUserRecoveryState.READY,
            operation_id=operation_id,
            chat_id=chat_id,
            plan=plan,
        )
