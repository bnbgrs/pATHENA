from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "windows-candidate-acceptance.yml"
REQUEST = ROOT / ".github" / "windows-candidate-request.txt"
PROCESS_HARNESS = ROOT / "scripts" / "windows_candidate_process_tree.ps1"
PACKAGED_SMOKE = ROOT / "scripts" / "windows_candidate_packaged_smoke.ps1"
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
    assert "timeout-minutes: 45" in workflow
    assert "cache:" not in workflow
    assert "github.event_name == 'workflow_dispatch' ||" in workflow
    assert "if: github.event_name == 'push'" in workflow
    assert "startsWith(github.event.head_commit.message" in workflow
    assert "windows-candidate-request.txt" in workflow
    assert len(_read(REQUEST).strip()) == 40
    assert "ref: ${{ env.CANDIDATE_SHA }}" in workflow
    assert "DEFAULT_CANDIDATE_SHA" not in workflow


def test_workflow_pins_actions_and_package_remains_nonpromotable() -> None:
    workflow = _read(WORKFLOW)

    assert "actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803" in workflow
    assert "actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow
    assert "UNSAFE-DIAGNOSTIC" in workflow
    assert "build_windows_portable.ps1" in workflow
    assert "windows_candidate_packaged_smoke.ps1" in workflow
    assert "pATHENA-Worker.exe" in workflow
    assert "package_configuration = \"supported-two-executable-onedir\"" in workflow
    assert "distributable_artifact = $null" in workflow
    assert "Candidate has no supported Windows package/EXE" not in workflow


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


def test_packaged_smoke_requires_worker_roles_and_rejects_desktop_recursion() -> None:
    smoke = _read(PACKAGED_SMOKE)

    assert "pATHENA.exe" in smoke
    assert "pATHENA-Worker.exe" in smoke
    assert "ATHENA_LOCAL_ROOT" in smoke
    assert "Get-CimInstance Win32_Process" in smoke
    assert "Desktop self-recursion detected" in smoke
    assert "athena\\.api\\.process" in smoke
    assert "--lane\\s+supervisor" in smoke
    assert "--lane\\s+control" in smoke
    assert "--lane\\s+provider" in smoke
    assert "Packaged processes remained after controlled tree shutdown" in smoke


def test_python_diagnostics_compile_and_cover_ten_reference_surfaces() -> None:
    for path in (DESKTOP_DRIVER, PROVIDER_PROBE):
        ast.parse(_read(path), filename=str(path))

    desktop = _read(DESKTOP_DRIVER)
    assert "app.quit" in desktop
    assert "navigation.count() != 7" in desktop
    assert "captured_reference_surfaces" in desktop
    assert "captured_reference_count" in desktop
    assert "assigned_reference_count" in desktop
    assert "expected_capture_count = 10" in desktop
    assert '"interactive PALLAS"' in desktop
    assert '"standalone search/command palette reference state"' in desktop
    assert '"Help"' in desktop
    assert '"not_implemented_as_target_screens": ["ComfyUI"]' in desktop
    assert "diagnostic semantic graph; presentation only" in desktop
    assert "CommandPaletteController" in desktop
    assert "PallasGroundedFieldController" in desktop

    provider = _read(PROVIDER_PROBE)
    assert "ThreadingHTTPServer" in provider
    assert "ProviderHealthStatus.READY" in provider
    assert "ProviderHealthStatus.UNAVAILABLE" in provider
