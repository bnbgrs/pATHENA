from __future__ import annotations

import math

import pytest

from athena.retrieval.fusion import reciprocal_rank_contribution


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "1", None])
def test_rrf_rejects_non_positive_integer_rank(value: object) -> None:
    with pytest.raises(ValueError, match="RRF rank must be a positive integer"):
        reciprocal_rank_contribution(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "60", None])
def test_rrf_rejects_non_positive_integer_k(value: object) -> None:
    with pytest.raises(ValueError, match="RRF k must be a positive integer"):
        reciprocal_rank_contribution(1, k=value)  # type: ignore[arg-type]


def test_rrf_huge_integer_inputs_underflow_safely_instead_of_overflowing() -> None:
    contribution = reciprocal_rank_contribution(10**400, k=10**400)

    assert contribution == 0.0
    assert math.isfinite(contribution)


def test_rrf_normal_boundary_remains_positive_and_finite() -> None:
    contribution = reciprocal_rank_contribution(1, k=60)

    assert contribution == pytest.approx(1.0 / 61.0)
    assert math.isfinite(contribution)
