from __future__ import annotations

from typing import Any, cast

import pytest

from athena.plugins.capabilities import PluginCapability, PluginPermission
from athena.plugins.manifest import PluginManifest, PluginManifestError


def _direct_manifest(**overrides: object) -> PluginManifest:
    values: dict[str, object] = {
        "plugin_id": "example.plugin",
        "name": "Example",
        "version": "1.0.0",
        "api_version": "1",
        "entrypoint": "example.plugin:activate",
        "permissions": frozenset({PluginPermission.READ_SOURCES}),
        "capabilities": frozenset({PluginCapability.READ_SELECTED_SOURCES}),
        "publisher": (("name", "Example Publisher"),),
    }
    values.update(overrides)
    return PluginManifest(**cast(Any, values))


def test_direct_manifest_construction_preserves_validated_runtime_contract() -> None:
    manifest = _direct_manifest()

    assert manifest.plugin_id == "example.plugin"
    assert manifest.permissions == frozenset({PluginPermission.READ_SOURCES})
    assert manifest.capabilities == frozenset(
        {PluginCapability.READ_SELECTED_SOURCES}
    )
    assert manifest.publisher_mapping() == {"name": "Example Publisher"}


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("plugin_id", "../escape", "plugin_id"),
        ("plugin_id", " Example.Plugin ", "canonical"),
        ("name", "Example\nforged", "unsafe"),
        ("version", "1/0", "version"),
        ("api_version", "one", "api_version"),
        ("entrypoint", "os.system", "entrypoint"),
    ],
)
def test_direct_manifest_rejects_invalid_scalar_fields(
    field: str,
    value: object,
    match: str,
) -> None:
    with pytest.raises(PluginManifestError, match=match):
        _direct_manifest(**{field: value})


def test_direct_manifest_rejects_runtime_collection_type_spoofing() -> None:
    with pytest.raises(PluginManifestError, match="permissions"):
        _direct_manifest(
            permissions=frozenset({"sources.read"}),
            capabilities=frozenset({PluginCapability.READ_SELECTED_SOURCES}),
        )

    with pytest.raises(PluginManifestError, match="capabilities"):
        _direct_manifest(
            permissions=frozenset({PluginPermission.READ_SOURCES}),
            capabilities=frozenset({"read_selected_sources"}),
        )


def test_direct_manifest_rejects_capability_without_required_permission() -> None:
    with pytest.raises(PluginManifestError, match="matching coarse permission"):
        _direct_manifest(
            permissions=frozenset({PluginPermission.REQUEST_NETWORK}),
            capabilities=frozenset({PluginCapability.READ_SELECTED_SOURCES}),
        )


@pytest.mark.parametrize(
    "publisher",
    [
        (("name", "Publisher"), ("name", "Spoof")),
        (("z", "Last"), ("a", "First")),
        (("name ", "Publisher"),),
        (("name", "Publisher\u202eforged"),),
    ],
)
def test_direct_manifest_rejects_noncanonical_publisher_metadata(
    publisher: object,
) -> None:
    with pytest.raises(PluginManifestError, match="publisher"):
        _direct_manifest(publisher=publisher)


def test_from_mapping_still_normalizes_before_runtime_validation() -> None:
    manifest = PluginManifest.from_mapping(
        {
            "plugin_id": "example.plugin",
            "name": "  Example  ",
            "version": "1.0.0",
            "api_version": "1",
            "entrypoint": "example.plugin:activate",
            "permissions": ["sources.read"],
            "capabilities": ["read_selected_sources"],
            "publisher": {"name": "  Publisher  "},
        }
    )

    assert manifest.name == "Example"
    assert manifest.publisher == (("name", "Publisher"),)
