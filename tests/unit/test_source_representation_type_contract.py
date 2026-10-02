from __future__ import annotations

import typing
import uuid

import pytest

from athena.source import models, representation_repository
from athena.storage import database


_SCHEMA_REPRESENTATION_TYPES = {
    "normalized_text",
    "extracted_text",
    "ocr_text",
    "transcript",
    "thumbnail",
    "page_images",
}


class _DatabaseMustNotBeTouched:
    def write_transaction(self) -> object:
        raise AssertionError("invalid representation type must fail before DB access")


def _existing_blob() -> models.BlobRecord:
    return models.BlobRecord(
        blob_id=uuid.uuid4(),
        byte_length=4,
        media_type="text/plain; charset=utf-8",
        storage_area=models.BlobStorageArea.SPOOL,
        storage_locator="representations/test.blob",
        integrity_sha256=b"x" * 32,
        encryption_state="none",
        created_at_us=1,
        verified_at_us=1,
    )


def test_source_representation_type_matches_persisted_schema_contract() -> None:
    assert {value.value for value in models.SourceRepresentationType} == (
        _SCHEMA_REPRESENTATION_TYPES
    )


@pytest.mark.parametrize(
    "representation_type",
    [
        models.SourceRepresentationType.THUMBNAIL,
        models.SourceRepresentationType.PAGE_IMAGES,
    ],
)
def test_retained_text_writer_rejects_binary_representation_types_before_db_access(
    representation_type: models.SourceRepresentationType,
) -> None:
    repository = representation_repository.SourceRepresentationRepository(
        typing.cast(database.SQLiteDatabase, _DatabaseMustNotBeTouched())
    )

    with pytest.raises(ValueError, match="textual representation type"):
        repository.create_retained_text(
            actor_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            processing_run_id=uuid.uuid4(),
            stored_blob=None,
            existing_blob=_existing_blob(),
            content_hash=b"x" * 32,
            parser_id="test",
            parser_version="1",
            options={},
            representation_type=representation_type,
        )
