"""Bind a durable Grounded request fingerprint to its provider-facing ContextPackage."""

from __future__ import annotations

import hashlib
import json

from athena.chat.request_fingerprint import (
    CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION,
    ChatRequestFingerprint,
)
from athena.retrieval.context_package import ContextPackage, ContextPackageError


class GroundedRequestContextBindingError(ValueError):
    """A durable request fingerprint conflicts with its provider-facing package."""


def _context_configuration(package: ContextPackage) -> dict[str, object] | None:
    configuration_json = package.model_signature.context_configuration_json
    if configuration_json is None:
        return None
    try:
        raw = json.loads(configuration_json)
    except json.JSONDecodeError as exc:
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage context configuration is invalid JSON."
        ) from exc
    if not isinstance(raw, dict):
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage context configuration must be a JSON object."
        )
    return raw


def validate_grounded_request_context_binding(
    *,
    package: ContextPackage,
    fingerprint: ChatRequestFingerprint,
) -> None:
    """Fail closed when explicitly requested model inputs drift before execution."""
    if fingerprint.format_version != CHAT_REQUEST_FINGERPRINT_FORMAT_VERSION:
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint format version is unsupported."
        )
    expected_sha256 = hashlib.sha256(fingerprint.payload_json.encode("utf-8")).hexdigest()
    if fingerprint.payload_sha256 != expected_sha256:
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint checksum does not match its payload."
        )
    try:
        payload = json.loads(fingerprint.payload_json)
    except json.JSONDecodeError as exc:
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint is not valid JSON."
        ) from exc
    if not isinstance(payload, dict):
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint must contain a JSON object."
        )
    if payload.get("fingerprint_format_version") != fingerprint.format_version:
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint payload version is inconsistent."
        )
    if payload.get("mode") != "grounded":
        raise GroundedRequestContextBindingError(
            "Grounded request fingerprint must use Grounded mode."
        )

    try:
        package_max_output_tokens, package_reasoning_mode = package.generation_controls()
        package_temperature = package.generation_temperature()
    except ContextPackageError as exc:
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage generation controls are invalid."
        ) from exc
    configuration = _context_configuration(package)

    requested_model_id = payload.get("requested_model_id")
    if (
        requested_model_id is not None
        and requested_model_id != package.model_signature.model_identifier
    ):
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage model conflicts with the durable request fingerprint."
        )

    requested_embedding_model_id = payload.get("requested_embedding_model_id")
    if requested_embedding_model_id is not None and (
        configuration is None
        or configuration.get("embedding_model_id") != requested_embedding_model_id
    ):
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage embedding model conflicts with the durable request fingerprint."
        )

    effective_context_limit = payload.get("effective_context_limit")
    if (
        effective_context_limit is not None
        and effective_context_limit != package.budget.effective_context_limit
    ):
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage context limit conflicts with the durable request fingerprint."
        )

    requested_max_output_tokens = payload.get("max_output_tokens")
    if (
        requested_max_output_tokens is not None
        and requested_max_output_tokens != package_max_output_tokens
    ):
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage output limit conflicts with the durable request fingerprint."
        )

    requested_temperature = payload.get("temperature")
    if requested_temperature != package_temperature:
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage temperature conflicts with the durable request fingerprint."
        )

    requested_reasoning_mode = payload.get("reasoning_mode")
    if requested_reasoning_mode != package_reasoning_mode:
        raise GroundedRequestContextBindingError(
            "Grounded ContextPackage reasoning mode conflicts with the durable request fingerprint."
        )
