from __future__ import annotations

import time
from pathlib import Path

import pytest

from athena.chat.repository import ChatRepository
from athena.chat.service import ChatService
from athena.knowledge.models import KnowledgeKind
from athena.knowledge.obsidian_export import ObsidianVaultExporter
from athena.knowledge.obsidian_import import ObsidianKnowledgeReconciler
from athena.knowledge.obsidian_sync import (
    ObsidianSyncState,
    ObsidianVaultWatcher,
    ObsidianVaultWatchService,
    ObsidianWatchStatus,
    ObsidianWriteStampRegistry,
)
from athena.knowledge.repository import KnowledgeRepository
from athena.knowledge.service import KnowledgeService
from athena.storage.database import SQLiteDatabase


def _runtime(tmp_path: Path):
    database = SQLiteDatabase(tmp_path / "athena.db")
    database.start()
    chat = ChatService(ChatRepository(database))
    repository = KnowledgeRepository(database)
    knowledge = KnowledgeService(repository, chat)
    chat_id = chat.create_chat()
    chat.add_user_message(chat_id=chat_id, content="Original body")
    created = knowledge.promote_chat_message(
        chat_id=chat_id,
        sequence_no=1,
        knowledge_kind=KnowledgeKind.DECISION,
        title="Original title",
    )
    vault = tmp_path / "vault"
    vault.mkdir()
    stamps = ObsidianWriteStampRegistry()
    exporter = ObsidianVaultExporter(vault, write_stamps=stamps)
    watcher = ObsidianVaultWatcher(
        vault,
        reconciler=ObsidianKnowledgeReconciler(repository=repository, chat=chat),
        write_stamps=stamps,
        stability_window_seconds=1.0,
    )
    return database, repository, created, exporter, watcher


def _replace_body(markdown: str, body: str) -> str:
    lines = markdown.splitlines()
    heading = next(index for index, line in enumerate(lines) if line.startswith("# "))
    lines[heading + 2 :] = body.splitlines()
    return "\n".join(lines) + "\n"


def _wait_until(predicate, *, timeout_seconds: float = 2.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while not predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("Timed out waiting for Obsidian sync state.")
        time.sleep(0.01)


def test_export_stamp_suppresses_self_import_after_stability_window(tmp_path: Path) -> None:
    database, repository, created, exporter, watcher = _runtime(tmp_path)
    try:
        result = exporter.export_snapshot(repository.load_current(created.knowledge_id))

        assert watcher.scan_once(now=0.0) == ()
        assert watcher.scan_once(now=0.5) == ()
        stable = watcher.scan_once(now=1.0)

        assert len(stable) == 1
        assert stable[0].status is ObsidianWatchStatus.SELF_WRITE_IGNORED
        assert repository.load_current(created.knowledge_id).revision.revision_no == 1
        assert result.path.exists()
    finally:
        database.stop()


def test_stable_external_edit_is_applied_once(tmp_path: Path) -> None:
    database, repository, created, exporter, watcher = _runtime(tmp_path)
    try:
        result = exporter.export_snapshot(repository.load_current(created.knowledge_id))
        watcher.scan_once(now=0.0)
        watcher.scan_once(now=1.0)
        result.path.write_text(
            _replace_body(result.path.read_text(encoding="utf-8"), "External body"),
            encoding="utf-8",
        )

        assert watcher.scan_once(now=2.0) == ()
        applied = watcher.scan_once(now=3.0)
        repeated = watcher.scan_once(now=4.0)

        assert len(applied) == 1
        assert applied[0].status is ObsidianWatchStatus.APPLIED
        assert repeated == ()
        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_no == 2
        assert current.payload.body == "External body"
    finally:
        database.stop()


def test_change_during_debounce_restarts_stability_window(tmp_path: Path) -> None:
    database, repository, created, exporter, watcher = _runtime(tmp_path)
    try:
        result = exporter.export_snapshot(repository.load_current(created.knowledge_id))
        watcher.scan_once(now=0.0)
        watcher.scan_once(now=1.0)
        original = result.path.read_text(encoding="utf-8")
        result.path.write_text(_replace_body(original, "First external body"), encoding="utf-8")
        watcher.scan_once(now=2.0)
        result.path.write_text(_replace_body(original, "Final external body"), encoding="utf-8")

        assert watcher.scan_once(now=2.5) == ()
        assert watcher.scan_once(now=3.4) == ()
        applied = watcher.scan_once(now=3.5)

        assert len(applied) == 1
        assert applied[0].status is ObsidianWatchStatus.APPLIED
        current = repository.load_current(created.knowledge_id).revision
        assert current.payload.body == "Final external body"
    finally:
        database.stop()


def test_watch_service_owns_thread_local_database_and_shutdown(tmp_path: Path) -> None:
    database, repository, created, _exporter, _watcher = _runtime(tmp_path)
    vault = tmp_path / "vault"
    stamps = ObsidianWriteStampRegistry()
    exporter = ObsidianVaultExporter(vault, write_stamps=stamps)
    result = exporter.export_snapshot(repository.load_current(created.knowledge_id))
    service = ObsidianVaultWatchService(
        vault,
        database_path=database.path,
        write_stamps=stamps,
        stability_window_seconds=0.02,
        poll_interval_seconds=0.01,
    )

    try:
        service.start()
        _wait_until(lambda: service.state is ObsidianSyncState.RUNNING)
        _wait_until(
            lambda: service.last_result is not None
            and service.last_result.status is ObsidianWatchStatus.SELF_WRITE_IGNORED
        )

        result.path.write_text(
            _replace_body(result.path.read_text(encoding="utf-8"), "Runtime edit"),
            encoding="utf-8",
        )
        _wait_until(
            lambda: service.last_result is not None
            and service.last_result.status is ObsidianWatchStatus.APPLIED
        )

        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_no == 2
        assert current.payload.body == "Runtime edit"
    finally:
        service.stop()
        database.stop()

    assert service.state is ObsidianSyncState.STOPPED


def test_watch_service_pauses_fail_closed_for_missing_vault(tmp_path: Path) -> None:
    service = ObsidianVaultWatchService(
        tmp_path / "missing-vault",
        database_path=tmp_path / "athena.db",
        write_stamps=ObsidianWriteStampRegistry(),
    )

    service.start()

    assert service.state is ObsidianSyncState.PAUSED
    assert "existing real directory" in (service.last_error or "")
    service.stop()
    assert service.state is ObsidianSyncState.STOPPED



def test_watch_service_resumes_when_missing_vault_appears(tmp_path: Path) -> None:
    vault = tmp_path / "missing-vault"
    service = ObsidianVaultWatchService(
        vault,
        database_path=tmp_path / "athena.db",
        write_stamps=ObsidianWriteStampRegistry(),
        poll_interval_seconds=0.01,
    )

    try:
        service.start()
        assert service.state is ObsidianSyncState.PAUSED

        vault.mkdir()

        _wait_until(lambda: service.state is ObsidianSyncState.RUNNING)
        assert service.last_error is None
    finally:
        service.stop()

    assert service.state is ObsidianSyncState.STOPPED


def test_watch_service_pauses_and_resumes_after_runtime_vault_loss(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    service = ObsidianVaultWatchService(
        vault,
        database_path=tmp_path / "athena.db",
        write_stamps=ObsidianWriteStampRegistry(),
        poll_interval_seconds=0.01,
    )

    try:
        service.start()
        _wait_until(lambda: service.state is ObsidianSyncState.RUNNING)

        vault.rmdir()
        _wait_until(lambda: service.state is ObsidianSyncState.PAUSED)
        assert "existing real directory" in (service.last_error or "")

        vault.mkdir()
        _wait_until(lambda: service.state is ObsidianSyncState.RUNNING)
        assert service.last_error is None
    finally:
        service.stop()

    assert service.state is ObsidianSyncState.STOPPED


def test_managed_file_move_into_subfolder_resolves_by_frontmatter_identity(
    tmp_path: Path,
) -> None:
    database, repository, created, exporter, watcher = _runtime(tmp_path)
    try:
        result = exporter.export_snapshot(repository.load_current(created.knowledge_id))
        watcher.scan_once(now=0.0)
        ignored = watcher.scan_once(now=1.0)
        assert len(ignored) == 1
        assert ignored[0].status is ObsidianWatchStatus.SELF_WRITE_IGNORED

        nested = result.path.parent / "Projects"
        nested.mkdir()
        moved = result.path.rename(nested / "Renamed by user.md")

        assert watcher.scan_once(now=2.0) == ()
        observed = watcher.scan_once(now=3.0)

        assert len(observed) == 1
        assert observed[0].status is ObsidianWatchStatus.UNCHANGED
        assert observed[0].relative_path == "Knowledge/Projects/Renamed by user.md"
        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_id == created.revision_id
        assert current.revision_no == 1
        assert moved.exists()
    finally:
        database.stop()


def test_new_markdown_without_athena_id_is_an_import_candidate(tmp_path: Path) -> None:
    database, repository, created, _exporter, watcher = _runtime(tmp_path)
    try:
        knowledge_root = tmp_path / "vault" / "Knowledge"
        knowledge_root.mkdir()
        manual = knowledge_root / "Manual note.md"
        manual.write_text("# Manual note\n\nUser-authored body\n", encoding="utf-8")

        assert watcher.scan_once(now=0.0) == ()
        observed = watcher.scan_once(now=1.0)

        assert len(observed) == 1
        assert observed[0].status is ObsidianWatchStatus.IMPORT_CANDIDATE
        assert observed[0].relative_path == "Knowledge/Manual note.md"
        assert "explicit import" in (observed[0].detail or "")
        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_id == created.revision_id
        assert current.revision_no == 1
    finally:
        database.stop()


def test_malformed_managed_identity_is_rejected_not_import_candidate(
    tmp_path: Path,
) -> None:
    database, _repository, _created, _exporter, watcher = _runtime(tmp_path)
    try:
        knowledge_root = tmp_path / "vault" / "Knowledge"
        knowledge_root.mkdir()
        broken = knowledge_root / "Broken managed note.md"
        broken.write_text(
            "---\n"
            'athena_id: "not-a-uuid"\n'
            'entity_type: "knowledge_unit"\n'
            "revision_no: 1\n"
            "projection_version: 1\n"
            "---\n\n"
            "# Broken\n\n"
            "Body\n",
            encoding="utf-8",
        )

        assert watcher.scan_once(now=0.0) == ()
        observed = watcher.scan_once(now=1.0)

        assert len(observed) == 1
        assert observed[0].status is ObsidianWatchStatus.REJECTED
        assert observed[0].status is not ObsidianWatchStatus.IMPORT_CANDIDATE
    finally:
        database.stop()


def test_disappearing_file_during_stable_read_is_transient(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database, repository, created, exporter, watcher = _runtime(tmp_path)
    try:
        result = exporter.export_snapshot(repository.load_current(created.knowledge_id))
        assert watcher.scan_once(now=0.0) == ()

        target = result.path
        original_read_bytes = Path.read_bytes

        def _read_bytes(path: Path) -> bytes:
            if path == target:
                target.unlink()
                raise FileNotFoundError(target)
            return original_read_bytes(path)

        monkeypatch.setattr(Path, "read_bytes", _read_bytes)

        assert watcher.scan_once(now=1.0) == ()
        current = repository.load_current(created.knowledge_id).revision
        assert current.revision_id == created.revision_id
        assert current.revision_no == 1
    finally:
        database.stop()


def test_nested_link_boundary_is_not_traversed(tmp_path: Path) -> None:
    database, _repository, _created, _exporter, watcher = _runtime(tmp_path)
    try:
        knowledge_root = tmp_path / "vault" / "Knowledge"
        knowledge_root.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "Foreign.md").write_text(
            "# Foreign\n\nMust remain outside the managed vault.\n",
            encoding="utf-8",
        )
        linked = knowledge_root / "linked"
        try:
            linked.symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip("Filesystem does not permit directory symlink creation.")

        assert watcher.scan_once(now=0.0) == ()
        assert watcher.scan_once(now=1.0) == ()
    finally:
        database.stop()

