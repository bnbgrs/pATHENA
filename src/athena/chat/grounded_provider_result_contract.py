"""Semantic integrity contract for durable Grounded provider results."""

from __future__ import annotations

import json


class GroundedProviderResultContractError(ValueError):
    """Provider-result content and its durable receipt disagree."""


def validate_provider_result_contract(
    *,
    assistant_content: str,
    receipt_payload_json: str,
) -> None:
    """Require the durable receipt to identify the exact assistant text."""
    if not assistant_content.strip():
        raise GroundedProviderResultContractError(
            "Provider result assistant content must not be blank."
        )
    try:
        payload = json.loads(receipt_payload_json)
    except json.JSONDecodeError as exc:
        raise GroundedProviderResultContractError(
            "Provider result receipt payload must be valid JSON."
        ) from exc
    if not isinstance(payload, dict):
        raise GroundedProviderResultContractError(
            "Provider result receipt payload must be a JSON object."
        )
    assistant_text = payload.get("assistant_text")
    if not isinstance(assistant_text, str) or not assistant_text.strip():
        raise GroundedProviderResultContractError(
            "Provider result receipt payload requires non-empty assistant_text."
        )
    if assistant_text != assistant_content:
        raise GroundedProviderResultContractError(
            "Provider result receipt assistant_text must match assistant content exactly."
        )
