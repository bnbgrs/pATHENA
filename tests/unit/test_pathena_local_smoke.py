from __future__ import annotations

from pathlib import Path

from athena.local_smoke import run_local_smoke


def test_local_smoke_persists_chat_across_core_api_restart(tmp_path: Path) -> None:
    report = run_local_smoke(tmp_path / "runtime")

    assert report.first_core_status in {"ok", "ready", "running"}
    assert report.restarted_core_status in {"ok", "ready", "running"}
    assert report.persisted_chat_count == 1
    assert report.chat_id
    assert (report.local_root / "state" / "athena.db").is_file()
