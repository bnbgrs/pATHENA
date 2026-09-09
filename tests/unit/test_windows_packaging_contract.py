from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BUILD_SCRIPT = _REPO_ROOT / "scripts" / "build_windows_portable.ps1"


def _build_script_text() -> str:
    return _BUILD_SCRIPT.read_text(encoding="utf-8")


def test_windows_portable_keeps_desktop_worker_two_exe_topology() -> None:
    script = _build_script_text()

    assert '-Name "pATHENA"' in script
    assert '-EntryPoint "src\\athena\\desktop\\packaged_app.py"' in script
    assert '-Name "pATHENA-Worker"' in script
    assert '-EntryPoint "src\\athena\\desktop\\packaged_worker.py"' in script
    assert '$workerTarget = Join-Path $packageRoot "pATHENA-Worker.exe"' in script
    assert 'Copy-Item -LiteralPath $workerSource -Destination $workerTarget -Force' in script
    assert 'Remove-Item -LiteralPath $workerDist -Recurse -Force' in script


def test_windows_portable_keeps_packaging_release_dependencies() -> None:
    script = _build_script_text()

    assert '"pyinstaller==6.15.0"' in script
    assert '--collect-all pypdf' in script
    assert '--contents-directory app_runtime' in script
