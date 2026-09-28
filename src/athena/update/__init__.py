"""Verified application-update contracts."""

from athena.update.manifest import (
    UpdateChannel,
    UpdateManifest,
    UpdateVerificationError,
    verify_package,
    verify_signed_manifest,
)

__all__ = [
    "UpdateChannel",
    "UpdateManifest",
    "UpdateVerificationError",
    "verify_package",
    "verify_signed_manifest",
]
