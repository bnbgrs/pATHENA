from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BUILD_SCRIPT = _REPO_ROOT / "scripts" / "build_windows_portable.ps1"
_PACKAGING_SAFETY = _REPO_ROOT / "scripts" / "windows_packaging_safety.ps1"
_PACKAGED_WORKER = _REPO_ROOT / "src" / "athena" / "desktop" / "packaged_worker.py"
_OUTPUT_MARKER = ".pathena-windows-portable-output"
_OUTPUT_MARKER_VALUE = "pATHENA Windows Portable Output v1"


def _build_script_text() -> str:
    return _BUILD_SCRIPT.read_text(encoding="utf-8")


def _packaging_safety_text() -> str:
    return _PACKAGING_SAFETY.read_text(encoding="utf-8")


def _packaged_worker_text() -> str:
    return _PACKAGED_WORKER.read_text(encoding="utf-8")


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _assert_output_root(
    *, repo_root: Path, output_root: Path, default_output_root: Path
) -> subprocess.CompletedProcess[str]:
    powershell = _powershell()
    if powershell is None:
        pytest.skip("PowerShell is required for native Windows packaging safety tests")
    command = "; ".join(
        (
            "$ErrorActionPreference = 'Stop'",
            f". {_ps_quote(_PACKAGING_SAFETY)}",
            "Assert-PathenaPortableOutputRoot "
            f"-RepoRoot {_ps_quote(repo_root)} "
            f"-OutputRoot {_ps_quote(output_root)} "
            f"-DefaultOutputRoot {_ps_quote(default_output_root)} | Out-Null",
        )
    )
    return subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )


def _windows_repo(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "src").mkdir()
    default_output = repo_root / "dist" / "windows-portable"
    return repo_root, default_output


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
    assert '& $uv.Source sync --locked --extra desktop' in script


def test_windows_portable_validates_output_before_first_recursive_cleanup() -> None:
    script = _build_script_text()

    load_helper = '. $packagingSafety'
    validate = '$resolvedOutput = Assert-PathenaPortableOutputRoot'
    cleanup = 'Remove-Item -LiteralPath $path -Recurse -Force'
    mark = 'Set-PathenaPortableOutputOwnershipMarker -OutputRoot $resolvedOutput'

    assert 'windows_packaging_safety.ps1' in script
    assert load_helper in script
    assert validate in script
    assert cleanup in script
    assert mark in script
    assert script.index(load_helper) < script.index(validate) < script.index(cleanup) < script.index(mark)


def test_windows_portable_safety_helper_keeps_owned_output_contract() -> None:
    helper = _packaging_safety_text()

    assert _OUTPUT_MARKER in helper
    assert _OUTPUT_MARKER_VALUE in helper
    assert "Test-PathenaPortableOutputOwnershipMarker" in helper
    assert "Test-PathenaPackagingReparsePointInChain" in helper
    assert "Refusing to recursively replace unowned Windows packaging OutputRoot" in helper
    assert "inside the repository but outside the managed" in helper


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


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_packaging_guard_accepts_default_and_fresh_custom_output(tmp_path: Path) -> None:
    repo_root, default_output = _windows_repo(tmp_path)
    default_output.mkdir(parents=True)

    default_result = _assert_output_root(
        repo_root=repo_root,
        output_root=default_output,
        default_output_root=default_output,
    )
    assert default_result.returncode == 0, default_result.stderr

    fresh_external = tmp_path / "external" / "fresh-package"
    fresh_result = _assert_output_root(
        repo_root=repo_root,
        output_root=fresh_external,
        default_output_root=default_output,
    )
    assert fresh_result.returncode == 0, fresh_result.stderr

    fresh_managed_child = default_output / "alternate"
    managed_result = _assert_output_root(
        repo_root=repo_root,
        output_root=fresh_managed_child,
        default_output_root=default_output,
    )
    assert managed_result.returncode == 0, managed_result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_packaging_guard_accepts_repeat_owned_custom_output(tmp_path: Path) -> None:
    repo_root, default_output = _windows_repo(tmp_path)
    owned_output = tmp_path / "external" / "owned-package"
    owned_output.mkdir(parents=True)
    (owned_output / _OUTPUT_MARKER).write_text(_OUTPUT_MARKER_VALUE, encoding="ascii")

    result = _assert_output_root(
        repo_root=repo_root,
        output_root=owned_output,
        default_output_root=default_output,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
@pytest.mark.parametrize("target_kind", ["repo", "src", "ancestor", "root", "unowned", "file"])
def test_packaging_guard_rejects_destructive_targets(tmp_path: Path, target_kind: str) -> None:
    repo_root, default_output = _windows_repo(tmp_path)
    if target_kind == "repo":
        unsafe = repo_root
    elif target_kind == "src":
        unsafe = repo_root / "src"
    elif target_kind == "ancestor":
        unsafe = repo_root.parent
    elif target_kind == "root":
        unsafe = Path(repo_root.anchor)
    elif target_kind == "unowned":
        unsafe = tmp_path / "external" / "unrelated-existing"
        unsafe.mkdir(parents=True)
    else:
        unsafe = tmp_path / "external" / "existing-file"
        unsafe.parent.mkdir(parents=True)
        unsafe.write_text("not a package directory", encoding="utf-8")

    result = _assert_output_root(
        repo_root=repo_root,
        output_root=unsafe,
        default_output_root=default_output,
    )
    assert result.returncode != 0
    assert "Refusing Windows packaging OutputRoot" in result.stderr or "Refusing to recursively replace" in result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_packaging_guard_rejects_case_variant_source_path(tmp_path: Path) -> None:
    repo_root, default_output = _windows_repo(tmp_path)
    source = Path(str(repo_root / "src").upper())

    result = _assert_output_root(
        repo_root=repo_root,
        output_root=source,
        default_output_root=default_output,
    )
    assert result.returncode != 0
    assert "outside the managed" in result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_packaging_guard_rejects_existing_junction_output(tmp_path: Path) -> None:
    repo_root, default_output = _windows_repo(tmp_path)
    target = tmp_path / "junction-target"
    target.mkdir()
    junction = tmp_path / "external-junction"
    mklink = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(target)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if mklink.returncode != 0:
        pytest.skip(f"junction creation unavailable: {mklink.stderr or mklink.stdout}")

    result = _assert_output_root(
        repo_root=repo_root,
        output_root=junction,
        default_output_root=default_output,
    )
    assert result.returncode != 0
    assert "junction or reparse point" in result.stderr
