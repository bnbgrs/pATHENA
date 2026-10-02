from __future__ import annotations

from pathlib import Path


def test_quality_gate_isolates_process_sensitive_direct_chat_module() -> None:
    workflow = Path(".github/workflows/quality.yml").read_text(encoding="utf-8")

    isolated_command = (
        "python -m pytest tests/unit/test_desktop_direct_chat.py "
        "2>&1 | tee .quality-evidence/pytest-desktop-direct-chat.txt"
    )
    assert isolated_command in workflow
    assert "--ignore=tests/unit/test_desktop_direct_chat.py" in workflow
    assert "direct_chat_status=${PIPESTATUS[0]}" in workflow
    assert '"$direct_chat_status" -ne 0' in workflow
