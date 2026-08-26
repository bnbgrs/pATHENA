from __future__ import annotations

import base64
import hashlib

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from athena.plugins.identity import (
    PLUGIN_PUBLISHER_SIGNATURE_VERSION,
    PluginPublisherIdentityError,
    TrustedPluginPublisher,
    canonical_plugin_identity_payload,
    verify_plugin_publisher_identity,
)
from athena.plugins.manifest import PluginManifest


def _manifest(*, name: str = "Example", publisher: str = "Display Corp") -> PluginManifest:
    return PluginManifest.from_mapping(
        {
            "plugin_id": "example.plugin",
            "name": name,
            "version": "1.2.3",
            "api_version": "1",
            "entrypoint": "example.plugin:activate",
            "permissions": ["sources.read"],
            "capabilities": ["read_selected_sources"],
            "publisher": {"name": publisher},
        }
    )


def _keypair() -> tuple[Ed25519PrivateKey, TrustedPluginPublisher]:
    private = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return private, TrustedPluginPublisher(key_id="publisher.example.v1", public_key=public)


def _signature(
    private: Ed25519PrivateKey,
    manifest: PluginManifest,
    package: bytes,
) -> str:
    payload = canonical_plugin_identity_payload(
        manifest,
        package_sha256=hashlib.sha256(package).hexdigest(),
    )
    return base64.b64encode(private.sign(payload)).decode("ascii")


def test_valid_trusted_signature_returns_authenticated_identity() -> None:
    manifest = _manifest()
    package = b"signed plugin package bytes"
    private, trusted = _keypair()

    result = verify_plugin_publisher_identity(
        manifest,
        package_bytes=package,
        signer_key_id=trusted.key_id,
        signature_b64=_signature(private, manifest, package),
        trust_roots={trusted.key_id: trusted},
    )

    assert result.key_id == trusted.key_id
    assert result.signature_version == PLUGIN_PUBLISHER_SIGNATURE_VERSION
    assert result.package_sha256 == hashlib.sha256(package).hexdigest()


def test_unknown_signer_fails_closed() -> None:
    manifest = _manifest()
    package = b"package"
    private, trusted = _keypair()

    with pytest.raises(PluginPublisherIdentityError, match="not trusted"):
        verify_plugin_publisher_identity(
            manifest,
            package_bytes=package,
            signer_key_id=trusted.key_id,
            signature_b64=_signature(private, manifest, package),
            trust_roots={},
        )


def test_package_tampering_invalidates_signature() -> None:
    manifest = _manifest()
    package = b"package"
    private, trusted = _keypair()
    signature = _signature(private, manifest, package)

    with pytest.raises(PluginPublisherIdentityError, match="verification failed"):
        verify_plugin_publisher_identity(
            manifest,
            package_bytes=package + b"-tampered",
            signer_key_id=trusted.key_id,
            signature_b64=signature,
            trust_roots={trusted.key_id: trusted},
        )


def test_security_relevant_manifest_tampering_invalidates_signature() -> None:
    manifest = _manifest(name="Original")
    package = b"package"
    private, trusted = _keypair()
    signature = _signature(private, manifest, package)
    altered = PluginManifest.from_mapping(
        {
            "plugin_id": "example.plugin",
            "name": "Original",
            "version": "1.2.4",
            "api_version": "1",
            "entrypoint": "example.plugin:activate",
            "permissions": ["sources.read"],
            "capabilities": ["read_selected_sources"],
            "publisher": {"name": "Display Corp"},
        }
    )

    with pytest.raises(PluginPublisherIdentityError, match="verification failed"):
        verify_plugin_publisher_identity(
            altered,
            package_bytes=package,
            signer_key_id=trusted.key_id,
            signature_b64=signature,
            trust_roots={trusted.key_id: trusted},
        )


def test_display_publisher_metadata_is_not_authenticated_identity() -> None:
    original = _manifest(publisher="Display Corp")
    altered_display = _manifest(publisher="Someone Else")
    package = b"package"
    private, trusted = _keypair()
    signature = _signature(private, original, package)

    result = verify_plugin_publisher_identity(
        altered_display,
        package_bytes=package,
        signer_key_id=trusted.key_id,
        signature_b64=signature,
        trust_roots={trusted.key_id: trusted},
    )

    assert altered_display.publisher_mapping()["name"] == "Someone Else"
    assert result.key_id == trusted.key_id


def test_malformed_signature_and_trust_root_mismatch_fail_closed() -> None:
    manifest = _manifest()
    private, trusted = _keypair()
    other = TrustedPluginPublisher(key_id="publisher.other.v1", public_key=trusted.public_key)

    with pytest.raises(PluginPublisherIdentityError, match="valid base64"):
        verify_plugin_publisher_identity(
            manifest,
            package_bytes=b"package",
            signer_key_id=trusted.key_id,
            signature_b64="%%%",
            trust_roots={trusted.key_id: trusted},
        )

    with pytest.raises(PluginPublisherIdentityError, match="does not match"):
        verify_plugin_publisher_identity(
            manifest,
            package_bytes=b"package",
            signer_key_id=trusted.key_id,
            signature_b64=_signature(private, manifest, b"package"),
            trust_roots={trusted.key_id: other},
        )
