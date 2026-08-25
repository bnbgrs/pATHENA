"""Bounded, fail-closed IPC message contract for a future plugin process host.

This is a serialization/validation layer only. It does not spawn a process, import an
entrypoint, open a socket, or make process isolation claims stronger than warranted.
"""

from __future__ import annotations

import json
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from athena.plugins.capabilities import PluginCapability

PLUGIN_IPC_PROTOCOL_VERSION = 1
PLUGIN_IPC_MAX_MESSAGE_BYTES = 16 * 1024
PLUGIN_IPC_MAX_REQUEST_ID_LENGTH = 128
PLUGIN_IPC_MAX_SCOPE_LENGTH = 512
_ALLOWED_KEYS = frozenset({"version", "type", "request_id", "capability", "scope"})
_UNSAFE_TEXT_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})


class PluginProtocolError(ValueError):
    """Raised when a plugin IPC message is malformed or unsupported."""


@dataclass(frozen=True, slots=True)
class PluginCapabilityRequest:
    """Validated payload-free request for one Core-mediated capability."""

    request_id: str
    capability: PluginCapability
    scope: str | None


def _unique_json_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PluginProtocolError("Plugin IPC message contains duplicate fields.")
        result[key] = value
    return result


def _contains_unsafe_text(value: str) -> bool:
    """Reject controls/formatting that can spoof logs, diagnostics, or UI text."""

    return any(unicodedata.category(char) in _UNSAFE_TEXT_CATEGORIES for char in value)


def decode_plugin_capability_request(payload: bytes) -> PluginCapabilityRequest:
    """Decode one complete UTF-8 JSON request with strict bounds and schema.

    Arbitrary plugin-supplied operation payloads are intentionally not accepted by
    this v1 contract. Capability-specific arguments, if ever needed, require their
    own separately bounded Core schema rather than an untyped pass-through object.
    """

    if not isinstance(payload, bytes):
        raise TypeError("Plugin IPC payload must be bytes.")
    if not payload:
        raise PluginProtocolError("Plugin IPC message is empty.")
    if len(payload) > PLUGIN_IPC_MAX_MESSAGE_BYTES:
        raise PluginProtocolError("Plugin IPC message exceeds the maximum size.")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise PluginProtocolError("Plugin IPC message is not valid UTF-8.") from exc
    try:
        raw: Any = json.loads(text, object_pairs_hook=_unique_json_object)
    except PluginProtocolError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise PluginProtocolError("Plugin IPC message is not valid JSON.") from exc
    if not isinstance(raw, dict):
        raise PluginProtocolError("Plugin IPC message must be a JSON object.")
    unknown = set(raw) - _ALLOWED_KEYS
    if unknown:
        raise PluginProtocolError("Plugin IPC message contains unknown fields.")
    version = raw.get("version")
    if type(version) is not int or version != PLUGIN_IPC_PROTOCOL_VERSION:
        raise PluginProtocolError("Plugin IPC protocol version is unsupported.")
    if raw.get("type") != "capability_request":
        raise PluginProtocolError("Plugin IPC operation type is unsupported.")

    request_id = raw.get("request_id")
    if (
        not isinstance(request_id, str)
        or not request_id
        or len(request_id) > PLUGIN_IPC_MAX_REQUEST_ID_LENGTH
        or _contains_unsafe_text(request_id)
    ):
        raise PluginProtocolError("Plugin IPC request_id is invalid.")

    capability_raw = raw.get("capability")
    if not isinstance(capability_raw, str):
        raise PluginProtocolError("Plugin IPC capability is invalid.")
    try:
        capability = PluginCapability(capability_raw)
    except ValueError as exc:
        raise PluginProtocolError("Plugin IPC capability is unknown.") from exc

    scope = raw.get("scope")
    if scope is not None:
        if (
            not isinstance(scope, str)
            or not scope.strip()
            or len(scope) > PLUGIN_IPC_MAX_SCOPE_LENGTH
            or _contains_unsafe_text(scope)
        ):
            raise PluginProtocolError("Plugin IPC scope is invalid.")

    return PluginCapabilityRequest(
        request_id=request_id,
        capability=capability,
        scope=scope,
    )
