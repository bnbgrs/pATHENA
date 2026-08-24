from __future__ import annotations

from dataclasses import dataclass

import pytest

from athena.model.domain import ModelInfo
from athena.model.signature_guard import (
    ModelSignatureDriftError,
    assert_runtime_model_matches_signature,
)


@dataclass(frozen=True)
class _Signature:
    provider: str = "lm_studio"
    model_identifier: str = "primary"
    model_revision: str | None = "rev-1"
    quantization: str | None = "Q4_K_M"


def _model(**overrides: object) -> ModelInfo:
    values: dict[str, object] = {
        "provider": "lm_studio",
        "backend_model_id": "primary",
        "display_name": "Primary",
        "model_type": "llm",
        "context_capacity": 8192,
        "quantization": "Q4_K_M",
        "loaded": True,
        "vision": False,
        "trained_for_tool_use": False,
        "model_revision": "rev-1",
    }
    values.update(overrides)
    return ModelInfo(**values)  # type: ignore[arg-type]


def test_signature_guard_accepts_exact_known_revision() -> None:
    assert_runtime_model_matches_signature(model=_model(), signature=_Signature())


@pytest.mark.parametrize(
    "overrides",
    [
        {"provider": "other"},
        {"backend_model_id": "other"},
        {"quantization": "Q8"},
    ],
)
def test_signature_guard_rejects_identity_drift(overrides: dict[str, object]) -> None:
    with pytest.raises(ModelSignatureDriftError, match="identity drifted"):
        assert_runtime_model_matches_signature(
            model=_model(**overrides),
            signature=_Signature(),
        )


@pytest.mark.parametrize("revision", ["rev-2", None])
def test_signature_guard_rejects_changed_or_unverifiable_pinned_revision(
    revision: str | None,
) -> None:
    with pytest.raises(ModelSignatureDriftError, match="revision drifted"):
        assert_runtime_model_matches_signature(
            model=_model(model_revision=revision),
            signature=_Signature(),
        )


def test_signature_guard_does_not_invent_unknown_pinned_revision() -> None:
    assert_runtime_model_matches_signature(
        model=_model(model_revision="later-observed"),
        signature=_Signature(model_revision=None),
    )
