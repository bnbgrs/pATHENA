from __future__ import annotations

import pytest

from athena.model.ports import controlled_structured_contract_prefix


@pytest.mark.parametrize(
    "schema_id",
    [
        "schema\nother",
        "schema\rother",
        "schema\x85other",
        "schema\u2028other",
        "schema\u2029other",
        "schema\x7fother",
    ],
)
def test_structured_contract_rejects_control_and_unicode_line_separators(
    schema_id: str,
) -> None:
    with pytest.raises(ValueError, match="single-line"):
        controlled_structured_contract_prefix(schema_id)


def test_structured_contract_preserves_valid_unicode_schema_id() -> None:
    value = controlled_structured_contract_prefix("analyse.schéma-v1")

    assert "ATHENA_SCHEMA_ID: analyse.schéma-v1\n" in value
