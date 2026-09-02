"""Persistent reconstructible HNSW sidecars for semantic candidate search."""

from __future__ import annotations

import hashlib
import importlib
import math
import os
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from numbers import Real
from pathlib import Path
from typing import Protocol

import numpy as np

_HNSW_FORMAT_VERSION = 1
_DEFAULT_CONNECTIVITY = 16
_DEFAULT_EXPANSION_ADD = 128
_DEFAULT_EXPANSION_SEARCH = 64


class HnswIndexError(RuntimeError):
    """Raised when a reconstructible HNSW sidecar cannot be used safely."""


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise HnswIndexError(f"{label} must be a positive integer.")
    return value


def _nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise HnswIndexError(f"{label} must be a non-negative integer.")
    return value


def _normalized_model_id(value: object) -> str:
    if not isinstance(value, str):
        raise HnswIndexError("HNSW model id must be text.")
    normalized = value.strip()
    if not normalized:
        raise HnswIndexError("HNSW model id must not be empty.")
    return normalized


def _real_float(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise HnswIndexError(f"{label} must be numeric.")
    return float(value)


def _validate_vector(
    vector: Sequence[float],
    *,
    dimensions: int,
    label: str,
) -> None:
    if len(vector) != dimensions:
        raise HnswIndexError(f"{label} dimensions differ from the index.")
    for component in vector:
        normalized_component = _real_float(component, f"{label} component")
        if not math.isfinite(normalized_component):
            raise HnswIndexError(f"{label} contains a non-finite component.")


@dataclass(frozen=True, slots=True)
class HnswMatch:
    reference: bytes
    similarity: float

    def __post_init__(self) -> None:
        if not isinstance(self.reference, bytes) or not self.reference:
            raise HnswIndexError("HNSW match reference must be non-empty bytes.")
        normalized_similarity = _real_float(
            self.similarity,
            "HNSW match similarity",
        )
        if not math.isfinite(normalized_similarity) or not -1.0 <= normalized_similarity <= 1.0:
            raise HnswIndexError("HNSW match similarity must be finite and between -1 and 1.")


class _HnswBackend(Protocol):
    @property
    def size(self) -> int: ...

    @property
    def dimensions(self) -> int: ...

    def add(self, key: int, vector: Sequence[float]) -> None: ...

    def search(self, vector: Sequence[float], limit: int) -> tuple[tuple[int, float], ...]: ...

    def save(self, path: Path) -> None: ...


BackendFactory = Callable[[int, Path | None], _HnswBackend]


class HnswIndexStore:
    """Own one model/snapshot-scoped USearch HNSW index plus fixed-size refs."""

    def __init__(
        self,
        root: Path,
        *,
        namespace: str,
        reference_size: int,
        backend_factory: BackendFactory | None = None,
    ) -> None:
        if not isinstance(root, Path):
            raise TypeError("HNSW root must be a pathlib.Path.")
        if not isinstance(namespace, str):
            raise ValueError("HNSW namespace must be text.")
        normalized_namespace = namespace.strip()
        if not normalized_namespace or not normalized_namespace.replace("-", "").isalnum():
            raise ValueError("HNSW namespace must be a simple non-empty identifier.")
        if isinstance(reference_size, bool) or not isinstance(reference_size, int) or reference_size < 1:
            raise ValueError("HNSW reference size must be a positive integer.")
        if root.is_symlink():
            raise HnswIndexError("HNSW root must not be a symbolic link.")
        self.root = root
        self.namespace = normalized_namespace
        self.reference_size = reference_size
        self._backend_factory = backend_factory or _usearch_backend_factory

    def ready(
        self,
        *,
        model_id: str,
        snapshot: int,
        dimensions: int,
        document_count: int,
    ) -> bool:
        try:
            normalized_model_id = _normalized_model_id(model_id)
            validated_snapshot = _nonnegative_int(snapshot, "HNSW snapshot")
            validated_dimensions = _positive_int(dimensions, "HNSW dimensions")
            validated_document_count = _nonnegative_int(
                document_count,
                "HNSW document count",
            )
        except HnswIndexError:
            return False
        if validated_document_count == 0:
            return True
        index_path, refs_path = self._paths(
            model_id=normalized_model_id,
            snapshot=validated_snapshot,
        )
        if (
            index_path.is_symlink()
            or refs_path.is_symlink()
            or not index_path.is_file()
            or not refs_path.is_file()
        ):
            return False
        try:
            if refs_path.stat().st_size != validated_document_count * self.reference_size:
                return False
            backend = self._backend_factory(validated_dimensions, index_path)
            return (
                backend.size == validated_document_count
                and backend.dimensions == validated_dimensions
            )
        except (OSError, RuntimeError, ValueError, ImportError):
            return False

    def build(
        self,
        *,
        model_id: str,
        snapshot: int,
        dimensions: int,
        entries: Sequence[tuple[bytes, Sequence[float]]],
    ) -> tuple[Path, Path] | None:
        normalized_model_id = _normalized_model_id(model_id)
        validated_snapshot = _nonnegative_int(snapshot, "HNSW snapshot")
        validated_dimensions = _positive_int(dimensions, "HNSW dimensions")
        if self.root.is_symlink():
            raise HnswIndexError("HNSW root must not be a symbolic link.")
        if not entries:
            self._remove_model_files(model_id=normalized_model_id, keep_snapshot=None)
            return None

        backend = self._backend_factory(validated_dimensions, None)
        references = bytearray()
        for key, (reference, vector) in enumerate(entries, start=1):
            if not isinstance(reference, bytes) or len(reference) != self.reference_size:
                raise HnswIndexError("HNSW reference has an invalid fixed size.")
            _validate_vector(
                vector,
                dimensions=validated_dimensions,
                label="HNSW vector",
            )
            backend.add(key, vector)
            references.extend(reference)

        if backend.size != len(entries) or backend.dimensions != validated_dimensions:
            raise HnswIndexError("HNSW backend did not retain the complete index.")

        self.root.mkdir(parents=True, exist_ok=True)
        if self.root.is_symlink() or not self.root.is_dir():
            raise HnswIndexError("HNSW root is not a safe directory.")
        index_path, refs_path = self._paths(
            model_id=normalized_model_id,
            snapshot=validated_snapshot,
        )
        if index_path.is_symlink() or refs_path.is_symlink():
            raise HnswIndexError("HNSW sidecar destination must not be a symbolic link.")
        suffix = uuid.uuid4().hex
        index_temp = index_path.with_name(f".{index_path.name}.{suffix}.tmp")
        refs_temp = refs_path.with_name(f".{refs_path.name}.{suffix}.tmp")
        try:
            backend.save(index_temp)
            with refs_temp.open("xb") as handle:
                handle.write(references)
                handle.flush()
                os.fsync(handle.fileno())
            if index_path.is_symlink() or refs_path.is_symlink():
                raise HnswIndexError("HNSW sidecar destination became a symbolic link.")
            os.replace(refs_temp, refs_path)
            os.replace(index_temp, index_path)
        finally:
            index_temp.unlink(missing_ok=True)
            refs_temp.unlink(missing_ok=True)

        self._remove_model_files(
            model_id=normalized_model_id,
            keep_snapshot=validated_snapshot,
        )
        if not self.ready(
            model_id=normalized_model_id,
            snapshot=validated_snapshot,
            dimensions=validated_dimensions,
            document_count=len(entries),
        ):
            raise HnswIndexError("Published HNSW sidecar failed validation.")
        return index_path, refs_path

    def search(
        self,
        query_vector: Sequence[float],
        *,
        model_id: str,
        snapshot: int,
        dimensions: int,
        document_count: int,
        limit: int,
    ) -> tuple[HnswMatch, ...]:
        normalized_model_id = _normalized_model_id(model_id)
        validated_snapshot = _nonnegative_int(snapshot, "HNSW snapshot")
        validated_dimensions = _positive_int(dimensions, "HNSW dimensions")
        validated_document_count = _nonnegative_int(
            document_count,
            "HNSW document count",
        )
        validated_limit = _positive_int(limit, "HNSW search limit")
        _validate_vector(
            query_vector,
            dimensions=validated_dimensions,
            label="HNSW query vector",
        )
        if validated_document_count == 0:
            return ()
        if not self.ready(
            model_id=normalized_model_id,
            snapshot=validated_snapshot,
            dimensions=validated_dimensions,
            document_count=validated_document_count,
        ):
            raise HnswIndexError("HNSW sidecar is missing, stale, or invalid.")

        index_path, refs_path = self._paths(
            model_id=normalized_model_id,
            snapshot=validated_snapshot,
        )
        backend = self._backend_factory(validated_dimensions, index_path)
        raw_matches = backend.search(
            query_vector,
            min(validated_limit, validated_document_count),
        )
        matches: list[HnswMatch] = []
        with refs_path.open("rb") as references:
            for key, distance in raw_matches:
                if isinstance(key, bool) or not isinstance(key, int):
                    raise HnswIndexError("HNSW returned a non-integer reference key.")
                if not 1 <= key <= validated_document_count:
                    raise HnswIndexError("HNSW returned an out-of-range reference key.")
                normalized_distance = _real_float(
                    distance,
                    "HNSW distance",
                )
                if not math.isfinite(normalized_distance):
                    raise HnswIndexError("HNSW returned a non-finite distance.")
                references.seek((key - 1) * self.reference_size)
                reference = references.read(self.reference_size)
                if len(reference) != self.reference_size:
                    raise HnswIndexError("HNSW reference sidecar is truncated.")
                similarity = max(-1.0, min(1.0, 1.0 - normalized_distance))
                matches.append(HnswMatch(reference=reference, similarity=similarity))
        return tuple(matches)

    def delete(self, *, model_id: str) -> int:
        """Delete only reconstructible HNSW sidecars for one embedding space."""
        return self._remove_model_files(model_id=model_id, keep_snapshot=None)

    def _paths(self, *, model_id: str, snapshot: int) -> tuple[Path, Path]:
        normalized_model_id = _normalized_model_id(model_id)
        validated_snapshot = _nonnegative_int(snapshot, "HNSW snapshot")
        digest = hashlib.sha256(normalized_model_id.encode("utf-8")).hexdigest()[:24]
        stem = (
            f"v{_HNSW_FORMAT_VERSION}-{self.namespace}-{digest}-snapshot-{validated_snapshot}"
        )
        return self.root / f"{stem}.usearch", self.root / f"{stem}.refs"

    def _remove_model_files(self, *, model_id: str, keep_snapshot: int | None) -> int:
        normalized_model_id = _normalized_model_id(model_id)
        validated_keep_snapshot = (
            None
            if keep_snapshot is None
            else _nonnegative_int(keep_snapshot, "HNSW keep snapshot")
        )
        if self.root.is_symlink():
            raise HnswIndexError("HNSW root must not be a symbolic link.")
        if not self.root.exists():
            return 0
        if not self.root.is_dir():
            raise HnswIndexError("HNSW root is not a directory.")
        digest = hashlib.sha256(normalized_model_id.encode("utf-8")).hexdigest()[:24]
        prefix = f"v{_HNSW_FORMAT_VERSION}-{self.namespace}-{digest}-snapshot-"
        keep_names: set[str] = set()
        if validated_keep_snapshot is not None:
            index_path, refs_path = self._paths(
                model_id=normalized_model_id,
                snapshot=validated_keep_snapshot,
            )
            keep_names = {index_path.name, refs_path.name}
        removed = 0
        for path in self.root.iterdir():
            if path.name.startswith(prefix) and path.name not in keep_names:
                path.unlink(missing_ok=True)
                removed += 1
        return removed


class _USearchBackend:
    def __init__(self, dimensions: int, path: Path | None) -> None:
        try:
            module = importlib.import_module("usearch.index")
            index_type = module.__dict__.get("Index")
            if index_type is None:
                raise AttributeError("usearch.index.Index is unavailable")
        except (ImportError, AttributeError) as exc:
            raise HnswIndexError(
                "USearch is required for ATHENA HNSW retrieval. "
                "Install the pinned project dependencies."
            ) from exc
        if path is None:
            self._index = index_type(
                ndim=dimensions,
                metric="cos",
                dtype="f32",
                connectivity=_DEFAULT_CONNECTIVITY,
                expansion_add=_DEFAULT_EXPANSION_ADD,
                expansion_search=_DEFAULT_EXPANSION_SEARCH,
            )
        else:
            restored = index_type.restore(str(path), view=False)
            if restored is None:
                raise HnswIndexError("USearch did not restore the persisted HNSW index.")
            self._index = restored

    @property
    def size(self) -> int:
        return int(len(self._index))

    @property
    def dimensions(self) -> int:
        return int(self._index.ndim)

    def add(self, key: int, vector: Sequence[float]) -> None:
        packed = np.asarray(vector, dtype=np.float32)
        self._index.add(key, packed)

    def search(self, vector: Sequence[float], limit: int) -> tuple[tuple[int, float], ...]:
        packed = np.asarray(vector, dtype=np.float32)
        matches = self._index.search(packed, limit)
        return tuple((int(match.key), float(match.distance)) for match in matches)

    def save(self, path: Path) -> None:
        self._index.save(str(path))


def _usearch_backend_factory(dimensions: int, path: Path | None) -> _HnswBackend:
    return _USearchBackend(dimensions, path)
