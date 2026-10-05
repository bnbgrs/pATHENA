"""Thread-neutral contract exposed by the local ATHENA Core API."""

from __future__ import annotations

from typing import Protocol

from athena.api.contracts import (
    CapabilitiesResponse,
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
from athena.chat.cancellation import ChatCancellationReservation
from athena.retrieval.universal import UniversalSearchEntityType


class CoreDomainSurface(Protocol):
    """Stable domain operations dispatched onto the Core owner thread."""

    def health(self) -> HealthResponse: ...

    def capabilities(self) -> CapabilitiesResponse: ...

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
        requested_model_id: str | None = None,
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

    def provider_health(self) -> ProviderHealthResponse: ...

    def preview_chat_deletion(self, chat_id: str) -> DeletionPreviewResponse: ...

    def delete_chat(
        self,
        chat_id: str,
        *,
        preview_digest: str,
    ) -> DeletionResultResponse: ...

    def list_models(self) -> tuple[ModelResponse, ...]: ...

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]: ...

    def reserve_chat_operation(
        self,
        operation_id: str,
    ) -> ChatCancellationReservation | None: ...

    def release_chat_operation(
        self,
        reservation: ChatCancellationReservation,
    ) -> None: ...

    def cancel_chat_operation(self, operation_id: str) -> bool: ...

    def send_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> ChatThreadResponse: ...

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
        requested_model_id: str | None = None,
        requested_embedding_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> GroundedChatResponse: ...


class CoreApiSurface(CoreDomainSurface, Protocol):
    """Complete local transport surface, including read-only runtime telemetry."""

    def storage_health(self) -> StorageHealthResponse: ...
