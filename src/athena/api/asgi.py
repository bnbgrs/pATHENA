"""Minimal versioned ASGI transport for the local ATHENA Core API."""

from __future__ import annotations

import base64
import binascii
import json
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, cast
from urllib.parse import parse_qs

from athena.api.contracts import ApiContract, JsonValue
from athena.api.ports import CoreApiSurface
from athena.api.runtime import LocalApiRuntime
from athena.api.service import (
    ChatMessageNotFoundError,
    ChatMessageRevisionMismatchError,
    KnowledgeReviewConflictError,
    KnowledgeReviewNotFoundError,
)
from athena.chat import repository as chat_repository
from athena.chat.cancellation import ChatOperationActiveError
from athena.chat.generation import GenerationCancelledError
from athena.chat.send_identity import (
    SendOperationState,
    SendOperationStateError,
)
from athena.chat.unified import UnifiedGroundedRecoveryRequiredError
from athena.chat.unified_replay import UnifiedReplayProjectionError
from athena.lifecycle.service import (
    LifecycleDeletionAlreadyDeletedError,
    LifecycleDeletionNotFoundError,
    LifecycleDeletionPreviewStaleError,
    LifecycleDeletionUnsupportedError,
    LifecycleTransitionStateError,
)
from athena.model.adapters.lm_studio import ProviderOutputLimitError
from athena.retrieval.universal import UniversalSearchEntityType

AsgiMessage = dict[str, Any]
AsgiScope = dict[str, Any]
AsgiReceive = Callable[[], Awaitable[AsgiMessage]]
AsgiSend = Callable[[AsgiMessage], Awaitable[None]]

_JSON_HEADERS = ((b"content-type", b"application/json; charset=utf-8"),)
_MAX_JSON_BODY_BYTES = 64 * 1024
_MAX_IMAGE_CAPTURE_JSON_BYTES = 17 * 1024 * 1024
_MAX_IMAGE_BYTES = 12 * 1024 * 1024


class CoreApiAsgiApp:
    """Small authenticated ASGI surface around :class:`CoreApiFacade`."""

    def __init__(
        self,
        *,
        facade: CoreApiSurface,
        runtime: LocalApiRuntime,
        allow_shutdown: bool = False,
    ) -> None:
        self._facade = facade
        self._runtime = runtime
        self._allow_shutdown = allow_shutdown

    async def __call__(
        self,
        scope: AsgiScope,
        receive: AsgiReceive,
        send: AsgiSend,
    ) -> None:
        if scope.get("type") != "http":
            await _send_problem(
                send,
                status=400,
                code="unsupported_transport",
                message="This ATHENA API endpoint accepts HTTP requests only.",
            )
            return

        request_id = str(uuid.uuid4())
        headers = _headers(scope)

        # Native desktop clients do not need browser Origin semantics. Reject
        # browser-originated requests by default rather than enabling wildcard
        # CORS or accidentally creating a localhost-CSRF surface.
        if "origin" in headers:
            await _send_problem(
                send,
                status=403,
                code="browser_origin_rejected",
                message="Browser-originated access is not enabled for this local ATHENA API.",
                request_id=request_id,
            )
            return

        token = _bearer_token(headers.get("authorization"))
        if token is None or not self._runtime.authenticate(token):
            await _send_problem(
                send,
                status=401,
                code="unauthorized",
                message="A valid local ATHENA session token is required.",
                request_id=request_id,
                extra_headers=((b"www-authenticate", b"Bearer"),),
            )
            return

        method = str(scope.get("method", "GET")).upper()
        path = str(scope.get("path", ""))

        try:
            if method == "GET" and path == "/api/v1/health":
                await _send_contract(send, self._facade.health(), request_id=request_id)
                return

            if method == "POST" and path == "/api/v1/sources/images":
                payload = await _read_json_object(
                    receive,
                    max_bytes=_MAX_IMAGE_CAPTURE_JSON_BYTES,
                )
                unknown = set(payload) - {
                    "data_base64",
                    "original_name",
                    "source_uri",
                }
                if unknown:
                    raise ValueError(
                        "Image capture request contains unsupported fields."
                    )
                encoded = payload.get("data_base64")
                original_name = payload.get("original_name")
                source_uri = payload.get("source_uri")
                if not isinstance(encoded, str) or not encoded:
                    raise ValueError("Image capture data_base64 must be non-empty text.")
                if not isinstance(original_name, str) or not original_name.strip():
                    raise ValueError("Image capture original_name must be non-empty text.")
                if not isinstance(source_uri, str) or not source_uri.strip():
                    raise ValueError("Image capture source_uri must be non-empty text.")
                try:
                    image_bytes = base64.b64decode(encoded, validate=True)
                except (binascii.Error, ValueError) as exc:
                    raise ValueError("Image capture data_base64 is invalid.") from exc
                if not image_bytes:
                    raise ValueError("Image capture data must not be empty.")
                if len(image_bytes) > _MAX_IMAGE_BYTES:
                    raise ValueError("Image capture exceeds the 12 MiB limit.")
                await _send_contract(
                    send,
                    self._facade.capture_image_source(
                        data=image_bytes,
                        original_name=original_name.strip(),
                        source_uri=source_uri.strip(),
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/storage/health":
                await _send_contract(
                    send,
                    self._facade.storage_health(),
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/capabilities":
                await _send_contract(send, self._facade.capabilities(), request_id=request_id)
                return

            if method == "GET" and path == "/api/v1/search":
                query, limit, entity_types = _universal_search_query(scope)
                await _send_json(
                    send,
                    status=200,
                    payload={
                        "items": [
                            item.to_dict()
                            for item in self._facade.universal_search(
                                query,
                                limit=limit,
                                entity_types=entity_types,
                            )
                        ]
                    },
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/news/profile":
                await _send_contract(
                    send,
                    self._facade.news_profile(),
                    request_id=request_id,
                )
                return

            if method == "PUT" and path == "/api/v1/news/profile":
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"timezone_name", "local_hour", "local_minute"}
                if unknown:
                    raise ValueError("News profile request contains unsupported fields.")
                timezone_name = payload.get("timezone_name")
                local_hour = payload.get("local_hour")
                local_minute = payload.get("local_minute")
                if not isinstance(timezone_name, str) or not timezone_name.strip():
                    raise ValueError("News timezone_name must be non-empty text.")
                if isinstance(local_hour, bool) or not isinstance(local_hour, int):
                    raise ValueError("News local_hour must be an integer.")
                if isinstance(local_minute, bool) or not isinstance(local_minute, int):
                    raise ValueError("News local_minute must be an integer.")
                await _send_contract(
                    send,
                    self._facade.configure_news_schedule(
                        timezone_name=timezone_name,
                        local_hour=local_hour,
                        local_minute=local_minute,
                    ),
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/chats":
                limit = _positive_limit(
                    scope,
                    default=50,
                    maximum=200,
                )
                offset = _nonnegative_offset(
                    scope,
                    default=0,
                )
                await _send_json(
                    send,
                    status=200,
                    payload={
                        "items": [
                            item.to_dict()
                            for item in self._facade.list_chats(
                                limit=limit,
                                offset=offset,
                            )
                        ]
                    },
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/chats/trash":
                limit = _positive_limit(
                    scope,
                    default=50,
                    maximum=200,
                )
                offset = _nonnegative_offset(
                    scope,
                    default=0,
                )
                await _send_json(
                    send,
                    status=200,
                    payload={
                        "items": [
                            item.to_dict()
                            for item in self._facade.list_trashed_chats(
                                limit=limit,
                                offset=offset,
                            )
                        ]
                    },
                    request_id=request_id,
                )
                return

            if method == "POST" and path == "/api/v1/chats":
                await _consume_empty_body(receive)
                await _send_contract(
                    send,
                    self._facade.create_chat(),
                    status=201,
                    request_id=request_id,
                )
                return

            if (
                method == "PUT"
                and path.startswith("/api/v1/chats/")
                and path.endswith("/pin")
            ):
                chat_id = path.removeprefix("/api/v1/chats/").removesuffix("/pin")
                chat_id = chat_id.removesuffix("/")
                if not chat_id or "/" in chat_id:
                    raise ValueError("Invalid chat pin resource path.")
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"pinned"}
                if unknown:
                    raise ValueError("Chat pin request contains unsupported fields.")
                pinned = payload.get("pinned")
                if not isinstance(pinned, bool):
                    raise ValueError("Chat pin state must be boolean.")
                await _send_contract(
                    send,
                    self._facade.set_chat_pinned(chat_id, pinned=pinned),
                    request_id=request_id,
                )
                return

            if (
                method == "PUT"
                and path.startswith("/api/v1/chats/")
            ):
                chat_id = path.removeprefix(
                    "/api/v1/chats/"
                )

                if not chat_id or "/" in chat_id:
                    raise ValueError(
                        "Invalid chat creation resource path."
                    )

                await _consume_empty_body(
                    receive
                )

                await _send_contract(
                    send,
                    self._facade.create_chat(
                        chat_id
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            trash_chat_id = _single_resource_id(
                path,
                prefix="/api/v1/chats/",
                suffix="/trash",
            )
            if method == "POST" and trash_chat_id is not None:
                await _consume_empty_body(receive)
                try:
                    trash_chat_id = str(uuid.UUID(trash_chat_id))
                except ValueError as exc:
                    raise ValueError("Chat ID must be a valid UUID.") from exc
                await _send_contract(
                    send,
                    self._facade.trash_chat(trash_chat_id),
                    request_id=request_id,
                )
                return

            restore_chat_id = _single_resource_id(
                path,
                prefix="/api/v1/chats/",
                suffix="/restore",
            )
            if method == "POST" and restore_chat_id is not None:
                await _consume_empty_body(receive)
                try:
                    restore_chat_id = str(uuid.UUID(restore_chat_id))
                except ValueError as exc:
                    raise ValueError("Chat ID must be a valid UUID.") from exc
                await _send_contract(
                    send,
                    self._facade.restore_chat(restore_chat_id),
                    request_id=request_id,
                )
                return

            edit_resource = _message_action_resource(path, action="edit")
            if method == "PATCH" and edit_resource is not None:
                chat_id, message_id = edit_resource
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"expected_revision_id", "content"}
                if unknown:
                    raise ValueError(
                        "Chat edit request contains unsupported fields."
                    )
                expected_revision_id = payload.get("expected_revision_id")
                if (
                    not isinstance(expected_revision_id, str)
                    or not expected_revision_id.strip()
                ):
                    raise ValueError(
                        "Chat edit expected_revision_id must be a non-empty UUID string."
                    )
                try:
                    expected_revision_id = str(uuid.UUID(expected_revision_id))
                except ValueError as exc:
                    raise ValueError(
                        "Chat edit expected_revision_id must be a valid UUID."
                    ) from exc
                content = payload.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise ValueError(
                        "Edited chat content must contain non-whitespace text."
                    )
                await _send_contract(
                    send,
                    self._facade.edit_chat_message(
                        chat_id,
                        message_id,
                        expected_revision_id=expected_revision_id,
                        content=content,
                    ),
                    request_id=request_id,
                )
                return

            fork_resource = _message_action_resource(path, action="fork")
            if method == "POST" and fork_resource is not None:
                chat_id, message_id = fork_resource
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"revision_id"}
                if unknown:
                    raise ValueError(
                        "Chat fork request contains unsupported fields."
                    )
                revision_id = payload.get("revision_id")
                if not isinstance(revision_id, str) or not revision_id.strip():
                    raise ValueError(
                        "Chat fork revision_id must be a non-empty UUID string."
                    )
                try:
                    revision_id = str(uuid.UUID(revision_id))
                except ValueError as exc:
                    raise ValueError(
                        "Chat fork revision_id must be a valid UUID."
                    ) from exc
                await _send_contract(
                    send,
                    self._facade.fork_chat_from_message(
                        chat_id,
                        message_id,
                        revision_id=revision_id,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            regenerate_resource = _message_action_resource(path, action="regenerate")
            if method == "POST" and regenerate_resource is not None:
                chat_id, message_id = regenerate_resource
                payload = await _read_json_object(receive)
                unknown = set(payload) - {
                    "revision_id",
                    "model_id",
                    "operation_id",
                    "effective_context_limit",
                    "max_output_tokens",
                    "temperature",
                    "thinking_enabled",
                }
                if unknown:
                    raise ValueError(
                        "Chat regenerate request contains unsupported fields."
                    )
                revision_id = payload.get("revision_id")
                if not isinstance(revision_id, str) or not revision_id.strip():
                    raise ValueError(
                        "Chat regenerate revision_id must be a non-empty UUID string."
                    )
                try:
                    revision_id = str(uuid.UUID(revision_id))
                except ValueError as exc:
                    raise ValueError(
                        "Chat regenerate revision_id must be a valid UUID."
                    ) from exc
                model_id = payload.get("model_id")
                if model_id is not None and (
                    not isinstance(model_id, str) or not model_id.strip()
                ):
                    raise ValueError(
                        "Chat regenerate model_id must be a non-empty string or null."
                    )
                operation_id = payload.get("operation_id")
                if operation_id is not None:
                    if not isinstance(operation_id, str) or not operation_id.strip():
                        raise ValueError(
                            "Chat regenerate operation_id must be a non-empty UUID string or null."
                        )
                    try:
                        operation_id = str(uuid.UUID(operation_id))
                    except ValueError as exc:
                        raise ValueError(
                            "Chat regenerate operation_id must be a valid UUID or null."
                        ) from exc
                effective_context_limit = payload.get("effective_context_limit")
                if effective_context_limit is not None and (
                    isinstance(effective_context_limit, bool)
                    or not isinstance(effective_context_limit, int)
                    or effective_context_limit < 1
                ):
                    raise ValueError(
                        "Chat regenerate effective_context_limit must be positive or null."
                    )
                max_output_tokens = payload.get("max_output_tokens")
                if max_output_tokens is not None and (
                    isinstance(max_output_tokens, bool)
                    or not isinstance(max_output_tokens, int)
                    or max_output_tokens < 1
                ):
                    raise ValueError(
                        "Chat regenerate max_output_tokens must be positive or null."
                    )
                temperature_value = payload.get("temperature")
                if temperature_value is not None and (
                    isinstance(temperature_value, bool)
                    or not isinstance(temperature_value, (int, float))
                    or not 0.0 <= float(temperature_value) <= 2.0
                ):
                    raise ValueError(
                        "Chat regenerate temperature must be between 0.0 and 2.0 or null."
                    )
                temperature = (
                    None if temperature_value is None else float(temperature_value)
                )
                thinking_enabled = payload.get("thinking_enabled")
                if thinking_enabled is not None and not isinstance(
                    thinking_enabled, bool
                ):
                    raise ValueError(
                        "Chat regenerate thinking_enabled must be boolean or null."
                    )
                await _send_contract(
                    send,
                    self._facade.regenerate_chat_message(
                        chat_id,
                        message_id,
                        revision_id=revision_id,
                        requested_model_id=model_id,
                        operation_id=operation_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                        temperature=temperature,
                        thinking_enabled=thinking_enabled,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            remember_resource = _message_action_resource(path, action="remember")
            if method == "POST" and remember_resource is not None:
                chat_id, message_id = remember_resource
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"revision_id"}
                if unknown:
                    raise ValueError(
                        "Remember request contains unsupported fields."
                    )
                revision_id = payload.get("revision_id")
                if not isinstance(revision_id, str) or not revision_id.strip():
                    raise ValueError(
                        "Remember revision_id must be a non-empty string."
                    )
                await _send_contract(
                    send,
                    self._facade.remember_chat_message(
                        chat_id,
                        message_id,
                        revision_id=revision_id,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            extraction_resource = _message_action_resource(
                path,
                action="knowledge-extraction",
            )
            if method == "POST" and extraction_resource is not None:
                chat_id, message_id = extraction_resource
                payload = await _read_json_object(receive)
                unknown = set(payload) - {
                    "revision_id",
                    "model_id",
                    "effective_context_limit",
                    "max_output_tokens",
                }
                if unknown:
                    raise ValueError(
                        "Knowledge extraction request contains unsupported fields."
                    )
                revision_id = payload.get("revision_id")
                if not isinstance(revision_id, str) or not revision_id.strip():
                    raise ValueError(
                        "Knowledge extraction revision_id must be a non-empty string."
                    )
                model_id = payload.get("model_id")
                if model_id is not None and (
                    not isinstance(model_id, str) or not model_id.strip()
                ):
                    raise ValueError(
                        "Knowledge extraction model_id must be a non-empty string or null."
                    )
                effective_context_limit = payload.get("effective_context_limit")
                if effective_context_limit is not None and (
                    isinstance(effective_context_limit, bool)
                    or not isinstance(effective_context_limit, int)
                    or effective_context_limit < 1
                ):
                    raise ValueError(
                        "Knowledge extraction effective_context_limit must be positive or null."
                    )
                max_output_tokens = payload.get("max_output_tokens")
                if max_output_tokens is not None and (
                    isinstance(max_output_tokens, bool)
                    or not isinstance(max_output_tokens, int)
                    or max_output_tokens < 1
                ):
                    raise ValueError(
                        "Knowledge extraction max_output_tokens must be positive or null."
                    )
                await _send_contract(
                    send,
                    self._facade.extract_chat_message_knowledge(
                        chat_id,
                        message_id,
                        revision_id=revision_id,
                        requested_model_id=model_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            selection_extraction_chat_id = _chat_selection_action_resource(
                path,
                action="knowledge-extraction",
            )
            if method == "POST" and selection_extraction_chat_id is not None:
                payload = await _read_json_object(receive)
                (
                    message_revisions,
                    model_id,
                    effective_context_limit,
                    max_output_tokens,
                ) = _parse_message_selection_request(payload)
                await _send_contract(
                    send,
                    self._facade.extract_chat_selection_knowledge(
                        selection_extraction_chat_id,
                        message_revisions=message_revisions,
                        requested_model_id=model_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            selection_summary_chat_id = _chat_selection_action_resource(
                path,
                action="summary",
            )
            if method == "POST" and selection_summary_chat_id is not None:
                payload = await _read_json_object(receive)
                (
                    message_revisions,
                    model_id,
                    effective_context_limit,
                    max_output_tokens,
                ) = _parse_message_selection_request(payload)
                await _send_contract(
                    send,
                    self._facade.summarize_chat_selection(
                        selection_summary_chat_id,
                        message_revisions=message_revisions,
                        requested_model_id=model_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                    ),
                    status=201,
                    request_id=request_id,
                )
                return

            if (
                method == "POST"
                and path.startswith("/api/v1/chats/")
                and path.endswith("/messages/unified-local")
            ):
                chat_id = path.removeprefix(
                    "/api/v1/chats/"
                ).removesuffix(
                    "/messages/unified-local"
                )
                if not chat_id or "/" in chat_id:
                    raise ValueError(
                        "Invalid Unified Local chat message resource path."
                    )

                payload = await _read_json_object(receive)
                unknown = set(payload) - {
                    "content",
                    "model_id",
                    "embedding_model_id",
                    "operation_id",
                    "effective_context_limit",
                    "max_output_tokens",
                    "temperature",
                    "thinking_enabled",
                }
                if unknown:
                    raise ValueError(
                        "Unified Local chat request contains unsupported fields."
                    )

                content = payload.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise ValueError(
                        "Chat message content must contain non-whitespace text."
                    )

                model_id = payload.get("model_id")
                if model_id is not None and (
                    not isinstance(model_id, str)
                    or not model_id.strip()
                ):
                    raise ValueError(
                        "Chat model_id must be a non-empty string or null."
                    )

                embedding_model_id = payload.get(
                    "embedding_model_id"
                )
                if embedding_model_id is not None and (
                    not isinstance(embedding_model_id, str)
                    or not embedding_model_id.strip()
                ):
                    raise ValueError(
                        "Chat embedding_model_id must be a "
                        "non-empty string or null."
                    )

                operation_id = payload.get("operation_id")
                if operation_id is not None:
                    if (
                        not isinstance(operation_id, str)
                        or not operation_id.strip()
                    ):
                        raise ValueError(
                            "Chat operation_id must be a "
                            "non-empty UUID string or null."
                        )
                    try:
                        operation_id = str(uuid.UUID(operation_id))
                    except ValueError as exc:
                        raise ValueError(
                            "Chat operation_id must be a "
                            "valid UUID string or null."
                        ) from exc

                effective_context_limit = payload.get(
                    "effective_context_limit"
                )
                if effective_context_limit is not None and (
                    isinstance(effective_context_limit, bool)
                    or not isinstance(effective_context_limit, int)
                    or effective_context_limit < 1
                ):
                    raise ValueError(
                        "Chat effective_context_limit must be a positive integer or null."
                    )

                max_output_tokens = payload.get("max_output_tokens")
                if max_output_tokens is not None and (
                    isinstance(max_output_tokens, bool)
                    or not isinstance(max_output_tokens, int)
                    or max_output_tokens < 1
                ):
                    raise ValueError(
                        "Chat max_output_tokens must be a positive integer or null."
                    )
                temperature_value = payload.get("temperature")
                if temperature_value is not None and (
                    isinstance(temperature_value, bool)
                    or not isinstance(temperature_value, (int, float))
                    or not 0.0 <= float(temperature_value) <= 2.0
                ):
                    raise ValueError(
                        "Chat temperature must be between 0.0 and 2.0 or null."
                    )
                temperature = (
                    None if temperature_value is None else float(temperature_value)
                )
                thinking_enabled = payload.get("thinking_enabled")
                if thinking_enabled is not None and not isinstance(
                    thinking_enabled, bool
                ):
                    raise ValueError(
                        "Chat thinking_enabled must be boolean or null."
                    )
                await _send_contract(
                    send,
                    self._facade.send_unified_local_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=model_id,
                        requested_embedding_model_id=(
                            embedding_model_id
                        ),
                        operation_id=operation_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                        temperature=temperature,
                        thinking_enabled=thinking_enabled,
                    ),
                    request_id=request_id,
                )
                return

            recovery_resource = _chat_operation_action_resource(
                path,
                action="recovery",
            )
            if method == "GET" and recovery_resource is not None:
                chat_id, operation_id = recovery_resource
                await _send_contract(
                    send,
                    self._facade.chat_operation_recovery(
                        chat_id,
                        operation_id,
                    ),
                    request_id=request_id,
                )
                return

            continue_resource = _chat_operation_action_resource(
                path,
                action="continue",
            )
            if method == "POST" and continue_resource is not None:
                chat_id, operation_id = continue_resource
                await _consume_empty_body(receive)
                await _send_contract(
                    send,
                    self._facade.continue_unified_local_chat_operation(
                        chat_id,
                        operation_id,
                    ),
                    request_id=request_id,
                )
                return

            cancel_operation_id = _single_resource_id(
                path,
                prefix="/api/v1/chat-operations/",
                suffix="/cancel",
            )
            if method == "POST" and cancel_operation_id is not None:
                await _consume_empty_body(receive)
                try:
                    canonical_operation_id = str(
                        uuid.UUID(cancel_operation_id)
                    )
                except ValueError as exc:
                    raise ValueError(
                        "Chat operation ID must be a valid UUID."
                    ) from exc
                accepted = self._facade.cancel_chat_operation(
                    canonical_operation_id
                )
                await _send_json(
                    send,
                    status=202,
                    payload={
                        "accepted": accepted,
                        "operation_id": canonical_operation_id,
                    },
                    request_id=request_id,
                )
                return

            if (
                method == "POST"
                and path.startswith("/api/v1/chats/")
                and path.endswith("/messages")
            ):
                chat_id = path.removeprefix("/api/v1/chats/").removesuffix(
                    "/messages"
                )
                if not chat_id or "/" in chat_id:
                    raise ValueError("Invalid chat message resource path.")
                payload = await _read_json_object(receive)
                unknown = set(payload) - {
                    "content",
                    "model_id",
                    "operation_id",
                    "effective_context_limit",
                    "max_output_tokens",
                    "temperature",
                    "thinking_enabled",
                    "image_source_ids",
                }
                if unknown:
                    raise ValueError(
                        "Chat message request contains unsupported fields."
                    )
                content = payload.get("content")
                if not isinstance(content, str) or not content.strip():
                    raise ValueError(
                        "Chat message content must contain non-whitespace text."
                    )
                model_id = payload.get("model_id")
                if model_id is not None and (
                    not isinstance(model_id, str) or not model_id.strip()
                ):
                    raise ValueError(
                        "Chat model_id must be a non-empty string or null."
                    )
                operation_id = payload.get("operation_id")
                if operation_id is not None:
                    if (
                        not isinstance(operation_id, str)
                        or not operation_id.strip()
                    ):
                        raise ValueError(
                            "Chat operation_id must be a "
                            "non-empty UUID string or null."
                        )
                    try:
                        uuid.UUID(operation_id)
                    except ValueError as exc:
                        raise ValueError(
                            "Chat operation_id must be a "
                            "valid UUID string or null."
                        ) from exc

                effective_context_limit = payload.get(
                    "effective_context_limit"
                )
                if effective_context_limit is not None and (
                    isinstance(effective_context_limit, bool)
                    or not isinstance(effective_context_limit, int)
                    or effective_context_limit < 1
                ):
                    raise ValueError(
                        "Chat effective_context_limit must be a positive integer or null."
                    )
                max_output_tokens = payload.get("max_output_tokens")
                if max_output_tokens is not None and (
                    isinstance(max_output_tokens, bool)
                    or not isinstance(max_output_tokens, int)
                    or max_output_tokens < 1
                ):
                    raise ValueError(
                        "Chat max_output_tokens must be a positive integer or null."
                    )
                temperature_value = payload.get("temperature")
                if temperature_value is not None and (
                    isinstance(temperature_value, bool)
                    or not isinstance(temperature_value, (int, float))
                    or not 0.0 <= float(temperature_value) <= 2.0
                ):
                    raise ValueError(
                        "Chat temperature must be between 0.0 and 2.0 or null."
                    )
                temperature = (
                    None if temperature_value is None else float(temperature_value)
                )
                thinking_enabled = payload.get("thinking_enabled")
                if thinking_enabled is not None and not isinstance(
                    thinking_enabled, bool
                ):
                    raise ValueError(
                        "Chat thinking_enabled must be boolean or null."
                    )
                raw_image_source_ids = payload.get("image_source_ids", [])
                if not isinstance(raw_image_source_ids, list):
                    raise ValueError("Chat image_source_ids must be a list.")
                if len(raw_image_source_ids) > 4:
                    raise ValueError("Chat accepts at most four image Sources.")
                image_source_ids: list[str] = []
                for raw_source_id in raw_image_source_ids:
                    if not isinstance(raw_source_id, str):
                        raise ValueError("Chat image Source IDs must be UUID strings.")
                    try:
                        canonical_source_id = str(uuid.UUID(raw_source_id))
                    except ValueError as exc:
                        raise ValueError(
                            "Chat image Source IDs must be valid UUID strings."
                        ) from exc
                    image_source_ids.append(canonical_source_id)
                if len(set(image_source_ids)) != len(image_source_ids):
                    raise ValueError("Chat image Source IDs must be unique.")
                await _send_contract(
                    send,
                    self._facade.send_chat_message(
                        chat_id,
                        content=content,
                        requested_model_id=model_id,
                        operation_id=operation_id,
                        effective_context_limit=effective_context_limit,
                        max_output_tokens=max_output_tokens,
                        temperature=temperature,
                        thinking_enabled=thinking_enabled,
                        image_source_ids=tuple(image_source_ids),
                    ),
                    request_id=request_id,
                )
                return

            if (
                method == "GET"
                and path.startswith("/api/v1/chats/")
                and path.endswith("/deletion-preview")
            ):
                chat_id = path.removeprefix(
                    "/api/v1/chats/"
                ).removesuffix("/deletion-preview")
                if not chat_id or "/" in chat_id:
                    raise ValueError("Invalid chat deletion-preview resource path.")
                await _send_contract(
                    send,
                    self._facade.preview_chat_deletion(chat_id),
                    request_id=request_id,
                )
                return

            if (
                method == "DELETE"
                and path.startswith("/api/v1/chats/")
            ):
                chat_id = path.removeprefix("/api/v1/chats/")
                if not chat_id or "/" in chat_id:
                    raise ValueError("Invalid chat deletion resource path.")
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"preview_digest"}
                if unknown:
                    raise ValueError(
                        "Chat deletion request contains unsupported fields."
                    )
                preview_digest = payload.get("preview_digest")
                if (
                    not isinstance(preview_digest, str)
                    or len(preview_digest) != 64
                ):
                    raise ValueError(
                        "Chat deletion preview_digest must be a 64-character SHA-256 hex digest."
                    )
                try:
                    digest_bytes = bytes.fromhex(preview_digest)
                except ValueError as exc:
                    raise ValueError(
                        "Chat deletion preview_digest must be valid hexadecimal."
                    ) from exc
                if len(digest_bytes) != 32:
                    raise ValueError(
                        "Chat deletion preview_digest must be a SHA-256 digest."
                    )
                await _send_contract(
                    send,
                    self._facade.delete_chat(
                        chat_id,
                        preview_digest=preview_digest,
                    ),
                    request_id=request_id,
                )
                return

            if method == "GET" and path.startswith("/api/v1/chats/"):
                chat_id = path.removeprefix("/api/v1/chats/")
                if not chat_id or "/" in chat_id:
                    raise ValueError("Invalid chat resource path.")
                await _send_contract(
                    send,
                    self._facade.load_chat(chat_id),
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/models/health":
                await _send_contract(
                    send,
                    self._facade.provider_health(),
                    request_id=request_id,
                )
                return

            if method == "GET" and path == "/api/v1/models":
                await _send_json(
                    send,
                    status=200,
                    payload={
                        "items": [item.to_dict() for item in self._facade.list_models()]
                    },
                    request_id=request_id,
                )
                return

            review_run_id = _single_resource_id(
                path,
                prefix="/api/v1/knowledge-extractions/",
                suffix="/review",
            )
            if method == "POST" and review_run_id is not None:
                await _consume_empty_body(receive)
                await _send_contract(
                    send,
                    self._facade.prepare_knowledge_review(review_run_id),
                    request_id=request_id,
                )
                return

            merge_decision_id = _single_resource_id(
                path,
                prefix="/api/v1/knowledge-merge-reviews/",
                suffix="/decision",
            )
            if method == "POST" and merge_decision_id is not None:
                payload = await _read_json_object(receive)
                unknown = set(payload) - {"decision"}
                if unknown:
                    raise ValueError(
                        "Knowledge merge decision contains unsupported fields."
                    )
                decision = payload.get("decision")
                if not isinstance(decision, str):
                    raise ValueError(
                        "Knowledge merge decision must be a string."
                    )
                await _send_contract(
                    send,
                    self._facade.resolve_knowledge_merge_review(
                        merge_decision_id,
                        decision=decision,
                    ),
                    request_id=request_id,
                )
                return

            merge_review_id = _single_resource_id(
                path,
                prefix="/api/v1/knowledge-merge-reviews/",
            )
            if method == "GET" and merge_review_id is not None:
                await _send_contract(
                    send,
                    self._facade.load_knowledge_merge_review(merge_review_id),
                    request_id=request_id,
                )
                return

            if method == "POST" and path == "/api/v1/system/shutdown":
                await _consume_empty_body(receive)
                if not self._allow_shutdown:
                    await _send_problem(
                        send,
                        status=409,
                        code="shutdown_unavailable",
                        message="ATHENA Core shutdown is unavailable in this process.",
                        request_id=request_id,
                    )
                    return
                await _send_json(
                    send,
                    status=202,
                    payload={"accepted": True},
                    request_id=request_id,
                )
                return
        except ChatMessageNotFoundError:
            await _send_problem(
                send,
                status=404,
                code="chat_message_not_found",
                message="The requested chat message does not exist in this chat.",
                request_id=request_id,
            )
            return
        except ChatMessageRevisionMismatchError:
            await _send_problem(
                send,
                status=409,
                code="chat_message_revision_stale",
                message="The requested chat message revision is stale.",
                request_id=request_id,
                retryable=False,
            )
            return
        except chat_repository.ChatMessageNotFoundError:
            await _send_problem(
                send,
                status=404,
                code="chat_message_not_found",
                message="The requested chat message does not exist in this chat.",
                request_id=request_id,
            )
            return
        except chat_repository.ChatRevisionConflictError:
            await _send_problem(
                send,
                status=409,
                code="chat_revision_conflict",
                message="The requested chat message revision is stale.",
                request_id=request_id,
                retryable=False,
            )
            return
        except chat_repository.UnsupportedMessageEditError:
            await _send_problem(
                send,
                status=409,
                code="chat_message_edit_unsupported",
                message="This chat message cannot be edited through the current path.",
                request_id=request_id,
                retryable=False,
            )
            return
        except chat_repository.UnsupportedChatForkError:
            await _send_problem(
                send,
                status=409,
                code="chat_fork_unsupported",
                message="This chat cannot be forked through the current path.",
                request_id=request_id,
                retryable=False,
            )
            return
        except chat_repository.UnsupportedChatRegenerationError:
            await _send_problem(
                send,
                status=409,
                code="chat_regenerate_unsupported",
                message="This assistant response cannot be regenerated through the current path.",
                request_id=request_id,
                retryable=False,
            )
            return
        except LifecycleTransitionStateError:
            await _send_problem(
                send,
                status=409,
                code="chat_lifecycle_transition_conflict",
                message="The chat lifecycle state changed or does not support this transition.",
                request_id=request_id,
                retryable=False,
            )
            return
        except KnowledgeReviewNotFoundError:
            await _send_problem(
                send,
                status=404,
                code="knowledge_review_not_found",
                message="The requested Knowledge review resource does not exist.",
                request_id=request_id,
            )
            return
        except KnowledgeReviewConflictError:
            await _send_problem(
                send,
                status=409,
                code="knowledge_review_conflict",
                message="Knowledge review state changed or requires another decision.",
                request_id=request_id,
                retryable=False,
            )
            return
        except UnifiedGroundedRecoveryRequiredError as exc:
            state = exc.status.state.value
            if state == "partial_available":
                code = "chat_recovery_partial_available"
                message = (
                    "Partial provider output is durably preserved, but the original "
                    "provider stream cannot be resumed safely."
                )
            elif state == "ambiguous":
                code = "chat_recovery_ambiguous"
                message = (
                    "The persisted operation may already have crossed the provider "
                    "boundary. ATHENA will not repeat it automatically."
                )
            elif state == "conflict":
                code = "chat_recovery_conflict"
                message = (
                    "The persisted operation has conflicting recovery state and "
                    "cannot be continued safely."
                )
            else:
                code = "chat_recovery_unavailable"
                message = (
                    "The persisted operation is not in a state that can be "
                    "continued safely."
                )
            await _send_problem(
                send,
                status=409,
                code=code,
                message=message,
                request_id=request_id,
                retryable=False,
            )
            return
        except UnifiedReplayProjectionError:
            await _send_problem(
                send,
                status=409,
                code="chat_recovery_conflict",
                message=(
                    "The persisted Unified recovery state failed integrity "
                    "validation and cannot be continued safely."
                ),
                request_id=request_id,
                retryable=False,
            )
            return
        except GenerationCancelledError:
            await _send_problem(
                send,
                status=409,
                code="generation_cancelled",
                message=(
                    "Chat generation was cancelled. "
                    "The incomplete assistant response was not persisted."
                ),
                request_id=request_id,
                retryable=False,
            )
            return
        except ChatOperationActiveError:
            await _send_problem(
                send,
                status=409,
                code="chat_operation_active",
                message="The chat send operation is already active.",
                request_id=request_id,
                retryable=False,
            )
            return

        except SendOperationStateError as exc:
            if exc.status.state is SendOperationState.INCOMPLETE:
                code = "send_operation_incomplete"
                message = (
                    "The send operation already has a persisted "
                    "user turn but no completed assistant turn. "
                    "Automatic re-execution is blocked."
                )
            elif exc.status.state is SendOperationState.CONFLICT:
                code = "send_operation_conflict"
                message = (
                    "The send operation identity conflicts with "
                    "the requested chat or content."
                )
            else:
                code = "send_operation_state_conflict"
                message = (
                    "The send operation cannot be executed from "
                    "its current durable state."
                )

            await _send_problem(
                send,
                status=409,
                code=code,
                message=message,
                request_id=request_id,
                retryable=False,
            )
            return

        except (ValueError, TypeError) as exc:
            await _send_problem(
                send,
                status=400,
                code="invalid_request",
                message=str(exc),
                request_id=request_id,
            )
            return
        except ProviderOutputLimitError:
            await _send_problem(
                send,
                status=409,
                code="output_limit_reached",
                message=(
                    "The model reached the configured maximum output tokens. "
                    "The incomplete assistant response was not persisted."
                ),
                request_id=request_id,
                retryable=False,
            )
            return
        except chat_repository.ChatNotFoundError:
            await _send_problem(
                send,
                status=404,
                code="chat_not_found",
                message="The requested chat does not exist.",
                request_id=request_id,
            )
            return
        except (
            LifecycleDeletionNotFoundError,
            LifecycleDeletionAlreadyDeletedError,
        ):
            await _send_problem(
                send,
                status=404,
                code="chat_not_found",
                message="The requested chat does not exist.",
                request_id=request_id,
            )
            return
        except LifecycleDeletionPreviewStaleError:
            await _send_problem(
                send,
                status=409,
                code="deletion_preview_stale",
                message="Chat dependencies changed; review deletion again.",
                request_id=request_id,
            )
            return
        except LifecycleDeletionUnsupportedError:
            await _send_problem(
                send,
                status=409,
                code="deletion_unsupported",
                message="This chat cannot be deleted through the current lifecycle path.",
                request_id=request_id,
            )
            return
        except Exception:
            # Client responses must never expose stack traces or provider/DB
            # implementation details. Server-side logging is added with the
            # concrete CoreApiServer lifecycle wrapper.
            await _send_problem(
                send,
                status=500,
                code="internal_error",
                message="ATHENA could not complete the request.",
                request_id=request_id,
                retryable=False,
            )
            return

        if _known_path(path):
            await _send_problem(
                send,
                status=405,
                code="method_not_allowed",
                message="The requested ATHENA API resource does not support this method.",
                request_id=request_id,
            )
            return

        await _send_problem(
            send,
            status=404,
            code="not_found",
            message="The requested ATHENA API resource does not exist.",
            request_id=request_id,
        )


def _known_path(path: str) -> bool:
    if path in {
        "/api/v1/health",
        "/api/v1/storage/health",
        "/api/v1/capabilities",
        "/api/v1/search",
        "/api/v1/news/profile",
        "/api/v1/chats",
        "/api/v1/models",
        "/api/v1/models/health",
        "/api/v1/system/shutdown",
    }:
        return True
    if _single_resource_id(
        path,
        prefix="/api/v1/chat-operations/",
        suffix="/cancel",
    ) is not None:
        return True
    if _chat_operation_action_resource(path, action="recovery") is not None:
        return True
    if _chat_operation_action_resource(path, action="continue") is not None:
        return True
    if (
        path.startswith("/api/v1/chats/")
        and path.endswith("/deletion-preview")
    ):
        chat_id = path.removeprefix(
            "/api/v1/chats/"
        ).removesuffix("/deletion-preview")
        return bool(chat_id) and "/" not in chat_id
    if (
        path.startswith("/api/v1/chats/")
        and path.endswith("/messages/unified-local")
    ):
        chat_id = path.removeprefix(
            "/api/v1/chats/"
        ).removesuffix(
            "/messages/unified-local"
        )
        return bool(chat_id) and "/" not in chat_id
    if _message_action_resource(path, action="edit") is not None:
        return True
    if _message_action_resource(path, action="fork") is not None:
        return True
    if _message_action_resource(path, action="regenerate") is not None:
        return True
    if _message_action_resource(path, action="remember") is not None:
        return True
    if _message_action_resource(path, action="knowledge-extraction") is not None:
        return True
    if _chat_selection_action_resource(path, action="knowledge-extraction") is not None:
        return True
    if _chat_selection_action_resource(path, action="summary") is not None:
        return True
    if path.startswith("/api/v1/chats/") and path.endswith("/messages"):
        chat_id = path.removeprefix("/api/v1/chats/").removesuffix(
            "/messages"
        )
        return bool(chat_id) and "/" not in chat_id
    if _single_resource_id(
        path,
        prefix="/api/v1/knowledge-extractions/",
        suffix="/review",
    ) is not None:
        return True
    if _single_resource_id(
        path,
        prefix="/api/v1/knowledge-merge-reviews/",
        suffix="/decision",
    ) is not None:
        return True
    if _single_resource_id(
        path,
        prefix="/api/v1/knowledge-merge-reviews/",
    ) is not None:
        return True
    if path.startswith("/api/v1/chats/"):
        chat_id = path.removeprefix("/api/v1/chats/")
        return bool(chat_id) and "/" not in chat_id
    return False



def _chat_operation_action_resource(
    path: str,
    *,
    action: str,
) -> tuple[str, str] | None:
    prefix = "/api/v1/chats/"
    suffix = f"/{action}"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    middle = path[len(prefix) : -len(suffix)]
    chat_id, separator, operation_id = middle.partition("/operations/")
    if (
        separator != "/operations/"
        or not chat_id
        or not operation_id
        or "/" in chat_id
        or "/" in operation_id
    ):
        return None
    return chat_id, operation_id


def _chat_selection_action_resource(
    path: str,
    *,
    action: str,
) -> str | None:
    prefix = "/api/v1/chats/"
    suffix = f"/message-selection/{action}"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    chat_id = path[len(prefix) : -len(suffix)]
    if not chat_id or "/" in chat_id:
        return None
    return chat_id


def _parse_message_selection_request(
    payload: dict[str, JsonValue],
) -> tuple[tuple[tuple[str, str], ...], str | None, int | None, int | None]:
    unknown = set(payload) - {
        "messages",
        "model_id",
        "effective_context_limit",
        "max_output_tokens",
    }
    if unknown:
        raise ValueError("Message selection request contains unsupported fields.")

    raw_messages = payload.get("messages")
    if not isinstance(raw_messages, list) or not raw_messages:
        raise ValueError("Message selection must contain at least one message.")
    if len(raw_messages) > 100:
        raise ValueError("Message selection cannot exceed 100 messages.")

    message_revisions: list[tuple[str, str]] = []
    for raw_item in raw_messages:
        if not isinstance(raw_item, dict) or set(raw_item) != {
            "message_id",
            "revision_id",
        }:
            raise ValueError(
                "Each selected message must contain only message_id and revision_id."
            )
        message_id = raw_item.get("message_id")
        revision_id = raw_item.get("revision_id")
        if (
            not isinstance(message_id, str)
            or not message_id.strip()
            or "/" in message_id
        ):
            raise ValueError("Selected message_id must be a non-empty path-safe string.")
        if not isinstance(revision_id, str) or not revision_id.strip():
            raise ValueError("Selected revision_id must be a non-empty string.")
        message_revisions.append((message_id, revision_id))
    if len({message_id for message_id, _revision_id in message_revisions}) != len(
        message_revisions
    ):
        raise ValueError("Message selection must not contain duplicate message IDs.")

    model_id = payload.get("model_id")
    if model_id is not None and (
        not isinstance(model_id, str) or not model_id.strip()
    ):
        raise ValueError("Selection model_id must be a non-empty string or null.")

    effective_context_limit = payload.get("effective_context_limit")
    if effective_context_limit is not None and (
        isinstance(effective_context_limit, bool)
        or not isinstance(effective_context_limit, int)
        or effective_context_limit < 1
    ):
        raise ValueError(
            "Selection effective_context_limit must be positive or null."
        )

    max_output_tokens = payload.get("max_output_tokens")
    if max_output_tokens is not None and (
        isinstance(max_output_tokens, bool)
        or not isinstance(max_output_tokens, int)
        or max_output_tokens < 1
    ):
        raise ValueError("Selection max_output_tokens must be positive or null.")

    return (
        tuple(message_revisions),
        model_id,
        effective_context_limit,
        max_output_tokens,
    )


def _message_action_resource(
    path: str,
    *,
    action: str,
) -> tuple[str, str] | None:
    prefix = "/api/v1/chats/"
    suffix = f"/{action}"
    if not path.startswith(prefix) or not path.endswith(suffix):
        return None
    middle = path[len(prefix) : -len(suffix)]
    chat_id, separator, message_id = middle.partition("/messages/")
    if (
        separator != "/messages/"
        or not chat_id
        or not message_id
        or "/" in chat_id
        or "/" in message_id
    ):
        return None
    return chat_id, message_id


def _single_resource_id(
    path: str,
    *,
    prefix: str,
    suffix: str = "",
) -> str | None:
    if not path.startswith(prefix):
        return None
    if suffix and not path.endswith(suffix):
        return None
    end = -len(suffix) if suffix else None
    resource_id = path[len(prefix) : end]
    if not resource_id or "/" in resource_id:
        return None
    return resource_id


def _headers(scope: AsgiScope) -> dict[str, str]:
    raw_headers = cast(list[tuple[bytes, bytes]], scope.get("headers", []))
    result: dict[str, str] = {}
    for raw_name, raw_value in raw_headers:
        name = raw_name.decode("latin-1").lower()
        value = raw_value.decode("latin-1")
        result[name] = value
    return result


def _bearer_token(value: str | None) -> str | None:
    if value is None:
        return None
    scheme, separator, token = value.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token:
        return None
    return token


def _universal_search_query(
    scope: AsgiScope,
) -> tuple[str, int, tuple[UniversalSearchEntityType, ...] | None]:
    raw_query = cast(bytes, scope.get("query_string", b""))
    values = parse_qs(
        raw_query.decode("ascii"),
        keep_blank_values=True,
    )
    unknown = set(values) - {"q", "limit", "types"}
    if unknown:
        raise ValueError("Universal search request contains unsupported query parameters.")

    raw_text = values.get("q")
    if raw_text is None or len(raw_text) != 1 or not raw_text[0].strip():
        raise ValueError("Query parameter 'q' must occur once and contain text.")
    query = " ".join(raw_text[0].split())

    limit = _positive_limit(scope, default=20, maximum=100)

    raw_types = values.get("types")
    if raw_types is None:
        return query, limit, None
    if len(raw_types) != 1:
        raise ValueError("Query parameter 'types' must occur once.")

    type_names = tuple(part.strip() for part in raw_types[0].split(","))
    if not type_names or any(not part for part in type_names):
        raise ValueError("Query parameter 'types' must contain entity type names.")
    if len(set(type_names)) != len(type_names):
        raise ValueError("Query parameter 'types' must not contain duplicates.")

    try:
        entity_types = tuple(
            UniversalSearchEntityType(part)
            for part in type_names
        )
    except ValueError as exc:
        raise ValueError("Query parameter 'types' contains an unknown entity type.") from exc
    return query, limit, entity_types


def _positive_limit(scope: AsgiScope, *, default: int, maximum: int) -> int:
    raw_query = cast(bytes, scope.get("query_string", b""))
    if not raw_query:
        return default
    values = parse_qs(raw_query.decode("ascii"), keep_blank_values=True)
    raw_limit = values.get("limit")
    if raw_limit is None:
        return default
    if len(raw_limit) != 1:
        raise ValueError("Query parameter 'limit' must occur once.")
    try:
        limit = int(raw_limit[0])
    except ValueError as exc:
        raise ValueError("Query parameter 'limit' must be an integer.") from exc
    if not 1 <= limit <= maximum:
        raise ValueError(f"Query parameter 'limit' must be between 1 and {maximum}.")
    return limit


def _nonnegative_offset(
    scope: AsgiScope,
    *,
    default: int,
) -> int:
    raw_query = cast(
        bytes,
        scope.get("query_string", b""),
    )
    if not raw_query:
        return default

    values = parse_qs(
        raw_query.decode("ascii"),
        keep_blank_values=True,
    )
    raw_offset = values.get("offset")

    if raw_offset is None:
        return default

    if len(raw_offset) != 1:
        raise ValueError(
            "Query parameter 'offset' must occur once."
        )

    try:
        offset = int(raw_offset[0])
    except ValueError as exc:
        raise ValueError(
            "Query parameter 'offset' must be an integer."
        ) from exc

    if offset < 0:
        raise ValueError(
            "Query parameter 'offset' must be zero or greater."
        )

    return offset


async def _read_json_object(
    receive: AsgiReceive,
    *,
    max_bytes: int = _MAX_JSON_BODY_BYTES,
) -> dict[str, JsonValue]:
    raw = bytearray()
    while True:
        message = await receive()
        if message.get("type") != "http.request":
            raise ValueError("Invalid HTTP request body event.")
        chunk = cast(bytes, message.get("body", b""))
        if (
            isinstance(max_bytes, bool)
            or not isinstance(max_bytes, int)
            or max_bytes < 1
        ):
            raise ValueError("JSON request size limit must be a positive integer.")
        if len(raw) + len(chunk) > max_bytes:
            raise ValueError("JSON request body is too large.")
        raw.extend(chunk)
        if not bool(message.get("more_body", False)):
            break
    if not raw:
        raise ValueError("This endpoint requires a JSON request body.")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must contain valid UTF-8 JSON.") from exc
    if not isinstance(payload, dict) or not all(
        isinstance(key, str) for key in payload
    ):
        raise ValueError("JSON request body must be an object.")
    return cast(dict[str, JsonValue], payload)


async def _consume_empty_body(receive: AsgiReceive) -> None:
    message = await receive()
    if message.get("type") != "http.request":
        raise ValueError("Invalid HTTP request body event.")
    body = cast(bytes, message.get("body", b""))
    if body:
        raise ValueError("This endpoint does not accept a request body.")
    if bool(message.get("more_body", False)):
        raise ValueError("This endpoint does not accept a streaming request body.")


async def _send_contract(
    send: AsgiSend,
    contract: ApiContract,
    *,
    status: int = 200,
    request_id: str,
) -> None:
    await _send_json(
        send,
        status=status,
        payload=contract.to_dict(),
        request_id=request_id,
    )


async def _send_problem(
    send: AsgiSend,
    *,
    status: int,
    code: str,
    message: str,
    request_id: str | None = None,
    retryable: bool = False,
    extra_headers: tuple[tuple[bytes, bytes], ...] = (),
) -> None:
    resolved_request_id = request_id or str(uuid.uuid4())
    await _send_json(
        send,
        status=status,
        payload={
            "code": code,
            "message": message,
            "request_id": resolved_request_id,
            "retryable": retryable,
            "details": None,
        },
        request_id=resolved_request_id,
        extra_headers=extra_headers,
    )


async def _send_json(
    send: AsgiSend,
    *,
    status: int,
    payload: dict[str, JsonValue],
    request_id: str,
    extra_headers: tuple[tuple[bytes, bytes], ...] = (),
) -> None:
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    headers = _JSON_HEADERS + (
        (b"content-length", str(len(body)).encode("ascii")),
        (b"x-request-id", request_id.encode("ascii")),
    ) + extra_headers
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": list(headers),
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
            "more_body": False,
        }
    )
