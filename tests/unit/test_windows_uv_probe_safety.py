from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMON = REPO_ROOT / "scripts" / "windows_common.ps1"
ENTRY_POINTS = (
    REPO_ROOT / "scripts" / "bootstrap_windows.ps1",
    REPO_ROOT / "scripts" / "start_windows.ps1",
    REPO_ROOT / "scripts" / "check_windows.ps1",
)


def test_uv_version_probe_validates_native_result_before_trimming() -> None:
    source = COMMON.read_text(encoding="utf-8")

    assert "function Get-PathenaUvVersion" in source
    assert "$exitCode = $LASTEXITCODE" in source
    assert "$exitCode -ne 0 -or $output.Count -eq 0" in source
    assert "$version = ($output -join [Environment]::NewLine).Trim()" in source
    assert "(& uv --version).Trim()" not in source


def test_all_windows_entry_points_use_shared_uv_probe() -> None:
    for path in ENTRY_POINTS:
        source = path.read_text(encoding="utf-8")
        assert "Get-PathenaUvVersion" in source, path
        assert "(& uv --version).Trim()" not in source, path
