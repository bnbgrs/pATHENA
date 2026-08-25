"""Fail-closed plugin manifest and capability contracts.

The v1 plugin package intentionally contains no executable plugin loader. Third-party
code must not be imported merely because a manifest exists on disk.
"""

from athena.plugins.capabilities import (
    PluginCapability,
    PluginCapabilityBoundary,
    PluginCapabilityDecision,
    PluginCapabilityDenied,
    PluginCapabilityGrant,
    PluginPermission,
)
from athena.plugins.manifest import (
    CORE_PLUGIN_API_VERSION,
    PluginCompatibilityError,
    PluginManifest,
    PluginManifestError,
    require_compatible_plugin_api,
)

__all__ = [
    "CORE_PLUGIN_API_VERSION",
    "PluginCapability",
    "PluginCapabilityBoundary",
    "PluginCapabilityDecision",
    "PluginCapabilityDenied",
    "PluginCapabilityGrant",
    "PluginCompatibilityError",
    "PluginManifest",
    "PluginManifestError",
    "PluginPermission",
    "require_compatible_plugin_api",
]
