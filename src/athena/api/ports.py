"""Thread-neutral contract exposed by the local ATHENA Core API."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from athena.api.contracts import (
    CapabilitiesResponse,
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

    def create_chat(
        self,
        chat_id: str | None = None,
    ) -> ChatThreadResponse: ...

    def load_chat(self, chat_id: str) -> ChatThreadResponse: ...

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

    def activate_model(
        self,
        model_id: str,
        *,
        context_length: int | None = None,
        unload_others: bool = True,
    ) -> ModelResponse: ...

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

    def stream_chat_message(
        self,
        chat_id: str,
        *,
        content: str,
        requested_model_id: str | None = None,
        operation_id: str,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
        on_delta: Callable[[str], None],
    ) -> ChatThreadResponse: ...

    def cancel_chat_operation(self, operation_id: str) -> bool: ...

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
