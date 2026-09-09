from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "quality.yml"


def _quality_workflow_text() -> str:
    return _QUALITY_WORKFLOW.read_text(encoding="utf-8")


def test_canonical_quality_runs_on_develop_without_cancelling_in_progress() -> None:
    workflow = _quality_workflow_text()

    assert "      - develop/pathena-next\n" in workflow
    assert "  cancel-in-progress: false\n" in workflow
    assert '  CANDIDATE_SHA: ${{ github.event.pull_request.head.sha || github.sha }}\n' in workflow


def test_canonical_local_install_smoke_keeps_pypdf_packaging_guard() -> None:
    workflow = _quality_workflow_text()

    assert "    name: Local install smoke\n" in workflow
    assert "      - name: Verify pypdf packaging metadata\n" in workflow
    assert "        run: uv run --locked --extra dev athena-packaging-smoke --json\n" in workflow
