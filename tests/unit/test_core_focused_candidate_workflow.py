from __future__ import annotations

from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/core-focused-candidate.yml")


def test_user_correction_tests_are_triggered_and_selected() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert '"tests/unit/test_user_correction*.py"' in workflow
    assert "test_user_correction.*" in workflow
