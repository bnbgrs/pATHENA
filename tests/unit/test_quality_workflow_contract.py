from __future__ import annotations

from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPOSITORY_ROOT / ".github" / "workflows" / "quality.yml"


def _workflow_text() -> str:
    return _QUALITY_WORKFLOW.read_text(encoding="utf-8")


def test_quality_workflow_cancels_superseded_runs_per_event_and_ref() -> None:
    workflow = _workflow_text()

    assert "concurrency:" in workflow
    assert (
        "group: ${{ github.workflow }}-${{ github.event_name }}-"
        "${{ github.event.pull_request.number || github.ref }}"
    ) in workflow
    assert "cancel-in-progress: true" in workflow


def test_quality_workflow_runs_keep_going_gate() -> None:
    workflow = _workflow_text()

    assert "python scripts/quality.py --keep-going" in workflow
