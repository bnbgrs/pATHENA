from __future__ import annotations

import json

import pytest

from athena.plugins.broker import PluginCapabilityBroker
from athena.plugins.capabilities import (
    PluginCapability,
    PluginCapabilityBoundary,
    PluginCapabilityGrant,
)
from athena.plugins.manifest import PluginManifest
from athena.plugins.protocol import (
    PLUGIN_IPC_MAX_MESSAGE_BYTES,
    PluginProtocolError,
    decode_plugin_capability_request,
)


def _manifest() -> PluginManifest:
    return PluginManifest.from_mapping(
        {
            "plugin_id": "example.plugin",
            "name": "Example",
            "version": "1.0.0",
            "api_version": "1",
            "entrypoint": "example.plugin:activate",
            "permissions": ["sources.read", "network.request"],
            "capabilities": ["read_selected_sources", "request_external_access"],
        }
    )


def _request(
    *,
    capability: str = "read_selected_sources",
    scope: str | None = "source:123",
    request_id: str = "req-1",
) -> bytes:
    return json.dumps(
        {
            "version": 1,
            "type": "capability_request",
            "request_id": request_id,
            "capability": capability,
            "scope": scope,
        },
        separators=(",", ":"),
    ).encode()


def test_valid_request_round_trips_into_typed_capability_request() -> None:
    request = decode_plugin_capability_request(_request())

    assert request.request_id == "req-1"
    assert request.capability is PluginCapability.READ_SELECTED_SOURCES
    assert request.scope == "source:123"


@pytest.mark.parametrize(
    "payload,match",
    [
        (b"[]", "JSON object"),
        (b'{"version":true,"type":"capability_request","request_id":"x","capability":"read_selected_sources"}', "version"),
        (b'{"version":2,"type":"capability_request","request_id":"x","capability":"read_selected_sources"}', "version"),
        (b'{"version":1,"type":"execute","request_id":"x","capability":"read_selected_sources"}', "operation"),
        (b'{"version":1,"type":"capability_request","request_id":"x","capability":"unknown"}', "unknown"),
        (b'{"version":1,"type":"capability_request","request_id":"x","capability":"read_selected_sources","payload":{}}', "unknown fields"),
        (b'{"version":1,"version":1,"type":"capability_request","request_id":"x","capability":"read_selected_sources"}', "duplicate"),
        (b"\xff", "UTF-8"),
    ],
)
def test_malformed_ambiguous_and_unknown_messages_fail_closed(
    payload: bytes,
    match: str,
) -> None:
    with pytest.raises(PluginProtocolError, match=match):
        decode_plugin_capability_request(payload)


def test_oversized_message_is_rejected_before_json_parse() -> None:
    payload = b"{" + b" " * PLUGIN_IPC_MAX_MESSAGE_BYTES + b"}"

    with pytest.raises(PluginProtocolError, match="maximum size"):
        decode_plugin_capability_request(payload)


@pytest.mark.parametrize(
    "request_id",
    [
        "req\nforged",
        "req\u0085forged",
        "req\u202eforged",
        "req\u2066forged",
        "req\u2028forged",
    ],
)
def test_request_id_rejects_log_and_display_spoofing_controls(request_id: str) -> None:
    with pytest.raises(PluginProtocolError, match="request_id"):
        decode_plugin_capability_request(_request(request_id=request_id))


@pytest.mark.parametrize(
    "scope",
    [
        "source:123\rforged",
        "source:123\u009bforged",
        "source:123\u202dforged",
        "source:123\u2069forged",
        "source:123\u2029forged",
    ],
)
def test_scope_rejects_log_and_display_spoofing_controls(scope: str) -> None:
    with pytest.raises(PluginProtocolError, match="scope"):
        decode_plugin_capability_request(_request(scope=scope))


def test_broker_denies_manifest_declared_but_ungranted_capability() -> None:
    boundary = PluginCapabilityBoundary(manifest=_manifest())
    broker = PluginCapabilityBroker(boundary=boundary)

    decision = broker.authorize(decode_plugin_capability_request(_request()))

    assert decision.allowed is False
    assert decision.reason_code == "capability_not_granted"
    assert decision.plugin_id == "example.plugin"


def test_broker_enforces_exact_core_issued_scope() -> None:
    manifest = _manifest()
    boundary = PluginCapabilityBoundary(
        manifest=manifest,
        grants=(
            PluginCapabilityGrant(
                plugin_id=manifest.plugin_id,
                capability=PluginCapability.READ_SELECTED_SOURCES,
                scopes=frozenset({"source:123"}),
            ),
        ),
    )
    broker = PluginCapabilityBroker(boundary=boundary)

    allowed = broker.authorize(decode_plugin_capability_request(_request()))
    denied = broker.authorize(
        decode_plugin_capability_request(_request(scope="source:456"))
    )

    assert allowed.allowed is True
    assert allowed.reason_code == "allowed"
    assert denied.allowed is False
    assert denied.reason_code == "scope_not_granted"


def test_broker_cannot_authorize_undeclared_capability_even_with_grant() -> None:
    manifest = PluginManifest.from_mapping(
        {
            "plugin_id": "example.plugin",
            "name": "Example",
            "version": "1.0.0",
            "api_version": "1",
            "entrypoint": "example.plugin:activate",
            "permissions": ["network.request"],
            "capabilities": [],
        }
    )
    boundary = PluginCapabilityBoundary(
        manifest=manifest,
        grants=(
            PluginCapabilityGrant(
                plugin_id=manifest.plugin_id,
                capability=PluginCapability.REQUEST_EXTERNAL_ACCESS,
            ),
        ),
    )
    broker = PluginCapabilityBroker(boundary=boundary)

    decision = broker.authorize(
        decode_plugin_capability_request(
            _request(capability="request_external_access", scope=None)
        )
    )

    assert decision.allowed is False
    assert decision.reason_code == "capability_not_declared"
