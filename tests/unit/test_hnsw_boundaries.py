from __future__ import annotations

import math
from pathlib import Path
from typing import Sequence

import pytest

from athena.retrieval.hnsw import HnswIndexError, HnswIndexStore


class _Backend:
    def __init__(
        self,
        dimensions: int,
        *,
        size: int = 1,
        matches: tuple[tuple[int, float], ...] = ((1, 0.25),),
    ) -> None:
        self._dimensions = dimensions
        self._size = size
        self._matches = matches

    @property
    def size(self) -> int:
        return self._size

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def add(self, key: int, vector: Sequence[float]) -> None:
        self._size = max(self._size, key)

    def search(
        self,
        vector: Sequence[float],
        limit: int,
    ) -> tuple[tuple[int, float], ...]:
        return self._matches[:limit]

    def save(self, path: Path) -> None:
        path.write_bytes(b"index")


def _store(
    tmp_path: Path,
    *,
    matches: tuple[tuple[int, float], ...] = ((1, 0.25),),
) -> HnswIndexStore:
    def factory(dimensions: int, path: Path | None) -> _Backend:
        return _Backend(dimensions, matches=matches)

    return HnswIndexStore(
        tmp_path / "hnsw",
        namespace="knowledge",
        reference_size=4,
        backend_factory=factory,
    )


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "4", None])
def test_hnsw_reference_size_requires_positive_integer(
    tmp_path: Path,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="reference size must be a positive integer"):
        HnswIndexStore(
            tmp_path / "hnsw",
            namespace="knowledge",
            reference_size=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [True, False, 0, -1, 1.5, "1", None])
def test_hnsw_search_limit_requires_positive_integer(
    tmp_path: Path,
    value: object,
) -> None:
    store = _store(tmp_path)
    with pytest.raises(HnswIndexError, match="search limit must be a positive integer"):
        store.search(
            (1.0, 0.0),
            model_id="model",
            snapshot=1,
            dimensions=2,
            document_count=0,
            limit=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("component", [True, math.nan, math.inf, -math.inf, "1"])
def test_hnsw_build_rejects_invalid_vector_components(
    tmp_path: Path,
    component: object,
) -> None:
    store = _store(tmp_path)
    with pytest.raises(HnswIndexError):
        store.build(
            model_id="model",
            snapshot=1,
            dimensions=2,
            entries=((b"abcd", (1.0, component)),),  # type: ignore[arg-type]
        )


def test_hnsw_search_rejects_nonfinite_backend_distance(tmp_path: Path) -> None:
    store = _store(tmp_path, matches=((1, math.nan),))
    store.root.mkdir()
    index_path, refs_path = store._paths(model_id="model", snapshot=1)
    index_path.write_bytes(b"index")
    refs_path.write_bytes(b"abcd")

    with pytest.raises(HnswIndexError, match="non-finite distance"):
        store.search(
            (1.0, 0.0),
            model_id="model",
            snapshot=1,
            dimensions=2,
            document_count=1,
            limit=1,
        )


def test_hnsw_ready_rejects_symlink_sidecar(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.root.mkdir()
    index_path, refs_path = store._paths(model_id="model", snapshot=1)
    target = tmp_path / "external-index"
    target.write_bytes(b"index")
    try:
        index_path.symlink_to(target)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"File symlink unavailable: {exc}")
    refs_path.write_bytes(b"abcd")

    assert not store.ready(
        model_id="model",
        snapshot=1,
        dimensions=2,
        document_count=1,
    )
