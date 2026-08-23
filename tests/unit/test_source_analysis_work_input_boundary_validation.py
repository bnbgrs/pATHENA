from __future__ import annotations

import uuid

import pytest

from athena.source.analysis_models import AnalysisInputKind, SourceAnalysisWorkInput


def _valid_anchor_input() -> dict[str, object]:
    return {
        "work_item_id": uuid.uuid4(),
        "ordinal": 0,
        "input_kind": AnalysisInputKind.SOURCE_ANCHOR,
        "source_anchor_id": uuid.uuid4(),
        "artifact_id": None,
    }


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("work_item_id", "not-a-uuid", TypeError),
        ("ordinal", True, TypeError),
        ("ordinal", 1.5, TypeError),
        ("ordinal", -1, ValueError),
        ("input_kind", "source_anchor", TypeError),
        ("source_anchor_id", "not-a-uuid", ValueError),
        ("source_anchor_id", None, ValueError),
        ("artifact_id", uuid.uuid4(), ValueError),
    ],
)
def test_source_anchor_work_input_rejects_malformed_identity(
    field: str,
    value: object,
    error_type: type[Exception],
) -> None:
    kwargs = _valid_anchor_input()
    kwargs[field] = value

    with pytest.raises(error_type):
        SourceAnalysisWorkInput(**kwargs)  # type: ignore[arg-type]


def test_artifact_work_input_requires_exact_artifact_uuid() -> None:
    with pytest.raises(ValueError):
        SourceAnalysisWorkInput(
            work_item_id=uuid.uuid4(),
            ordinal=0,
            input_kind=AnalysisInputKind.ARTIFACT,
            source_anchor_id=None,
            artifact_id="not-a-uuid",  # type: ignore[arg-type]
        )


def test_current_source_anchor_work_input_is_valid() -> None:
    kwargs = _valid_anchor_input()
    value = SourceAnalysisWorkInput(**kwargs)  # type: ignore[arg-type]

    assert value.input_kind is AnalysisInputKind.SOURCE_ANCHOR
    assert isinstance(value.source_anchor_id, uuid.UUID)


def test_current_artifact_work_input_is_valid() -> None:
    artifact_id = uuid.uuid4()
    value = SourceAnalysisWorkInput(
        work_item_id=uuid.uuid4(),
        ordinal=1,
        input_kind=AnalysisInputKind.ARTIFACT,
        source_anchor_id=None,
        artifact_id=artifact_id,
    )

    assert value.artifact_id == artifact_id
