from __future__ import annotations

import hashlib
from pathlib import Path

from athena.source.representation_store import TextRepresentationStore
from athena.storage.paths import RuntimePaths


def _runtime_paths(root: Path) -> RuntimePaths:
    state_root = root / "state"
    return RuntimePaths(
        local_root=root,
        state_root=state_root,
        database_path=state_root / "athena.db",
        spool_root=state_root / "spool",
        derived_root=root / "derived",
        log_root=root / "logs",
        temp_root=root / "tmp",
        archive_root=None,
        backup_root=None,
        projection_root=None,
    )


def test_prepare_text_stages_normalized_utf8_with_content_hash(tmp_path: Path) -> None:
    store = TextRepresentationStore(_runtime_paths(tmp_path))

    prepared = store.prepare_text("alpha\r\nbeta\rgamma\nλ")

    expected = "alpha\nbeta\ngamma\nλ".encode()
    assert prepared.staging_path.read_bytes() == expected
    assert prepared.byte_length == len(expected)
    assert prepared.content_sha256 == hashlib.sha256(expected).digest()

    store.discard(prepared)
    assert not prepared.staging_path.exists()


def test_prepare_text_accepts_empty_provider_output(tmp_path: Path) -> None:
    store = TextRepresentationStore(_runtime_paths(tmp_path))

    prepared = store.prepare_text("")

    assert prepared.staging_path.read_bytes() == b""
    assert prepared.byte_length == 0
    assert prepared.content_sha256 == hashlib.sha256(b"").digest()
