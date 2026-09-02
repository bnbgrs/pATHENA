from __future__ import annotations

import pytest

from athena.model.ports import controlled_structured_contract_prefix


@pytest.mark.parametrize(
    "schema_id",
    [" schema", "schema ", "schema\nnext", "schema\rnext", "schema\tnext", "schema\x00next", "schema\x7fnext"],
)
def test_controlled_structured_contract_rejects_noncanonical_schema_ids(
    schema_id: str,
) -> None:
    with pytest.raises(ValueError, match="control characters"):
        controlled_structured_contract_prefix(schema_id)


def test_controlled_structured_contract_preserves_canonical_schema_id() -> None:
    prefix = controlled_structured_contract_prefix("athena.answer.v1")

    assert "ATHENA_SCHEMA_ID: athena.answer.v1\n" in prefix
    assert prefix.endswith("ATHENA_JSON_SCHEMA: ")
