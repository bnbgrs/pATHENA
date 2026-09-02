from __future__ import annotations

import uuid

import pytest

from athena.research.idempotency import (
    _synthesis_work_idempotency_key,
    _work_idempotency_key,
)
from athena.research.models import ResearchSynthesisInputKind, ResearchSynthesisStage


def test_research_work_idempotency_requires_sha256_digest() -> None:
    with pytest.raises(ValueError, match="32-byte SHA-256"):
        _work_idempotency_key(
            scope_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            content_sha256=b"short",
        )


@pytest.mark.parametrize("value", [True, -1, 1.5])
def test_research_synthesis_idempotency_rejects_invalid_level(value: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        _synthesis_work_idempotency_key(
            scope_id=uuid.uuid4(),
            stage=ResearchSynthesisStage.REDUCE,
            level=value,  # type: ignore[arg-type]
            ordinal=0,
            inputs=[(ResearchSynthesisInputKind.SOURCE_ANALYSIS_ARTIFACT, uuid.uuid4())],
            descriptor={"kind": "reduce"},
            pipeline_version="v1",
            prompt_template_id="research.reduce",
            prompt_template_version="1",
        )


def test_research_synthesis_idempotency_rejects_noncanonical_prompt_identity() -> None:
    with pytest.raises(ValueError, match="canonical non-empty text"):
        _synthesis_work_idempotency_key(
            scope_id=uuid.uuid4(),
            stage=ResearchSynthesisStage.REDUCE,
            level=0,
            ordinal=0,
            inputs=[(ResearchSynthesisInputKind.SOURCE_ANALYSIS_ARTIFACT, uuid.uuid4())],
            descriptor={"kind": "reduce"},
            pipeline_version="v1",
            prompt_template_id=" research.reduce",
            prompt_template_version="1",
        )
