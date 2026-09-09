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


def test_canonical_windows_path_safety_keeps_exact_sha_and_storage_regressions() -> None:
    workflow = _quality_workflow_text()

    assert "  windows-path-safety:\n" in workflow
    assert "    runs-on: windows-latest\n" in workflow
    assert "          ref: ${{ env.CANDIDATE_SHA }}\n" in workflow
    assert "      - name: Run deterministic Windows locality regressions\n" in workflow
    assert "      - name: Run Windows storage path regressions\n" in workflow
    assert "tests/unit/test_storage_safe_mode.py" in workflow


def test_canonical_quality_keeps_full_pytest_and_enforces_all_core_checks() -> None:
    workflow = _quality_workflow_text()

    assert "uv run --locked --extra dev --extra desktop python -m pytest 2>&1 | tee .quality-evidence/pytest.txt" in workflow
    assert 'SPEC_OUTCOME: ${{ steps.quality_spec.outcome }}' in workflow
    assert 'RUFF_OUTCOME: ${{ steps.quality_ruff.outcome }}' in workflow
    assert 'MYPY_OUTCOME: ${{ steps.quality_mypy.outcome }}' in workflow
    assert 'PYTEST_OUTCOME: ${{ steps.quality_pytest.outcome }}' in workflow
    assert 'failures = [name for name, outcome in outcomes.items() if outcome != "success"]' in workflow


def test_canonical_quality_keeps_storage_bootstrap_and_runtime_boundary_regressions() -> None:
    workflow = _quality_workflow_text()

    assert "  storage-regressions:\n" in workflow
    assert "tests/unit/test_storage_bootstrap.py" in workflow
    assert workflow.count("      - name: Run API runtime path-boundary regressions\n") == 2
    assert workflow.count("tests/unit/test_api_runtime_boundaries.py") == 2
