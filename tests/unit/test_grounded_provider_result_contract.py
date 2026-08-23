from __future__ import annotations

import json

import pytest

from athena.chat.grounded_provider_result_contract import (
    GroundedProviderResultContractError,
    validate_provider_result_contract,
)


@pytest.mark.parametrize("value", [None, b"text", 1, True, object()])
def test_provider_result_rejects_non_text_assistant_content(value: object) -> None:
    with pytest.raises(GroundedProviderResultContractError, match="assistant content must be text"):
        validate_provider_result_contract(
            assistant_content=value,  # type: ignore[arg-type]
            receipt_payload_json=json.dumps({"assistant_text": "text"}),
        )


@pytest.mark.parametrize("value", [None, b"{}", 1, True, object()])
def test_provider_result_rejects_non_text_receipt_payload(value: object) -> None:
    with pytest.raises(GroundedProviderResultContractError, match="receipt payload must be text"):
        validate_provider_result_contract(
            assistant_content="text",
            receipt_payload_json=value,  # type: ignore[arg-type]
        )


def test_provider_result_requires_exact_receipt_assistant_text() -> None:
    with pytest.raises(GroundedProviderResultContractError, match="match assistant content exactly"):
        validate_provider_result_contract(
            assistant_content="exact text",
            receipt_payload_json=json.dumps({"assistant_text": "different text"}),
        )


def test_provider_result_accepts_exact_text_match() -> None:
    validate_provider_result_contract(
        assistant_content="exact text",
        receipt_payload_json=json.dumps({"assistant_text": "exact text"}),
    )
