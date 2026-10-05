from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import pytest

from athena.api import client as client_module
from athena.api.client import CoreApiClient, CoreApiClientError
from athena.retrieval.universal import UniversalSearchEntityType


class _Response:
    def __init__(self, payload: dict[str, Any], *, status: int = 200) -> None:
        self.status = status
        self._raw = json.dumps(payload).encode("utf-8")

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> bool:
        del args
        return False

    def read(self) -> bytes:
        return self._raw


def _bootstrap(runtime_root: Path, *, port: int = 32123, token: str = "token-one") -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    token_path = runtime_root / "core-api.token"
    token_path.write_text(token + "\n", encoding="ascii")
    (runtime_root / "core-api.json").write_text(
        json.dumps(
            {
                "api_version": "v1",
                "host": "127.0.0.1",
                "port": port,
                "token_path": str(token_path),
                "process_id": 1234,
            }
        ),
        encoding="utf-8",
    )


def _request_header(request: Any, name: str) -> str | None:
    return request.get_header(name)

def _chat_thread_payload(
    *,
    chat_id: str,
    message_id: str = "22222222-2222-2222-2222-222222222222",
    revision_id: str = "33333333-3333-3333-3333-333333333333",
    content: str = "hello",
) -> dict[str, Any]:
    return {
        "chat_id": chat_id,
        "started_at_us": 10,
        "ended_at_us": None,
        "archive_mode": "standard",
        "lifecycle_state": "active",
        "messages": [
            {
                "message_id": message_id,
                "chat_id": chat_id,
                "sequence_no": 1,
                "message_type": "user",
                "actor_id": "44444444-4444-4444-4444-444444444444",
                "created_at_us": 11,
                "revision_id": revision_id,
                "content": content,
                "content_format": "text/plain",
            }
        ],
    }


def test_client_health_reads_discovery_and_authenticates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    seen: list[tuple[str, str, str | None]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        assert timeout == 2.5
        seen.append(
            (
                request.get_method(),
                request.full_url,
                _request_header(request, "Authorization"),
            )
        )
        return _Response({"api_version": "v1", "core_status": "ready", "detail": None})

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    response = CoreApiClient(runtime_root, timeout_seconds=2.5).health()

    assert response.core_status == "ready"
    assert seen == [
        (
            "GET",
            "http://127.0.0.1:32123/api/v1/health",
            "Bearer token-one",
        )
    ]


def test_client_universal_search_encodes_filters_and_parses_missing_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    seen: list[tuple[str, str]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        seen.append((request.get_method(), request.full_url))
        return _Response(
            {
                "items": [
                    {
                        "result_ref": (
                            "source:55555555-5555-5555-5555-555555555555"
                        ),
                        "title": "Alpha.pdf",
                        "preview": "application/pdf",
                        "entity_type": "source",
                        "revision_id": None,
                        "rank": 1,
                        "retrieval_methods": ["lexical"],
                        "source_anchor": None,
                        "protection": {
                            "state": "unprotected",
                            "protection_scope_id": None,
                        },
                    }
                ]
            }
        )

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    result = CoreApiClient(runtime_root).universal_search(
        "alpha design",
        limit=7,
        entity_types=(
            UniversalSearchEntityType.SOURCE,
            UniversalSearchEntityType.JOB,
        ),
    )

    assert len(result) == 1
    assert result[0].revision_id is None
    assert result[0].entity_type == "source"
    assert seen == [
        (
            "GET",
            (
                "http://127.0.0.1:32123/api/v1/search"
                "?q=alpha+design&limit=7&types=source%2Cjob"
            ),
        )
    ]


def test_client_edits_chat_message_with_exact_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"
    revision_id = "33333333-3333-3333-3333-333333333333"
    seen: list[tuple[str, str, dict[str, Any]]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        body = json.loads(request.data.decode("utf-8"))
        seen.append((request.get_method(), request.full_url, body))
        return _Response(
            _chat_thread_payload(
                chat_id=chat_id,
                message_id=message_id,
                revision_id="55555555-5555-5555-5555-555555555555",
                content="revised",
            )
        )

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    thread = CoreApiClient(runtime_root).edit_chat_message(
        chat_id,
        message_id,
        expected_revision_id=revision_id,
        content="revised",
    )

    assert thread.messages[0].content == "revised"
    assert seen == [
        (
            "PATCH",
            (
                "http://127.0.0.1:32123/api/v1/chats/"
                + chat_id
                + "/messages/"
                + message_id
                + "/edit"
            ),
            {
                "expected_revision_id": revision_id,
                "content": "revised",
            },
        )
    ]


def test_client_forks_chat_from_exact_message_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"
    revision_id = "33333333-3333-3333-3333-333333333333"
    fork_chat_id = "66666666-6666-6666-6666-666666666666"
    seen: list[tuple[str, str, dict[str, Any]]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        body = json.loads(request.data.decode("utf-8"))
        seen.append((request.get_method(), request.full_url, body))
        return _Response(_chat_thread_payload(chat_id=fork_chat_id), status=201)

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    thread = CoreApiClient(runtime_root).fork_chat_from_message(
        chat_id,
        message_id,
        revision_id=revision_id,
    )

    assert thread.chat_id == fork_chat_id
    assert seen == [
        (
            "POST",
            (
                "http://127.0.0.1:32123/api/v1/chats/"
                + chat_id
                + "/messages/"
                + message_id
                + "/fork"
            ),
            {"revision_id": revision_id},
        )
    ]


def test_client_chat_edit_and_fork_reject_invalid_revision_ids(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    client = CoreApiClient(runtime_root)
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"

    with pytest.raises(ValueError, match="Expected message revision"):
        client.edit_chat_message(
            chat_id,
            message_id,
            expected_revision_id="not-a-uuid",
            content="revised",
        )

    with pytest.raises(ValueError, match="Fork message revision"):
        client.fork_chat_from_message(
            chat_id,
            message_id,
            revision_id="not-a-uuid",
        )


def test_client_posts_chat_cancellation_with_canonical_operation_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    operation_id = "55555555-5555-4555-8555-555555555555"
    seen: list[tuple[str, str]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        seen.append((request.get_method(), request.full_url))
        return _Response(
            {
                "accepted": True,
                "operation_id": operation_id,
            },
            status=202,
        )

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    accepted = CoreApiClient(runtime_root).cancel_chat_operation(operation_id)

    assert accepted is True
    assert seen == [
        (
            "POST",
            (
                "http://127.0.0.1:32123/api/v1/chat-operations/"
                + operation_id
                + "/cancel"
            ),
        )
    ]


def test_client_reads_and_updates_news_schedule(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    seen: list[tuple[str, str, dict[str, Any] | None]] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        body = json.loads(request.data.decode("utf-8")) if request.data else None
        seen.append((request.get_method(), request.full_url, body))
        if request.get_method() == "GET":
            return _Response({
                "api_version": "v1",
                "enabled": True,
                "timezone_name": "Europe/Berlin",
                "local_hour": 7,
                "local_minute": 0,
            })
        return _Response({
            "api_version": "v1",
            "enabled": True,
            "timezone_name": "Europe/Berlin",
            "local_hour": 6,
            "local_minute": 30,
        })

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)
    client = CoreApiClient(runtime_root)

    initial = client.news_profile()
    saved = client.configure_news_schedule(
        timezone_name="Europe/Berlin",
        local_hour=6,
        local_minute=30,
    )

    assert (initial.local_hour, initial.local_minute) == (7, 0)
    assert (saved.local_hour, saved.local_minute) == (6, 30)
    assert seen[0][:2] == ("GET", "http://127.0.0.1:32123/api/v1/news/profile")
    assert seen[1] == (
        "PUT",
        "http://127.0.0.1:32123/api/v1/news/profile",
        {"timezone_name": "Europe/Berlin", "local_hour": 6, "local_minute": 30},
    )


def test_client_reloads_bootstrap_and_retries_safe_get_after_core_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root, port=32123, token="token-one")
    calls = 0

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        nonlocal calls
        del timeout
        calls += 1
        if calls == 1:
            _bootstrap(runtime_root, port=32124, token="token-two")
            raise URLError("old core stopped")
        assert request.full_url == "http://127.0.0.1:32124/api/v1/capabilities"
        assert _request_header(request, "Authorization") == "Bearer token-two"
        return _Response({"api_version": "v1", "features": ["health"]})

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    response = CoreApiClient(runtime_root).capabilities()

    assert response.features == ("health",)
    assert calls == 2


def test_client_does_not_retry_ambiguous_post_transport_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    calls = 0

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        nonlocal calls
        del request, timeout
        calls += 1
        raise URLError("response lost")

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    with pytest.raises(CoreApiClientError, match="unavailable") as exc_info:
        CoreApiClient(runtime_root).create_chat()

    assert exc_info.value.retryable is True
    assert calls == 1


def test_client_rejects_non_loopback_discovery(tmp_path: Path) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    discovery = runtime_root / "core-api.json"
    payload = json.loads(discovery.read_text(encoding="utf-8"))
    payload["host"] = "192.168.1.10"
    discovery.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(CoreApiClientError, match="non-loopback") as exc_info:
        CoreApiClient(runtime_root).health()

    assert exc_info.value.code == "invalid_discovery"


def test_client_rejects_symlink_runtime_ancestor(tmp_path: Path) -> None:
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    link_parent = tmp_path / "linked-parent"
    try:
        link_parent.symlink_to(real_parent, target_is_directory=True)
    except OSError:
        pytest.skip("symlink creation unavailable")

    runtime_root = link_parent / "api"
    _bootstrap(runtime_root)

    with pytest.raises(
        CoreApiClientError,
        match="runtime directory is not trusted",
    ) as exc_info:
        CoreApiClient(runtime_root).discovery_process_id()

    assert exc_info.value.code == "invalid_discovery"


def test_client_rejects_runtime_ancestor_reported_as_link_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "safe" / "api"
    _bootstrap(runtime_root)
    original_is_link_boundary = client_module.is_link_boundary
    unsafe_ancestor = runtime_root.parent

    def fake_is_link_boundary(path: Path) -> bool:
        if path == unsafe_ancestor:
            return True
        return original_is_link_boundary(path)

    monkeypatch.setattr(
        client_module,
        "is_link_boundary",
        fake_is_link_boundary,
    )

    with pytest.raises(
        CoreApiClientError,
        match="runtime directory is not trusted",
    ) as exc_info:
        CoreApiClient(runtime_root).discovery_process_id()

    assert exc_info.value.code == "invalid_discovery"


def test_client_rejects_token_path_outside_runtime_root(tmp_path: Path) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    external = tmp_path / "foreign.token"
    external.write_text("foreign-token\n", encoding="ascii")
    discovery = runtime_root / "core-api.json"
    payload = json.loads(discovery.read_text(encoding="utf-8"))
    payload["token_path"] = str(external)
    discovery.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(CoreApiClientError, match="unexpected token path") as exc_info:
        CoreApiClient(runtime_root).health()

    assert exc_info.value.code == "invalid_discovery"


def test_client_surfaces_structured_problem_without_stacktrace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        raw = json.dumps(
            {
                "code": "chat_not_found",
                "message": "The requested chat does not exist.",
                "request_id": "request-123",
                "retryable": False,
                "details": None,
            }
        ).encode("utf-8")
        raise HTTPError(
            request.full_url,
            404,
            "Not Found",
            hdrs=None,
            fp=io.BytesIO(raw),
        )

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    with pytest.raises(CoreApiClientError, match="does not exist") as exc_info:
        CoreApiClient(runtime_root).load_chat("019ffake")

    error = exc_info.value
    assert error.status == 404
    assert error.code == "chat_not_found"
    assert error.request_id == "request-123"
    assert "Traceback" not in str(error)


def test_client_parses_chat_and_model_lists(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        if request.full_url.endswith(
            "/api/v1/chats?limit=7&offset=3"
        ):
            return _Response(
                {
                    "items": [
                        {
                            "chat_id": "chat-1",
                            "started_at_us": 10,
                            "ended_at_us": None,
                            "archive_mode": "default",
                            "lifecycle_state": "active",
                            "message_count": 3,
                        }
                    ]
                }
            )
        if request.full_url.endswith("/api/v1/models"):
            return _Response(
                {
                    "items": [
                        {
                            "provider": "lm_studio",
                            "backend_model_id": "model-1",
                            "display_name": "Model One",
                            "model_type": "llm",
                            "context_capacity": 128000,
                            "quantization": "Q4_K_S",
                            "loaded": True,
                            "vision": False,
                            "trained_for_tool_use": True,
                            "loaded_context_length": 48000,
                        }
                    ]
                }
            )
        raise AssertionError(request.full_url)

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)
    client = CoreApiClient(runtime_root)

    chats = client.list_chats(
        limit=7,
        offset=3,
    )
    models = client.list_models()

    assert chats[0].chat_id == "chat-1"
    assert chats[0].message_count == 3
    assert models[0].backend_model_id == "model-1"
    assert models[0].loaded_context_length == 48000


def test_client_rejects_invalid_response_shape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    monkeypatch.setattr(
        client_module,
        "urlopen",
        lambda request, timeout: _Response({"items": ["not-an-object"]}),
    )

    with pytest.raises(CoreApiClientError, match="invalid item") as exc_info:
        CoreApiClient(runtime_root).list_models()

    assert exc_info.value.code == "invalid_response"


def test_client_from_environment_uses_core_api_runtime_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    local_root = (tmp_path / "athena-local").resolve()
    monkeypatch.setenv("ATHENA_LOCAL_ROOT", str(local_root))
    monkeypatch.delenv("ATHENA_ARCHIVE_ROOT", raising=False)
    monkeypatch.delenv("ATHENA_BACKUP_ROOT", raising=False)
    monkeypatch.delenv("ATHENA_PROJECTION_ROOT", raising=False)

    client = CoreApiClient.from_environment(timeout_seconds=1.25)

    assert client.runtime_root == local_root / "tmp" / "core-api"
    assert client.timeout_seconds == 1.25


def test_client_exposes_trusted_discovery_process_id(tmp_path: Path) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    assert CoreApiClient(runtime_root).discovery_process_id() == 1234


def test_client_shutdown_command_is_not_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)
    calls = 0

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        nonlocal calls
        del timeout
        calls += 1
        assert request.get_method() == "POST"
        assert request.full_url.endswith("/api/v1/system/shutdown")
        return _Response({"accepted": True}, status=202)

    monkeypatch.setattr(client_module, "urlopen", fake_urlopen)

    CoreApiClient(runtime_root).request_shutdown()

    assert calls == 1



@pytest.mark.parametrize(
    "timeout",
    [
        True,
        False,
        0,
        -1,
        float("nan"),
        float("inf"),
        float("-inf"),
        10**400,
        "5",
    ],
)
def test_client_rejects_invalid_transport_timeout_values(
    tmp_path: Path,
    timeout: object,
) -> None:
    with pytest.raises((TypeError, ValueError), match="timeout"):
        CoreApiClient(
            tmp_path / "api",
            timeout_seconds=timeout,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "timeout",
    [
        True,
        False,
        0,
        -1,
        float("nan"),
        float("inf"),
        float("-inf"),
        10**400,
        "30",
    ],
)
def test_client_rejects_invalid_generation_timeout_values(
    tmp_path: Path,
    timeout: object,
) -> None:
    with pytest.raises((TypeError, ValueError), match="generation timeout"):
        CoreApiClient(
            tmp_path / "api",
            generation_timeout_seconds=timeout,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("limit", "offset", "message"),
    [
        (True, 0, "limit must be an integer"),
        (1.5, 0, "limit must be an integer"),
        ("20", 0, "limit must be an integer"),
        (20, True, "offset must be an integer"),
        (20, 1.5, "offset must be an integer"),
        (20, "1", "offset must be an integer"),
    ],
)
def test_client_rejects_non_integer_chat_pagination_before_discovery(
    tmp_path: Path,
    limit: object,
    offset: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        CoreApiClient(tmp_path / "missing-runtime").list_chats(
            limit=limit,  # type: ignore[arg-type]
            offset=offset,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf"), 10**400],
)
def test_client_rejects_nonfinite_numeric_response_fields(
    value: int | float,
) -> None:
    with pytest.raises(
        CoreApiClientError,
        match="not finite",
    ) as exc_info:
        client_module._required_float(
            {"confidence": value},
            "confidence",
        )

    assert exc_info.value.code == "invalid_response"


def test_client_rejects_negative_chat_offset(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    with pytest.raises(
        ValueError,
        match="offset",
    ):
        CoreApiClient(
            runtime_root
        ).list_chats(
            offset=-1
        )



@pytest.mark.parametrize(
    ("source_anchor", "protection"),
    [
        (
            {
                "representation_id": (
                    "33333333-3333-3333-3333-333333333333"
                ),
                "start_offset": 8,
                "end_offset": 8,
                "quoted_sha256": "0" * 64,
            },
            {
                "state": "unprotected",
                "protection_scope_id": None,
            },
        ),
        (
            None,
            {
                "state": "unprotected",
                "protection_scope_id": (
                    "44444444-4444-4444-4444-444444444444"
                ),
            },
        ),
    ],
)
def test_client_universal_search_normalizes_invalid_nested_contracts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_anchor: dict[str, Any] | None,
    protection: dict[str, Any],
) -> None:
    runtime_root = tmp_path / "api"
    _bootstrap(runtime_root)

    monkeypatch.setattr(
        client_module,
        "urlopen",
        lambda request, timeout: _Response(
            {
                "items": [
                    {
                        "result_ref": (
                            "source:"
                            "55555555-5555-5555-5555-555555555555"
                        ),
                        "title": "Alpha.pdf",
                        "preview": "application/pdf",
                        "entity_type": "source",
                        "revision_id": None,
                        "rank": 1,
                        "retrieval_methods": ["lexical"],
                        "source_anchor": source_anchor,
                        "protection": protection,
                    }
                ]
            }
        ),
    )

    with pytest.raises(
        CoreApiClientError,
        match="invalid Search result",
    ) as exc_info:
        CoreApiClient(runtime_root).universal_search("alpha")

    assert exc_info.value.code == "invalid_response"
