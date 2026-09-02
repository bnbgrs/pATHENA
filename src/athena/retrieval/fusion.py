"""Rank-based fusion primitives for heterogeneous retrieval methods."""

from __future__ import annotations

DEFAULT_RRF_K = 60


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer.")
    return value


def reciprocal_rank_contribution(rank: int, *, k: int = DEFAULT_RRF_K) -> float:
    """Return one Reciprocal Rank Fusion contribution for a 1-based rank."""
    validated_rank = _positive_int(rank, "RRF rank")
    validated_k = _positive_int(k, "RRF k")
    denominator = validated_k + validated_rank
    try:
        return 1.0 / denominator
    except OverflowError:
        # Python must convert very large integers to float for true division.
        # Once that conversion overflows, the mathematically positive RRF
        # contribution is below the representable range relevant to ranking.
        return 0.0
