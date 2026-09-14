from __future__ import annotations

from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "quality.yml"


def _workflow_text() -> str:
    return _QUALITY_WORKFLOW.read_text(encoding="utf-8")


def test_quality_concurrency_is_scoped_by_event_and_pull_request() -> None:
    workflow = _workflow_text()

    assert "${{ github.workflow }}" in workflow
    assert "${{ github.event_name }}" in workflow
    assert "${{ github.event.pull_request.number || github.ref }}" in workflow


def test_quality_cancels_only_superseded_pull_request_runs() -> None:
    workflow = _workflow_text()

    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in workflow
    assert "cancel-in-progress: true" not in workflow
