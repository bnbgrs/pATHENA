from __future__ import annotations

import time
from pathlib import Path

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
