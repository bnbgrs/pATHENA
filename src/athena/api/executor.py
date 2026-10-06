"""Single-owner execution boundary for the long-lived ATHENA Core process."""

from __future__ import annotations

import threading
from concurrent.futures import Future
from queue import Queue
from typing import Callable, TypeVar, cast

from athena.api.contracts import (
    CapabilitiesResponse,
    ChatLifecycleTransitionResponse,
    ChatOperationRecoveryResponse,
    ChatSummaryResponse,
    ChatThreadResponse,
    DeletionPreviewResponse,
    DeletionResultResponse,
    GroundedChatResponse,
    HealthResponse,
    ImageSourceResponse,
    KnowledgeMergeReviewResponse,
    KnowledgeReviewResponse,
    MessageKnowledgeExtractionResponse,
    ModelResponse,
    NewsProfileResponse,
    ProviderHealthResponse,
    RememberedChatMessageResponse,
    StorageHealthResponse,
)
from athena.api.ports import CoreDomainSurface
from athena.api.search_contracts import SearchResultResponse
from athena.chat.cancellation import (
    ChatCancellationReservation,
    ChatOperationActiveError,
)
from athena.core.application import ApplicationState, AthenaApplication
from athena.retrieval.universal import UniversalSearchEntityType

_ResultT = TypeVar("_ResultT")
_QueuedCall = tuple[Callable[[], object], Future[object]] | None


class CoreDomainExecutorError(RuntimeError):
    """Raised when the dedicated Core owner thread cannot execute safely."""


class CoreDomainExecutor:
    """Own ATHENA startup, SQLite, domain calls, and shutdown on one thread."""

    def __init__(self, app: AthenaApplication) -> None:
        self.app = app
        self._queue: Queue[_QueuedCall] = Queue()
        self._submission_lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._thread_id: int | None = None
        self._shutdown_error: BaseException | None = None
        self._accepting = False

    @property
    def running(self) -> bool:
        thread = self._thread
        return (
            thread is not None
            and thread.is_alive()
            and self._accepting
            and self.app.state is ApplicationState.RUNNING
        )

    @property
    def thread_id(self) -> int | None:
        return self._thread_id

    def start(self) -> None:
        if self.running:
            return
        if self._thread is not None:
            raise CoreDomainExecutorError(
                "ATHENA Core owner thread startup is already in progress."
            )

        self._shutdown_error = None
        startup_result: Queue[BaseException | None] = Queue(maxsize=1)

        thread = threading.Thread(
            target=self._run,
            args=(startup_result,),
            name="athena-core-domain-owner",
            daemon=False,
        )
        self._thread = thread
        thread.start()

        startup_error = startup_result.get()
        if startup_error is not None:
            thread.join()
            self._thread = None
            self._thread_id = None
            raise CoreDomainExecutorError(
                "ATHENA Core owner thread could not start."
            ) from startup_error

        if not self.running:
            self.stop()
            raise CoreDomainExecutorError(
                "ATHENA Core owner thread exited during startup."
            )

    def call(self, callback: Callable[[], _ResultT]) -> _ResultT:
        if threading.get_ident() == self._thread_id:
            return callback()

        future: Future[object] = Future()
        with self._submission_lock:
            if not self._accepting:
                raise CoreDomainExecutorError(
                    "ATHENA Core owner thread is not accepting API work."
                )
            self._queue.put((cast(Callable[[], object], callback), future))

        return cast(_ResultT, future.result())

    def stop(self) -> None:
        thread = self._thread
        if thread is None:
            return

        with self._submission_lock:
            if self._accepting:
                self._accepting = False
                self._queue.put(None)

        if threading.get_ident() == self._thread_id:
            raise CoreDomainExecutorError(
                "ATHENA Core owner thread cannot synchronously join itself."
            )

        thread.join()
        self._thread = None
        self._thread_id = None

        shutdown_error = self._shutdown_error
        self._shutdown_error = None
        if shutdown_error is not None:
            raise CoreDomainExecutorError(
                "ATHENA Core owner thread did not stop cleanly."
            ) from shutdown_error

    def _run(
        self,
        startup_result: Queue[BaseException | None],
    ) -> None:
        self._thread_id = threading.get_ident()

        try:
            self.app.start()
        except BaseException as exc:
            try:
                if self.app.state is not ApplicationState.STOPPED:
                    self.app.stop()
            except BaseException as stop_exc:
                self._shutdown_error = stop_exc
            finally:
                startup_result.put(exc)
            return

        with self._submission_lock:
            self._accepting = True
        startup_result.put(None)

        try:
            while True:
                item = self._queue.get()
                if item is None:
                    break

                callback, future = item
                if not future.set_running_or_notify_cancel():
                    continue

                try:
                    result = callback()
                except BaseException as exc:
                    future.set_exception(exc)
                else:
                    future.set_result(result)
        finally:
            try:
                if self.app.state is not ApplicationState.STOPPED:
                    self.app.stop()
            except BaseException as exc:
                self._shutdown_error = exc
            finally:
                with self._submission_lock:
                    self._accepting = False


class SerializedCoreApiSurface:
    """Dispatch every Core API operation onto its single owner thread."""

    def __init__(
        self,
        surface: CoreDomainSurface,
        executor: CoreDomainExecutor,
        *,
        storage_health: Callable[[], StorageHealthResponse] | None = None,
    ) -> None:
        self._surface = surface
        self._executor = executor
        self._storage_health = storage_health

    def health(self) -> HealthResponse:
        return self._executor.call(self._surface.health)

    def storage_health(self) -> StorageHealthResponse:
        callback = self._storage_health
        if callback is None:
            raise CoreDomainExecutorError(
                "ATHENA Core storage health telemetry is not configured."
            )
        return self._executor.call(callback)

    def capabilities(self) -> CapabilitiesResponse:
        return self._executor.call(self._surface.capabilities)

    def news_profile(self) -> NewsProfileResponse:
        return self._executor.call(self._surface.news_profile)

    def configure_news_schedule(
        self,
        *,
        timezone_name: str,
        local_hour: int,
        local_minute: int,
    ) -> NewsProfileResponse:
        return self._executor.call(
            lambda: self._surface.configure_news_schedule(
                timezone_name=timezone_name,
                local_hour=local_hour,
                local_minute=local_minute,
            )
        )

    def list_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        return self._executor.call(
            lambda: self._surface.list_chats(limit=limit, offset=offset)
        )

    def list_trashed_chats(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[ChatSummaryResponse, ...]:
        return self._executor.call(
            lambda: self._surface.list_trashed_chats(limit=limit, offset=offset)
        )

    def set_chat_pinned(
        self,
        chat_id: str,
        *,
        pinned: bool,
    ) -> ChatSummaryResponse:
        return self._executor.call(
            lambda: self._surface.set_chat_pinned(
                chat_id,
                pinned=pinned,
            )
        )

    def create_chat(self, chat_id: str | None = None) -> ChatThreadResponse:
        if chat_id is None:
            return self._executor.call(self._surface.create_chat)
        return self._executor.call(lambda: self._surface.create_chat(chat_id))

    def capture_image_source(
        self,
        *,
        data: bytes,
        original_name: str,
        source_uri: str,
    ) -> ImageSourceResponse:
        return self._executor.call(
            lambda: self._surface.capture_image_source(
                data=data,
                original_name=original_name,
                source_uri=source_uri,
            )
        )

    def load_chat(self, chat_id: str) -> ChatThreadResponse:
        return self._executor.call(lambda: self._surface.load_chat(chat_id))

    def edit_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        expected_revision_id: str,
        content: str,
    ) -> ChatThreadResponse:
        return self._executor.call(
            lambda: self._surface.edit_chat_message(
                chat_id,
                message_id,
                expected_revision_id=expected_revision_id,
                content=content,
            )
        )

    def fork_chat_from_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> ChatThreadResponse:
        return self._executor.call(
            lambda: self._surface.fork_chat_from_message(
                chat_id,
                message_id,
                revision_id=revision_id,
            )
        )

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
        if operation_id is None:
            return self._executor.call(
                lambda: self._surface.regenerate_chat_message(
                    chat_id,
                    message_id,
                    revision_id=revision_id,
                    requested_model_id=requested_model_id,
                    operation_id=None,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )

        reservation = self._surface.reserve_chat_operation(operation_id)
        if reservation is None:
            raise ChatOperationActiveError(
                "The chat regeneration operation is already active."
            )
        try:
            return self._executor.call(
                lambda: self._surface.regenerate_chat_message(
                    chat_id,
                    message_id,
                    revision_id=revision_id,
                    requested_model_id=requested_model_id,
                    operation_id=operation_id,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )
        finally:
            self._surface.release_chat_operation(reservation)

    def provider_health(self) -> ProviderHealthResponse:
        return self._executor.call(self._surface.provider_health)

    def remember_chat_message(
        self,
        chat_id: str,
        message_id: str,
        *,
        revision_id: str,
    ) -> RememberedChatMessageResponse:
        return self._executor.call(
            lambda: self._surface.remember_chat_message(
                chat_id,
                message_id,
                revision_id=revision_id,
            )
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
        return self._executor.call(
            lambda: self._surface.extract_chat_message_knowledge(
                chat_id,
                message_id,
                revision_id=revision_id,
                requested_model_id=requested_model_id,
                effective_context_limit=effective_context_limit,
                max_output_tokens=max_output_tokens,
            )
        )

    def prepare_knowledge_review(self, processing_run_id: str) -> KnowledgeReviewResponse:
        return self._executor.call(
            lambda: self._surface.prepare_knowledge_review(processing_run_id)
        )

    def load_knowledge_merge_review(
        self,
        review_id: str,
    ) -> KnowledgeMergeReviewResponse:
        return self._executor.call(
            lambda: self._surface.load_knowledge_merge_review(review_id)
        )

    def resolve_knowledge_merge_review(
        self,
        review_id: str,
        *,
        decision: str,
    ) -> KnowledgeMergeReviewResponse:
        return self._executor.call(
            lambda: self._surface.resolve_knowledge_merge_review(
                review_id,
                decision=decision,
            )
        )

    def trash_chat(self, chat_id: str) -> ChatLifecycleTransitionResponse:
        return self._executor.call(lambda: self._surface.trash_chat(chat_id))

    def restore_chat(self, chat_id: str) -> ChatLifecycleTransitionResponse:
        return self._executor.call(lambda: self._surface.restore_chat(chat_id))

    def preview_chat_deletion(self, chat_id: str) -> DeletionPreviewResponse:
        return self._executor.call(lambda: self._surface.preview_chat_deletion(chat_id))

    def delete_chat(
        self,
        chat_id: str,
        *,
        preview_digest: str,
    ) -> DeletionResultResponse:
        return self._executor.call(
            lambda: self._surface.delete_chat(
                chat_id,
                preview_digest=preview_digest,
            )
        )

    def list_models(self) -> tuple[ModelResponse, ...]:
        return self._executor.call(self._surface.list_models)

    def universal_search(
        self,
        query: str,
        *,
        limit: int = 20,
        entity_types: tuple[UniversalSearchEntityType, ...] | None = None,
    ) -> tuple[SearchResultResponse, ...]:
        return self._executor.call(
            lambda: self._surface.universal_search(
                query,
                limit=limit,
                entity_types=entity_types,
            )
        )

    def reserve_chat_operation(
        self,
        operation_id: str,
    ) -> ChatCancellationReservation | None:
        """Reserve only thread-safe cancellation state outside the owner queue."""
        return self._surface.reserve_chat_operation(operation_id)

    def release_chat_operation(
        self,
        reservation: ChatCancellationReservation,
    ) -> None:
        """Release one exact control-plane reservation outside the owner queue."""
        self._surface.release_chat_operation(reservation)

    def cancel_chat_operation(self, operation_id: str) -> bool:
        """Signal cancellation without waiting behind owner-thread generation."""
        return self._surface.cancel_chat_operation(operation_id)

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
        if operation_id is None:
            if (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_source_ids=image_source_ids,
                    )
                )
            if (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_source_ids=image_source_ids,
                        effective_context_limit=effective_context_limit,
                    )
                )
            return self._executor.call(
                lambda: self._surface.send_chat_message(
                    chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )

        reservation = self._surface.reserve_chat_operation(operation_id)
        if reservation is None:
            raise ChatOperationActiveError(
                "The chat send operation is already active."
            )

        try:
            if (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_source_ids=image_source_ids,
                        operation_id=operation_id,
                    )
                )
            if (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        image_source_ids=image_source_ids,
                        operation_id=operation_id,
                        effective_context_limit=effective_context_limit,
                    )
                )
            return self._executor.call(
                lambda: self._surface.send_chat_message(
                    chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    operation_id=operation_id,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )
        finally:
            self._surface.release_chat_operation(reservation)

    def chat_operation_recovery(
        self,
        chat_id: str,
        operation_id: str,
    ) -> ChatOperationRecoveryResponse:
        return self._executor.call(
            lambda: self._surface.chat_operation_recovery(
                chat_id,
                operation_id,
            )
        )

    def continue_unified_local_chat_operation(
        self,
        chat_id: str,
        operation_id: str,
    ) -> GroundedChatResponse:
        reservation = self._surface.reserve_chat_operation(operation_id)
        if reservation is None:
            raise ChatOperationActiveError(
                "The chat send operation is already active."
            )
        try:
            return self._executor.call(
                lambda: self._surface.continue_unified_local_chat_operation(
                    chat_id,
                    operation_id,
                )
            )
        finally:
            self._surface.release_chat_operation(reservation)

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
        if operation_id is None:
            if (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_unified_local_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                    )
                )
            if (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_unified_local_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                        effective_context_limit=effective_context_limit,
                    )
                )
            return self._executor.call(
                lambda: self._surface.send_unified_local_chat_message(
                    chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    requested_embedding_model_id=requested_embedding_model_id,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )

        reservation = self._surface.reserve_chat_operation(operation_id)
        if reservation is None:
            raise ChatOperationActiveError(
                "The chat send operation is already active."
            )

        try:
            if (
                effective_context_limit is None
                and max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_unified_local_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                        operation_id=operation_id,
                    )
                )
            if (
                max_output_tokens is None
                and temperature is None
                and thinking_enabled is None
            ):
                return self._executor.call(
                    lambda: self._surface.send_unified_local_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=requested_model_id,
                        requested_embedding_model_id=requested_embedding_model_id,
                        operation_id=operation_id,
                        effective_context_limit=effective_context_limit,
                    )
                )
            return self._executor.call(
                lambda: self._surface.send_unified_local_chat_message(
                    chat_id,
                    content=content,
                    requested_model_id=requested_model_id,
                    requested_embedding_model_id=requested_embedding_model_id,
                    operation_id=operation_id,
                    effective_context_limit=effective_context_limit,
                    max_output_tokens=max_output_tokens,
                    temperature=temperature,
                    thinking_enabled=thinking_enabled,
                )
            )
        finally:
            self._surface.release_chat_operation(reservation)
