from __future__ import annotations

from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPOSITORY_ROOT / ".github" / "workflows" / "quality.yml"
_DOCS_SPEC_WORKFLOW = _REPOSITORY_ROOT / ".github" / "workflows" / "docs-spec.yml"


def _workflow_text(path: Path = _QUALITY_WORKFLOW) -> str:
    return path.read_text(encoding="utf-8")


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


def test_quality_workflow_ignores_docs_only_churn() -> None:
    workflow = _workflow_text()

    assert workflow.count('paths-ignore:') == 2
    assert workflow.count('- "docs/**"') == 2


def test_docs_spec_workflow_validates_docs_without_full_gate() -> None:
    workflow = _workflow_text(_DOCS_SPEC_WORKFLOW)

    assert workflow.count("paths:") == 2
    assert workflow.count('- "docs/**"') == 2
    assert "python scripts/validate_spec.py" in workflow
    assert "scripts/quality.py" not in workflow
    assert "cancel-in-progress: true" in workflow
