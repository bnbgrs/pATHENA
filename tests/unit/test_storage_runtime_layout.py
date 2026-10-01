from __future__ import annotations

import os
from pathlib import Path

import pytest

import athena.storage.runtime as runtime
from athena.storage.runtime import RuntimeLayoutService, RuntimePathError


def test_reparse_ancestor_uses_shared_link_boundary_predicate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ancestor = tmp_path / "redirected"
    ancestor.mkdir()
    child = ancestor / "state" / "spool"

    monkeypatch.setattr(
        runtime,
        "is_link_boundary",
        lambda path: path == ancestor,
    )

    with pytest.raises(RuntimePathError, match="reparse-point ancestor"):
        runtime._reject_symlink_ancestors(child)


def test_runtime_directory_rejects_reparse_leaf_before_use(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "spool"
    directory.mkdir()

    monkeypatch.setattr(
        runtime,
        "is_link_boundary",
        lambda path: path == directory,
    )

    with pytest.raises(RuntimePathError, match="symbolic link or reparse point"):
        RuntimeLayoutService._ensure_directory(directory)

    assert directory.is_dir()


def test_writable_probe_rejects_reparse_leaf_without_creating_probe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "logs"
    directory.mkdir()

    monkeypatch.setattr(
        runtime,
        "is_link_boundary",
        lambda path: path == directory,
    )

    with pytest.raises(RuntimePathError, match="not a safe directory"):
        RuntimeLayoutService._verify_writable(directory)

    assert list(directory.iterdir()) == []


def test_writable_probe_collision_never_deletes_preexisting_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "state"
    directory.mkdir()
    monkeypatch.setattr(runtime.secrets, "token_hex", lambda _size: "collision")
    probe = directory / f".athena-write-probe-{os.getpid()}-collision"
    probe.write_bytes(b"owned-by-someone-else")

    with pytest.raises(RuntimePathError, match="not writable"):
        RuntimeLayoutService._verify_writable(directory)

    assert probe.read_bytes() == b"owned-by-someone-else"


def test_writable_probe_identity_change_fails_closed_without_unlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    directory = tmp_path / "state"
    directory.mkdir()
    monkeypatch.setattr(runtime.secrets, "token_hex", lambda _size: "identity")
    monkeypatch.setattr(runtime.os.path, "samestat", lambda _left, _right: False)
    probe = directory / f".athena-write-probe-{os.getpid()}-identity"

    with pytest.raises(RuntimePathError, match="identity changed before cleanup"):
        RuntimeLayoutService._verify_writable(directory)

    assert probe.read_bytes() == b"ATHENA"
    probe.unlink()
