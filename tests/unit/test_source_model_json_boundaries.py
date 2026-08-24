from __future__ import annotations

import uuid

import pytest

from athena.source.models import (
    RepresentationRetentionState,
    SourceRepresentationRecord,
    SourceRepresentationStructureRecord,
    SourceRepresentationStructureType,
    SourceRepresentationType,
)


def _representation(options_json: str) -> SourceRepresentationRecord:
    return SourceRepresentationRecord(
        representation_id=uuid.uuid4(),
        source_id=uuid.uuid4(),
        representation_type=SourceRepresentationType.EXTRACTED_TEXT,
        blob_id=uuid.uuid4(),
        processing_run_id=uuid.uuid4(),
        content_hash=b"a" * 32,
        retention_state=RepresentationRetentionState.RETAINED,
        media_type="text/plain",
        parser_id="test",
        parser_version="1",
        options_json=options_json,
        created_at_us=0,
        provenance_id=uuid.uuid4(),
    )


def _structure(metadata_json: str) -> SourceRepresentationStructureRecord:
    return SourceRepresentationStructureRecord(
        structure_id=uuid.uuid4(),
        representation_id=uuid.uuid4(),
        structure_index=0,
        structure_type=SourceRepresentationStructureType.PARAGRAPH,
        path="/p/0",
        parent_structure_id=None,
        start_offset=0,
        end_offset=1,
        content_hash=b"b" * 32,
        metadata_json=metadata_json,
    )


@pytest.mark.parametrize(
    "value",
    ['{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}', "[]", "null"],
)
def test_source_representation_options_require_strict_json_object(value: str) -> None:
    with pytest.raises(ValueError):
        _representation(value)


@pytest.mark.parametrize(
    "value",
    ['{"x":NaN}', '{"x":Infinity}', '{"x":1,"x":2}', "[]", "null"],
)
def test_source_structure_metadata_requires_strict_json_object(value: str) -> None:
    with pytest.raises(ValueError):
        _structure(value)


def test_source_representation_json_objects_accept_empty_and_nested_objects() -> None:
    assert _representation("{}").options_json == "{}"
    assert _structure('{"page":{"number":1}}').metadata_json == '{"page":{"number":1}}'
