"""Safe transition from a frozen Unified pre-user plan into durable chat state."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from athena.chat.grounded_send import GroundedSendCoordinator
from athena.chat.models import ChatMessage
from athena.chat.request_fingerprint import ChatRequestFingerprint
from athena.chat.unified_pre_user_recovery import (
    UnifiedPreUserRecoveryInspector,
    UnifiedPreUserRecoveryState,
)
from athena.chat.unified_send_plan import UnifiedSendPlanRecord
from athena.retrieval.context_package import ContextPackageService
from athena.storage.database import SQLiteDatabase


class UnifiedPreUserTransitionError(RuntimeError):
    """A frozen Unified plan cannot safely transition into the user operation."""


@dataclass(frozen=True, slots=True)
class UnifiedPreUserTransition:
    plan: UnifiedSendPlanRecord
    user_message: ChatMessage
    package_snapshot_commit_seq: int


class UnifiedPreUserTransitionService:
    """Consume exactly one READY send plan without repeating retrieval."""

    def __init__(self, database: SQLiteDatabase) -> None:
        self.database = database
        self.inspector = UnifiedPreUserRecoveryInspector(database)
        self.coordinator = GroundedSendCoordinator(database)
        self.context_packages = ContextPackageService(database)

    def start(
        self,
        *,
        operation_id: uuid.UUID,
        chat_id: uuid.UUID,
        content: str,
        fingerprint: ChatRequestFingerprint,
    ) -> UnifiedPreUserTransition:
        status = self.inspector.inspect(
            operation_id=operation_id,
            chat_id=chat_id,
            fingerprint=fingerprint,
        )
        if status.state is not UnifiedPreUserRecoveryState.READY or status.plan is None:
            raise UnifiedPreUserTransitionError(
                "Unified pre-user transition requires a READY durable send plan; "
                f"state={status.state.value}."
            )
        plan = status.plan
        started = self.coordinator.start(
            operation_id=operation_id,
            chat_id=chat_id,
            actor_id=plan.user_actor_id,
            content=content,
            fingerprint=fingerprint,
        )
        if started.user_message.message_id != operation_id:
            raise UnifiedPreUserTransitionError(
                "Unified pre-user transition lost deterministic user-message identity."
            )
        if started.user_message.actor_id != plan.user_actor_id:
            raise UnifiedPreUserTransitionError(
                "Unified pre-user transition lost its frozen trigger actor."
            )
        package_snapshot_commit_seq = self.context_packages.assert_user_commit_follows(
            plan.retrieval_snapshot_commit_seq,
            started.user_message,
        )
        return UnifiedPreUserTransition(
            plan=plan,
            user_message=started.user_message,
            package_snapshot_commit_seq=package_snapshot_commit_seq,
        )
