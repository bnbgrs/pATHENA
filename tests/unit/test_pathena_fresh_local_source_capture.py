from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.source.blob_store import BlobStore
from athena.source.models import BlobStorageArea
from athena.storage.paths import RuntimePaths


def test_fresh_local_install_captures_source_without_archive_root(tmp_path: Path) -> None:
    settings = AthenaSettings(local_root=(tmp_path / "runtime").resolve())
    paths = RuntimePaths.from_settings(settings)
    store = BlobStore(paths)
    source = tmp_path / "note.txt"
    source.write_text("local-first source", encoding="utf-8")

    prepared = store.capture_file(source)

    assert prepared.storage_area is BlobStorageArea.SPOOL
    assert paths.archive_root is None
    stored = store.verify_blob(
        storage_area=prepared.storage_area,
        storage_locator=prepared.storage_locator,
        expected_sha256=prepared.integrity_sha256,
        expected_length=prepared.byte_length,
    )
    assert stored.is_file()
    assert stored.read_text(encoding="utf-8") == "local-first source"
    assert stored.is_relative_to(paths.spool_root)
