from pathlib import Path

WORKFLOW = Path(".github/workflows/core-focused-candidate.yml")


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_core_focused_candidate_excludes_deleted_python_paths() -> None:
    text = _workflow_text()
    selector = "git diff --diff-filter=ACMR --name-only $env:BASE_SHA $env:CANDIDATE_SHA"

    assert text.count(selector) == 3
    assert "git diff --name-only $env:BASE_SHA $env:CANDIDATE_SHA" not in text


def test_core_focused_remediation_ignores_only_untracked_evidence() -> None:
    text = _workflow_text()

    assert text.count("git status --porcelain --untracked-files=no") == 2
    assert "git status --porcelain).Count" not in text
    assert "git reset --hard $env:CANDIDATE_SHA" in text
    assert "Diagnostic remediation did not restore the immutable candidate tracked worktree." in text
