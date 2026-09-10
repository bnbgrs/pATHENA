import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BUILD_SCRIPT = _REPO_ROOT / "scripts" / "build_windows_portable.ps1"
_PACKAGED_WORKER = _REPO_ROOT / "src" / "athena" / "desktop" / "packaged_worker.py"
_OUTPUT_MARKER = ".pathena-windows-package-root"
_OUTPUT_MARKER_CONTENT = "pATHENA Windows portable package output v1"


def _build_script_text() -> str:
    return _BUILD_SCRIPT.read_text(encoding="utf-8")


def _packaged_worker_text() -> str:
    return _PACKAGED_WORKER.read_text(encoding="utf-8")


def _run_output_validation(output_root: Path) -> subprocess.CompletedProcess[str]:
    pwsh = shutil.which("pwsh")
    assert pwsh is not None, "windows-latest must provide PowerShell 7"
    return subprocess.run(
        [
            pwsh,
            "-NoProfile",
            "-NonInteractive",
            "-File",
            str(_BUILD_SCRIPT),
            "-OutputRoot",
            str(output_root),
            "-ValidateOutputRootOnly",
        ],
        cwd=_REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_windows_portable_keeps_desktop_worker_two_exe_topology() -> None:
    script = _build_script_text()

    assert '-Name "pATHENA"' in script
    assert '-EntryPoint "src\\athena\\desktop\\packaged_app.py"' in script
    assert '-Name "pATHENA-Worker"' in script
    assert '-EntryPoint "src\\athena\\desktop\\packaged_worker.py"' in script
    assert '$workerTarget = Join-Path $packageRoot "pATHENA-Worker.exe"' in script
    assert 'Copy-Item -LiteralPath $workerSource -Destination $workerTarget -Force' in script
    assert "Remove-PathenaGeneratedDirectory -Path $workerDist" in script


def test_windows_portable_keeps_packaging_release_dependencies() -> None:
    script = _build_script_text()

    assert '"pyinstaller==6.15.0"' in script
    assert '--collect-all pypdf' in script
    assert '--contents-directory app_runtime' in script


def test_windows_portable_output_cleanup_is_bounded_and_owned() -> None:
    script = _build_script_text()

    boundary = script.index("$resolvedOutput = Assert-PathenaPackagingOutputBoundary")
    reparse = script.index("Assert-PathenaPackagingPathHasNoReparseAncestor -Path $resolvedOutput")
    ownership = script.index("\nInitialize-PathenaPackagingOutputRoot `\n    -OutputRoot")
    validation_exit = script.index("if ($ValidateOutputRootOnly)")
    resolver = script.index("$uv = Get-Command uv")

    assert boundary < reparse < ownership < validation_exit < resolver
    assert '$packageRoot = Join-Path $resolvedOutput "pATHENA"' in script
    assert "Remove-PathenaGeneratedDirectory -Path $packageRoot" in script
    assert "foreach ($path in @($resolvedOutput, $workRoot" not in script
    assert "Remove-Item -LiteralPath $resolvedOutput -Recurse -Force" not in script
    assert '$packageOutputMarkerName = ".pathena-windows-package-root"' in script
    assert "Refusing non-empty custom Windows package output" in script


def test_windows_portable_output_cleanup_rejects_reparse_points() -> None:
    script = _build_script_text()

    assert "Assert-PathenaPackagingPathHasNoReparseAncestor -Path $resolvedOutput" in script
    assert "[System.IO.FileAttributes]::ReparsePoint" in script
    assert "Refusing recursive cleanup of reparse-point package directory" in script


@pytest.mark.skipif(sys.platform != "win32", reason="requires native Windows PowerShell")
def test_windows_output_validation_accepts_fresh_and_owned_custom_root(tmp_path: Path) -> None:
    output_root = tmp_path / "package-output"

    first = _run_output_validation(output_root)
    assert first.returncode == 0, first.stderr
    marker = output_root / _OUTPUT_MARKER
    assert marker.read_text(encoding="ascii").strip() == _OUTPUT_MARKER_CONTENT

    unrelated_file = output_root / "keep-me.txt"
    unrelated_file.write_text("preserve", encoding="utf-8")
    second = _run_output_validation(output_root)
    assert second.returncode == 0, second.stderr
    assert unrelated_file.read_text(encoding="utf-8") == "preserve"


@pytest.mark.skipif(sys.platform != "win32", reason="requires native Windows PowerShell")
def test_windows_output_validation_rejects_unsafe_roots_without_deleting(tmp_path: Path) -> None:
    unrelated_root = tmp_path / "unrelated-existing"
    unrelated_root.mkdir()
    sentinel = unrelated_root / "sentinel.txt"
    sentinel.write_text("must survive", encoding="utf-8")

    unsafe_roots = [
        unrelated_root,
        _REPO_ROOT,
        _REPO_ROOT / "src",
        _REPO_ROOT.parent,
        Path(_REPO_ROOT.anchor),
    ]
    for unsafe_root in unsafe_roots:
        result = _run_output_validation(unsafe_root)
        assert result.returncode != 0, f"unsafe output unexpectedly accepted: {unsafe_root}"

    assert sentinel.read_text(encoding="utf-8") == "must survive"


def test_packaged_worker_keeps_fail_closed_argv_and_desktop_refusal() -> None:
    worker = _packaged_worker_text()

    assert (
        "except PackagedInvocationError as exc:\n"
        '        print(f"pATHENA worker error: {exc}", file=sys.stderr)\n'
        "        return 2\n"
    ) in worker
    assert (
        "if invocation.target is PackagedTarget.DESKTOP:\n"
        '        print("pATHENA worker refuses a desktop invocation.", file=sys.stderr)\n'
        "        return 2\n"
    ) in worker
