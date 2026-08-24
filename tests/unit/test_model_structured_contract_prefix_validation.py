from __future__ import annotations

import pytest

from athena.model.ports import (
    CONTROLLED_STRUCTURED_CONTRACT_VERSION,
    controlled_structured_contract_prefix,
)


@pytest.mark.parametrize(
    "schema_id",
    [
        "",
        "   ",
        " padded",
        "padded ",
        "schema\nINJECTED: value",
        "schema\rINJECTED: value",
        None,
        1,
        True,
    ],
)
def test_structured_contract_prefix_rejects_noncanonical_schema_id(
    schema_id: object,
) -> None:
    with pytest.raises(ValueError):
        controlled_structured_contract_prefix(schema_id)  # type: ignore[arg-type]


def test_structured_contract_prefix_preserves_exact_control_lines() -> None:
    prefix = controlled_structured_contract_prefix("athena.schema.v1")

    assert prefix.startswith(
        "\n\nATHENA_STRUCTURED_CONTRACT_VERSION: "
        f"{CONTROLLED_STRUCTURED_CONTRACT_VERSION}\n"
        "ATHENA_SCHEMA_ID: athena.schema.v1\n"
    )
    assert prefix.endswith("ATHENA_JSON_SCHEMA: ")
