"""Strict, side-effect-free validation for future pATHENA plugin manifests."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from athena.plugins.capabilities import (
    PluginCapability,
    PluginPermission,
    required_permission,
)

CORE_PLUGIN_API_VERSION = "1"

_PLUGIN_ID_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]{0,63}$")
_API_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
_ENTRYPOINT_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
    r":[A-Za-z_][A-Za-z0-9_]*$"
)
_ALLOWED_KEYS = frozenset(
    {
        "plugin_id",
        "name",
        "version",
        "api_version",
        "entrypoint",
        "permissions",
        "capabilities",
        "publisher",
    }
)
_REQUIRED_KEYS = _ALLOWED_KEYS - {"publisher"}
_UNSAFE_DISPLAY_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})


class PluginManifestError(ValueError):
    """Raised when a plugin manifest is structurally or semantically invalid."""


class PluginCompatibilityError(PluginManifestError):
    """Raised when a valid manifest targets an unsupported plugin API version."""


def _reject_unsafe_display_text(value: str, *, field: str) -> None:
    """Reject characters that can inject lines or visually spoof metadata."""

    for character in value:
        if unicodedata.category(character) in _UNSAFE_DISPLAY_CATEGORIES:
            raise PluginManifestError(
                f"Plugin manifest field {field!r} contains unsafe control or format characters."
            )


def _required_string(
    payload: Mapping[str, object],
    key: str,
    *,
    max_length: int,
) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise PluginManifestError(f"Plugin manifest field {key!r} must be a string.")
    normalized = value.strip()
    if not normalized or len(normalized) > max_length:
        raise PluginManifestError(
            f"Plugin manifest field {key!r} must be 1..{max_length} characters."
        )
    _reject_unsafe_display_text(normalized, field=key)
    return normalized


def _string_sequence(payload: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = payload.get(key)
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise PluginManifestError(f"Plugin manifest field {key!r} must be an array.")
    items: list[str] = []
    for raw in value:
        if not isinstance(raw, str) or not raw.strip():
            raise PluginManifestError(
                f"Plugin manifest field {key!r} contains a non-string or empty item."
            )
        items.append(raw.strip())
    if len(items) != len(set(items)):
        raise PluginManifestError(
            f"Plugin manifest field {key!r} contains duplicate entries."
        )
    return tuple(items)


def _publisher_metadata(payload: Mapping[str, object]) -> tuple[tuple[str, str], ...]:
    raw = payload.get("publisher")
    if raw is None:
        return ()
    if not isinstance(raw, Mapping):
        raise PluginManifestError("Plugin manifest publisher must be an object.")
    if len(raw) > 16:
        raise PluginManifestError("Plugin manifest publisher metadata is too large.")

    pairs: list[tuple[str, str]] = []
    for key, value in raw.items():
        if not isinstance(key, str) or not key.strip():
            raise PluginManifestError("Plugin publisher keys must be non-empty strings.")
        if not isinstance(value, str) or not value.strip():
            raise PluginManifestError("Plugin publisher values must be non-empty strings.")
        normalized_key = key.strip()
        normalized_value = value.strip()
        if len(normalized_key) > 64 or len(normalized_value) > 512:
            raise PluginManifestError("Plugin publisher metadata field is too large.")
        _reject_unsafe_display_text(normalized_key, field="publisher key")
        _reject_unsafe_display_text(normalized_value, field=f"publisher.{normalized_key}")
        pairs.append((normalized_key, normalized_value))
    return tuple(sorted(pairs))


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Validated manifest data only; parsing never imports the declared entrypoint."""

    plugin_id: str
    name: str
    version: str
    api_version: str
    entrypoint: str
    permissions: frozenset[PluginPermission]
    capabilities: frozenset[PluginCapability]
    publisher: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> PluginManifest:
        if not isinstance(raw, Mapping):
            raise PluginManifestError("Plugin manifest must be a mapping object.")

        keys = frozenset(raw.keys())
        if any(not isinstance(key, str) for key in keys):
            raise PluginManifestError("Plugin manifest keys must be strings.")
        missing = _REQUIRED_KEYS - keys
        if missing:
            names = ", ".join(sorted(missing))
            raise PluginManifestError(f"Plugin manifest is missing required fields: {names}.")
        unknown = keys - _ALLOWED_KEYS
        if unknown:
            names = ", ".join(sorted(unknown))
            raise PluginManifestError(f"Plugin manifest contains unknown fields: {names}.")

        plugin_id = _required_string(raw, "plugin_id", max_length=128)
        if not _PLUGIN_ID_RE.fullmatch(plugin_id):
            raise PluginManifestError(
                "Plugin plugin_id must use lowercase alphanumerics separated by . _ or -."
            )

        name = _required_string(raw, "name", max_length=120)
        version = _required_string(raw, "version", max_length=64)
        if not _VERSION_RE.fullmatch(version):
            raise PluginManifestError("Plugin version contains unsupported characters.")

        api_version = _required_string(raw, "api_version", max_length=32)
        if not _API_VERSION_RE.fullmatch(api_version):
            raise PluginManifestError("Plugin api_version must be a numeric dotted version.")

        entrypoint = _required_string(raw, "entrypoint", max_length=240)
        if not _ENTRYPOINT_RE.fullmatch(entrypoint):
            raise PluginManifestError(
                "Plugin entrypoint must be a Python module path plus callable name."
            )

        permission_names = _string_sequence(raw, "permissions")
        capability_names = _string_sequence(raw, "capabilities")
        try:
            permissions = frozenset(PluginPermission(item) for item in permission_names)
        except ValueError as exc:
            raise PluginManifestError("Plugin manifest requests an unknown permission.") from exc
        try:
            capabilities = frozenset(PluginCapability(item) for item in capability_names)
        except ValueError as exc:
            raise PluginManifestError("Plugin manifest requests an unknown capability.") from exc

        for capability in capabilities:
            permission = required_permission(capability)
            if permission not in permissions:
                raise PluginManifestError(
                    "Plugin capability requires its matching coarse permission: "
                    f"{capability.value!r} -> {permission.value!r}."
                )

        return cls(
            plugin_id=plugin_id,
            name=name,
            version=version,
            api_version=api_version,
            entrypoint=entrypoint,
            permissions=permissions,
            capabilities=capabilities,
            publisher=_publisher_metadata(raw),
        )

    def publisher_mapping(self) -> dict[str, str]:
        return dict(self.publisher)


def require_compatible_plugin_api(
    manifest: PluginManifest,
    *,
    supported_version: str = CORE_PLUGIN_API_VERSION,
) -> None:
    """Fail closed before activation when the plugin API contract is incompatible."""

    if not isinstance(manifest, PluginManifest):
        raise TypeError("Plugin compatibility check requires a PluginManifest.")
    if not isinstance(supported_version, str) or not _API_VERSION_RE.fullmatch(
        supported_version
    ):
        raise ValueError("Supported plugin API version is invalid.")
    if manifest.api_version != supported_version:
        raise PluginCompatibilityError(
            f"Plugin API {manifest.api_version!r} is incompatible with "
            f"Core plugin API {supported_version!r}."
        )
