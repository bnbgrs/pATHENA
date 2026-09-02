from __future__ import annotations

import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from athena.security.service import ProtectedContentService
from athena.source import protected_blob
from athena.source.blob_store import BlobStore
from athena.source.protected_blob import ProtectedBlobStore


class _Crypto:
    def random_key(self) -> bytes:
        return b"k" * 32


class _ProtectedContent:
    def __init__(self, *, fail_wrap: bool) -> None:
        self.crypto = _Crypto()
        self.fail_wrap = fail_wrap

    def wrap_blob_dek(self, *args: object, **kwargs: object) -> object:
        if self.fail_wrap:
            raise RuntimeError("wrap failed")
        return object()


def _record_wipes(monkeypatch: pytest.MonkeyPatch) -> list[bytes]:
    wiped: list[bytes] = []
    original_wipe = protected_blob._wipe

    def record_wipe(value: bytearray) -> None:
        original_wipe(value)
        wiped.append(bytes(value))

    monkeypatch.setattr(protected_blob, "_wipe", record_wipe)
    return wiped


def test_capture_wipes_dek_when_wrap_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(b"protected source")
    wiped = _record_wipes(monkeypatch)
    store = ProtectedBlobStore(
        blob_store=cast(BlobStore, object()),
        protected_content=cast(
            ProtectedContentService,
            _ProtectedContent(fail_wrap=True),
        ),
    )

    with pytest.raises(RuntimeError, match="wrap failed"):
        store.capture_file(
            source_path,
            protection_scope_id=uuid.uuid4(),
        )

    assert wiped == [b"\x00" * 32]


def test_capture_wipes_dek_when_staging_directory_creation_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = tmp_path / "source.bin"
    source_path.write_bytes(b"protected source")
    spool_root = tmp_path / "spool-file"
    spool_root.write_bytes(b"not a directory")
    wiped = _record_wipes(monkeypatch)
    blob_store = SimpleNamespace(paths=SimpleNamespace(spool_root=spool_root))
    store = ProtectedBlobStore(
        blob_store=cast(BlobStore, blob_store),
        protected_content=cast(
            ProtectedContentService,
            _ProtectedContent(fail_wrap=False),
        ),
    )

    with pytest.raises(OSError):
        store.capture_file(
            source_path,
            protection_scope_id=uuid.uuid4(),
        )

    assert wiped == [b"\x00" * 32]
