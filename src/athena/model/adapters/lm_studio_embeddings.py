"""Local LM Studio embedding adapter."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from athena.model.adapters.lm_studio import (
    LMStudioProvider,
    ModelProviderError,
    ProviderProtocolError,
    ProviderUnavailableError,
)
from athena.model.domain import ModelInfo


def _positive_finite_timeout(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Embedding generation timeout must be a finite number > 0.")
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError("Embedding generation timeout must be a finite number > 0.")
    return parsed


def _model_id(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Embedding model id must be text.")
    normalized = value.strip()
    if not normalized:
        raise ValueError("Embedding model id must not be empty.")
    return normalized


def _embedding_texts(value: object) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ValueError("Embedding texts must be a sequence of text values.")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("Embedding texts must contain text values only.")
        if not item.strip():
            raise ValueError("Embedding texts must not be empty.")
        normalized.append(item)
    return tuple(normalized)


@dataclass(frozen=True, slots=True)
class LMStudioEmbeddingProvider:
    """Generate infrastructure embeddings through local LM Studio."""

    model_provider: LMStudioProvider
    generation_timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        if not isinstance(self.model_provider, LMStudioProvider):
            raise TypeError("Embedding model_provider must be an LMStudioProvider.")
        object.__setattr__(
            self,
            "generation_timeout_seconds",
            _positive_finite_timeout(self.generation_timeout_seconds),
        )

    @property
    def embeddings_url(self) -> str:
        return f"{self.model_provider.base_url}/v1/embeddings"

    def discover_embedding_models(self) -> tuple[ModelInfo, ...]:
        models = self.model_provider.discover_models()
        return tuple(
            model
            for model in models
            if model.model_type.casefold() in {"embedding", "embeddings"}
        )

    def resolve_model(self, requested_model_id: str | None = None) -> ModelInfo:
        models = self.discover_embedding_models()
        if requested_model_id is not None:
            try:
                normalized = _model_id(requested_model_id)
            except ValueError as exc:
                raise ModelProviderError(str(exc)) from exc
            matches = [
                model for model in models if model.backend_model_id == normalized
            ]
            if not matches:
                raise ModelProviderError(
                    f"LM Studio embedding model {normalized!r} is not available."
                )
            return matches[0]

        loaded = [model for model in models if model.loaded]
        candidates = loaded if loaded else list(models)
        if not candidates:
            raise ModelProviderError(
                "LM Studio has no embedding model available to ATHENA."
            )
        if len(candidates) != 1:
            ids = ", ".join(model.backend_model_id for model in candidates)
            raise ModelProviderError(
                "More than one LM Studio embedding model is available. "
                f"Choose one explicitly: {ids}"
            )
        return candidates[0]

    def embed(
        self,
        *,
        model_id: str,
        texts: Sequence[str],
    ) -> tuple[tuple[float, ...], ...]:
        normalized_model_id = _model_id(model_id)
        normalized_texts = _embedding_texts(texts)
        if not normalized_texts:
            return ()

        request_payload = {
            "model": normalized_model_id,
            "input": list(normalized_texts),
        }
        request = Request(
            self.embeddings_url,
            data=json.dumps(request_payload, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.generation_timeout_seconds) as response:
                raw = response.read()
        except HTTPError as exc:
            raise ModelProviderError(
                f"LM Studio returned HTTP {exc.code} during embedding generation."
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ProviderUnavailableError(
                "LM Studio embedding generation failed at "
                f"{self.model_provider.base_url}."
            ) from exc

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderProtocolError(
                "LM Studio returned invalid JSON for embeddings."
            ) from exc
        if not isinstance(payload, Mapping):
            raise ProviderProtocolError(
                "LM Studio returned a non-object embeddings response."
            )

        raw_data = payload.get("data")
        if not isinstance(raw_data, list) or len(raw_data) != len(normalized_texts):
            raise ProviderProtocolError(
                "LM Studio embeddings response has an unexpected data length."
            )

        indexed: dict[int, tuple[float, ...]] = {}
        for raw_item in raw_data:
            if not isinstance(raw_item, Mapping):
                raise ProviderProtocolError(
                    "LM Studio returned an invalid embedding item."
                )
            item = cast(Mapping[str, Any], raw_item)
            index = item.get("index")
            if isinstance(index, bool) or not isinstance(index, int):
                raise ProviderProtocolError(
                    "LM Studio embedding item has an invalid index."
                )
            vector = self._parse_vector(item.get("embedding"))
            if index in indexed:
                raise ProviderProtocolError(
                    "LM Studio returned a duplicate embedding index."
                )
            indexed[index] = vector

        try:
            ordered = tuple(indexed[index] for index in range(len(normalized_texts)))
        except KeyError as exc:
            raise ProviderProtocolError(
                "LM Studio embeddings response is missing an input index."
            ) from exc

        dimensions = {len(vector) for vector in ordered}
        if len(dimensions) != 1:
            raise ProviderProtocolError(
                "LM Studio returned inconsistent embedding dimensions."
            )
        return ordered

    @staticmethod
    def _parse_vector(value: object) -> tuple[float, ...]:
        if not isinstance(value, list) or not value:
            raise ProviderProtocolError(
                "LM Studio embedding item is missing a vector."
            )
        vector: list[float] = []
        for component in value:
            if isinstance(component, bool) or not isinstance(component, (int, float)):
                raise ProviderProtocolError(
                    "LM Studio embedding vector contains a non-number."
                )
            number = float(component)
            if not math.isfinite(number):
                raise ProviderProtocolError(
                    "LM Studio embedding vector contains a non-finite number."
                )
            vector.append(number)
        return tuple(vector)
