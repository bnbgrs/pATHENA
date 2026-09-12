from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMON = _REPO_ROOT / "scripts" / "windows_common.ps1"


def _common_text() -> str:
    return _COMMON.read_text(encoding="utf-8")


def _powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def _ps_quote(value: Path | str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _assert_runtime_root(*, repo_root: Path, runtime_root: Path) -> subprocess.CompletedProcess[str]:
    powershell = _powershell()
    if powershell is None:
        pytest.skip("PowerShell is required for native Windows runtime-boundary tests")
    command = "; ".join(
        (
            "$ErrorActionPreference = 'Stop'",
            f". {_ps_quote(_COMMON)}",
            "Assert-PathenaRuntimeRootOutsideRepository "
            f"-RepoRoot {_ps_quote(repo_root)} "
            f"-RuntimeRoot {_ps_quote(runtime_root)} | Out-Null",
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


def _make_junction(link: Path, target: Path) -> None:
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation unavailable: {result.stderr or result.stdout}")


def test_windows_runtime_boundary_has_explicit_reparse_chain_guard() -> None:
    text = _common_text()

    assert "Test-PathenaWindowsReparsePointInExistingChain" in text
    assert "[System.IO.FileAttributes]::ReparsePoint" in text
    assert "repository root must not traverse a junction or reparse point" in text
    assert "runtime root must not traverse a junction or reparse point" in text


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_windows_runtime_boundary_accepts_real_outside_future_directory(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    runtime_root = tmp_path / "runtime" / "future-state"

    result = _assert_runtime_root(repo_root=repo_root, runtime_root=runtime_root)

    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_windows_runtime_boundary_rejects_repository_descendant_after_normalization(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    runtime_root = repo_root / "child" / ".." / "state"

    result = _assert_runtime_root(repo_root=repo_root, runtime_root=runtime_root)

    assert result.returncode != 0
    assert "must be outside the repository" in result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_windows_runtime_boundary_rejects_outside_junction_alias_into_repository(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    outside_alias = tmp_path / "outside-alias"
    _make_junction(outside_alias, repo_root)

    result = _assert_runtime_root(
        repo_root=repo_root,
        runtime_root=outside_alias / "state",
    )

    assert result.returncode != 0
    assert "junction or reparse point" in result.stderr


@pytest.mark.skipif(sys.platform != "win32", reason="native Windows path semantics")
def test_windows_runtime_boundary_rejects_repository_root_through_junction(
    tmp_path: Path,
) -> None:
    real_repo = tmp_path / "real-repo"
    real_repo.mkdir()
    repo_alias = tmp_path / "repo-alias"
    _make_junction(repo_alias, real_repo)
    runtime_root = real_repo / "state"

    result = _assert_runtime_root(repo_root=repo_alias, runtime_root=runtime_root)

    assert result.returncode != 0
    assert "repository root must not traverse a junction or reparse point" in result.stderr
