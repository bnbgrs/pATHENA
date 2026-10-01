from __future__ import annotations

from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.source.blob_store import (
    BlobIntegrityError,
    BlobReadTooLargeError,
    SourceChangedDuringCaptureError,
)
from athena.source.models import SourceType


def _started_app(tmp_path: Path) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=tmp_path / "local",
        )
    )
    app.start()
    return app


def _png_payload() -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"pATHENA clipboard image bytes"


def test_image_bytes_are_preserved_in_raw_archive_across_restart(
    tmp_path: Path,
) -> None:
    payload = _png_payload()
    first = _started_app(tmp_path)
    captured = first.sources.capture_image_bytes(
        payload,
        original_name="clipboard-image.png",
        source_uri="clipboard://composer",
    )
    source_id = captured.source.source_id

    assert captured.source.source_type is SourceType.IMAGE
    assert captured.source.mime_type == "image/png"
    assert captured.source.original_modified_at_us is None
    assert captured.source.source_uri == "clipboard://composer"
    assert first.sources.verify(source_id).read_bytes() == payload
    first.stop()

    second = _started_app(tmp_path)
    source, blob = second.sources.get(source_id)
    assert source.source_type is SourceType.IMAGE
    assert source.blob_id == blob.blob_id
    assert second.sources.verify(source_id).read_bytes() == payload
    second.stop()


def test_image_byte_capture_reuses_verified_blob_without_collapsing_sources(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    payload = _png_payload()

    first = app.sources.capture_image_bytes(
        payload,
        original_name="first.png",
        source_uri="clipboard://composer/first",
    )
    second = app.sources.capture_image_bytes(
        payload,
        original_name="second.png",
        source_uri="clipboard://composer/second",
    )

    assert first.source.source_id != second.source.source_id
    assert first.blob.blob_id == second.blob.blob_id
    assert not first.reused_blob
    assert second.reused_blob
    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM sources WHERE source_type = 'image'"
    ).fetchone()[0] == 2
    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM blob_records"
    ).fetchone()[0] == 1
    app.stop()


def test_image_byte_capture_prefers_magic_bytes_over_filename_extension(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    captured = app.sources.capture_image_bytes(
        _png_payload(),
        original_name="misleading.jpg",
        source_uri="clipboard://composer",
    )

    assert captured.source.mime_type == "image/png"
    assert captured.blob.media_type == "image/png"
    app.stop()


def test_image_byte_capture_rejects_non_image_before_archive_write(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)

    with pytest.raises(ValueError, match="recognized PNG, JPEG, or GIF"):
        app.sources.capture_image_bytes(
            b"plain text pretending to be an image",
            original_name="fake.png",
            source_uri="clipboard://composer",
        )

    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM sources"
    ).fetchone()[0] == 0
    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM blob_records"
    ).fetchone()[0] == 0
    assert not tuple((app.paths.spool_root / "blobs").rglob("*.blob"))
    app.stop()


def test_image_byte_capture_enforces_size_limit_before_source_commit(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    payload = _png_payload()

    with pytest.raises(
        SourceChangedDuringCaptureError,
        match="maximum capture size",
    ):
        app.sources.capture_image_bytes(
            payload,
            original_name="too-large.png",
            source_uri="clipboard://composer",
            max_file_bytes=len(payload) - 1,
        )

    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM sources"
    ).fetchone()[0] == 0
    assert app.database.connection.execute(
        "SELECT COUNT(*) FROM blob_records"
    ).fetchone()[0] == 0
    app.stop()


@pytest.mark.parametrize(
    "value",
    [bytearray(_png_payload()), memoryview(_png_payload())],
)
def test_image_byte_capture_requires_immutable_bytes(
    tmp_path: Path,
    value: object,
) -> None:
    app = _started_app(tmp_path)
    try:
        with pytest.raises(TypeError, match="immutable bytes"):
            app.sources.capture_image_bytes(
                value,  # type: ignore[arg-type]
                original_name="clipboard-image.png",
                source_uri="clipboard://composer",
            )
    finally:
        app.stop()


def test_image_bytes_are_read_only_through_bounded_integrity_check(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    payload = _png_payload()
    captured = app.sources.capture_image_bytes(
        payload,
        original_name="clipboard-image.png",
        source_uri="clipboard://composer",
    )

    assert app.sources.read_image_bytes(
        captured.source.source_id,
        max_bytes=len(payload),
    ) == payload

    with pytest.raises(BlobReadTooLargeError, match="read limit"):
        app.sources.read_image_bytes(
            captured.source.source_id,
            max_bytes=len(payload) - 1,
        )
    app.stop()


def test_image_byte_read_fails_closed_after_archive_corruption(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path)
    captured = app.sources.capture_image_bytes(
        _png_payload(),
        original_name="clipboard-image.png",
        source_uri="clipboard://composer",
    )
    stored_path = app.blob_store.resolve_blob_path(
        storage_area=captured.blob.storage_area,
        storage_locator=captured.blob.storage_locator,
    )
    stored_path.write_bytes(b"corrupt")

    with pytest.raises(BlobIntegrityError, match="integrity|length changed"):
        app.sources.read_image_bytes(
            captured.source.source_id,
            max_bytes=1024,
        )
    app.stop()


def test_image_byte_read_rejects_non_image_source(
    tmp_path: Path,
) -> None:
    original = tmp_path / "note.txt"
    original.write_text("not an image", encoding="utf-8")
    app = _started_app(tmp_path)
    captured = app.sources.capture_file(original)

    with pytest.raises(ValueError, match="not an image"):
        app.sources.read_image_bytes(
            captured.source.source_id,
            max_bytes=1024,
        )
    app.stop()
