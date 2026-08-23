from __future__ import annotations

import uuid

import pytest

from athena.source.analysis_models import AnalysisInputKind, SourceAnalysisWorkInput


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def test_source_anchor_input_requires_only_anchor_reference() -> None:
    item = SourceAnalysisWorkInput(
        work_item_id=_uuid(),
        ordinal=0,
        input_kind=AnalysisInputKind.SOURCE_ANCHOR,
        source_anchor_id=_uuid(),
        artifact_id=None,
    )

    assert item.input_kind is AnalysisInputKind.SOURCE_ANCHOR
    assert item.source_anchor_id is not None
    assert item.artifact_id is None


@pytest.mark.parametrize(
    ("source_anchor_id", "artifact_id"),
    [
        (None, None),
        (_uuid(), _uuid()),
        (None, _uuid()),
    ],
)
def test_source_anchor_input_rejects_ambiguous_reference(
    source_anchor_id: uuid.UUID | None,
    artifact_id: uuid.UUID | None,
) -> None:
    with pytest.raises(ValueError, match="exactly one source_anchor_id"):
        SourceAnalysisWorkInput(
            work_item_id=_uuid(),
            ordinal=0,
            input_kind=AnalysisInputKind.SOURCE_ANCHOR,
            source_anchor_id=source_anchor_id,
            artifact_id=artifact_id,
        )


def test_artifact_input_requires_only_artifact_reference() -> None:
    item = SourceAnalysisWorkInput(
        work_item_id=_uuid(),
        ordinal=2,
        input_kind=AnalysisInputKind.ARTIFACT,
        source_anchor_id=None,
        artifact_id=_uuid(),
    )

    assert item.input_kind is AnalysisInputKind.ARTIFACT
    assert item.source_anchor_id is None
    assert item.artifact_id is not None


@pytest.mark.parametrize("ordinal", [True, False, 1.5, "1", None])
def test_work_input_rejects_non_integer_ordinal(ordinal: object) -> None:
    with pytest.raises(TypeError, match="ordinal must be an integer"):
        SourceAnalysisWorkInput(
            work_item_id=_uuid(),
            ordinal=ordinal,  # type: ignore[arg-type]
            input_kind=AnalysisInputKind.ARTIFACT,
            source_anchor_id=None,
            artifact_id=_uuid(),
        )


def test_work_input_rejects_negative_ordinal() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        SourceAnalysisWorkInput(
            work_item_id=_uuid(),
            ordinal=-1,
            input_kind=AnalysisInputKind.ARTIFACT,
            source_anchor_id=None,
            artifact_id=_uuid(),
        )
