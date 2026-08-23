from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WINDOWS_COMMON = REPO_ROOT / "scripts" / "windows_common.ps1"
CHECK_WINDOWS = REPO_ROOT / "scripts" / "check_windows.ps1"
ENTRYPOINTS = (
    REPO_ROOT / "scripts" / "bootstrap_windows.ps1",
    CHECK_WINDOWS,
    REPO_ROOT / "scripts" / "start_windows.ps1",
)


def test_windows_common_defines_single_effective_runtime_root_contract() -> None:
    source = WINDOWS_COMMON.read_text(encoding="utf-8")

    assert "function Resolve-PathenaDefaultLocalRoot" in source
    assert "function Resolve-PathenaEffectiveLocalRoot" in source
    assert "function Assert-PathenaRuntimeRootOutsideRepository" in source
    assert "function Assert-PathenaLocalRootReady" in source
    assert ".pathena-write-probe-" in source
    assert "pATHENA runtime root is not writable" in source
    assert "runtime root must be outside the repository" in source


def test_all_windows_entrypoints_preflight_runtime_root() -> None:
    for path in ENTRYPOINTS:
        source = path.read_text(encoding="utf-8")
        assert "Assert-PathenaLocalRootReady -RepoRoot $RepoRoot" in source, path


def test_windows_check_can_preserve_restart_smoke_artifacts() -> None:
    source = CHECK_WINDOWS.read_text(encoding="utf-8")

    assert '[string]$SmokeRoot = ""' in source
    assert '$smokeArgs += @("--keep-root", $resolvedSmokeRoot)' in source
    assert "persistent Core/API restart smoke test" in source
