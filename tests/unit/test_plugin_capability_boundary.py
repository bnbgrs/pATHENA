from __future__ import annotations

import importlib

import pytest

from athena.plugins import (
    PluginCapability,
    PluginCapabilityBoundary,
    PluginCapabilityDenied,
    PluginCapabilityGrant,
    PluginCompatibilityError,
    PluginManifest,
    PluginManifestError,
    require_compatible_plugin_api,
)


def _manifest_payload() -> dict[str, object]:
    return {
        "plugin_id": "local.example-reader",
        "name": "Example Reader",
        "version": "1.0.0",
        "api_version": "1",
        "entrypoint": "example_reader.plugin:run",
        "permissions": [
            "sources.read",
            "network.request",
            "projects.read",
        ],
        "capabilities": [
            "read_selected_sources",
            "request_external_access",
            "read_project_scope",
        ],
        "publisher": {
            "kind": "local-development",
            "name": "Example",
        },
    }


def _manifest() -> PluginManifest:
    return PluginManifest.from_mapping(_manifest_payload())


def test_manifest_parsing_is_side_effect_free_and_does_not_import_entrypoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def _unexpected_import(name: str, package: str | None = None) -> object:
        calls.append(name)
        raise AssertionError("manifest parsing must not import plugin code")

    monkeypatch.setattr(importlib, "import_module", _unexpected_import)

    manifest = _manifest()

    assert manifest.plugin_id == "local.example-reader"
    assert manifest.entrypoint == "example_reader.plugin:run"
    assert manifest.publisher_mapping()["kind"] == "local-development"
    assert calls == []


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("plugin_id", "Bad Plugin"),
        ("version", "1.0;calc.exe"),
        ("api_version", "v1"),
        ("entrypoint", "example_reader.plugin:run;calc.exe"),
    ),
)
def test_manifest_rejects_unsafe_identity_or_entrypoint_syntax(
    field: str,
    value: object,
) -> None:
    payload = _manifest_payload()
    payload[field] = value

    with pytest.raises(PluginManifestError):
        PluginManifest.from_mapping(payload)


def test_manifest_rejects_unknown_fields_permissions_and_capabilities() -> None:
    payload = _manifest_payload()
    payload["shell_command"] = "calc.exe"
    with pytest.raises(PluginManifestError, match="unknown fields"):
        PluginManifest.from_mapping(payload)

    payload = _manifest_payload()
    payload["permissions"] = ["filesystem.raw"]
    with pytest.raises(PluginManifestError, match="unknown permission"):
        PluginManifest.from_mapping(payload)

    payload = _manifest_payload()
    payload["capabilities"] = ["raw_database_connection"]
    with pytest.raises(PluginManifestError, match="unknown capability"):
        PluginManifest.from_mapping(payload)


def test_manifest_requires_coarse_permission_for_each_capability() -> None:
    payload = _manifest_payload()
    payload["permissions"] = ["sources.read", "projects.read"]

    with pytest.raises(PluginManifestError, match="matching coarse permission"):
        PluginManifest.from_mapping(payload)


def test_incompatible_api_version_is_disabled_before_activation() -> None:
    payload = _manifest_payload()
    payload["api_version"] = "2"
    manifest = PluginManifest.from_mapping(payload)

    with pytest.raises(PluginCompatibilityError, match="incompatible"):
        require_compatible_plugin_api(manifest)


def test_declared_capability_is_still_denied_without_explicit_grant() -> None:
    boundary = PluginCapabilityBoundary(manifest=_manifest())

    decision = boundary.evaluate(PluginCapability.READ_SELECTED_SOURCES)

    assert decision.allowed is False
    assert decision.reason_code == "capability_not_granted"
    with pytest.raises(PluginCapabilityDenied, match="capability_not_granted"):
        boundary.require(PluginCapability.READ_SELECTED_SOURCES)


def test_runtime_grant_cannot_create_a_capability_missing_from_manifest() -> None:
    payload = _manifest_payload()
    payload["permissions"] = ["sources.read"]
    payload["capabilities"] = ["read_selected_sources"]
    manifest = PluginManifest.from_mapping(payload)
    grant = PluginCapabilityGrant(
        plugin_id=manifest.plugin_id,
        capability=PluginCapability.REQUEST_EXTERNAL_ACCESS,
    )
    boundary = PluginCapabilityBoundary(manifest=manifest, grants=(grant,))

    decision = boundary.evaluate(PluginCapability.REQUEST_EXTERNAL_ACCESS)

    assert decision.allowed is False
    assert decision.reason_code == "capability_not_declared"


def test_scoped_grant_allows_only_exact_core_issued_scope() -> None:
    manifest = _manifest()
    grant = PluginCapabilityGrant(
        plugin_id=manifest.plugin_id,
        capability=PluginCapability.READ_PROJECT_SCOPE,
        scopes=frozenset({"project:alpha"}),
    )
    boundary = PluginCapabilityBoundary(manifest=manifest, grants=(grant,))

    assert boundary.require(
        PluginCapability.READ_PROJECT_SCOPE,
        scope="project:alpha",
    ).allowed
    denied = boundary.evaluate(
        PluginCapability.READ_PROJECT_SCOPE,
        scope="project:beta",
    )
    assert denied.allowed is False
    assert denied.reason_code == "scope_not_granted"


def test_unscoped_explicit_grant_is_allowed_but_wildcard_scope_is_not_interpreted() -> None:
    manifest = _manifest()
    grant = PluginCapabilityGrant(
        plugin_id=manifest.plugin_id,
        capability=PluginCapability.REQUEST_EXTERNAL_ACCESS,
    )
    boundary = PluginCapabilityBoundary(manifest=manifest, grants=(grant,))

    assert boundary.require(
        PluginCapability.REQUEST_EXTERNAL_ACCESS,
        scope="domain:example.com",
    ).allowed

    with pytest.raises(ValueError, match="wildcard"):
        PluginCapabilityGrant(
            plugin_id=manifest.plugin_id,
            capability=PluginCapability.REQUEST_EXTERNAL_ACCESS,
            scopes=frozenset({"*"}),
        )


def test_grant_for_another_plugin_is_rejected_at_boundary_construction() -> None:
    manifest = _manifest()
    grant = PluginCapabilityGrant(
        plugin_id="other.plugin",
        capability=PluginCapability.READ_SELECTED_SOURCES,
    )

    with pytest.raises(ValueError, match="different plugin_id"):
        PluginCapabilityBoundary(manifest=manifest, grants=(grant,))
