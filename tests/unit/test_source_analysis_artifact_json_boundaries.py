from __future__ import annotations

import uuid

import pytest

from athena.source.analysis_models import AnalysisStage, SourceAnalysisArtifact


def _artifact(content_json: str) -> SourceAnalysisArtifact:
    return SourceAnalysisArtifact(
        artifact_id=uuid.uuid4(),
        analysis_id=uuid.uuid4(),
        work_item_id=uuid.uuid4(),
        artifact_kind=AnalysisStage.MAP,
        level=0,
        ordinal=0,
        content_json=content_json,
        content_hash=b"x" * 32,
        processing_run_id=uuid.uuid4(),
        created_at_us=0,
    )


@pytest.mark.parametrize(
    "content_json",
    [
        '{"value":NaN}',
        '{"value":Infinity}',
        '{"value":-Infinity}',
        '{"value":1,"value":2}',
    ],
)
def test_source_analysis_artifact_rejects_non_strict_json(content_json: str) -> None:
    with pytest.raises(ValueError, match="strict JSON"):
        _artifact(content_json)


@pytest.mark.parametrize("content_json", ["[]", '"value"', "1", "null"])
def test_source_analysis_artifact_requires_json_object(content_json: str) -> None:
    with pytest.raises(ValueError, match="JSON object"):
        _artifact(content_json)


@pytest.mark.parametrize("content_json", ['{"value":1}', "{}"])
def test_source_analysis_artifact_accepts_strict_json_objects(content_json: str) -> None:
    artifact = _artifact(content_json)
    assert artifact.content_json == content_json
