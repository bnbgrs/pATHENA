"""Fail-closed plugin manifest, identity, and capability contracts.

The v1 plugin package intentionally contains no executable plugin loader. Third-party
code must not be imported merely because a manifest or signature exists on disk.
"""

from athena.plugins.capabilities import (
    PluginCapability,
    PluginCapabilityBoundary,
    PluginCapabilityDecision,
    PluginCapabilityDenied,
    PluginCapabilityGrant,
    PluginPermission,
)
from athena.plugins.identity import (
    PLUGIN_PUBLISHER_SIGNATURE_VERSION,
    PluginPublisherIdentityError,
    TrustedPluginPublisher,
    VerifiedPluginPublisherIdentity,
    canonical_plugin_identity_payload,
    verify_plugin_publisher_identity,
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
    "PLUGIN_PUBLISHER_SIGNATURE_VERSION",
    "PluginCapability",
    "PluginCapabilityBoundary",
    "PluginCapabilityDecision",
    "PluginCapabilityDenied",
    "PluginCapabilityGrant",
    "PluginCompatibilityError",
    "PluginManifest",
    "PluginManifestError",
    "PluginPermission",
    "PluginPublisherIdentityError",
    "TrustedPluginPublisher",
    "VerifiedPluginPublisherIdentity",
    "canonical_plugin_identity_payload",
    "require_compatible_plugin_api",
    "verify_plugin_publisher_identity",
]
