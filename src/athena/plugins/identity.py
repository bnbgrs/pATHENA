"""Cryptographic publisher identity verification for future pATHENA plugins.

This module verifies detached Ed25519 signatures over a versioned, canonical
plugin identity payload. Display-oriented manifest publisher metadata is never
treated as authenticated identity. No plugin code is imported or executed here.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from athena.plugins.manifest import PluginManifest

PLUGIN_PUBLISHER_SIGNATURE_VERSION = "pathena-plugin-publisher-v1"
_KEY_ID_RE = re.compile(r"^[a-z0-9]+(?:[._:-][a-z0-9]+)*$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PluginPublisherIdentityError(ValueError):
    """Raised when authenticated plugin publisher identity cannot be established."""


@dataclass(frozen=True, slots=True)
class TrustedPluginPublisher:
    """Explicit trust root for one authenticated plugin publisher key."""

    key_id: str
    public_key: bytes

    def __post_init__(self) -> None:
        if not _KEY_ID_RE.fullmatch(self.key_id):
            raise PluginPublisherIdentityError("Plugin publisher key_id is invalid.")
        if len(self.public_key) != 32:
            raise PluginPublisherIdentityError(
                "Ed25519 plugin publisher public keys must be exactly 32 bytes."
            )


@dataclass(frozen=True, slots=True)
class VerifiedPluginPublisherIdentity:
    """Authenticated identity result, deliberately separate from display metadata."""

    key_id: str
    signature_version: str
    package_sha256: str


def canonical_plugin_identity_payload(
    manifest: PluginManifest,
    *,
    package_sha256: str,
) -> bytes:
    """Return the exact versioned bytes that a trusted publisher signs.

    The signed identity binds executable selection and requested authority to the
    package digest. Human-readable publisher metadata is intentionally excluded so
    it cannot become an authentication signal or alter signature semantics.
    """

    if not isinstance(manifest, PluginManifest):
        raise TypeError("Plugin identity payload requires a validated PluginManifest.")
    normalized_digest = package_sha256.strip().lower()
    if not _SHA256_RE.fullmatch(normalized_digest):
        raise PluginPublisherIdentityError("Plugin package_sha256 must be 64 lowercase hex digits.")

    payload = {
        "signature_version": PLUGIN_PUBLISHER_SIGNATURE_VERSION,
        "plugin_id": manifest.plugin_id,
        "version": manifest.version,
        "api_version": manifest.api_version,
        "entrypoint": manifest.entrypoint,
        "permissions": sorted(item.value for item in manifest.permissions),
        "capabilities": sorted(item.value for item in manifest.capabilities),
        "package_sha256": normalized_digest,
    }
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def verify_plugin_publisher_identity(
    manifest: PluginManifest,
    *,
    package_bytes: bytes,
    signer_key_id: str,
    signature_b64: str,
    trust_roots: Mapping[str, TrustedPluginPublisher],
) -> VerifiedPluginPublisherIdentity:
    """Verify one plugin package against an explicitly configured trust root.

    Unknown signers, malformed signatures, trust-root/key-id mismatches and any
    manifest/package tampering fail closed. The function performs no dynamic import
    and does not consult manifest ``publisher`` display metadata for trust.
    """

    if not isinstance(package_bytes, bytes):
        raise TypeError("Plugin package bytes must be bytes.")
    if not isinstance(signer_key_id, str) or not _KEY_ID_RE.fullmatch(signer_key_id):
        raise PluginPublisherIdentityError("Plugin signer key_id is invalid.")
    trusted = trust_roots.get(signer_key_id)
    if trusted is None:
        raise PluginPublisherIdentityError("Plugin signer is not trusted.")
    if trusted.key_id != signer_key_id:
        raise PluginPublisherIdentityError("Plugin trust root key_id does not match its map key.")
    if not isinstance(signature_b64, str) or not signature_b64:
        raise PluginPublisherIdentityError("Plugin publisher signature is missing.")
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, binascii.Error) as exc:  # type: ignore[name-defined]
        raise PluginPublisherIdentityError("Plugin publisher signature is not valid base64.") from exc
    if len(signature) != 64:
        raise PluginPublisherIdentityError("Ed25519 plugin publisher signature must be 64 bytes.")

    package_sha256 = hashlib.sha256(package_bytes).hexdigest()
    payload = canonical_plugin_identity_payload(
        manifest,
        package_sha256=package_sha256,
    )
    try:
        Ed25519PublicKey.from_public_bytes(trusted.public_key).verify(signature, payload)
    except (InvalidSignature, ValueError) as exc:
        raise PluginPublisherIdentityError("Plugin publisher signature verification failed.") from exc

    return VerifiedPluginPublisherIdentity(
        key_id=signer_key_id,
        signature_version=PLUGIN_PUBLISHER_SIGNATURE_VERSION,
        package_sha256=package_sha256,
    )
