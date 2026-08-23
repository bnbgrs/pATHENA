from pathlib import Path


_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_QUALITY_WORKFLOW = _REPOSITORY_ROOT / ".github" / "workflows" / "quality.yml"


def _workflow_text() -> str:
    return _QUALITY_WORKFLOW.read_text(encoding="utf-8")


def test_quality_workflow_collapses_pending_runs_without_cancelling_active_gate() -> None:
    workflow = _workflow_text()

    assert "concurrency:" in workflow
    assert (
        "group: ${{ github.workflow }}-${{ github.event_name }}-"
        "${{ github.event.pull_request.number || github.ref }}"
    ) in workflow
    assert "cancel-in-progress: false" in workflow


def test_quality_workflow_runs_keep_going_gate() -> None:
    workflow = _workflow_text()

    assert "python scripts/quality.py --keep-going" in workflow


def test_quality_workflow_avoids_duplicate_feature_branch_push_runs() -> None:
    workflow = _workflow_text()

    assert "push:\n    branches:\n      - main" in workflow
    assert "pull_request:" in workflow


def test_quality_workflow_has_focused_linux_storage_lane() -> None:
    workflow = _workflow_text()

    assert "storage-regressions:" in workflow
    assert "name: Linux storage regressions" in workflow
    assert "name: Run focused storage regressions" in workflow
    for test_path in (
        "tests/unit/test_migration_safety.py",
        "tests/unit/test_migration_clone.py",
        "tests/unit/test_migration_journal.py",
        "tests/unit/test_migration_activation.py",
        "tests/unit/test_migration_lock.py",
        "tests/unit/test_migration_executor.py",
        "tests/unit/test_migration_plan.py",
        "tests/unit/test_migration_recovery.py",
        "tests/unit/test_migration_coordinator.py",
        "tests/unit/test_emergency_reserve.py",
        "tests/unit/test_disk_pressure.py",
        "tests/unit/test_storage_bootstrap.py",
    ):
        assert test_path in workflow


def test_quality_workflow_has_disposable_local_smoke_lane() -> None:
    workflow = _workflow_text()

    assert "local-smoke:" in workflow
    assert "name: Local install smoke" in workflow
    assert "name: Run disposable Core/API restart smoke" in workflow
    assert "athena-local-smoke --restart-cycles 1" in workflow


def test_quality_workflow_has_targeted_windows_path_safety_lane() -> None:
    workflow = _workflow_text()

    assert "windows-path-safety:" in workflow
    assert "runs-on: windows-latest" in workflow
    assert "name: Probe native active-state locality" in workflow
    assert "assert_active_state_root_local(Path.cwd())" in workflow
    assert "name: Run deterministic Windows locality regressions" in workflow
    assert "tests/unit/test_storage_locality.py -k windows" in workflow
    assert "name: Run Windows storage path regressions" in workflow
    for test_path in (
        "tests/unit/test_database_preflight_locality.py",
        "tests/unit/test_runtime_paths.py",
        "tests/unit/test_migration_clone.py",
        "tests/unit/test_migration_journal.py",
        "tests/unit/test_migration_activation.py",
        "tests/unit/test_migration_lock.py",
        "tests/unit/test_migration_executor.py",
        "tests/unit/test_migration_recovery.py",
        "tests/unit/test_emergency_reserve.py",
        "tests/unit/test_disk_pressure.py",
    ):
        assert test_path in workflow
