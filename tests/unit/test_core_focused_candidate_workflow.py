from pathlib import Path

WORKFLOW = Path(".github/workflows/core-focused-candidate.yml")


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_core_focused_candidate_excludes_deleted_python_paths() -> None:
    text = _workflow_text()
    selector = "git diff --diff-filter=ACMR --name-only $env:BASE_SHA $env:CANDIDATE_SHA"

    assert text.count(selector) == 4
    assert "git diff --name-only $env:BASE_SHA $env:CANDIDATE_SHA" not in text


def test_core_focused_pytest_selects_only_core_owned_test_families() -> None:
    text = _workflow_text()
    selector = (
        "^tests/unit/(test_claim.*|test_knowledge.*|test_concept_note.*|"
        "test_identity_transition.*|test_temporal.*|test_user_correction.*)\\.py$"
    )

    assert selector in text
    assert "^tests/unit/test_.*\\.py$" not in text
    assert "No changed Core-owned unit-test files selected" in text


def test_core_focused_lints_and_types_knowledge_api_sources() -> None:
    text = _workflow_text()
    selector = "^(src/athena/knowledge/.*|src/athena/api/knowledge_.*|tests/unit/.*)\\.py$"

    assert '"src/athena/api/knowledge_*.py"' in text
    assert text.count(selector) == 3
    assert "Mypy changed Core Python files" in text
    assert "mypy @changed" in text
    assert 'id: mypy' in text
    assert 'steps.mypy.outcome' in text
    assert "requires Ruff, mypy and focused pytest to succeed" in text


def test_core_focused_remediation_ignores_only_untracked_evidence() -> None:
    text = _workflow_text()

    assert text.count("git status --porcelain --untracked-files=no") == 2
    assert "git status --porcelain).Count" not in text
    assert "git reset --hard $env:CANDIDATE_SHA" in text
    assert "Diagnostic remediation did not restore the immutable candidate tracked worktree." in text


def test_user_correction_tests_are_triggered_and_selected() -> None:
    text = _workflow_text()

    assert '"tests/unit/test_user_correction*.py"' in text
    assert "test_user_correction.*" in text
