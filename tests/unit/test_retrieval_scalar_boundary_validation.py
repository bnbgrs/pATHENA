from __future__ import annotations

import pytest

from athena.retrieval.fusion import reciprocal_rank_contribution
from athena.retrieval.lexical_relevance import required_term_matches


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.0, "1", None])
def test_rrf_rank_rejects_non_positive_exact_int(value: object) -> None:
    with pytest.raises(ValueError):
        reciprocal_rank_contribution(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [True, False, 0, -1, 60.0, "60", None])
def test_rrf_k_rejects_non_positive_exact_int(value: object) -> None:
    with pytest.raises(ValueError):
        reciprocal_rank_contribution(1, k=value)  # type: ignore[arg-type]


def test_rrf_current_contract_is_unchanged() -> None:
    assert reciprocal_rank_contribution(1) == 1.0 / 61.0
    assert reciprocal_rank_contribution(3, k=10) == 1.0 / 13.0


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.0, "1", None])
def test_required_term_matches_rejects_non_positive_exact_int(value: object) -> None:
    with pytest.raises(ValueError):
        required_term_matches(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("term_count", "expected"),
    [(1, 1), (3, 3), (4, 3), (5, 3), (6, 4), (9, 6)],
)
def test_required_term_matches_current_thresholds(
    term_count: int,
    expected: int,
) -> None:
    assert required_term_matches(term_count) == expected
