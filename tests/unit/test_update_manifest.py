from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from athena.update.manifest import (
    UpdateChannel,
    UpdateManifest,
    UpdateVerificationError,
    verify_package,
    verify_signed_manifest,
)


def _manifest(package: bytes = b"signed package") -> UpdateManifest:
    return UpdateManifest(
        channel=UpdateChannel.BETA,
        app_version="0.1.0-beta.1",
        package_name="athena-0.1.0-beta.1.zip",
        package_size=len(package),
        package_sha256=hashlib.sha256(package).hexdigest(),
        minimum_schema_version=40,
        maximum_schema_version=41,
    )


def _public_bytes(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def test_signed_manifest_and_package_are_verified(tmp_path: Path) -> None:
    package = b"signed package"
    manifest = _manifest(package)
    raw = manifest.to_bytes()
    private_key = Ed25519PrivateKey.generate()
    signature = base64.b64encode(private_key.sign(raw)).decode("ascii")

    verified = verify_signed_manifest(
        raw,
        signature_base64=signature,
        public_key=_public_bytes(private_key),
    )
    package_path = tmp_path / manifest.package_name
    package_path.write_bytes(package)
    verify_package(package_path, verified)

    assert verified == manifest
    assert verified.supports_schema(40)
    assert verified.supports_schema(41)
    assert not verified.supports_schema(39)


def test_manifest_rejects_tampering_noncanonical_json_and_unknown_channel() -> None:
    manifest = _manifest()
    raw = manifest.to_bytes()
    private_key = Ed25519PrivateKey.generate()
    signature = base64.b64encode(private_key.sign(raw)).decode("ascii")

    with pytest.raises(UpdateVerificationError, match="signature"):
        verify_signed_manifest(
            raw.replace(b"beta", b"evil"),
            signature_base64=signature,
            public_key=_public_bytes(private_key),
        )

    payload = json.loads(raw)
    with pytest.raises(UpdateVerificationError, match="canonical"):
        UpdateManifest.from_bytes(json.dumps(payload, indent=2).encode("utf-8"))

    payload["channel"] = "nightly"
    unsupported = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    with pytest.raises(UpdateVerificationError, match="channel"):
        UpdateManifest.from_bytes(unsupported)


def test_package_rejects_hash_mismatch_and_symlink(tmp_path: Path) -> None:
    manifest = _manifest()
    package_path = tmp_path / manifest.package_name
    package_path.write_bytes(b"signed packagf")

    with pytest.raises(UpdateVerificationError, match="SHA-256"):
        verify_package(package_path, manifest)

    target = tmp_path / "target.zip"
    target.write_bytes(b"signed package")
    link_root = tmp_path / "link-root"
    link_root.mkdir()
    link = link_root / manifest.package_name
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("Symlink creation is unavailable on this platform.")
    with pytest.raises(UpdateVerificationError, match="package"):
        verify_package(link, manifest)
