"""Verified application-update contracts."""

from athena.update.manifest import (
    UpdateChannel,
    UpdateManifest,
    UpdateVerificationError,
    verify_package,
    verify_signed_manifest,
)
from athena.update.preflight import (
    UpdateRecoveryPoint,
    prepare_update_recovery_point,
)

__all__ = [
    "UpdateChannel",
    "UpdateManifest",
    "UpdateRecoveryPoint",
    "UpdateVerificationError",
    "prepare_update_recovery_point",
    "verify_package",
    "verify_signed_manifest",
]
