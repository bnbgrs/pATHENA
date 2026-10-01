"""Fail-closed contracts for signed ATHENA application updates."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, BinaryIO, cast

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

_MANIFEST_VERSION = 1
_MAX_MANIFEST_BYTES = 64 * 1024
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_SEMVER_PATTERN = re.compile(
    r"(?P<major>0|[1-9][0-9]*)\\."
    r"(?P<minor>0|[1-9][0-9]*)\\."
    r"(?P<patch>0|[1-9][0-9]*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*))?"
    r"(?:\\+(?P<build>[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*))?"
)
_PACKAGE_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
_MANIFEST_FIELDS = frozenset(
    {
        "manifest_version",
        "channel",
        "app_version",
        "package_name",
        "package_size",
        "package_sha256",
        "minimum_schema_version",
        "maximum_schema_version",
    }
)


class UpdateVerificationError(ValueError):
    """Raised when update metadata or package integrity cannot be verified."""


class UpdateChannel(StrEnum):
    """Explicitly supported application-update channels."""

    STABLE = "stable"
    BETA = "beta"


def _is_semver(value: str) -> bool:
    match = _SEMVER_PATTERN.fullmatch(value)
    if match is None:
        return False
    prerelease = match.group("prerelease")
    if prerelease is None:
        return True
    for identifier in prerelease.split("."):
        if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
            return False
    return True


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UpdateVerificationError(f"Duplicate update-manifest field: {key!r}.")
        result[key] = value
    return result


def _required_int(payload: dict[str, Any], field: str, *, minimum: int = 0) -> int:
    value = payload[field]
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise UpdateVerificationError(
            f"Update-manifest field {field!r} must be an integer >= {minimum}."
        )
    return value


def _required_string(payload: dict[str, Any], field: str) -> str:
    value = payload[field]
    if not isinstance(value, str):
        raise UpdateVerificationError(
            f"Update-manifest field {field!r} must be a string."
        )
    return value


@dataclass(frozen=True, slots=True)
class UpdateManifest:
    """Authenticated metadata required before an update package is trusted."""

    channel: UpdateChannel
    app_version: str
    package_name: str
    package_size: int
    package_sha256: str
    minimum_schema_version: int
    maximum_schema_version: int
    manifest_version: int = _MANIFEST_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.channel, UpdateChannel):
            raise UpdateVerificationError(
                "Application update channel must be an UpdateChannel value."
            )
        if (
            isinstance(self.manifest_version, bool)
            or not isinstance(self.manifest_version, int)
            or self.manifest_version != _MANIFEST_VERSION
        ):
            raise UpdateVerificationError("Unsupported update-manifest version.")
        if (
            not isinstance(self.app_version, str)
            or not _is_semver(self.app_version)
        ):
            raise UpdateVerificationError("Application update version is invalid.")
        if (
            not isinstance(self.package_name, str)
            or _PACKAGE_NAME_PATTERN.fullmatch(self.package_name) is None
        ):
            raise UpdateVerificationError("Update package name is invalid.")
        if (
            isinstance(self.package_size, bool)
            or not isinstance(self.package_size, int)
            or self.package_size < 1
        ):
            raise UpdateVerificationError(
                "Update package size must be a positive integer."
            )
        if (
            not isinstance(self.package_sha256, str)
            or _SHA256_PATTERN.fullmatch(self.package_sha256) is None
        ):
            raise UpdateVerificationError("Update package SHA-256 is invalid.")
        if (
            isinstance(self.minimum_schema_version, bool)
            or not isinstance(self.minimum_schema_version, int)
            or self.minimum_schema_version < 1
        ):
            raise UpdateVerificationError(
                "Minimum schema version must be a positive integer."
            )
        if (
            isinstance(self.maximum_schema_version, bool)
            or not isinstance(self.maximum_schema_version, int)
            or self.maximum_schema_version < self.minimum_schema_version
        ):
            raise UpdateVerificationError(
                "Maximum schema version must be an integer not below the minimum."
            )

    @classmethod
    def from_bytes(cls, raw: bytes) -> UpdateManifest:
        """Parse strict canonical JSON after signature verification."""
        if not isinstance(raw, bytes):
            raise UpdateVerificationError("Update manifest payload must be bytes.")
        if len(raw) > _MAX_MANIFEST_BYTES:
            raise UpdateVerificationError("Update manifest payload is too large.")
        try:
            parsed: object = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise UpdateVerificationError("Update manifest is not valid UTF-8 JSON.") from exc

        if not isinstance(parsed, dict):
            raise UpdateVerificationError("Update manifest must be a JSON object.")
        payload = cast(dict[str, Any], parsed)
        fields = frozenset(payload)
        if fields != _MANIFEST_FIELDS:
            missing = sorted(_MANIFEST_FIELDS - fields)
            unknown = sorted(fields - _MANIFEST_FIELDS)
            raise UpdateVerificationError(
                f"Update manifest fields are invalid; missing={missing}, unknown={unknown}."
            )

        manifest_version = _required_int(payload, "manifest_version", minimum=1)
        if manifest_version != _MANIFEST_VERSION:
            raise UpdateVerificationError(
                f"Unsupported update-manifest version {manifest_version}."
            )

        try:
            channel = UpdateChannel(_required_string(payload, "channel"))
        except ValueError as exc:
            raise UpdateVerificationError("Unsupported application-update channel.") from exc

        app_version = _required_string(payload, "app_version")
        if not _is_semver(app_version):
            raise UpdateVerificationError("Application update version is invalid.")

        package_name = _required_string(payload, "package_name")
        if _PACKAGE_NAME_PATTERN.fullmatch(package_name) is None:
            raise UpdateVerificationError("Update package name is invalid.")

        package_sha256 = _required_string(payload, "package_sha256")
        if _SHA256_PATTERN.fullmatch(package_sha256) is None:
            raise UpdateVerificationError("Update package SHA-256 is invalid.")

        minimum_schema_version = _required_int(
            payload, "minimum_schema_version", minimum=1
        )
        maximum_schema_version = _required_int(
            payload, "maximum_schema_version", minimum=minimum_schema_version
        )
        manifest = cls(
            manifest_version=manifest_version,
            channel=channel,
            app_version=app_version,
            package_name=package_name,
            package_size=_required_int(payload, "package_size", minimum=1),
            package_sha256=package_sha256,
            minimum_schema_version=minimum_schema_version,
            maximum_schema_version=maximum_schema_version,
        )
        if not hmac.compare_digest(raw, manifest.to_bytes()):
            raise UpdateVerificationError("Update manifest must use canonical JSON encoding.")
        return manifest

    def to_bytes(self) -> bytes:
        """Return the one canonical byte representation covered by the signature."""
        payload = {
            "app_version": self.app_version,
            "channel": self.channel.value,
            "manifest_version": self.manifest_version,
            "maximum_schema_version": self.maximum_schema_version,
            "minimum_schema_version": self.minimum_schema_version,
            "package_name": self.package_name,
            "package_sha256": self.package_sha256,
            "package_size": self.package_size,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def supports_schema(self, schema_version: int) -> bool:
        """Return whether this package declares compatibility with a database schema."""
        if isinstance(schema_version, bool) or not isinstance(schema_version, int):
            return False
        return self.minimum_schema_version <= schema_version <= self.maximum_schema_version


def verify_signed_manifest(
    raw: bytes,
    *,
    signature_base64: str,
    public_key: bytes,
) -> UpdateManifest:
    """Verify the detached Ed25519 signature before accepting update metadata."""
    if not isinstance(raw, bytes):
        raise UpdateVerificationError("Update manifest payload must be bytes.")
    if len(raw) > _MAX_MANIFEST_BYTES:
        raise UpdateVerificationError("Update manifest payload is too large.")
    if not isinstance(signature_base64, str):
        raise UpdateVerificationError("Update manifest signature must be base64 text.")
    if len(signature_base64) > 128:
        raise UpdateVerificationError("Update manifest signature is invalid.")
    if not isinstance(public_key, bytes) or len(public_key) != 32:
        raise UpdateVerificationError("Update manifest public key is invalid.")
    try:
        signature = base64.b64decode(signature_base64, validate=True)
        if len(signature) != 64:
            raise UpdateVerificationError("Update manifest signature is invalid.")
        verifier = Ed25519PublicKey.from_public_bytes(public_key)
        verifier.verify(signature, raw)
    except UpdateVerificationError:
        raise
    except (ValueError, binascii.Error, InvalidSignature) as exc:
        raise UpdateVerificationError("Update manifest signature is invalid.") from exc
    return UpdateManifest.from_bytes(raw)


def verify_package(path: Path, manifest: UpdateManifest) -> None:
    """Verify a regular, non-link package against signed size and SHA-256 metadata."""
    if path.name != manifest.package_name:
        raise UpdateVerificationError("Update package name does not match its manifest.")
    package = _open_verified_package(path)
    try:
        with package:
            metadata = os.fstat(package.fileno())
            if metadata.st_size != manifest.package_size:
                raise UpdateVerificationError(
                    "Update package size does not match its manifest."
                )
            digest = hashlib.sha256()
            for chunk in iter(lambda: package.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise UpdateVerificationError("Update package cannot be read.") from exc
    if not hmac.compare_digest(digest.hexdigest(), manifest.package_sha256):
        raise UpdateVerificationError("Update package SHA-256 does not match its manifest.")


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction is not None and is_junction())


def _open_verified_package(path: Path) -> BinaryIO:
    """Open one package descriptor and prove its path identity before hashing."""
    descriptor = -1
    try:
        parent_stat = os.lstat(path.parent)
        if not stat.S_ISDIR(parent_stat.st_mode) or _is_link_or_junction(path.parent):
            raise UpdateVerificationError(
                "Update package parent must be a regular non-link directory."
            )
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        descriptor = os.open(path, flags)
        path_stat = os.lstat(path)
        opened_stat = os.fstat(descriptor)
        parent_after = os.lstat(path.parent)
        if (
            not stat.S_ISREG(path_stat.st_mode)
            or _is_link_or_junction(path)
            or not stat.S_ISREG(opened_stat.st_mode)
            or not os.path.samestat(opened_stat, path_stat)
            or not os.path.samestat(parent_stat, parent_after)
        ):
            raise UpdateVerificationError(
                "Update package identity changed or resolves through a link."
            )
        package = os.fdopen(descriptor, "rb")
        descriptor = -1
        return package
    except UpdateVerificationError:
        raise
    except OSError as exc:
        raise UpdateVerificationError("Update package cannot be securely opened.") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
