from __future__ import annotations

from pathlib import Path

import pytest

from athena.knowledge.obsidian_conflicts import ObsidianConflictStore


def test_conflict_store_survives_restart_without_persisting_body(tmp_path: Path) -> None:
    state_path = tmp_path / "conflicts.json"
    payload = b"# Example title\n\nExample body marker\n"
    ObsidianConflictStore(state_path).record(
        relative_path="Knowledge/example.md",
        payload=payload,
        detail="stale projection",
    )

    records = ObsidianConflictStore(state_path).list()

    assert len(records) == 1
    assert records[0].relative_path == "Knowledge/example.md"
    assert len(records[0].projection_sha256) == 64
    persisted = state_path.read_text(encoding="utf-8")
    assert "Example title" not in persisted
    assert "Example body marker" not in persisted


def test_conflict_store_resolves_only_requested_path(tmp_path: Path) -> None:
    state_path = tmp_path / "conflicts.json"
    store = ObsidianConflictStore(state_path)
    store.record(relative_path="Knowledge/a.md", payload=b"a", detail="a conflict")
    store.record(relative_path="Knowledge/b.md", payload=b"b", detail="b conflict")

    store.resolve("Knowledge/a.md")

    assert [record.relative_path for record in store.list()] == ["Knowledge/b.md"]


def test_conflict_store_fails_closed_for_malformed_digest(tmp_path: Path) -> None:
    state_path = tmp_path / "conflicts.json"
    state_path.write_text(
        '{"version":1,"conflicts":[{"relative_path":"Knowledge/a.md","projection_sha256":"bad","detail":"x"}]}',
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="malformed SHA-256"):
        ObsidianConflictStore(state_path).list()
