"""Asynchronous Core API refresh boundary for the ATHENA desktop shell."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from queue import Empty, SimpleQueue
from typing import Literal, Protocol

from PySide6.QtCore import QMetaObject, QObject, QRunnable, Qt, QThreadPool, Signal, Slot

from athena.api.client import CoreApiClientError
from athena.api.contracts import (
    ChatOperationRecoveryResponse,
    ChatSummaryResponse,
    ChatThreadResponse,
    DeletionPreviewResponse,
    DeletionResultResponse,
    GroundedChatResponse,
    HealthResponse,
    KnowledgeMergeReviewResponse,
    KnowledgeReviewResponse,
    MessageKnowledgeExtractionResponse,
    ModelResponse,
    NewsProfileResponse,
    ProviderHealthResponse,
    RememberedChatMessageResponse,
    StorageHealthResponse,
)
from athena.api.search_contracts import SearchResultResponse
from athena.chat.send_identity import (
    assistant_message_id_for_operation,
    chat_id_for_operation,
)
from athena.common.ids import new_uuid7
from athena.retrieval.universal import UniversalSearchEntityType


class CoreApiGateway(Protocol):
    """Minimal local Core API surface consumed by the desktop controller."""

    def health(self) -> HealthResponse: ...

    def provider_health(self) -> ProviderHealthResponse: ...

    def storage_health(self) -> StorageHealthResponse: ...

    def list_models(self) -> tuple[ModelResponse, ...]: ...

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]: ...

    def news_profile(self) -> NewsProfileResponse: ...

    def configure_news_schedule(
        self,
        *,
        timezone_name: str,
        local_hour: int,
        local_minute: int,
    ) -> NewsProfileResponse: ...

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]: ...

    def set_chat_pinned(
        self,
        chat_id: str,
        *,
        pinned: bool,
    ) -> ChatSummaryResponse: ...

    def create_chat(
        self,
        chat_id: str | None = None,
    ) -> ChatThreadResponse: ...

    def load_chat(self, chat_id: str) -> ChatThreadResponse: ...

    def edit_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        expected_revision_id: str,
        content: str,
    ) -> ChatThreadResponse: ...

    def fork_chat_from_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> ChatThreadResponse: ...

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> ChatThreadResponse: ...

    def cancel_chat_operation(self, operation_id: str) -> bool:
        """Request cancellation for one active direct-chat send."""

        ...

    def chat_operation_recovery(
        self,
        chat_id: str,
        operation_id: str,
    ) -> ChatOperationRecoveryResponse: ...

    def continue_unified_local_chat_operation(
        self,
        chat_id: str,
        operation_id: str,
    ) -> GroundedChatResponse: ...

    def send_unified_local_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        model_id: str | None = None,
        embedding_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> GroundedChatResponse: ...

    def remember_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> RememberedChatMessageResponse: ...

    def extract_chat_message_knowledge(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
        model_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
    ) -> MessageKnowledgeExtractionResponse: ...

    def prepare_knowledge_review(
        self,
        processing_run_id: str,
    ) -> KnowledgeReviewResponse: ...

    def load_knowledge_merge_review(
        self,
        review_id: str,
    ) -> KnowledgeMergeReviewResponse: ...

    def resolve_knowledge_merge_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> KnowledgeMergeReviewResponse: ...

    def preview_chat_deletion(self, chat_id: str) -> DeletionPreviewResponse: ...

    def delete_chat(
        self,
        chat_id: str,
        *,
        preview_digest: str,
    ) -> DeletionResultResponse: ...


SnapshotFreshness = Literal["fresh", "stale", "unavailable"]


@dataclass(frozen=True, slots=True)
class DesktopApiSnapshot:
    """One coherent read snapshot rendered by the desktop shell."""

    health: HealthResponse
    provider: ProviderHealthResponse | None
    models: tuple[ModelResponse, ...]
    chats: tuple[ChatSummaryResponse, ...]
    chat_error: str | None = None
    model_error: str | None = None
    chat_freshness: SnapshotFreshness | None = None
    model_freshness: SnapshotFreshness | None = None
    storage: StorageHealthResponse | None = None
    storage_error: str | None = None

    @property
    def loaded_model(self) -> ModelResponse | None:
        return next((model for model in self.models if model.loaded), None)

    @property
    def resolved_chat_freshness(self) -> SnapshotFreshness:
        if self.chat_freshness is not None:
            return self.chat_freshness
        return "fresh" if self.chat_error is None else "unavailable"

    @property
    def resolved_model_freshness(self) -> SnapshotFreshness:
        if self.model_freshness is not None:
            return self.model_freshness
        return "fresh" if self.model_error is None else "unavailable"


@dataclass(frozen=True, slots=True)
class _RefreshOutcome:
    snapshot: DesktopApiSnapshot | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if (self.snapshot is None) == (self.error is None):
            raise ValueError("Refresh outcome requires exactly one result kind.")


@dataclass(frozen=True, slots=True)
class _SearchOutcome:
    request_id: int
    query: str
    results: tuple[SearchResultResponse, ...] | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if self.request_id < 1:
            raise ValueError("Search outcome request_id must be positive.")
        if not self.query:
            raise ValueError("Search outcome query must not be empty.")
        if (self.results is None) == (self.error is None):
            raise ValueError("Search outcome requires exactly one result kind.")


@dataclass(frozen=True, slots=True)
class _ChatOperationOutcome:
    operation: str
    thread: ChatThreadResponse | None = None
    grounded: GroundedChatResponse | None = None
    recovery: ChatOperationRecoveryResponse | None = None
    deletion_preview: DeletionPreviewResponse | None = None
    deleted_chat_id: str | None = None
    remembered: RememberedChatMessageResponse | None = None
    knowledge_extraction: MessageKnowledgeExtractionResponse | None = None
    knowledge_review: KnowledgeReviewResponse | None = None
    merge_review: KnowledgeMergeReviewResponse | None = None
    pinned_chat_id: str | None = None
    pinned_state: bool | None = None
    error: str | None = None
    operation_id: str | None = None
    cancelled: bool = False

    def __post_init__(self) -> None:
        result_count = sum(
            item is not None
            for item in (
                self.thread,
                self.grounded,
                self.recovery,
                self.deletion_preview,
                self.deleted_chat_id,
                self.remembered,
                self.knowledge_extraction,
                self.knowledge_review,
                self.merge_review,
                self.pinned_chat_id,
            )
        )
        if result_count > 1:
            raise ValueError("Chat outcome cannot contain multiple result kinds.")
        if self.cancelled:
            if (
                self.operation not in {"send", "send_grounded", "continue_recovery"}
                or self.operation_id is None
                or self.error is not None
                or result_count > 1
            ):
                raise ValueError(
                    "Cancelled chat outcome requires one cancellable send operation identity."
                )
            return
        if self.error is None and result_count != 1:
            raise ValueError("Successful chat outcome requires exactly one result.")


@dataclass(frozen=True, slots=True)
class _ChatCancelOutcome:
    operation_id: str
    accepted: bool | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        if (self.accepted is None) == (self.error is None):
            raise ValueError(
                "Chat cancellation outcome requires exactly one result kind."
            )


_DirectSendReconciliationState = Literal[
    "absent",
    "incomplete",
    "complete",
    "conflict",
]


def _classify_direct_send(
    thread: ChatThreadResponse,
    *,
    chat_id: str,
    operation_id: str,
    content: str,
) -> _DirectSendReconciliationState:
    if thread.chat_id != chat_id:
        return "conflict"

    try:
        parsed_operation_id = uuid.UUID(
            operation_id
        )
    except ValueError:
        return "conflict"

    expected_user_id = str(
        parsed_operation_id
    )

    expected_assistant_id = str(
        assistant_message_id_for_operation(
            parsed_operation_id
        )
    )

    user_matches = tuple(
        message
        for message in thread.messages
        if message.message_id == expected_user_id
    )

    assistant_matches = tuple(
        message
        for message in thread.messages
        if message.message_id == expected_assistant_id
    )

    if (
        not user_matches
        and not assistant_matches
    ):
        return "absent"

    if len(user_matches) != 1:
        return "conflict"

    user_message = user_matches[0]

    if (
        user_message.chat_id != chat_id
        or user_message.message_type != "user"
        or user_message.content != content
    ):
        return "conflict"

    if not assistant_matches:
        return "incomplete"

    if len(assistant_matches) != 1:
        return "conflict"

    assistant_message = assistant_matches[0]

    if (
        assistant_message.chat_id != chat_id
        or assistant_message.message_type != "assistant"
        or assistant_message.sequence_no
        != user_message.sequence_no + 1
    ):
        return "conflict"

    return "complete"


class _ChatTask(QRunnable):
    """Run one chat read/mutation away from the UI thread."""

    def __init__(
        self,
        *,
        gateway: CoreApiGateway,
        operation: str,
        chat_id: str | None,
        content: str | None,
        model_id: str | None,
        operation_id: str | None,
        effective_context_limit: int | None,
        max_output_tokens: int | None,
        temperature: float | None,
        thinking_enabled: bool | None,
        preview_digest: str | None,
        message_id: str | None,
        revision_id: str | None,
        processing_run_id: str | None = None,
        review_id: str | None = None,
        review_decision: str | None = None,
        pinned_state: bool | None = None,
        outcomes: SimpleQueue[_ChatOperationOutcome],
        receiver: QObject,
    ) -> None:
        super().__init__()
        self.gateway = gateway
        self.operation = operation
        self.chat_id = chat_id
        self.content = content
        self.model_id = model_id
        self.operation_id = operation_id
        self.effective_context_limit = effective_context_limit
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.thinking_enabled = thinking_enabled
        self.preview_digest = preview_digest
        self.message_id = message_id
        self.revision_id = revision_id
        self.processing_run_id = processing_run_id
        self.review_id = review_id
        self.review_decision = review_decision
        self.pinned_state = pinned_state
        self.outcomes = outcomes
        self.receiver = receiver
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        resolved_chat_id = self.chat_id
        try:
            if self.operation == "load":
                if resolved_chat_id is None:
                    raise ValueError("Chat load requires a chat ID.")
                thread = self.gateway.load_chat(
                    resolved_chat_id
                )
                if thread.chat_id != resolved_chat_id:
                    raise RuntimeError(
                        "Loaded chat belongs to another chat."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    thread=thread,
                )
            elif self.operation == "edit":
                message_id = self.message_id
                revision_id = self.revision_id
                content = self.content
                if (
                    resolved_chat_id is None
                    or message_id is None
                    or revision_id is None
                    or content is None
                    or not content.strip()
                ):
                    raise ValueError(
                        "Chat edit requires stable message identity and content."
                    )
                thread = self.gateway.edit_chat_message(
                    resolved_chat_id,
                    message_id,
                    expected_revision_id=revision_id,
                    content=content,
                )
                if thread.chat_id != resolved_chat_id:
                    raise RuntimeError(
                        "Edited chat belongs to another chat."
                    )
                edited = next(
                    (
                        message
                        for message in thread.messages
                        if message.message_id == message_id
                    ),
                    None,
                )
                if edited is None or edited.content != content:
                    raise RuntimeError(
                        "Edited chat does not contain the requested revision."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    thread=thread,
                )
            elif self.operation == "fork":
                message_id = self.message_id
                revision_id = self.revision_id
                if (
                    resolved_chat_id is None
                    or message_id is None
                    or revision_id is None
                ):
                    raise ValueError(
                        "Chat fork requires stable message identity."
                    )
                thread = self.gateway.fork_chat_from_message(
                    resolved_chat_id,
                    message_id,
                    revision_id=revision_id,
                )
                if thread.chat_id == resolved_chat_id:
                    raise RuntimeError(
                        "Forked chat reused the source chat identity."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    thread=thread,
                )
            elif self.operation == "inspect_recovery":
                operation_id = self.operation_id
                if resolved_chat_id is None or operation_id is None:
                    raise ValueError(
                        "Recovery inspection requires stable chat and operation identity."
                    )
                recovery = self.gateway.chat_operation_recovery(
                    resolved_chat_id,
                    operation_id,
                )
                if (
                    recovery.chat_id != resolved_chat_id
                    or recovery.operation_id != operation_id
                ):
                    raise RuntimeError(
                        "Recovery state belongs to another chat operation."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    recovery=recovery,
                )
            elif self.operation == "continue_recovery":
                operation_id = self.operation_id
                if resolved_chat_id is None or operation_id is None:
                    raise ValueError(
                        "Recovery continuation requires stable chat and operation identity."
                    )
                grounded = self.gateway.continue_unified_local_chat_operation(
                    resolved_chat_id,
                    operation_id,
                )
                if grounded.thread.chat_id != resolved_chat_id:
                    raise RuntimeError(
                        "Continued Grounded response belongs to another chat."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    grounded=grounded,
                )
            elif self.operation == "send":
                content = self.content
                operation_id = self.operation_id

                if content is None or not content.strip():
                    raise ValueError(
                        "Chat send requires message content."
                    )

                if operation_id is None:
                    raise ValueError(
                        "Direct chat send requires "
                        "a stable operation ID."
                    )

                parsed_operation_id = uuid.UUID(
                    operation_id
                )

                if resolved_chat_id is None:
                    resolved_chat_id = str(
                        chat_id_for_operation(
                            parsed_operation_id
                        )
                    )

                    try:
                        created = self.gateway.create_chat(
                            resolved_chat_id
                        )
                    except CoreApiClientError as create_exc:
                        if create_exc.status is not None:
                            raise

                        try:
                            created = self.gateway.load_chat(
                                resolved_chat_id
                            )
                        except Exception as reconcile_exc:
                            raise create_exc from reconcile_exc

                    if created.chat_id != resolved_chat_id:
                        raise RuntimeError(
                            "Created chat belongs to another chat."
                        )

                if (
                    self.effective_context_limit is None
                    and self.max_output_tokens is None
                    and self.temperature is None
                    and self.thinking_enabled is None
                ):
                    thread = self.gateway.send_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                    )
                elif (
                    self.max_output_tokens is None
                    and self.temperature is None
                    and self.thinking_enabled is None
                ):
                    thread = self.gateway.send_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                        effective_context_limit=(
                            self.effective_context_limit
                        ),
                    )
                else:
                    thread = self.gateway.send_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                        effective_context_limit=(
                            self.effective_context_limit
                        ),
                        max_output_tokens=(
                            self.max_output_tokens
                        ),
                        temperature=self.temperature,
                        thinking_enabled=(
                            self.thinking_enabled
                        ),
                    )

                if (
                    _classify_direct_send(
                        thread,
                        chat_id=resolved_chat_id,
                        operation_id=operation_id,
                        content=content,
                    )
                    != "complete"
                ):
                    raise RuntimeError(
                        "Direct chat response does not contain "
                        "the expected durable send operation."
                    )

                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    thread=thread,
                )
            elif self.operation == "send_grounded":
                content = self.content
                operation_id = self.operation_id

                if content is None or not content.strip():
                    raise ValueError(
                        "Grounded chat send requires message content."
                    )

                if operation_id is None:
                    raise ValueError(
                        "Grounded chat send requires "
                        "a stable operation ID."
                    )

                parsed_operation_id = uuid.UUID(
                    operation_id
                )

                if resolved_chat_id is None:
                    resolved_chat_id = str(
                        chat_id_for_operation(
                            parsed_operation_id
                        )
                    )

                    try:
                        created = self.gateway.create_chat(
                            resolved_chat_id
                        )
                    except CoreApiClientError as create_exc:
                        if create_exc.status is not None:
                            raise

                        try:
                            created = self.gateway.load_chat(
                                resolved_chat_id
                            )
                        except Exception as reconcile_exc:
                            raise create_exc from reconcile_exc

                    if created.chat_id != resolved_chat_id:
                        raise RuntimeError(
                            "Created Grounded chat belongs to another chat."
                        )

                if (
                    self.effective_context_limit is None
                    and self.max_output_tokens is None
                    and self.temperature is None
                    and self.thinking_enabled is None
                ):
                    grounded = self.gateway.send_unified_local_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                    )
                elif (
                    self.max_output_tokens is None
                    and self.temperature is None
                    and self.thinking_enabled is None
                ):
                    grounded = self.gateway.send_unified_local_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                        effective_context_limit=self.effective_context_limit,
                    )
                else:
                    grounded = self.gateway.send_unified_local_chat_message(
                        resolved_chat_id,
                        content=content,
                        model_id=self.model_id,
                        operation_id=operation_id,
                        effective_context_limit=self.effective_context_limit,
                        max_output_tokens=self.max_output_tokens,
                        temperature=self.temperature,
                        thinking_enabled=self.thinking_enabled,
                    )

                if grounded.thread.chat_id != resolved_chat_id:
                    raise RuntimeError(
                        "Grounded response belongs to another chat."
                    )

                if (
                    _classify_direct_send(
                        grounded.thread,
                        chat_id=resolved_chat_id,
                        operation_id=operation_id,
                        content=content,
                    )
                    != "complete"
                ):
                    raise RuntimeError(
                        "Grounded response does not contain "
                        "the expected durable send operation."
                    )

                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    grounded=grounded,
                )
            elif self.operation == "remember":
                message_id = self.message_id
                revision_id = self.revision_id
                if (
                    resolved_chat_id is None
                    or message_id is None
                    or revision_id is None
                ):
                    raise ValueError(
                        "Remember requires stable chat-message identity."
                    )
                remembered = self.gateway.remember_chat_message(
                    resolved_chat_id,
                    message_id,
                    revision_id=revision_id,
                )
                if (
                    remembered.chat_id != resolved_chat_id
                    or remembered.message_id != message_id
                    or remembered.message_revision_id != revision_id
                ):
                    raise RuntimeError(
                        "Remember result belongs to another message revision."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    remembered=remembered,
                )
            elif self.operation == "extract_knowledge":
                message_id = self.message_id
                revision_id = self.revision_id
                if (
                    resolved_chat_id is None
                    or message_id is None
                    or revision_id is None
                ):
                    raise ValueError(
                        "Knowledge extraction requires stable chat-message identity."
                    )
                extraction = self.gateway.extract_chat_message_knowledge(
                    resolved_chat_id,
                    message_id,
                    revision_id=revision_id,
                    model_id=self.model_id,
                    effective_context_limit=self.effective_context_limit,
                    max_output_tokens=self.max_output_tokens,
                )
                if (
                    extraction.chat_id != resolved_chat_id
                    or extraction.message_id != message_id
                    or extraction.message_revision_id != revision_id
                ):
                    raise RuntimeError(
                        "Knowledge extraction result belongs to another message revision."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    knowledge_extraction=extraction,
                )
            elif self.operation == "prepare_knowledge_review":
                processing_run_id = self.processing_run_id
                if processing_run_id is None:
                    raise ValueError(
                        "Knowledge review requires a ProcessingRun ID."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    knowledge_review=self.gateway.prepare_knowledge_review(
                        processing_run_id
                    ),
                )
            elif self.operation == "load_merge_review":
                review_id = self.review_id
                if review_id is None:
                    raise ValueError("Merge review load requires a review ID.")
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    merge_review=self.gateway.load_knowledge_merge_review(
                        review_id
                    ),
                )
            elif self.operation == "resolve_merge_review":
                review_id = self.review_id
                review_decision = self.review_decision
                if review_id is None or review_decision is None:
                    raise ValueError(
                        "Merge review resolution requires review identity and decision."
                    )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    merge_review=self.gateway.resolve_knowledge_merge_review(
                        review_id,
                        decision=review_decision,
                    ),
                )
            elif self.operation == "pin":
                if resolved_chat_id is None or self.pinned_state is None:
                    raise ValueError("Chat pin mutation requires a chat ID and state.")
                summary = self.gateway.set_chat_pinned(
                    resolved_chat_id,
                    pinned=self.pinned_state,
                )
                if (
                    summary.chat_id != resolved_chat_id
                    or summary.pinned is not self.pinned_state
                ):
                    raise RuntimeError("Chat pin result is inconsistent.")
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    pinned_chat_id=resolved_chat_id,
                    pinned_state=self.pinned_state,
                )
            elif self.operation == "preview_delete":
                if resolved_chat_id is None:
                    raise ValueError("Chat deletion preview requires a chat ID.")
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    deletion_preview=self.gateway.preview_chat_deletion(
                        resolved_chat_id
                    ),
                )
            elif self.operation == "delete":
                if resolved_chat_id is None or self.preview_digest is None:
                    raise ValueError("Chat deletion requires a preview digest.")
                result = self.gateway.delete_chat(
                    resolved_chat_id,
                    preview_digest=self.preview_digest,
                )
                if result.entity_id != resolved_chat_id:
                    raise RuntimeError("Deletion result belongs to another chat.")
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    deleted_chat_id=resolved_chat_id,
                )
            else:
                raise ValueError("Unknown desktop chat operation.")
        except CoreApiClientError as exc:
            if (
                self.operation == "send"
                and resolved_chat_id is not None
                and self.operation_id is not None
                and self.content is not None
            ):
                try:
                    reconciled = self.gateway.load_chat(
                        resolved_chat_id
                    )
                except Exception:
                    reconciled = None

                if reconciled is None:
                    if exc.code == "generation_cancelled":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            operation_id=self.operation_id,
                            cancelled=True,
                        )
                    else:
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            error=str(exc),
                        )
                else:
                    state = _classify_direct_send(
                        reconciled,
                        chat_id=resolved_chat_id,
                        operation_id=self.operation_id,
                        content=self.content,
                    )

                    if state == "complete":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                        )
                    elif (
                        exc.code == "generation_cancelled"
                        and state in {"absent", "incomplete"}
                    ):
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=(
                                reconciled
                                if state == "incomplete"
                                else None
                            ),
                            operation_id=self.operation_id,
                            cancelled=True,
                        )
                    elif state == "incomplete":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=(
                                "Direct send persisted the user turn "
                                "but no completed assistant turn. "
                                "Automatic re-execution is blocked."
                            ),
                        )
                    elif state == "conflict":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=(
                                "Direct send reconciliation detected "
                                "conflicting durable message identity."
                            ),
                        )
                    else:
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=str(exc),
                        )

            elif (
                self.operation == "send_grounded"
                and resolved_chat_id is not None
                and self.operation_id is not None
                and self.content is not None
            ):
                try:
                    reconciled = self.gateway.load_chat(
                        resolved_chat_id
                    )
                except Exception:
                    reconciled = None

                if reconciled is None:
                    if exc.code == "generation_cancelled":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            operation_id=self.operation_id,
                            cancelled=True,
                        )
                    else:
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            error=str(exc),
                        )
                else:
                    state = _classify_direct_send(
                        reconciled,
                        chat_id=resolved_chat_id,
                        operation_id=self.operation_id,
                        content=self.content,
                    )

                    if state == "complete":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=(
                                "Grounded send completed durably, but the "
                                "grounded response payload was lost. Retry "
                                "the same operation to replay it."
                            ),
                        )
                    elif (
                        exc.code == "generation_cancelled"
                        and state in {"absent", "incomplete"}
                    ):
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=(
                                reconciled
                                if state == "incomplete"
                                else None
                            ),
                            operation_id=self.operation_id,
                            cancelled=True,
                        )
                    elif state == "incomplete":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=(
                                "Grounded send is durably incomplete. Retry "
                                "the same operation identity to resume or "
                                "recover it safely."
                            ),
                        )
                    elif state == "conflict":
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=(
                                "Grounded send reconciliation detected "
                                "conflicting identity."
                            ),
                        )
                    else:
                        outcome = _ChatOperationOutcome(
                            operation=self.operation,
                            thread=reconciled,
                            error=str(exc),
                        )

            elif (
                self.operation == "continue_recovery"
                and self.operation_id is not None
                and exc.code == "generation_cancelled"
            ):
                thread = (
                    self.gateway.load_chat(self.chat_id)
                    if self.chat_id is not None
                    else None
                )
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    thread=thread,
                    operation_id=self.operation_id,
                    cancelled=True,
                )

            elif (
                self.operation == "delete"
                and resolved_chat_id is not None
                and exc.status is None
            ):
                deletion_reconciled = False

                try:
                    self.gateway.load_chat(
                        resolved_chat_id
                    )
                except CoreApiClientError as reconcile_exc:
                    deletion_reconciled = (
                        reconcile_exc.status == 404
                        and reconcile_exc.code == "chat_not_found"
                    )
                except Exception:
                    deletion_reconciled = False

                if deletion_reconciled:
                    outcome = _ChatOperationOutcome(
                        operation=self.operation,
                        deleted_chat_id=resolved_chat_id,
                    )
                else:
                    outcome = _ChatOperationOutcome(
                        operation=self.operation,
                        error=str(exc),
                    )

            else:
                outcome = _ChatOperationOutcome(
                    operation=self.operation,
                    error=str(exc),
                )
        except Exception:
            outcome = _ChatOperationOutcome(
                operation=self.operation,
                error="ATHENA chat operation failed.",
            )

        self.outcomes.put(outcome)
        queued = QMetaObject.invokeMethod(
            self.receiver,
            "_drain_chat_outcome",
            Qt.ConnectionType.QueuedConnection,
        )
        if not queued:
            raise RuntimeError("ATHENA desktop could not queue the chat result.")


class _ChatCancelTask(QRunnable):
    """Signal one active direct-chat operation away from the UI and send pool."""

    def __init__(
        self,
        *,
        gateway: CoreApiGateway,
        operation_id: str,
        outcomes: SimpleQueue[_ChatCancelOutcome],
        receiver: QObject,
    ) -> None:
        super().__init__()
        self.gateway = gateway
        self.operation_id = operation_id
        self.outcomes = outcomes
        self.receiver = receiver
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        try:
            accepted = self.gateway.cancel_chat_operation(self.operation_id)
        except CoreApiClientError as exc:
            outcome = _ChatCancelOutcome(
                operation_id=self.operation_id,
                error=str(exc),
            )
        except Exception:
            outcome = _ChatCancelOutcome(
                operation_id=self.operation_id,
                error="ATHENA generation cancellation request failed.",
            )
        else:
            outcome = _ChatCancelOutcome(
                operation_id=self.operation_id,
                accepted=accepted,
            )

        self.outcomes.put(outcome)
        queued = QMetaObject.invokeMethod(
            self.receiver,
            "_drain_chat_cancel_outcome",
            Qt.ConnectionType.QueuedConnection,
        )
        if not queued:
            raise RuntimeError(
                "ATHENA desktop could not queue the cancellation result."
            )


def _chat_snapshot(
    gateway: CoreApiGateway,
    *,
    chat_limit: int,
) -> tuple[tuple[ChatSummaryResponse, ...], str | None]:
    chats: list[ChatSummaryResponse] = []
    seen_chat_ids: set[str] = set()
    offset = 0

    while True:
        try:
            page = (
                gateway.list_chats(
                    limit=chat_limit,
                )
                if offset == 0
                else gateway.list_chats(
                    limit=chat_limit,
                    offset=offset,
                )
            )
        except CoreApiClientError as exc:
            return (), str(exc)
        except Exception:
            return (), "ATHENA chat status refresh failed."

        if len(page) > chat_limit:
            return (
                (),
                "ATHENA chat pagination exceeded the requested page size.",
            )

        for chat in page:
            if chat.chat_id in seen_chat_ids:
                return (
                    (),
                    "ATHENA chat pagination returned a duplicate chat identity.",
                )

            seen_chat_ids.add(
                chat.chat_id
            )

        chats.extend(page)

        if len(page) < chat_limit:
            return tuple(chats), None

        offset += len(page)


def _model_snapshot(
    gateway: CoreApiGateway,
) -> tuple[ProviderHealthResponse | None, tuple[ModelResponse, ...], str | None]:
    try:
        provider = gateway.provider_health()
    except CoreApiClientError as exc:
        return None, (), str(exc)
    except Exception:
        return None, (), "ATHENA model provider status refresh failed."

    try:
        return provider, gateway.list_models(), None
    except CoreApiClientError as exc:
        return provider, (), str(exc)
    except Exception:
        return provider, (), "ATHENA model list refresh failed."


def _storage_snapshot(
    gateway: CoreApiGateway,
) -> tuple[StorageHealthResponse | None, str | None]:
    try:
        return gateway.storage_health(), None
    except CoreApiClientError as exc:
        return None, str(exc)
    except Exception:
        return None, "ATHENA storage status refresh failed."


def _collect_snapshot(
    gateway: CoreApiGateway,
    *,
    chat_limit: int,
) -> DesktopApiSnapshot:
    health = gateway.health()
    chats, chat_error = _chat_snapshot(gateway, chat_limit=chat_limit)
    provider, models, model_error = _model_snapshot(gateway)
    storage, storage_error = _storage_snapshot(gateway)
    return DesktopApiSnapshot(
        health=health,
        provider=provider,
        models=models,
        chats=chats,
        chat_error=chat_error,
        model_error=model_error,
        storage=storage,
        storage_error=storage_error,
    )


class _RefreshTask(QRunnable):
    """Collect one API snapshot in a pool thread and queue delivery to the UI."""

    def __init__(
        self,
        *,
        gateway: CoreApiGateway,
        chat_limit: int,
        outcomes: SimpleQueue[_RefreshOutcome],
        receiver: QObject,
    ) -> None:
        super().__init__()
        self.gateway = gateway
        self.chat_limit = chat_limit
        self.outcomes = outcomes
        self.receiver = receiver

        # The controller retains this runnable until the queued UI delivery
        # completes. Do not let QThreadPool delete the native runnable first.
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        try:
            snapshot = _collect_snapshot(
                self.gateway,
                chat_limit=self.chat_limit,
            )
        except CoreApiClientError as exc:
            outcome = _RefreshOutcome(error=str(exc))
        except Exception:
            outcome = _RefreshOutcome(
                error="ATHENA Core status refresh failed."
            )
        else:
            outcome = _RefreshOutcome(snapshot=snapshot)

        # SimpleQueue is the only cross-thread data boundary. No UI QObject
        # state is mutated from this worker thread.
        self.outcomes.put(outcome)

        queued = QMetaObject.invokeMethod(
            self.receiver,
            "_drain_worker_outcome",
            Qt.ConnectionType.QueuedConnection,
        )

        if not queued:
            raise RuntimeError(
                "ATHENA desktop could not queue the API refresh result."
            )


class _SearchTask(QRunnable):
    """Run one Core-backed universal search away from the Qt UI thread."""

    def __init__(
        self,
        *,
        gateway: CoreApiGateway,
        request_id: int,
        query: str,
        limit: int,
        outcomes: SimpleQueue[_SearchOutcome],
        receiver: QObject,
    ) -> None:
        super().__init__()
        self.gateway = gateway
        self.request_id = request_id
        self.query = query
        self.limit = limit
        self.outcomes = outcomes
        self.receiver = receiver
        self.setAutoDelete(False)

    @Slot()
    def run(self) -> None:
        try:
            results = self.gateway.universal_search(
                self.query,
                limit=self.limit,
            )
        except CoreApiClientError as exc:
            outcome = _SearchOutcome(
                request_id=self.request_id,
                query=self.query,
                error=str(exc),
            )
        except Exception:
            outcome = _SearchOutcome(
                request_id=self.request_id,
                query=self.query,
                error="ATHENA Core search failed.",
            )
        else:
            outcome = _SearchOutcome(
                request_id=self.request_id,
                query=self.query,
                results=results,
            )

        self.outcomes.put(outcome)
        queued = QMetaObject.invokeMethod(
            self.receiver,
            "_drain_search_outcome",
            Qt.ConnectionType.QueuedConnection,
        )
        if not queued:
            raise RuntimeError(
                "ATHENA desktop could not queue the search result."
            )


class DesktopApiController(QObject):
    """Run Core API work off the Qt UI thread and publish immutable results."""

    snapshot_ready = Signal(object)
    connection_failed = Signal(str)
    refresh_state_changed = Signal(bool)
    chat_loaded = Signal(object)
    chat_sent = Signal(object)
    grounded_chat_sent = Signal(object)
    chat_recovery_ready = Signal(object)
    chat_deletion_preview_ready = Signal(object)
    chat_deleted = Signal(str)
    chat_pin_changed = Signal(str, bool)
    message_remembered = Signal(object)
    knowledge_extraction_ready = Signal(object)
    knowledge_review_ready = Signal(object)
    knowledge_merge_review_ready = Signal(object)
    chat_operation_failed = Signal(str, str)
    chat_busy_changed = Signal(bool)
    chat_cancel_state_changed = Signal(str, str)
    chat_cancelled = Signal(str)
    search_ready = Signal(int, str, object)
    search_failed = Signal(int, str, str)
    search_state_changed = Signal(bool)

    def __init__(
        self,
        gateway: CoreApiGateway,
        *,
        thread_pool: QThreadPool | None = None,
        control_thread_pool: QThreadPool | None = None,
        chat_limit: int = 50,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        if not 1 <= chat_limit <= 200:
            raise ValueError("Desktop chat limit must be between 1 and 200.")
        self.gateway = gateway
        self.thread_pool = thread_pool or QThreadPool.globalInstance()
        if control_thread_pool is None:
            control_thread_pool = QThreadPool(self)
            control_thread_pool.setMaxThreadCount(1)
        self.control_thread_pool = control_thread_pool
        self.chat_limit = chat_limit
        self._refreshing = False
        self._refresh_requested = False
        self._outcomes: SimpleQueue[_RefreshOutcome] = SimpleQueue()
        self._active_task: _RefreshTask | None = None
        self._last_good_chats: tuple[ChatSummaryResponse, ...] | None = None
        self._last_good_provider: ProviderHealthResponse | None = None
        self._last_good_models: tuple[ModelResponse, ...] | None = None
        self._chat_busy = False
        self._chat_outcomes: SimpleQueue[_ChatOperationOutcome] = SimpleQueue()
        self._active_chat_task: _ChatTask | None = None
        self._active_chat_operation_id: str | None = None
        self._active_chat_operation_kind: str | None = None
        self._chat_cancel_outcomes: SimpleQueue[_ChatCancelOutcome] = SimpleQueue()
        self._active_chat_cancel_task: _ChatCancelTask | None = None
        self._chat_cancel_state = "idle"
        self._chat_cancel_detail = ""
        self._search_outcomes: SimpleQueue[_SearchOutcome] = SimpleQueue()
        self._active_search_tasks: dict[int, _SearchTask] = {}
        self._next_search_request_id = 1

    @property
    def refreshing(self) -> bool:
        return self._refreshing

    @property
    def chat_busy(self) -> bool:
        return self._chat_busy

    @property
    def search_busy(self) -> bool:
        return bool(self._active_search_tasks)

    def search(
        self,
        query: str,
        *,
        limit: int = 30,
    ) -> int:
        if not isinstance(query, str):
            raise TypeError("Desktop search query must be text.")
        normalized = " ".join(query.split())
        if not normalized:
            raise ValueError("Desktop search query must not be empty.")
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("Desktop search limit must be an integer.")
        if not 1 <= limit <= 100:
            raise ValueError("Desktop search limit must be between 1 and 100.")

        request_id = self._next_search_request_id
        self._next_search_request_id += 1
        task = _SearchTask(
            gateway=self.gateway,
            request_id=request_id,
            query=normalized,
            limit=limit,
            outcomes=self._search_outcomes,
            receiver=self,
        )
        was_busy = self.search_busy
        self._active_search_tasks[request_id] = task
        if not was_busy:
            self.search_state_changed.emit(True)
        self.thread_pool.start(task)
        return request_id

    @property
    def can_cancel_active_chat(self) -> bool:
        return (
            self._chat_busy
            and self._active_chat_operation_kind
            in {"send", "send_grounded", "continue_recovery"}
            and self._active_chat_operation_id is not None
        )

    @property
    def chat_cancel_pending(self) -> bool:
        return self._chat_cancel_state in {"requesting", "accepted"}

    @property
    def chat_cancel_state(self) -> str:
        return self._chat_cancel_state

    @property
    def chat_cancel_detail(self) -> str:
        return self._chat_cancel_detail

    def _set_chat_cancel_state(self, state: str, detail: str) -> None:
        self._chat_cancel_state = state
        self._chat_cancel_detail = detail
        self.chat_cancel_state_changed.emit(state, detail)

    def cancel_active_chat_operation(self) -> bool:
        operation_id = self._active_chat_operation_id
        if (
            not self.can_cancel_active_chat
            or operation_id is None
            or self.chat_cancel_pending
            or self._active_chat_cancel_task is not None
        ):
            return False

        task = _ChatCancelTask(
            gateway=self.gateway,
            operation_id=operation_id,
            outcomes=self._chat_cancel_outcomes,
            receiver=self,
        )
        self._active_chat_cancel_task = task
        self._set_chat_cancel_state(
            "requesting",
            "Requesting generation cancellation…",
        )
        self.control_thread_pool.start(task)
        return True

    def load_chat(self, chat_id: str) -> None:
        if not chat_id or self._chat_busy:
            return
        self._start_chat_task(operation="load", chat_id=chat_id)

    def edit_message(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
        content: str,
    ) -> None:
        if (
            self._chat_busy
            or not chat_id
            or not message_id
            or not revision_id
            or not content.strip()
        ):
            return
        self._start_chat_task(
            operation="edit",
            chat_id=chat_id,
            message_id=message_id,
            revision_id=revision_id,
            content=content,
        )

    def fork_chat_from_message(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
    ) -> None:
        if (
            self._chat_busy
            or not chat_id
            or not message_id
            or not revision_id
        ):
            return
        self._start_chat_task(
            operation="fork",
            chat_id=chat_id,
            message_id=message_id,
            revision_id=revision_id,
        )

    def inspect_chat_recovery(
        self,
        *,
        chat_id: str,
        operation_id: str,
    ) -> None:
        if self._chat_busy or not chat_id or not operation_id:
            return
        self._start_chat_task(
            operation="inspect_recovery",
            chat_id=chat_id,
            operation_id=operation_id,
        )

    def continue_chat_operation(
        self,
        *,
        chat_id: str,
        operation_id: str,
    ) -> None:
        if self._chat_busy or not chat_id or not operation_id:
            return
        self._start_chat_task(
            operation="continue_recovery",
            chat_id=chat_id,
            operation_id=operation_id,
        )

    def send_message(
        self,
        *,
        chat_id: str | None,
        content: str,
        model_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> None:
        if self._chat_busy or not content.strip():
            return
        self._start_chat_task(
            operation="send",
            chat_id=chat_id,
            content=content,
            model_id=model_id,
            operation_id=str(new_uuid7()),
            effective_context_limit=effective_context_limit,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            thinking_enabled=thinking_enabled,
        )

    def send_grounded_message(
        self,
        *,
        chat_id: str | None,
        content: str,
        model_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> None:
        if self._chat_busy or not content.strip():
            return
        self._start_chat_task(
            operation="send_grounded",
            chat_id=chat_id,
            content=content,
            model_id=model_id,
            operation_id=str(new_uuid7()),
            effective_context_limit=effective_context_limit,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            thinking_enabled=thinking_enabled,
        )

    def remember_message(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
    ) -> None:
        if self._chat_busy or not chat_id or not message_id or not revision_id:
            return
        self._start_chat_task(
            operation="remember",
            chat_id=chat_id,
            message_id=message_id,
            revision_id=revision_id,
        )

    def extract_message_knowledge(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
        model_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        if self._chat_busy or not chat_id or not message_id or not revision_id:
            return
        self._start_chat_task(
            operation="extract_knowledge",
            chat_id=chat_id,
            message_id=message_id,
            revision_id=revision_id,
            model_id=model_id,
            effective_context_limit=effective_context_limit,
            max_output_tokens=max_output_tokens,
        )

    def prepare_knowledge_review(
        self,
        processing_run_id: str,
    ) -> None:
        if self._chat_busy or not processing_run_id:
            return
        self._start_chat_task(
            operation="prepare_knowledge_review",
            chat_id=None,
            processing_run_id=processing_run_id,
        )

    def load_knowledge_merge_review(self, review_id: str) -> None:
        if self._chat_busy or not review_id:
            return
        self._start_chat_task(
            operation="load_merge_review",
            chat_id=None,
            review_id=review_id,
        )

    def resolve_knowledge_merge_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> None:
        if (
            self._chat_busy
            or not review_id
            or decision not in {"merge", "keep_separate"}
        ):
            return
        self._start_chat_task(
            operation="resolve_merge_review",
            chat_id=None,
            review_id=review_id,
            review_decision=decision,
        )

    def set_chat_pinned(self, chat_id: str, *, pinned: bool) -> None:
        if not chat_id or self._chat_busy or not isinstance(pinned, bool):
            return
        self._start_chat_task(
            operation="pin",
            chat_id=chat_id,
            pinned_state=pinned,
        )

    def preview_chat_deletion(self, chat_id: str) -> None:
        if not chat_id or self._chat_busy:
            return
        self._start_chat_task(operation="preview_delete", chat_id=chat_id)

    def delete_chat(self, chat_id: str, *, preview_digest: str) -> None:
        if not chat_id or not preview_digest or self._chat_busy:
            return
        self._start_chat_task(
            operation="delete",
            chat_id=chat_id,
            preview_digest=preview_digest,
        )

    def _start_chat_task(
        self,
        *,
        operation: str,
        chat_id: str | None,
        content: str | None = None,
        model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
        preview_digest: str | None = None,
        message_id: str | None = None,
        revision_id: str | None = None,
        processing_run_id: str | None = None,
        review_id: str | None = None,
        review_decision: str | None = None,
        pinned_state: bool | None = None,
    ) -> None:
        task = _ChatTask(
            gateway=self.gateway,
            operation=operation,
            chat_id=chat_id,
            content=content,
            model_id=model_id,
            operation_id=operation_id,
            effective_context_limit=effective_context_limit,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            thinking_enabled=thinking_enabled,
            preview_digest=preview_digest,
            message_id=message_id,
            revision_id=revision_id,
            processing_run_id=processing_run_id,
            review_id=review_id,
            review_decision=review_decision,
            pinned_state=pinned_state,
            outcomes=self._chat_outcomes,
            receiver=self,
        )
        self._active_chat_task = task
        self._active_chat_operation_kind = operation
        self._active_chat_operation_id = (
            operation_id
            if operation in {"send", "send_grounded", "continue_recovery"}
            else None
        )
        self._chat_cancel_state = "idle"
        self._chat_cancel_detail = ""
        self._chat_busy = True
        self.chat_busy_changed.emit(True)
        self.thread_pool.start(task)

    @Slot()
    def refresh(self) -> None:
        if self._refreshing:
            self._refresh_requested = True
            return
        self._start_refresh_task()

    def _start_refresh_task(self) -> None:
        task = _RefreshTask(
            gateway=self.gateway,
            chat_limit=self.chat_limit,
            outcomes=self._outcomes,
            receiver=self,
        )
        self._active_task = task
        if not self._refreshing:
            self._refreshing = True
            self.refresh_state_changed.emit(True)
        self.thread_pool.start(task)

    def _stabilize_snapshot(
        self,
        snapshot: DesktopApiSnapshot,
    ) -> DesktopApiSnapshot:
        if snapshot.chat_error is None:
            chats = snapshot.chats
            self._last_good_chats = chats
            chat_freshness: SnapshotFreshness = "fresh"
        elif self._last_good_chats is not None:
            chats = self._last_good_chats
            chat_freshness = "stale"
        else:
            chats = ()
            chat_freshness = "unavailable"

        provider = snapshot.provider
        models = snapshot.models

        if snapshot.model_error is None:
            self._last_good_provider = provider
            self._last_good_models = models
            model_freshness: SnapshotFreshness = "fresh"
        else:
            if provider is not None:
                self._last_good_provider = provider

            if self._last_good_models is not None:
                provider = (
                    provider
                    if provider is not None
                    else self._last_good_provider
                )
                models = self._last_good_models
                model_freshness = "stale"
            else:
                provider = (
                    provider
                    if provider is not None
                    else self._last_good_provider
                )
                models = ()
                model_freshness = "unavailable"

        return DesktopApiSnapshot(
            health=snapshot.health,
            provider=provider,
            models=models,
            chats=chats,
            chat_error=snapshot.chat_error,
            model_error=snapshot.model_error,
            chat_freshness=chat_freshness,
            model_freshness=model_freshness,
            storage=snapshot.storage,
            storage_error=snapshot.storage_error,
        )

    @Slot()
    def _drain_worker_outcome(self) -> None:
        try:
            try:
                outcome = self._outcomes.get_nowait()
            except Empty:
                self.connection_failed.emit(
                    "ATHENA Core status refresh result was lost."
                )
                return
            if outcome.snapshot is not None:
                self.snapshot_ready.emit(
                    self._stabilize_snapshot(outcome.snapshot)
                )
                return
            assert outcome.error is not None
            self.connection_failed.emit(outcome.error)
        finally:
            self._finish_refresh()

    def _finish_refresh(self) -> None:
        self._active_task = None
        if self._refresh_requested:
            self._refresh_requested = False
            self._start_refresh_task()
            return
        self._refreshing = False
        self.refresh_state_changed.emit(False)

    @Slot()
    def _drain_chat_cancel_outcome(self) -> None:
        try:
            outcome = self._chat_cancel_outcomes.get_nowait()
        except Empty:
            self._set_chat_cancel_state(
                "failed",
                "ATHENA cancellation result was lost; generation may still be running.",
            )
            return

        if (
            self._active_chat_cancel_task is not None
            and self._active_chat_cancel_task.operation_id == outcome.operation_id
        ):
            self._active_chat_cancel_task = None
        if outcome.operation_id != self._active_chat_operation_id:
            return

        if outcome.error is not None:
            self._set_chat_cancel_state(
                "failed",
                outcome.error,
            )
            return

        if outcome.accepted is True:
            self._set_chat_cancel_state(
                "accepted",
                "Cancellation accepted; waiting for generation to stop.",
            )
            return

        self._set_chat_cancel_state(
            "expired",
            "The generation completed or expired before cancellation was accepted.",
        )

    @Slot()
    def _drain_search_outcome(self) -> None:
        try:
            try:
                outcome = self._search_outcomes.get_nowait()
            except Empty:
                return

            self._active_search_tasks.pop(outcome.request_id, None)
            if outcome.error is not None:
                self.search_failed.emit(
                    outcome.request_id,
                    outcome.query,
                    outcome.error,
                )
            else:
                assert outcome.results is not None
                self.search_ready.emit(
                    outcome.request_id,
                    outcome.query,
                    outcome.results,
                )
        finally:
            if not self._active_search_tasks:
                self.search_state_changed.emit(False)

    @Slot()
    def _drain_chat_outcome(self) -> None:
        try:
            try:
                outcome = self._chat_outcomes.get_nowait()
            except Empty:
                self.chat_operation_failed.emit(
                    "unknown",
                    "ATHENA chat result was lost.",
                )
                return

            if outcome.cancelled:
                if outcome.thread is not None:
                    self.chat_loaded.emit(outcome.thread)
                assert outcome.operation_id is not None
                self.chat_cancelled.emit(outcome.operation_id)
                return

            if outcome.error is not None:
                # Failed send mutations may have committed the user turn. The
                # worker reconciles only with a safe GET; it never retries POST.
                if outcome.thread is not None:
                    self.chat_loaded.emit(outcome.thread)
                self.chat_operation_failed.emit(
                    outcome.operation,
                    outcome.error,
                )
                return

            if outcome.recovery is not None:
                self.chat_recovery_ready.emit(outcome.recovery)
            elif outcome.grounded is not None:
                if self.chat_cancel_pending:
                    self._set_chat_cancel_state(
                        "expired",
                        "Generation completed before cancellation could take effect.",
                    )
                self.grounded_chat_sent.emit(outcome.grounded)
            elif outcome.deletion_preview is not None:
                self.chat_deletion_preview_ready.emit(outcome.deletion_preview)
            elif outcome.deleted_chat_id is not None:
                self.chat_deleted.emit(outcome.deleted_chat_id)
            elif outcome.pinned_chat_id is not None:
                assert outcome.pinned_state is not None
                self.chat_pin_changed.emit(
                    outcome.pinned_chat_id,
                    outcome.pinned_state,
                )
                self.refresh()
            elif outcome.remembered is not None:
                self.message_remembered.emit(outcome.remembered)
            elif outcome.knowledge_extraction is not None:
                self.knowledge_extraction_ready.emit(outcome.knowledge_extraction)
            elif outcome.knowledge_review is not None:
                self.knowledge_review_ready.emit(outcome.knowledge_review)
            elif outcome.merge_review is not None:
                self.knowledge_merge_review_ready.emit(outcome.merge_review)
            elif outcome.thread is not None:
                if outcome.operation == "send":
                    if self.chat_cancel_pending:
                        self._set_chat_cancel_state(
                            "expired",
                            "Generation completed before cancellation could take effect.",
                        )
                    self.chat_sent.emit(outcome.thread)
                else:
                    self.chat_loaded.emit(outcome.thread)
        finally:
            self._active_chat_task = None
            self._active_chat_operation_id = None
            self._active_chat_operation_kind = None
            self._chat_cancel_state = "idle"
            self._chat_cancel_detail = ""
            self._chat_busy = False
            self.chat_busy_changed.emit(False)
