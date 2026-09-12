from __future__ import annotations

from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_windows.ps1"


def _script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_windows_check_loads_shared_runtime_root_guard() -> None:
    text = _script_text()

    assert '$CommonScript = Join-Path $ScriptDir "windows_common.ps1"' in text
    assert ". $CommonScript" in text
    assert "Assert-PathenaRuntimeRootOutsideRepository" in text


def test_explicit_smoke_root_is_guarded_before_keep_root_is_forwarded() -> None:
    text = _script_text()
    explicit_block_start = text.index("if ($SmokeRoot.Trim()) {")
    explicit_block_end = text.index("} else {", explicit_block_start)
    explicit_block = text[explicit_block_start:explicit_block_end]

    resolve = "$resolvedSmokeRoot = [System.IO.Path]::GetFullPath($SmokeRoot.Trim())"
    guard = (
        "$resolvedSmokeRoot = Assert-PathenaRuntimeRootOutsideRepository "
        "-RepoRoot $RepoRoot -RuntimeRoot $resolvedSmokeRoot"
    )
    forward = '$smokeArgs += @("--keep-root", $resolvedSmokeRoot)'

    assert resolve in explicit_block
    assert guard in explicit_block
    assert forward in explicit_block
    assert explicit_block.index(resolve) < explicit_block.index(guard) < explicit_block.index(forward)


def test_repository_guard_runs_before_local_smoke_process() -> None:
    text = _script_text()
    guard_index = text.index("Assert-PathenaRuntimeRootOutsideRepository")
    smoke_process_index = text.index("& uv @smokeArgs")

    assert guard_index < smoke_process_index
