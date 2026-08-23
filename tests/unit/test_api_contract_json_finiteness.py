from __future__ import annotations

import math
from dataclasses import dataclass

import pytest

from athena.api.contracts import ApiContract, JsonValue


@dataclass(frozen=True, slots=True)
class _FloatContract(ApiContract):
    value: float


@dataclass(frozen=True, slots=True)
class _NestedContract(ApiContract):
    payload: dict[str, JsonValue]


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_api_contract_rejects_nonfinite_top_level_float(value: float) -> None:
    with pytest.raises(TypeError, match="floats must be finite"):
        _FloatContract(value=value).to_dict()


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_api_contract_rejects_nonfinite_nested_float(value: float) -> None:
    contract = _NestedContract(payload={"items": [1, value]})

    with pytest.raises(TypeError, match="floats must be finite"):
        contract.to_dict()


def test_api_contract_keeps_finite_float_and_boolean_types() -> None:
    contract = _NestedContract(payload={"confidence": 0.75, "ready": True})

    assert contract.to_dict() == {
        "payload": {"confidence": 0.75, "ready": True}
    }
