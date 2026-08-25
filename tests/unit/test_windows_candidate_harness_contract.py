from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "windows-candidate-acceptance.yml"
REQUEST = ROOT / ".github" / "windows-candidate-request.txt"
PROCESS_HARNESS = ROOT / "scripts" / "windows_candidate_process_tree.ps1"
DESKTOP_DRIVER = ROOT / "scripts" / "windows_candidate_desktop_driver.py"
PROVIDER_PROBE = ROOT / "scripts" / "windows_candidate_provider_probe.py"

KNOWN_UNSAFE = "bf54714d23a0b3da27fcac5d8215b55c2715ce48"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_workflow_is_sha_bound_native_windows_and_cache_free() -> None:
    workflow = _read(WORKFLOW)

    assert "runs-on: windows-2025" in workflow
    assert f"KNOWN_UNSAFE_SHA: {KNOWN_UNSAFE}" in workflow
    assert "git ls-remote" in workflow
    assert "refs/heads/bot/pathena-candidate" in workflow
    assert "timeout-minutes: 35" in workflow
    assert "cache:" not in workflow
    assert "github.event_name == 'workflow_dispatch' ||" in workflow
    assert "if: github.event_name == 'push'" in workflow
    assert "startsWith(github.event.head_commit.message" in workflow
    assert "windows-candidate-request.txt" in workflow
    assert len(_read(REQUEST).strip()) == 40
    assert "ref: ${{ env.CANDIDATE_SHA }}" in workflow
    assert "DEFAULT_CANDIDATE_SHA" not in workflow


def test_workflow_pins_actions_and_never_builds_a_distributable() -> None:
    workflow = _read(WORKFLOW)

    assert "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803" in workflow
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow
    assert "UNSAFE-DIAGNOSTIC" in workflow
    assert "pyinstaller" not in workflow.casefold()
    assert "*.exe" not in workflow.casefold()
    assert ".zip" not in workflow.casefold()
    assert "distributable_artifact = $null" in workflow


def test_process_harness_enforces_full_tree_and_orphan_boundaries() -> None:
    harness = _read(PROCESS_HARNESS)

    assert "Get-CimInstance -ClassName Win32_Process" in harness
    assert "ParentProcessId" in harness
    assert "CommandLine" in harness
    assert "Update-KnownDescendants" in harness
    assert "[AllowEmptyCollection()][object[]]$Processes" in harness
    assert "-ge $MaximumRelevantProcesses" in harness
    assert "[int]$MaximumRelevantProcesses = 20" in harness
    assert "[int]$PostExitSeconds = 10" in harness
    assert "Repeated self-recursion signature" in harness
    assert "Unbounded process growth" in harness
    assert "Orphan cleanup was required" in harness
    assert "UNSAFE-DIAGNOSTIC and RED" in harness


def test_python_diagnostics_compile_and_describe_incomplete_target_coverage() -> None:
    for path in (DESKTOP_DRIVER, PROVIDER_PROBE):
        ast.parse(_read(path), filename=str(path))

    desktop = _read(DESKTOP_DRIVER)
    assert "app.quit" in desktop
    assert "navigation.count() != 7" in desktop
    assert "not_implemented_as_target_screens" in desktop
    assert '"interactive PALLAS"' in desktop

    provider = _read(PROVIDER_PROBE)
    assert "ThreadingHTTPServer" in provider
    assert "ProviderHealthStatus.READY" in provider
    assert "ProviderHealthStatus.UNAVAILABLE" in provider
