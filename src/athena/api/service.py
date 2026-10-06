"""Transport-neutral v1 API facade over existing ATHENA domain services."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from typing import Any, Protocol

from athena.api.contracts import (
    API_VERSION,
    CanonicalClaimResponse,
    CanonicalClaimRevisionResponse,
    CanonicalMergeReviewResponse,
    CapabilitiesResponse,
    ChatMessageResponse,
    ChatOperationRecoveryResponse,
    ChatSummaryResponse,
    ChatThreadResponse,
    ClaimProposalResponse,
    ContradictionReviewResponse,
    DedupDecisionResponse,
    DeletionDependencyResponse,
    DeletionPreviewResponse,
    DeletionResultResponse,
    LifecycleTransitionResponse,
    ExtractorMergeCandidateResponse,
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundedMemoryResponse,
    GroundingResponse,
    HealthResponse,
    ImageSourceResponse,
    KnowledgeMergeReviewResponse,
    KnowledgeReviewResponse,
    KnowledgeUnitProposalResponse,
    MessageKnowledgeExtractionResponse,
    ModelResponse,
    NewsProfileResponse,
    ProviderHealthResponse,
    RelationProposalResponse,
    RememberedChatMessageResponse,
)
from athena.api.knowledge_explanation import KnowledgeProvenanceExplanationResponse
from athena.api.knowledge_history import KnowledgeHistoryResponse
from athena.api.knowledge_inspection import KnowledgeInspectionApiService
from athena.api.knowledge_read import KnowledgeReadApiService
from athena.api.search_adapter import (
    hybrid_search_result_response,
    universal_search_result_response,
)
from athena.api.search_contracts import SearchResultResponse
from athena.chat.cancellation import (
    ChatCancellationRegistry,
    ChatCancellationReservation,
)
from athena.chat.grounded_recovery import GroundedRecoveryState, GroundedRecoveryStatus
from athena.chat.models import ChatMessage, ChatSummary, ChatThread
from athena.chat.provenance import strip_durable_provenance_manifest
from athena.chat.send_identity import (
    SendOperationState,
    SendOperationStateError,
)
from athena.chat.service import ChatService
from athena.chat.unified import UnifiedLocalChatResult
from athena.knowledge.acceptance_service import ProposalAcceptanceError
from athena.knowledge.deduplication import (
    CanonicalMergeCandidate,
    DedupDecision,
    DeduplicationPlan,
)
from athena.knowledge.extraction_models import ChatExtractionResult
from athena.knowledge.extraction_service import (
    ExtractionMessageNotFoundError,
    ExtractionMessageRevisionMismatchError,
)
from athena.knowledge.extraction_snapshot import (
    ExtractionSnapshotNotFoundError,
)
from athena.knowledge.review_service import (
    MergeReviewDetails,
    ReviewError,
    ReviewItem,
)
from athena.lifecycle.service import (
    DeletionPreview,
    DeletionResult,
    LifecycleDeletionService,
)
from athena.lifecycle.trash import LifecycleTransitionResult, LifecycleTrashService
from athena.memory.models import PersonalMemoryRevision
from athena.model.domain import ModelImageInput, ModelInfo
from athena.model.ports import ModelDiscoveryProvider
from athena.observability.health import HealthService
from athena.retrieval.hybrid import HybridSearchResult
from athena.retrieval.search import SearchEntityType
from athena.retrieval.universal import (
    UniversalSearchEntityType,
    UniversalSearchResult,
)
from athena.source.models import SourceCaptureResult


class DirectChatSender(Protocol):
    """Minimal direct-chat orchestration boundary used by the API."""

    def send_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        requested_model_id: str | None = None,
        operation_id: uuid.UUID | None = None,
        effective_context_limit: int | None = None,
        output_reserve: int = 2048,
        temperature: float | None = None,
        reasoning_mode: str | None = "off",
        cancel_requested: Callable[[], bool] | None = None,
        image_inputs: tuple[ModelImageInput, ...] = (),
        image_source_ids: tuple[uuid.UUID, ...] = (),
    ) -> object: ...


class ImageSourceService(Protocol):
    """Verified Raw Archive boundary used by direct vision chat."""

    def capture_image_bytes(
        self,
        data: bytes,
        *,
        original_name: str,
        source_uri: str,
        max_file_bytes: int | None = None,
    ) -> SourceCaptureResult: ...

    def read_image_payload(
        self,
        source_id: uuid.UUID,
        *,
        max_bytes: int,
    ) -> tuple[str, bytes]: ...


class PersonalMemoryWriter(Protocol):
    """Minimal explicit Personal Memory boundary used by message actions."""

    def remember(self, *, content: str) -> PersonalMemoryRevision: ...


class NewsProfileService(Protocol):
    """Minimal existing News configuration boundary exposed by the Core API."""

    def profile(self) -> dict[str, Any]: ...

    def configure_profile(
        self,
        *,
        timezone_name: str | None = None,
        local_hour: int | None = None,
        local_minute: int | None = None,
    ) -> dict[str, Any]: ...


class MessageKnowledgeExtractor(Protocol):
    """Minimal message-scoped extraction boundary used by the API."""

    def extract_message(
        self,
        *,
        chat_id: uuid.UUID,
        message_id: uuid.UUID,
        revision_id: uuid.UUID,
        requested_model_id: str | None = None,
        context_limit: int | None = None,
        output_reserve: int | None = None,
    ) -> ChatExtractionResult: ...


class ChatMessageNotFoundError(LookupError):
    """Raised when a message action targets no message in the requested chat."""


class ChatMessageRevisionMismatchError(RuntimeError):
    """Raised when a message action targets a stale persisted revision."""


class ExtractionSnapshotLoader(Protocol):
    """Load one immutable extraction snapshot by ProcessingRun."""

    def load(self, processing_run_id: uuid.UUID) -> ChatExtractionResult: ...


class ProposalReviewPlanner(Protocol):
    """Existing acceptance preflight used as the canonical review planner."""

    def preflight(self, result: ChatExtractionResult) -> DeduplicationPlan: ...

    def queue_merge_reviews(
        self,
        result: ChatExtractionResult,
        plan: DeduplicationPlan,
    ) -> tuple[uuid.UUID, ...]: ...


class KnowledgeReviewQueue(Protocol):
    """Persistent semantic-review operations required by the API."""

    def get(self, review_id: uuid.UUID) -> ReviewItem: ...

    def merge_details(self, review_id: uuid.UUID) -> MergeReviewDetails: ...

    def resolve_merge(
        self,
        review_id: uuid.UUID,
        *,
        actor_id: uuid.UUID,
        decision: str,
    ) -> ReviewItem: ...


class KnowledgeReviewNotFoundError(LookupError):
    """Raised when a frozen extraction or merge review cannot be found."""


class KnowledgeReviewConflictError(RuntimeError):
    """Raised when current review state blocks the requested action."""


class UnifiedLocalChatSender(Protocol):
    """Minimal Unified Local orchestration boundary used by the API."""

    def inspect_operation_recovery(
        self,
        *,
        chat_id: uuid.UUID,
        operation_id: uuid.UUID,
    ) -> GroundedRecoveryStatus: ...

    def continue_operation(
        self,
        *,
        chat_id: uuid.UUID,
        operation_id: uuid.UUID,
        cancel_requested: Callable[[], bool] | None = None,
    ) -> UnifiedLocalChatResult: ...

    def send_message(
        self,
        *,
        chat_id: uuid.UUID,
        content: str,
        requested_model_id: str | None = None,
        requested_embedding_model_id: str | None = None,
        operation_id: uuid.UUID | None = None,
        effective_context_limit: int | None = None,
        output_reserve: int = 2048,
        temperature: float | None = None,
        reasoning_mode: str | None = "off",
        cancel_requested: Callable[[], bool] | None = None,
    ) -> UnifiedLocalChatResult: ...


class NormalSearch(Protocol):
    """Minimal normal Hybrid retrieval boundary exposed by the Core API."""

    def search(
        self,
        query: str,
        *,
        model_id: str,
        limit: int = 20,
        entity_type: SearchEntityType | None = None,
    ) -> tuple[HybridSearchResult, ...]: ...


class UniversalSearch(Protocol):
    """Local cross-domain lexical search boundary exposed by the Core API."""

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[UniversalSearchResult, ...]: ...


class CoreApiFacade:
    """Stable client boundary used by desktop and future transports.

    The facade deliberately exposes DTOs instead of repositories, SQLite rows,
    provider payloads, or other implementation details. HTTP/ASGI can be added
    around this boundary without changing domain services.
    """

    _FEATURES = (
        "health",
        "capabilities",
        "chat.read",
        "chat.create",
        "chat.edit.user_message",
        "chat.fork",
        "chat.regenerate",
        "chat.pin",
        "chat.vision",
        "source.image.capture",
        "chat.recovery.read",
        "chat.recovery.continue",
        "models.read",
    )

    def __init__(
        self,
        *,
        health: HealthService,
        chat: ChatService,
        model_provider: ModelDiscoveryProvider,
        direct_chat: DirectChatSender | None = None,
        lifecycle_deletion: LifecycleDeletionService | None = None,
        lifecycle_trash: LifecycleTrashService | None = None,
        image_sources: ImageSourceService | None = None,
    ) -> None:
        self._health = health
        self._chat = chat
        self._model_provider = model_provider
        self._direct_chat = direct_chat
        self._lifecycle_deletion = lifecycle_deletion
        self._lifecycle_trash = lifecycle_trash
        self._image_sources = image_sources
        self._unified_local_chat: UnifiedLocalChatSender | None = None
        self._personal_memory: PersonalMemoryWriter | None = None
        self._knowledge_extraction: MessageKnowledgeExtractor | None = None
        self._extraction_snapshots: ExtractionSnapshotLoader | None = None
        self._proposal_review_planner: ProposalReviewPlanner | None = None
        self._knowledge_reviews: KnowledgeReviewQueue | None = None
        self._knowledge_inspection: KnowledgeInspectionApiService | None = None
        self._knowledge_read: KnowledgeReadApiService | None = None
        self._normal_search: NormalSearch | None = None
        self._universal_search: UniversalSearch | None = None
        self._news: NewsProfileService | None = None
        self._chat_cancellations = ChatCancellationRegistry()

    def reserve_chat_operation(
        self,
        operation_id: str,
    ) -> ChatCancellationReservation | None:
        """Reserve cancellation state before a send enters the owner queue."""
        return self._chat_cancellations.reserve(uuid.UUID(operation_id))

    def release_chat_operation(
        self,
        reservation: ChatCancellationReservation,
    ) -> None:
        """Release one exact cancellation reservation without stale cleanup."""
        self._chat_cancellations.release(reservation)

    def cancel_chat_operation(self, operation_id: str) -> bool:
        """Signal one known active send without touching domain or SQLite state."""
        return self._chat_cancellations.cancel(uuid.UUID(operation_id))

    def attach_news(self, news: NewsProfileService) -> None:
        """Attach the existing durable News profile exactly once."""
        if self._news is not None:
            raise RuntimeError("News profile is already attached to the Core API.")
        self._news = news

    def news_profile(self) -> NewsProfileResponse:
        news = self._news
        if news is None:
            raise RuntimeError("News profile is unavailable in this Core process.")
        return _news_profile_response(news.profile())

    def configure_news_schedule(
        self,
        *,
        timezone_name: str,
        local_hour: int,
        local_minute: int,
    ) -> NewsProfileResponse:
        news = self._news
        if news is None:
            raise RuntimeError("News profile is unavailable in this Core process.")
        return _news_profile_response(
            news.configure_profile(
                timezone_name=timezone_name,
                local_hour=local_hour,
                local_minute=local_minute,
            )
        )

    def attach_normal_search(self, search: NormalSearch) -> None:
        """Attach normal Hybrid Search exactly once after app construction."""

        if self._normal_search is not None:
            raise RuntimeError("Normal Hybrid Search is already attached to the Core API.")
        self._normal_search = search

    def attach_universal_search(self, search: UniversalSearch) -> None:
        """Attach local Universal Search exactly once after app construction."""

        if self._universal_search is not None:
            raise RuntimeError("Universal Search is already attached to the Core API.")
        self._universal_search = search

    def attach_knowledge_inspection(
        self,
        inspection: KnowledgeInspectionApiService,
    ) -> None:
        """Attach canonical Claim inspection exactly once."""

        if self._knowledge_inspection is not None:
            raise RuntimeError("Knowledge inspection is already attached to the Core API.")
        self._knowledge_inspection = inspection

    def attach_knowledge_read(self, knowledge_read: KnowledgeReadApiService) -> None:
        """Attach truthful Knowledge provenance/history reads exactly once."""

        if self._knowledge_read is not None:
            raise RuntimeError("Knowledge read is already attached to the Core API.")
        self._knowledge_read = knowledge_read

    def attach_unified_local_chat(
        self,
        sender: UnifiedLocalChatSender,
    ) -> None:
        """Attach Unified Local chat exactly once after app construction."""

        if self._unified_local_chat is not None:
            raise RuntimeError(
                "Unified Local chat is already attached to the Core API."
            )
        self._unified_local_chat = sender

    def attach_knowledge_interaction(
        self,
        *,
        personal_memory: PersonalMemoryWriter,
        extraction: MessageKnowledgeExtractor,
    ) -> None:
        """Attach message-memory and extraction services exactly once."""

        if self._personal_memory is not None or self._knowledge_extraction is not None:
            raise RuntimeError(
                "Knowledge interaction is already attached to the Core API."
            )
        self._personal_memory = personal_memory
        self._knowledge_extraction = extraction

    def attach_knowledge_review(
        self,
        *,
        extraction_snapshots: ExtractionSnapshotLoader,
        proposal_review_planner: ProposalReviewPlanner,
        reviews: KnowledgeReviewQueue,
    ) -> None:
        """Attach frozen-proposal review services exactly once."""

        if (
            self._extraction_snapshots is not None
            or self._proposal_review_planner is not None
            or self._knowledge_reviews is not None
        ):
            raise RuntimeError(
                "Knowledge review is already attached to the Core API."
            )
        self._extraction_snapshots = extraction_snapshots
        self._proposal_review_planner = proposal_review_planner
        self._knowledge_reviews = reviews

    def health(self) -> HealthResponse:
        snapshot = self._health.snapshot()
        return HealthResponse(
            api_version=API_VERSION,
            core_status=snapshot.status.value,
            detail=snapshot.detail,
        )

    def capabilities(self) -> CapabilitiesResponse:
        features: tuple[str, ...] = self._FEATURES
        if self._direct_chat is not None:
            features = (
                *features,
                "chat.send.direct",
                "chat.cancel",
            )
        if self._unified_local_chat is not None:
            features = (*features, "chat.send.unified_local")
        if self._lifecycle_deletion is not None:
            features = (*features, "chat.delete")
        if self._lifecycle_trash is not None:
            features = (*features, "chat.trash", "chat.restore", "chat.trash.list")
        if self._personal_memory is not None and self._knowledge_extraction is not None:
            features = (
                *features,
                "memory.remember.chat_message",
                "knowledge.extract.chat_message",
            )
        if (
            self._extraction_snapshots is not None
            and self._proposal_review_planner is not None
            and self._knowledge_reviews is not None
        ):
            features = (
                *features,
                "knowledge.review.preflight",
                "knowledge.review.merge",
            )
        if self._knowledge_inspection is not None:
            features = (
                *features,
                "knowledge.claim.inspect",
                "knowledge.review.contradiction",
            )
        if self._knowledge_read is not None:
            features = (
                *features,
                "knowledge.read.why_known",
                "knowledge.read.revision_history",
            )
        if self._normal_search is not None:
            features = (*features, "search.normal.hybrid")
        if self._universal_search is not None:
            features = (*features, "search.universal.local")
        if self._news is not None:
            features = (*features, "news.profile.read", "news.schedule.write")
        return CapabilitiesResponse(
            api_version=API_VERSION,
            features=features,
        )

    def why_known(self, knowledge_id: str) -> KnowledgeProvenanceExplanationResponse:
        return self._knowledge_read_service().why_known(knowledge_id)

    def knowledge_revision_history(self, knowledge_id: str) -> KnowledgeHistoryResponse:
        return self._knowledge_read_service().revision_history(knowledge_id)

    def _knowledge_read_service(self) -> KnowledgeReadApiService:
        knowledge_read = self._knowledge_read
        if knowledge_read is None:
            raise RuntimeError("Knowledge read is unavailable in this Core process.")
        return knowledge_read

    def list_claims(self, *, limit: int = 100) -> tuple[CanonicalClaimResponse, ...]:
        return self._knowledge_inspection_service().list_claims(limit=limit)

    def load_claim(self, claim_id: str) -> CanonicalClaimResponse:
        return self._knowledge_inspection_service().load_claim(claim_id)

    def claim_history(
        self,
        claim_id: str,
    ) -> tuple[CanonicalClaimRevisionResponse, ...]:
        return self._knowledge_inspection_service().claim_history(claim_id)

    def list_pending_contradictions(
        self,
        *,
        limit: int = 100,
    ) -> tuple[ContradictionReviewResponse, ...]:
        return self._knowledge_inspection_service().list_pending_contradictions(
            limit=limit
        )

    def load_contradiction_review(
        self,
        review_id: str,
    ) -> ContradictionReviewResponse:
        return self._knowledge_inspection_service().load_contradiction_review(review_id)

    def resolve_contradiction_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> ContradictionReviewResponse:
        return self._knowledge_inspection_service().resolve_contradiction_review(
            review_id,
            decision=decision,
        )

    def _knowledge_inspection_service(self) -> KnowledgeInspectionApiService:
        inspection = self._knowledge_inspection
        if inspection is None:
            raise RuntimeError(
                "Knowledge inspection is unavailable in this Core process."
            )
        return inspection

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        return tuple(
            _chat_summary(summary)
            for summary in self._chat.list_chats(
                limit=limit,
                offset=offset,
            )
        )

    def list_trashed_chats(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        if self._lifecycle_trash is None:
            raise RuntimeError("Chat trash is unavailable in this Core process.")
        return tuple(
            _chat_summary(summary)
            for summary in self._lifecycle_trash.list_trashed_chats(
                limit=limit,
                offset=offset,
            )
        )

    def trash_chat(self, chat_id: str) -> LifecycleTransitionResponse:
        if self._lifecycle_trash is None:
            raise RuntimeError("Chat trash is unavailable in this Core process.")
        return _lifecycle_transition(
            self._lifecycle_trash.trash_chat(uuid.UUID(chat_id))
        )

    def restore_chat(self, chat_id: str) -> LifecycleTransitionResponse:
        if self._lifecycle_trash is None:
            raise RuntimeError("Chat restore is unavailable in this Core process.")
        return _lifecycle_transition(
            self._lifecycle_trash.restore_chat(uuid.UUID(chat_id))
        )

    def set_chat_pinned(
        self,
        chat_id: str,
        *,
        pinned: bool,
    ) -> ChatSummaryResponse:
        parsed_chat_id = uuid.UUID(chat_id)
        self._chat.set_chat_pinned(
            chat_id=parsed_chat_id,
            pinned=pinned,
        )
        summary = next(
            (
                item
                for item in self._chat.list_chats(limit=500)
                if item.chat_id == parsed_chat_id
            ),
            None,
        )
        if summary is None:
            raise RuntimeError("Pinned chat disappeared from the canonical chat list.")
        return _chat_summary(summary)

    def create_chat(
        self,
        chat_id: str | None = None,
    ) -> ChatThreadResponse:
        if chat_id is None:
            created_chat_id = self._chat.create_chat()
        else:
            created_chat_id = self._chat.create_chat(
                chat_id=uuid.UUID(chat_id)
            )

        return _chat_thread(
            self._chat.load_chat(
                created_chat_id
            )
        )

    def load_chat(self, chat_id: str) -> ChatThreadResponse:
        parsed_chat_id = uuid.UUID(chat_id)
        return _chat_thread(self._chat.load_chat(parsed_chat_id))

    def edit_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        expected_revision_id: str,
        content: str,
    ) -> ChatThreadResponse:
        parsed_chat_id = uuid.UUID(chat_id)
        self._chat.edit_user_message(
            chat_id=parsed_chat_id,
            message_id=uuid.UUID(message_id),
            expected_revision_id=uuid.UUID(expected_revision_id),
            content=content,
        )
        return _chat_thread(self._chat.load_chat(parsed_chat_id))

    def fork_chat_from_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> ChatThreadResponse:
        forked_chat_id = self._chat.fork_chat_from_message(
            chat_id=uuid.UUID(chat_id),
            source_message_id=uuid.UUID(message_id),
            source_revision_id=uuid.UUID(revision_id),
        )
        return _chat_thread(self._chat.load_chat(forked_chat_id))

    def regenerate_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
        requested_model_id: str | None = None,
        operation_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
    ) -> ChatThreadResponse:
        """Regenerate one exact assistant response on a new durable branch."""
        if self._direct_chat is None:
            raise RuntimeError(
                "Direct chat is unavailable in this Core process."
            )

        plan = self._chat.prepare_assistant_regeneration(
            chat_id=uuid.UUID(chat_id),
            source_assistant_message_id=uuid.UUID(message_id),
            source_assistant_revision_id=uuid.UUID(revision_id),
        )
        prompt = plan.source_prompt
        if prompt.content is None or not prompt.content.strip():
            raise RuntimeError(
                "The persisted regeneration prompt has no available text."
            )

        return self.send_chat_message(
            str(plan.branch_chat_id),
            content=prompt.content,
            requested_model_id=requested_model_id,
            operation_id=operation_id,
            effective_context_limit=effective_context_limit,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            thinking_enabled=thinking_enabled,
            image_source_ids=tuple(str(source_id) for source_id in prompt.source_ids),
        )

    def capture_image_source(
        self,
        *,
        data: bytes,
        original_name: str,
        source_uri: str,
    ) -> ImageSourceResponse:
        service = self._image_sources
        if service is None:
            raise RuntimeError("Image capture is unavailable in this Core process.")
        result = service.capture_image_bytes(
            data,
            original_name=original_name,
            source_uri=source_uri,
            max_file_bytes=12 * 1024 * 1024,
        )
        media_type = result.blob.media_type or result.source.mime_type
        if media_type not in {"image/png", "image/jpeg", "image/gif"}:
            raise RuntimeError("Captured image has no supported media type.")
        return ImageSourceResponse(
            source_id=str(result.source.source_id),
            media_type=media_type,
            original_name=result.source.original_name or original_name,
            byte_length=result.blob.byte_length,
        )

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
        image_source_ids: tuple[str, ...] = (),
    ) -> ChatThreadResponse:
        if self._direct_chat is None:
            raise RuntimeError(
                "Direct chat is unavailable in this Core process."
            )

        parsed_chat_id = uuid.UUID(chat_id)

        if len(image_source_ids) > 4:
            raise ValueError("Vision chat accepts at most four image Sources.")
        if len(set(image_source_ids)) != len(image_source_ids):
            raise ValueError("Vision image Source IDs must be unique.")
        parsed_image_source_ids = tuple(
            uuid.UUID(source_id)
            for source_id in image_source_ids
        )
        image_inputs: tuple[ModelImageInput, ...] = ()
        if parsed_image_source_ids:
            source_service = self._image_sources
            if source_service is None:
                raise RuntimeError(
                    "Vision chat is unavailable because image Sources are not attached."
                )
            loaded_images = tuple(
                source_service.read_image_payload(
                    source_id,
                    max_bytes=12 * 1024 * 1024,
                )
                for source_id in parsed_image_source_ids
            )
            if sum(len(data) for _media_type, data in loaded_images) > 20 * 1024 * 1024:
                raise ValueError(
                    "Vision chat image payload exceeds the 20 MiB total in-memory limit."
                )
            image_inputs = tuple(
                ModelImageInput(
                    media_type=media_type,
                    data=data,
                )
                for media_type, data in loaded_images
            )

        parsed_operation_id = (
            None
            if operation_id is None
            else uuid.UUID(operation_id)
        )
        cancellation_reservation = (
            None
            if parsed_operation_id is None
            else self._chat_cancellations.get_or_reserve(parsed_operation_id)
        )
        cancel_requested = (
            None
            if cancellation_reservation is None
            else cancellation_reservation.cancel_requested
        )

        try:
            if parsed_operation_id is None:
                if (
                    effective_context_limit is None
                    and max_output_tokens is None
                    and temperature is None
                    and thinking_enabled is None
                ):
                    self._direct_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_inputs=image_inputs,
                        image_source_ids=parsed_image_source_ids,
                    )
                elif (
                    max_output_tokens is None
                    and temperature is None
                    and thinking_enabled is None
                ):
                    self._direct_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_inputs=image_inputs,
                        image_source_ids=parsed_image_source_ids,
                        effective_context_limit=effective_context_limit,
                    )
                else:
                    self._direct_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_inputs=image_inputs,
                        image_source_ids=parsed_image_source_ids,
                        effective_context_limit=effective_context_limit,
                        output_reserve=(
                            2048
                            if max_output_tokens is None
                            else max_output_tokens
                        ),
                        temperature=temperature,
                        reasoning_mode=(
                            None
                            if thinking_enabled is True
                            else "off"
                        ),
                    )
            elif (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                self._direct_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    image_inputs=image_inputs,
                    image_source_ids=parsed_image_source_ids,
                    operation_id=parsed_operation_id,
                    cancel_requested=cancel_requested,
                )
            elif (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                self._direct_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    image_inputs=image_inputs,
                    image_source_ids=parsed_image_source_ids,
                    operation_id=parsed_operation_id,
                    effective_context_limit=effective_context_limit,
                    cancel_requested=cancel_requested,
                )
            else:
                self._direct_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    image_inputs=image_inputs,
                    image_source_ids=parsed_image_source_ids,
                    operation_id=parsed_operation_id,
                    effective_context_limit=effective_context_limit,
                    output_reserve=(
                        2048
                        if max_output_tokens is None
                        else max_output_tokens
                    ),
                    temperature=temperature,
                    reasoning_mode=(
                        None
                        if thinking_enabled is True
                        else "off"
                    ),
                    cancel_requested=cancel_requested,
                )

        except SendOperationStateError as exc:
            status = exc.status

            if (
                parsed_operation_id is None
                or status.chat_id != parsed_chat_id
                or status.operation_id != parsed_operation_id
            ):
                raise RuntimeError(
                    "Direct chat returned send-operation "
                    "state for another request."
                ) from exc

            if (
                status.state
                is SendOperationState.COMPLETE
            ):
                return _chat_thread(
                    self._chat.load_chat(
                        parsed_chat_id
                    )
                )

            raise
        finally:
            if cancellation_reservation is not None:
                self._chat_cancellations.release(cancellation_reservation)

        return _chat_thread(
            self._chat.load_chat(
                parsed_chat_id
            )
        )

    def chat_operation_recovery(
        self,
        chat_id: str,
        operation_id: str,
    ) -> ChatOperationRecoveryResponse:
        sender = self._unified_local_chat
        parsed_chat_id = uuid.UUID(chat_id)
        parsed_operation_id = uuid.UUID(operation_id)
        if sender is None:
            return ChatOperationRecoveryResponse(
                operation_id=str(parsed_operation_id),
                chat_id=str(parsed_chat_id),
                mode="grounded",
                state=GroundedRecoveryState.ABSENT.value,
                can_continue=False,
                processing_run_id=None,
            )

        status = sender.inspect_operation_recovery(
            chat_id=parsed_chat_id,
            operation_id=parsed_operation_id,
        )
        return ChatOperationRecoveryResponse(
            operation_id=str(status.operation_id),
            chat_id=str(status.chat_id),
            mode="grounded",
            state=status.state.value,
            can_continue=status.state in {
                GroundedRecoveryState.RESUMABLE,
                GroundedRecoveryState.RESULT_AVAILABLE,
                GroundedRecoveryState.FINALIZATION_REQUIRED,
            },
            processing_run_id=(
                None
                if status.processing_run_id is None
                else str(status.processing_run_id)
            ),
            partial_output=(
                None
                if status.partial_output is None
                else status.partial_output.content
            ),
        )

    def continue_unified_local_chat_operation(
        self,
        chat_id: str,
        operation_id: str,
    ) -> GroundedChatResponse:
        sender = self._unified_local_chat
        if sender is None:
            raise RuntimeError(
                "Unified Local chat is unavailable in this Core process."
            )
        parsed_chat_id = uuid.UUID(chat_id)
        parsed_operation_id = uuid.UUID(operation_id)
        cancellation_reservation = self._chat_cancellations.get_or_reserve(
            parsed_operation_id
        )
        try:
            result = sender.continue_operation(
                chat_id=parsed_chat_id,
                operation_id=parsed_operation_id,
                cancel_requested=cancellation_reservation.cancel_requested,
            )
        finally:
            self._chat_cancellations.release(cancellation_reservation)

        return _grounded_chat_response(
            result,
            self._chat.load_chat(parsed_chat_id),
        )

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
    ) -> GroundedChatResponse:
        if self._unified_local_chat is None:
            raise RuntimeError(
                "Unified Local chat is unavailable in this Core process."
            )
        parsed_chat_id = uuid.UUID(chat_id)
        parsed_operation_id = (
            None
            if operation_id is None
            else uuid.UUID(operation_id)
        )
        cancellation_reservation = (
            None
            if parsed_operation_id is None
            else self._chat_cancellations.get_or_reserve(parsed_operation_id)
        )
        cancel_requested = (
            None
            if cancellation_reservation is None
            else cancellation_reservation.cancel_requested
        )

        try:
            if parsed_operation_id is None:
                if (
                    effective_context_limit is None
                    and max_output_tokens is None
                    and temperature is None
                    and thinking_enabled is None
                ):
                    result = self._unified_local_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                    )
                elif (
                    max_output_tokens is None
                    and temperature is None
                    and thinking_enabled is None
                ):
                    result = self._unified_local_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                        effective_context_limit=effective_context_limit,
                    )
                else:
                    result = self._unified_local_chat.send_message(
                        chat_id=parsed_chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                        effective_context_limit=effective_context_limit,
                        output_reserve=(
                            2048 if max_output_tokens is None else max_output_tokens
                        ),
                        temperature=temperature,
                        reasoning_mode=(None if thinking_enabled is True else "off"),
                    )
            elif (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                result = self._unified_local_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    requested_embedding_model_id=requested_embedding_model_id,
                    operation_id=parsed_operation_id,
                    cancel_requested=cancel_requested,
                )
            elif (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                result = self._unified_local_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    requested_embedding_model_id=requested_embedding_model_id,
                    operation_id=parsed_operation_id,
                    effective_context_limit=effective_context_limit,
                    cancel_requested=cancel_requested,
                )
            else:
                result = self._unified_local_chat.send_message(
                    chat_id=parsed_chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    requested_embedding_model_id=requested_embedding_model_id,
                    operation_id=parsed_operation_id,
                    effective_context_limit=effective_context_limit,
                    output_reserve=(
                        2048 if max_output_tokens is None else max_output_tokens
                    ),
                    temperature=temperature,
                    reasoning_mode=(None if thinking_enabled is True else "off"),
                    cancel_requested=cancel_requested,
                )
        finally:
            if cancellation_reservation is not None:
                self._chat_cancellations.release(cancellation_reservation)

        return _grounded_chat_response(
            result,
            self._chat.load_chat(parsed_chat_id),
        )

    def remember_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> RememberedChatMessageResponse:
        if self._personal_memory is None:
            raise RuntimeError(
                "Personal Memory interaction is unavailable in this Core process."
            )
        parsed_chat_id, parsed_message_id, parsed_revision_id, message = (
            self._resolve_message_revision(
                chat_id=chat_id,
                message_id=message_id,
                revision_id=revision_id,
            )
        )
        content = _chat_message(message).content
        if content is None or not content.strip():
            raise ValueError("The selected chat message has no rememberable text.")
        memory = self._personal_memory.remember(content=content)
        return RememberedChatMessageResponse(
            chat_id=str(parsed_chat_id),
            message_id=str(parsed_message_id),
            message_revision_id=str(parsed_revision_id),
            memory_id=str(memory.memory_id),
            memory_revision_id=str(memory.revision_id),
            content=memory.payload.content,
        )

    def extract_chat_message_knowledge(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
        requested_model_id: str | None = None,
        effective_context_limit: int | None = None,
        max_output_tokens: int | None = None,
    ) -> MessageKnowledgeExtractionResponse:
        if self._knowledge_extraction is None:
            raise RuntimeError(
                "Knowledge extraction is unavailable in this Core process."
            )
        parsed_chat_id, parsed_message_id, parsed_revision_id, _ = (
            self._resolve_message_revision(
                chat_id=chat_id,
                message_id=message_id,
                revision_id=revision_id,
            )
        )
        try:
            result = self._knowledge_extraction.extract_message(
                chat_id=parsed_chat_id,
                message_id=parsed_message_id,
                revision_id=parsed_revision_id,
                requested_model_id=requested_model_id,
                context_limit=effective_context_limit,
                output_reserve=max_output_tokens,
            )
        except ExtractionMessageNotFoundError as exc:
            raise ChatMessageNotFoundError(str(exc)) from exc
        except ExtractionMessageRevisionMismatchError as exc:
            raise ChatMessageRevisionMismatchError(str(exc)) from exc
        if result.chat_id != parsed_chat_id:
            raise RuntimeError("Knowledge extraction returned another chat.")
        return _message_knowledge_extraction_response(
            result,
            message_id=parsed_message_id,
            revision_id=parsed_revision_id,
        )

    def _resolve_message_revision(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
    ) -> tuple[uuid.UUID, uuid.UUID, uuid.UUID, ChatMessage]:
        parsed_chat_id = uuid.UUID(chat_id)
        parsed_message_id = uuid.UUID(message_id)
        parsed_revision_id = uuid.UUID(revision_id)
        thread = self._chat.load_chat(parsed_chat_id)
        message = next(
            (item for item in thread.messages if item.message_id == parsed_message_id),
            None,
        )
        if message is None:
            raise ChatMessageNotFoundError(
                "The requested chat message does not exist in this chat."
            )
        if message.revision_id != parsed_revision_id:
            raise ChatMessageRevisionMismatchError(
                "The requested chat message revision is stale."
            )
        return parsed_chat_id, parsed_message_id, parsed_revision_id, message

    def prepare_knowledge_review(
        self,
        processing_run_id: str,
    ) -> KnowledgeReviewResponse:
        snapshots, planner, _reviews = self._knowledge_review_services()
        parsed_run_id = uuid.UUID(processing_run_id)
        try:
            result = snapshots.load(parsed_run_id)
        except ExtractionSnapshotNotFoundError as exc:
            raise KnowledgeReviewNotFoundError(str(exc)) from exc
        if result.processing_run.processing_run_id != parsed_run_id:
            raise RuntimeError(
                "Frozen Knowledge extraction returned another ProcessingRun."
            )

        if result.proposals.merge_candidates:
            return KnowledgeReviewResponse(
                processing_run_id=str(parsed_run_id),
                model_signature_id=str(result.model_signature.model_signature_id),
                ready_to_accept=False,
                blocked_reason="extractor_merge_candidates",
                preflight_digest=None,
                knowledge_decisions=(),
                claim_decisions=(),
                canonical_merge_candidates=(),
            )

        try:
            plan = planner.preflight(result)
        except ProposalAcceptanceError as exc:
            raise KnowledgeReviewConflictError(str(exc)) from exc

        review_ids: tuple[uuid.UUID, ...] = ()
        if plan.merge_candidates:
            try:
                review_ids = planner.queue_merge_reviews(result, plan)
            except ProposalAcceptanceError as exc:
                raise KnowledgeReviewConflictError(str(exc)) from exc
            if len(review_ids) != len(plan.merge_candidates):
                raise RuntimeError(
                    "Knowledge merge-review queue returned inconsistent identity data."
                )

        return _knowledge_review_response(
            result=result,
            plan=plan,
            review_ids=review_ids,
        )

    def load_knowledge_merge_review(
        self,
        review_id: str,
    ) -> KnowledgeMergeReviewResponse:
        _snapshots, _planner, reviews = self._knowledge_review_services()
        return self._load_knowledge_merge_review(
            reviews=reviews,
            review_id=uuid.UUID(review_id),
        )

    def resolve_knowledge_merge_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> KnowledgeMergeReviewResponse:
        if decision not in {"merge", "keep_separate"}:
            raise ValueError(
                "Knowledge merge decision must be 'merge' or 'keep_separate'."
            )
        _snapshots, _planner, reviews = self._knowledge_review_services()
        parsed_review_id = uuid.UUID(review_id)
        current = self._load_knowledge_merge_review(
            reviews=reviews,
            review_id=parsed_review_id,
        )
        if current.status != "pending":
            if current.status == "accepted" and current.decision == decision:
                return current
            raise KnowledgeReviewConflictError(
                "Knowledge merge review is already resolved differently."
            )
        try:
            reviews.resolve_merge(
                parsed_review_id,
                actor_id=self._chat.ensure_local_user(),
                decision=decision,
            )
        except ReviewError as exc:
            raise KnowledgeReviewConflictError(str(exc)) from exc
        return self._load_knowledge_merge_review(
            reviews=reviews,
            review_id=parsed_review_id,
        )

    def _knowledge_review_services(
        self,
    ) -> tuple[
        ExtractionSnapshotLoader,
        ProposalReviewPlanner,
        KnowledgeReviewQueue,
    ]:
        snapshots = self._extraction_snapshots
        planner = self._proposal_review_planner
        reviews = self._knowledge_reviews
        if snapshots is None or planner is None or reviews is None:
            raise RuntimeError(
                "Knowledge review is unavailable in this Core process."
            )
        return snapshots, planner, reviews

    @staticmethod
    def _load_knowledge_merge_review(
        *,
        reviews: KnowledgeReviewQueue,
        review_id: uuid.UUID,
    ) -> KnowledgeMergeReviewResponse:
        try:
            item = reviews.get(review_id)
        except ReviewError as exc:
            raise KnowledgeReviewNotFoundError(str(exc)) from exc
        if item.review_type != "merge_candidate":
            raise KnowledgeReviewConflictError(
                "Review item is not a Knowledge merge candidate."
            )
        try:
            details = reviews.merge_details(review_id)
        except ReviewError as exc:
            raise RuntimeError(
                "Knowledge merge-review payload is missing or invalid."
            ) from exc
        return _knowledge_merge_review_response(item, details)

    def preview_chat_deletion(self, chat_id: str) -> DeletionPreviewResponse:
        if self._lifecycle_deletion is None:
            raise RuntimeError("Chat deletion is unavailable in this Core process.")
        parsed_chat_id = uuid.UUID(chat_id)
        preview = self._lifecycle_deletion.preview(parsed_chat_id)
        if preview.entity_type != "chat":
            raise RuntimeError("Deletion preview resolved a non-chat entity.")
        return _deletion_preview(preview)

    def delete_chat(
        self,
        chat_id: str,
        *,
        preview_digest: str,
    ) -> DeletionResultResponse:
        if self._lifecycle_deletion is None:
            raise RuntimeError("Chat deletion is unavailable in this Core process.")
        parsed_chat_id = uuid.UUID(chat_id)
        result = self._lifecycle_deletion.delete(
            parsed_chat_id,
            preview_digest=preview_digest,
        )
        if result.entity_type != "chat":
            raise RuntimeError("Deletion result resolved a non-chat entity.")
        return _deletion_result(result)

    def provider_health(self) -> ProviderHealthResponse:
        snapshot = self._model_provider.health()
        return ProviderHealthResponse(
            provider=self._model_provider.provider_id,
            status=snapshot.status.value,
            detail=snapshot.detail,
        )

    def list_models(self) -> tuple[ModelResponse, ...]:
        return tuple(_model(model) for model in self._model_provider.discover_models())

    def search(
        self,
        query: str,
        *,
        model_id: str,
        limit: int = 20,
        entity_type: SearchEntityType | None = None,
    ) -> tuple[SearchResultResponse, ...]:
        if self._normal_search is None:
            raise RuntimeError("Normal Hybrid Search is unavailable in this Core process.")
        return tuple(
            hybrid_search_result_response(result)
            for result in self._normal_search.search(
                query,
                model_id=model_id,
                limit=limit,
                entity_type=entity_type,
            )
        )

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]:
        if self._universal_search is None:
            raise RuntimeError("Universal Search is unavailable in this Core process.")
        return tuple(
            universal_search_result_response(result)
            for result in self._universal_search.search(
                query,
                limit=limit,
                entity_types=entity_types,
            )
        )


def _message_knowledge_extraction_response(
    result: ChatExtractionResult,
    *,
    message_id: uuid.UUID,
    revision_id: uuid.UUID,
) -> MessageKnowledgeExtractionResponse:
    return MessageKnowledgeExtractionResponse(
        chat_id=str(result.chat_id),
        message_id=str(message_id),
        message_revision_id=str(revision_id),
        processing_run_id=str(result.processing_run.processing_run_id),
        model_id=result.model.backend_model_id,
        model_signature_id=str(result.model_signature.model_signature_id),
        knowledge_units=tuple(
            KnowledgeUnitProposalResponse(
                proposal_index=index,
                source_sequence_no=item.source_sequence_no,
                source_quote=item.source_quote,
                knowledge_kind=item.knowledge_kind.value,
                title=item.title,
                body=item.body,
                epistemic_status=item.epistemic_status.value,
                confidence=item.confidence,
            )
            for index, item in enumerate(result.proposals.knowledge_units)
        ),
        claims=tuple(
            ClaimProposalResponse(
                proposal_index=index,
                source_sequence_no=item.source_sequence_no,
                source_quote=item.source_quote,
                claim_kind=item.claim_kind.value,
                statement=item.statement,
                epistemic_status=item.epistemic_status.value,
                confidence=item.confidence,
            )
            for index, item in enumerate(result.proposals.claims)
        ),
        relations=tuple(
            RelationProposalResponse(
                relation_index=index,
                left_type=item.left_type.value,
                left_index=item.left_index,
                relation_type=item.relation_type,
                right_type=item.right_type.value,
                right_index=item.right_index,
                confidence=item.confidence,
            )
            for index, item in enumerate(result.proposals.relations)
        ),
        extractor_merge_candidates=tuple(
            ExtractorMergeCandidateResponse(
                candidate_index=index,
                proposal_type=item.proposal_type.value,
                proposal_index=item.proposal_index,
                reason=item.reason,
                confidence=item.confidence,
            )
            for index, item in enumerate(result.proposals.merge_candidates)
        ),
    )


def _dedup_decision_response(
    decision: DedupDecision,
) -> DedupDecisionResponse:
    return DedupDecisionResponse(
        proposal_type=decision.proposal_type.value,
        proposal_index=decision.proposal_index,
        action=decision.action.value,
        existing_entity_id=(
            None
            if decision.existing_entity_id is None
            else str(decision.existing_entity_id)
        ),
        existing_revision_id=(
            None
            if decision.existing_revision_id is None
            else str(decision.existing_revision_id)
        ),
        duplicate_of_proposal_index=decision.duplicate_of_proposal_index,
    )


def _canonical_merge_review_response(
    *,
    candidate_index: int,
    candidate: CanonicalMergeCandidate,
    review_id: uuid.UUID,
) -> CanonicalMergeReviewResponse:
    return CanonicalMergeReviewResponse(
        candidate_index=candidate_index,
        review_id=str(review_id),
        proposal_type=candidate.proposal_type.value,
        proposal_index=candidate.proposal_index,
        existing_entity_id=str(candidate.existing_entity_id),
        existing_revision_id=str(candidate.existing_revision_id),
        similarity=candidate.similarity,
        reason=candidate.reason,
    )


def _dedup_plan_digest(plan: DeduplicationPlan) -> str:
    payload = {
        "knowledge": [
            item.to_dict()
            for item in (
                _dedup_decision_response(decision)
                for decision in plan.knowledge
            )
        ],
        "claims": [
            item.to_dict()
            for item in (
                _dedup_decision_response(decision)
                for decision in plan.claims
            )
        ],
        "merge_candidates": [
            {
                "proposal_type": candidate.proposal_type.value,
                "proposal_index": candidate.proposal_index,
                "existing_entity_id": str(candidate.existing_entity_id),
                "existing_revision_id": str(candidate.existing_revision_id),
                "similarity": candidate.similarity,
                "reason": candidate.reason,
            }
            for candidate in plan.merge_candidates
        ],
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _knowledge_review_response(
    *,
    result: ChatExtractionResult,
    plan: DeduplicationPlan,
    review_ids: tuple[uuid.UUID, ...],
) -> KnowledgeReviewResponse:
    blocked = bool(plan.merge_candidates)
    if blocked and len(review_ids) != len(plan.merge_candidates):
        raise RuntimeError(
            "Knowledge merge-review identities do not match the preflight plan."
        )
    return KnowledgeReviewResponse(
        processing_run_id=str(result.processing_run.processing_run_id),
        model_signature_id=str(result.model_signature.model_signature_id),
        ready_to_accept=not blocked,
        blocked_reason=("canonical_merge_candidates" if blocked else None),
        preflight_digest=(None if blocked else _dedup_plan_digest(plan)),
        knowledge_decisions=tuple(
            _dedup_decision_response(item) for item in plan.knowledge
        ),
        claim_decisions=tuple(
            _dedup_decision_response(item) for item in plan.claims
        ),
        canonical_merge_candidates=tuple(
            _canonical_merge_review_response(
                candidate_index=index,
                candidate=candidate,
                review_id=review_ids[index],
            )
            for index, candidate in enumerate(plan.merge_candidates)
        ),
    )


def _knowledge_merge_review_response(
    item: ReviewItem,
    details: MergeReviewDetails,
) -> KnowledgeMergeReviewResponse:
    if item.review_id != details.review_id:
        raise RuntimeError("Knowledge merge-review identity mismatch.")
    return KnowledgeMergeReviewResponse(
        review_id=str(item.review_id),
        status=item.status.value,
        proposal_type=details.proposal_type.value,
        proposal_index=details.proposal_index,
        source_entity_id=str(details.source_entity_id),
        source_revision_id=str(details.source_revision_id),
        proposal_text=details.proposal_text,
        proposal_kind=details.proposal_kind,
        proposal_epistemic_status=details.proposal_epistemic_status,
        similarity=details.similarity,
        decision=details.decision,
        existing_entity_id=str(details.existing_entity_id),
        existing_revision_id=str(details.existing_revision_id),
    )


def _chat_summary(summary: ChatSummary) -> ChatSummaryResponse:
    return ChatSummaryResponse(
        chat_id=str(summary.chat_id),
        started_at_us=summary.started_at_us,
        ended_at_us=summary.ended_at_us,
        archive_mode=summary.archive_mode,
        lifecycle_state=summary.lifecycle_state,
        message_count=summary.message_count,
        pinned=summary.pinned,
    )


def _chat_message(message: ChatMessage) -> ChatMessageResponse:
    content = message.content
    if (
        message.message_type.value == "assistant"
        and content is not None
    ):
        content = strip_durable_provenance_manifest(content)

    return ChatMessageResponse(
        message_id=str(message.message_id),
        chat_id=str(message.chat_id),
        sequence_no=message.sequence_no,
        message_type=message.message_type.value,
        actor_id=None if message.actor_id is None else str(message.actor_id),
        created_at_us=message.created_at_us,
        revision_id=str(message.revision_id),
        content=content,
        content_format=message.content_format,
        source_ids=tuple(str(source_id) for source_id in message.source_ids),
    )


def _chat_thread(thread: ChatThread) -> ChatThreadResponse:
    return ChatThreadResponse(
        chat_id=str(thread.chat_id),
        started_at_us=thread.started_at_us,
        ended_at_us=thread.ended_at_us,
        archive_mode=thread.archive_mode,
        lifecycle_state=thread.lifecycle_state,
        messages=tuple(_chat_message(message) for message in thread.messages),
    )


def _grounded_chat_response(
    result: UnifiedLocalChatResult,
    thread: ChatThread,
) -> GroundedChatResponse:
    report = result.generation.grounding_report
    if report is None:
        raise RuntimeError(
            "Unified Local chat completed without a grounding report."
        )
    if report.invalid_context_ids:
        raise RuntimeError(
            "Unified Local chat produced invalid grounding references."
        )

    assistant = result.generation.assistant_message
    if assistant.chat_id != thread.chat_id:
        raise RuntimeError(
            "Grounded assistant message belongs to another chat."
        )
    if assistant.content is None:
        raise RuntimeError(
            "Grounded assistant message has no persisted content."
        )
    if not any(
        item.message_id == assistant.message_id
        and item.revision_id == assistant.revision_id
        for item in thread.messages
    ):
        raise RuntimeError(
            "Grounded assistant message is missing from persisted chat."
        )

    assistant_text = strip_durable_provenance_manifest(
        assistant.content
    ).strip()
    if not assistant_text:
        raise RuntimeError(
            "Grounded assistant display projection must not be blank."
        )

    cited_context_ids = tuple(report.cited_context_ids)
    cited = set(cited_context_ids)
    if len(cited) != len(cited_context_ids):
        raise RuntimeError(
            "Grounding report contains duplicate cited context IDs."
        )

    evidence: list[GroundedEvidenceResponse] = []

    for context_item in result.memory_context.items:
        classification = result.evidence_selection.classification_for(
            entity_type=context_item.entity_type,
            entity_id=context_item.entity_id,
            revision_id=context_item.revision_id,
        )
        evidence.append(
            GroundedEvidenceResponse(
                context_id=context_item.context_id,
                evidence_class=classification.evidence_class.value,
                entity_type=context_item.entity_type.value,
                entity_id=str(context_item.entity_id),
                revision_id=str(context_item.revision_id),
                title=context_item.title,
                text=context_item.text,
                cited=context_item.context_id in cited,
                epistemic_status=(
                    None
                    if classification.epistemic_status is None
                    else classification.epistemic_status.value
                ),
                source_id=None,
                representation_id=None,
                source_name=None,
                source_uri=None,
                start_offset=None,
                end_offset=None,
                page_start=None,
                page_end=None,
                quoted_sha256=None,
                truncated=context_item.truncated,
            )
        )

    for source_item in result.source_context.items:
        evidence.append(
            GroundedEvidenceResponse(
                context_id=source_item.context_id,
                evidence_class="source",
                entity_type="source_anchor",
                entity_id=str(source_item.anchor_id),
                revision_id=None,
                title=source_item.source_name,
                text=source_item.text,
                cited=source_item.context_id in cited,
                epistemic_status=None,
                source_id=str(source_item.source_id),
                representation_id=str(source_item.representation_id),
                source_name=source_item.source_name,
                source_uri=source_item.source_uri,
                start_offset=source_item.start_offset,
                end_offset=source_item.end_offset,
                page_start=source_item.page_start,
                page_end=source_item.page_end,
                quoted_sha256=source_item.quoted_hash.hex(),
                truncated=source_item.truncated,
            )
        )

    evidence_ids = tuple(item.context_id for item in evidence)
    if len(set(evidence_ids)) != len(evidence_ids):
        raise RuntimeError(
            "Unified Local chat produced duplicate evidence context IDs."
        )
    if not cited.issubset(evidence_ids):
        raise RuntimeError(
            "Grounding report cites evidence missing from transport output."
        )

    evidence_class_by_id = {
        item.context_id: item.evidence_class
        for item in evidence
    }
    typed_groups = (
        (report.canonical_context_ids, "canonical"),
        (report.user_statement_context_ids, "user_statement"),
        (report.conversation_context_ids, "conversation_record"),
        (report.source_context_ids, "source"),
        (report.research_context_ids, "research"),
        (report.news_context_ids, "news"),
    )
    for context_ids, expected_class in typed_groups:
        for context_id in context_ids:
            if evidence_class_by_id.get(context_id) != expected_class:
                raise RuntimeError(
                    "Grounding evidence class disagrees with transport evidence."
                )

    return GroundedChatResponse(
        thread=_chat_thread(thread),
        assistant_text=assistant_text,
        evidence=tuple(evidence),
        personal_memory=tuple(
            GroundedMemoryResponse(
                context_id=item.context_id,
                memory_id=str(item.memory_id),
                revision_id=str(item.revision_id),
                memory_kind=item.memory_kind,
                scope_kind=item.scope_kind,
                scope_entity_id=(
                    None
                    if item.scope_entity_id is None
                    else str(item.scope_entity_id)
                ),
                content=item.content,
            )
            for item in result.memory_context.memory_items
        ),
        grounding=GroundingResponse(
            cited_context_ids=cited_context_ids,
            canonical_context_ids=tuple(
                report.canonical_context_ids
            ),
            user_statement_context_ids=tuple(
                report.user_statement_context_ids
            ),
            conversation_context_ids=tuple(
                report.conversation_context_ids
            ),
            source_context_ids=tuple(report.source_context_ids),
            research_context_ids=tuple(
                report.research_context_ids
            ),
            news_context_ids=tuple(report.news_context_ids),
            invalid_context_ids=tuple(
                report.invalid_context_ids
            ),
            uses_inference=report.uses_inference,
            uses_model_prior=report.uses_model_prior,
            uses_unknown=report.uses_unknown,
            has_provenance_marker=report.has_provenance_marker,
        ),
        processing_run_id=str(
            result.processing_run.processing_run_id
        ),
        model_id=result.generation.model.backend_model_id,
        embedding_model_id=(
            None
            if result.embedding_model is None
            else result.embedding_model.backend_model_id
        ),
    )


def _deletion_preview(preview: DeletionPreview) -> DeletionPreviewResponse:
    return DeletionPreviewResponse(
        entity_id=str(preview.entity_id),
        entity_type=preview.entity_type,
        lifecycle_state=preview.lifecycle_state,
        dependencies=tuple(
            DeletionDependencyResponse(
                relation=item.relation,
                count=item.count,
                dependent_entity_id=(
                    None
                    if item.dependent_entity_id is None
                    else str(item.dependent_entity_id)
                ),
                dependent_entity_type=item.dependent_entity_type,
            )
            for item in preview.dependencies
        ),
        preview_digest=preview.preview_digest,
    )


def _deletion_result(result: DeletionResult) -> DeletionResultResponse:
    return DeletionResultResponse(
        entity_id=str(result.entity_id),
        entity_type=result.entity_type,
        commit_id=str(result.commit_id),
        deleted_entity_ids=tuple(str(item) for item in result.deleted_entity_ids),
        preview_digest=result.preview_digest,
    )


def _lifecycle_transition(
    result: LifecycleTransitionResult,
) -> LifecycleTransitionResponse:
    return LifecycleTransitionResponse(
        entity_id=str(result.entity_id),
        entity_type=result.entity_type,
        lifecycle_state=result.lifecycle_state,
        commit_id=str(result.commit_id),
        affected_entity_ids=tuple(str(item) for item in result.affected_entity_ids),
    )


def _news_profile_response(profile: dict[str, Any]) -> NewsProfileResponse:
    timezone_name = profile.get("timezone_name")
    local_hour = profile.get("local_hour")
    local_minute = profile.get("local_minute")
    enabled = profile.get("enabled")
    if not isinstance(timezone_name, str) or not timezone_name.strip():
        raise RuntimeError("News profile returned an invalid timezone.")
    if isinstance(local_hour, bool) or not isinstance(local_hour, int) or not 0 <= local_hour <= 23:
        raise RuntimeError("News profile returned an invalid hour.")
    if isinstance(local_minute, bool) or not isinstance(local_minute, int) or not 0 <= local_minute <= 59:
        raise RuntimeError("News profile returned an invalid minute.")
    if isinstance(enabled, bool):
        enabled_value = enabled
    elif isinstance(enabled, int) and enabled in {0, 1}:
        enabled_value = bool(enabled)
    else:
        raise RuntimeError("News profile returned an invalid enabled state.")
    return NewsProfileResponse(
        api_version=API_VERSION,
        enabled=enabled_value,
        timezone_name=timezone_name,
        local_hour=local_hour,
        local_minute=local_minute,
    )


def _model(model: ModelInfo) -> ModelResponse:
    return ModelResponse(
        provider=model.provider,
        backend_model_id=model.backend_model_id,
        display_name=model.display_name,
        model_type=model.model_type,
        context_capacity=model.context_capacity,
        quantization=model.quantization,
        loaded=model.loaded,
        vision=model.vision,
        trained_for_tool_use=model.trained_for_tool_use,
        loaded_context_length=model.loaded_context_length,
    )
