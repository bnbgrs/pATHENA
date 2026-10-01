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


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"channel": "beta"}, id="channel-text"),
        pytest.param({"manifest_version": True}, id="manifest-version-bool"),
        pytest.param({"manifest_version": 2}, id="manifest-version-unsupported"),
        pytest.param({"app_version": ""}, id="app-version-empty"),
        pytest.param({"app_version": "01.2.3"}, id="app-version-core-leading-zero"),
        pytest.param({"app_version": "1.2.3-01"}, id="app-version-prerelease-leading-zero"),
        pytest.param({"package_name": "../athena.zip"}, id="package-name-traversal"),
        pytest.param({"package_size": True}, id="package-size-bool"),
        pytest.param({"package_size": 0}, id="package-size-zero"),
        pytest.param({"package_sha256": "A" * 64}, id="sha256-noncanonical"),
        pytest.param({"minimum_schema_version": True}, id="minimum-schema-bool"),
        pytest.param({"minimum_schema_version": 0}, id="minimum-schema-zero"),
        pytest.param({"maximum_schema_version": True}, id="maximum-schema-bool"),
        pytest.param({"maximum_schema_version": 39}, id="maximum-schema-before-minimum"),
    ],
)
def test_direct_manifest_construction_rejects_invalid_runtime_values(
    overrides: dict[str, object],
) -> None:
    package = b"signed package"
    values: dict[str, object] = {
        "channel": UpdateChannel.BETA,
        "app_version": "0.1.0-beta.1",
        "package_name": "athena-0.1.0-beta.1.zip",
        "package_size": len(package),
        "package_sha256": hashlib.sha256(package).hexdigest(),
        "minimum_schema_version": 40,
        "maximum_schema_version": 41,
    }
    values.update(overrides)

    with pytest.raises(UpdateVerificationError):
        UpdateManifest(**values)  # type: ignore[arg-type]


def test_manifest_accepts_semver_prerelease_and_build_metadata() -> None:
    package = b"signed package"
    manifest = UpdateManifest(
        channel=UpdateChannel.BETA,
        app_version="1.2.3-beta.1+windows.x64",
        package_name="athena-1.2.3-beta.1-windows-x64.zip",
        package_size=len(package),
        package_sha256=hashlib.sha256(package).hexdigest(),
        minimum_schema_version=40,
        maximum_schema_version=41,
    )

    parsed = UpdateManifest.from_bytes(manifest.to_bytes())

    assert parsed.app_version == "1.2.3-beta.1+windows.x64"


@pytest.mark.parametrize("schema_version", [True, False, 40.0, "40", None])
def test_schema_compatibility_rejects_non_integer_runtime_values(
    schema_version: object,
) -> None:
    manifest = _manifest()

    assert manifest.supports_schema(schema_version) is False  # type: ignore[arg-type]


def test_manifest_parser_runtime_boundaries_fail_closed() -> None:
    with pytest.raises(UpdateVerificationError, match="bytes"):
        UpdateManifest.from_bytes("{}")  # type: ignore[arg-type]

    with pytest.raises(UpdateVerificationError, match="too large"):
        UpdateManifest.from_bytes(b" " * (64 * 1024 + 1))


@pytest.mark.parametrize(
    ("raw", "signature", "public_key"),
    [
        pytest.param("{}", "AA==", b"x" * 32, id="payload-text"),
        pytest.param(b"{}", b"AA==", b"x" * 32, id="signature-bytes"),
        pytest.param(b"{}", "A" * 256, b"x" * 32, id="signature-oversized"),
        pytest.param(b"{}", "AA==", bytearray(b"x" * 32), id="public-key-bytearray"),
        pytest.param(b"{}", "AA==", b"x" * 31, id="public-key-wrong-length"),
    ],
)
def test_signed_manifest_runtime_boundaries_fail_closed(
    raw: object,
    signature: object,
    public_key: object,
) -> None:
    with pytest.raises(UpdateVerificationError):
        verify_signed_manifest(
            raw,  # type: ignore[arg-type]
            signature_base64=signature,  # type: ignore[arg-type]
            public_key=public_key,  # type: ignore[arg-type]
        )

