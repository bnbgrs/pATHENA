from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "core-focused-candidate.yml"


def _workflow_text() -> str:
    return _WORKFLOW.read_text(encoding="utf-8")


def test_core_focused_diff_selection_excludes_deleted_candidate_paths() -> None:
    workflow = _workflow_text()

    selector = "git diff --name-only --diff-filter=ACMRT $env:BASE_SHA $env:CANDIDATE_SHA"
    assert workflow.count(selector) == 3
    assert "--diff-filter=ACMRT" in workflow
    assert "--diff-filter=ACMRTD" not in workflow


def test_core_focused_remediation_ignores_only_untracked_diagnostics() -> None:
    workflow = _workflow_text()

    tracked_clean = "git status --porcelain --untracked-files=no"
    assert workflow.count(tracked_clean) == 2
    assert "Candidate tracked worktree must be clean before diagnostic Ruff remediation." in workflow
    assert "Diagnostic remediation did not restore the immutable candidate tracked worktree." in workflow


def test_core_focused_still_enforces_both_lint_and_changed_tests() -> None:
    workflow = _workflow_text()

    assert 'if ($ruff -ne "success" -or $tests -ne "success")' in workflow
    assert "Exact changed-file Ruff contract failed." in workflow
    assert "Exact changed-test Core candidate contract failed." in workflow
