from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from athena.source.representation_store import (
    TextRepresentationError,
    TextRepresentationStore,
)
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

    store.discard(prepared)


def test_prepare_text_matches_native_leading_bom_and_newline_contract(
    tmp_path: Path,
) -> None:
    store = TextRepresentationStore(_runtime_paths(tmp_path))
    source = tmp_path / "native.txt"
    source.write_bytes(b"\xef\xbb\xbfalpha\r\nbeta\r")

    native = store.extract(source)
    provider = store.prepare_text("\ufeffalpha\r\nbeta\r")

    expected = b"alpha\nbeta\n"
    assert native.staging_path.read_bytes() == expected
    assert provider.staging_path.read_bytes() == expected
    assert provider.byte_length == native.byte_length
    assert provider.content_sha256 == native.content_sha256

    store.discard(native)
    store.discard(provider)


def test_prepare_text_preserves_embedded_bom(tmp_path: Path) -> None:
    store = TextRepresentationStore(_runtime_paths(tmp_path))

    prepared = store.prepare_text("\ufeffalpha\ufeffbeta")

    expected = "alpha\ufeffbeta".encode("utf-8")
    assert prepared.staging_path.read_bytes() == expected
    assert prepared.content_sha256 == hashlib.sha256(expected).digest()

    store.discard(prepared)


def test_prepare_text_rejects_non_utf8_scalar_and_cleans_staging(tmp_path: Path) -> None:
    paths = _runtime_paths(tmp_path)
    store = TextRepresentationStore(paths)

    with pytest.raises(TextRepresentationError, match="UTF-8"):
        store.prepare_text("bad\ud800text")

    staging_dir = paths.spool_root / "representations" / "staging"
    assert staging_dir.is_dir()
    assert tuple(staging_dir.iterdir()) == ()
