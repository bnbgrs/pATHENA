from pathlib import Path

from athena.local_smoke import run_local_smoke
from athena.storage.schema import SCHEMA_VERSION


def test_local_smoke_initializes_and_reopens_current_schema(tmp_path: Path) -> None:
    report = run_local_smoke(tmp_path, restart_cycles=3)

    assert report.local_root == tmp_path.resolve()
    assert report.chat_id
    assert report.first_core_status == "running"
    assert report.restarted_core_status == "running"
    assert report.restart_cycles == 3
    assert report.persisted_chat_count >= 1
    assert report.database_schema_version == SCHEMA_VERSION
    assert report.api_runtime_clean is True
