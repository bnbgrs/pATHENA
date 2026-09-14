from __future__ import annotations

import io
import uuid
from pathlib import Path
from typing import Any

import pytest

from athena.source.blob_store import BlobStore, SourceFileTooLargeError
from athena.source.import_intake import ImportIntakeService, ImportRequest, ImportState
from athena.source.protected_blob import ProtectedBlobStore
from athena.storage.paths import RuntimePaths


def _runtime_paths(tmp_path: Path) -> RuntimePaths:
    local = tmp_path / "local"
    state = local / "state"
    spool = state / "spool"
    derived = local / "derived"
    logs = local / "logs"
    temp = local / "tmp"
    for path in (state, spool, derived, logs, temp):
        path.mkdir(parents=True, exist_ok=True)
    archive_root = tmp_path / "archive"
    archive_root.mkdir(parents=True)
    return RuntimePaths(
        local_root=local,
        state_root=state,
        database_path=state / "athena.db",
        spool_root=spool,
        derived_root=derived,
        log_root=logs,
        temp_root=temp,
        archive_root=archive_root,
        backup_root=None,
        projection_root=None,
    )


def _open_with_stream_override(
    monkeypatch: pytest.MonkeyPatch,
    source_path: Path,
    payload: bytes,
) -> None:
    original_open = Path.open
    resolved_source = source_path.resolve()

    def patched_open(self: Path, *args: Any, **kwargs: Any) -> Any:
        mode = args[0] if args else kwargs.get("mode", "r")
        if self.resolve() == resolved_source and mode == "rb":
            return io.BytesIO(payload)
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", patched_open)


def test_raw_capture_rejects_oversize_before_staging(tmp_path: Path) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "large.bin"
    source.write_bytes(b"123456")

    with pytest.raises(SourceFileTooLargeError):
        BlobStore(paths).capture_file(source, max_file_bytes=5)

    assert not (paths.spool_root / "imports").exists()


def test_raw_capture_rejects_stream_growth_before_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "growing.bin"
    source.write_bytes(b"1234")
    _open_with_stream_override(monkeypatch, source, b"123456")

    with pytest.raises(SourceFileTooLargeError):
        BlobStore(paths).capture_file(source, max_file_bytes=5)

    staging = paths.spool_root / "imports"
    assert staging.is_dir()
    assert tuple(staging.iterdir()) == ()
    assert not tuple(paths.archive_root.rglob("*.blob"))  # type: ignore[union-attr]


class _FakeCrypto:
    def random_key(self) -> bytes:
        return b"k" * 32

    def encrypt_with_nonce(self, *_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("oversize plaintext must be rejected before encryption")


class _FakeProtectedContent:
    def __init__(self) -> None:
        self.crypto = _FakeCrypto()

    def wrap_blob_dek(self, *_args: Any, **_kwargs: Any) -> object:
        return object()


def test_protected_capture_rejects_plaintext_stream_growth_and_cleans_staging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "protected-growing.bin"
    source.write_bytes(b"1234")
    _open_with_stream_override(monkeypatch, source, b"123456")
    store = ProtectedBlobStore(  # type: ignore[arg-type]
        blob_store=BlobStore(paths),
        protected_content=_FakeProtectedContent(),
    )

    with pytest.raises(SourceFileTooLargeError):
        store.capture_file(
            source,
            protection_scope_id=uuid.uuid4(),
            max_file_bytes=5,
        )

    staging = paths.spool_root / "imports"
    assert staging.is_dir()
    assert tuple(staging.iterdir()) == ()
    assert not tuple(paths.archive_root.rglob("*.blob"))  # type: ignore[union-attr]


class _LegacySources:
    def __init__(self) -> None:
        self.calls = 0

    def capture_file(self, path: Path) -> Any:
        self.calls += 1
        return {"path": path}

    def capture_protected_file(
        self,
        path: Path,
        *,
        protection_scope_id: uuid.UUID,
    ) -> Any:
        self.calls += 1
        return {"path": path, "scope": protection_scope_id}


class _LimitAwareSources:
    def __init__(self, *, failure: BaseException | None = None) -> None:
        self.failure = failure
        self.calls: list[tuple[str, Path, uuid.UUID | None, int | None]] = []

    def capture_file(
        self,
        path: Path,
        *,
        max_file_bytes: int | None = None,
    ) -> Any:
        self.calls.append(("plain", path, None, max_file_bytes))
        if self.failure is not None:
            raise self.failure
        return {"path": path}

    def capture_protected_file(
        self,
        path: Path,
        *,
        protection_scope_id: uuid.UUID,
        max_file_bytes: int | None = None,
    ) -> Any:
        self.calls.append(("protected", path, protection_scope_id, max_file_bytes))
        if self.failure is not None:
            raise self.failure
        return {"path": path, "scope": protection_scope_id}


def test_unbounded_intake_preserves_legacy_capture_call_shape(tmp_path: Path) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "plain.txt"
    source.write_text("ok", encoding="utf-8")
    sources = _LegacySources()
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=paths,
    )

    result = service.capture(ImportRequest.from_paths([source]))

    assert result.state is ImportState.READY
    assert sources.calls == 1


@pytest.mark.parametrize("protected", [False, True])
def test_intake_threads_configured_limit_to_capture_boundary(
    tmp_path: Path,
    protected: bool,
) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "bounded.txt"
    source.write_bytes(b"1234")
    sources = _LimitAwareSources()
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=paths,
    )
    scope_id = uuid.uuid4() if protected else None
    request = ImportRequest.from_paths(
        [source],
        max_file_bytes=5,
        protection_scope_id=scope_id,
    )

    result = service.capture(request)

    assert result.state is ImportState.READY
    assert len(sources.calls) == 1
    kind, captured_path, captured_scope, captured_limit = sources.calls[0]
    assert kind == ("protected" if protected else "plain")
    assert captured_path == source.resolve()
    assert captured_scope == scope_id
    assert captured_limit == 5


def test_intake_rechecks_size_after_preflight(tmp_path: Path) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "grows-after-preflight.bin"
    source.write_bytes(b"1234")
    sources = _LimitAwareSources()
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=paths,
    )
    request = ImportRequest.from_paths([source], max_file_bytes=5)
    preflight = service.preflight(request)
    assert not preflight.blocked

    source.write_bytes(b"123456")

    with pytest.raises(SourceFileTooLargeError):
        service._validated_capture_path(preflight.candidates[0])
    assert sources.calls == []


def test_permanent_oversize_capture_failure_is_not_retried(tmp_path: Path) -> None:
    paths = _runtime_paths(tmp_path)
    source = tmp_path / "bounded.bin"
    source.write_bytes(b"1234")
    sources = _LimitAwareSources(
        failure=SourceFileTooLargeError("grew while capture was streaming")
    )
    service = ImportIntakeService(  # type: ignore[arg-type]
        sources=sources,
        paths=paths,
    )

    result = service.capture(
        ImportRequest.from_paths([source], max_file_bytes=5)
    )

    assert result.state is ImportState.FAILED
    assert len(sources.calls) == 1
    assert len(result.failures) == 1
    assert result.failures[0].error_type == "SourceFileTooLargeError"
