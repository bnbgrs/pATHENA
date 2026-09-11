from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXACT_SHA = "1" * 40
_WINDOWS_STEPS = (
    "Probe native active-state locality",
    "Run deterministic Windows locality regressions",
    "Run Windows storage path regressions",
    "Run Windows durable filesystem regressions",
    "Run API runtime path-boundary regressions",
    "Run Windows Core/API ownership lifecycle regressions",
    "Run Windows packaged runtime contract regressions",
    "Run Windows adaptive chat reserve contract",
    "Run Windows Core/API restart smoke",
    "Verify Windows pypdf packaging metadata",
    "Enforce Windows release-guard result",
)


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts" / script), *args, "--json"],
        cwd=_REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_storage_identity_audit_reproduces_current_open_boundaries() -> None:
    result = _run("audit_storage_identity_contract.py")
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["be046_open"] is True
    assert report["be052_open"] is True
    assert report["findings"] == [
        "BE-046_POSIX_FD_CLOSED_BEFORE_PATH_UNLINK",
        "BE-046_NONPOSIX_PATHNAME_UNLINK_AFTER_IDENTITY_CHECK",
        "BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN",
        "BE-052_FILESET_SIDECAR_ATTESTATION_DROPPED_BEFORE_WRITER",
    ]
    assert len(report["acceptance_cases"]) == 6
    assert {
        case["id"] for case in report["acceptance_cases"]
    } >= {
        "BE046_WINDOWS_PARENT_DIRECTORY_SUBSTITUTION",
        "BE052_WAL_APPEARS_AFTER_PREFLIGHT",
        "BE052_SHM_REPLACED_AFTER_PREFLIGHT",
    }
    assert report["evidence"]["BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN"][
        "preflight_line"
    ] is not None


def test_ui_reference_manifest_obeys_fail_closed_claim_rules() -> None:
    result = _run("validate_ui_reference_evidence.py")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["slots"] == 11
    assert report["errors"] == []
    assert report["match_claims"] == 0


def test_ui_pair_evidence_requires_same_state_and_exact_sha(tmp_path: Path) -> None:
    rows: list[dict[str, object]] = []
    for index in range(1, 12):
        rows.append(
            {
                "slot": f"{index:02d}",
                "reference_opened": False,
                "render_opened": False,
                "verdict": "UNVERIFIED",
            }
        )
    rows[0] = {
        "slot": "01",
        "reference_opened": True,
        "reference_id": "reference-01",
        "render_opened": True,
        "render_id": "runtime-01",
        "render_sha": _EXACT_SHA,
        "reference_state": "chat-empty",
        "render_state": "chat-empty",
        "verdict": "GAP",
        "visible_gaps": ["workspace spacing differs"],
    }
    evidence = tmp_path / "ui-evidence.json"
    evidence.write_text(json.dumps(rows), encoding="utf-8")

    result = _run("validate_ui_pair_evidence.py", str(evidence))
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["slots"] == 11
    assert report["verified_pairs"] == 1
    assert report["visual_ready_11_of_11"] is False
    assert report["verdict_counts"]["GAP"] == 1
    assert report["errors"] == []


def test_ui_pair_evidence_rejects_cross_state_match(tmp_path: Path) -> None:
    rows = [
        {
            "slot": f"{index:02d}",
            "reference_opened": False,
            "render_opened": False,
            "verdict": "UNVERIFIED",
        }
        for index in range(1, 12)
    ]
    rows[0] = {
        "slot": "01",
        "reference_opened": True,
        "reference_id": "reference-01",
        "render_opened": True,
        "render_id": "runtime-01",
        "render_sha": _EXACT_SHA,
        "reference_state": "chat-populated",
        "render_state": "chat-empty",
        "verdict": "MATCH",
        "visible_gaps": [],
    }
    evidence = tmp_path / "ui-bad-evidence.json"
    evidence.write_text(json.dumps(rows), encoding="utf-8")

    result = _run("validate_ui_pair_evidence.py", str(evidence))
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["visual_ready_11_of_11"] is False
    assert any("same reference/runtime state" in error for error in report["errors"])


def test_windows_release_contract_has_required_guards() -> None:
    result = _run("validate_windows_release_contract.py")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["windows_runner"] is True
    assert report["two_exe_contract"] is True
    assert report["pypdf_locked"] is True
    assert report["desktop_runtime_locked"] is True
    assert report["missing"] == []


def test_windows_exact_sha_evidence_accepts_complete_native_lane(tmp_path: Path) -> None:
    payload = {
        "head_sha": _EXACT_SHA,
        "status": "completed",
        "conclusion": "success",
        "jobs": [
            {
                "name": "Windows path safety",
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {"name": name, "status": "completed", "conclusion": "success"}
                    for name in _WINDOWS_STEPS
                ],
            }
        ],
    }
    evidence = tmp_path / "windows-evidence.json"
    evidence.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(
        "validate_windows_exact_sha_evidence.py",
        str(evidence),
        "--sha",
        _EXACT_SHA,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["exact_sha"] is True
    assert report["windows_job_success"] is True
    assert report["release_evidence_ready"] is True
    assert report["missing_steps"] == []
    assert report["failing_steps"] == []


def test_windows_exact_sha_evidence_rejects_stale_sha(tmp_path: Path) -> None:
    payload = {
        "head_sha": "2" * 40,
        "status": "completed",
        "conclusion": "success",
        "jobs": [
            {
                "name": "Windows path safety",
                "status": "completed",
                "conclusion": "success",
                "steps": [
                    {"name": name, "status": "completed", "conclusion": "success"}
                    for name in _WINDOWS_STEPS
                ],
            }
        ],
    }
    evidence = tmp_path / "windows-stale-evidence.json"
    evidence.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(
        "validate_windows_exact_sha_evidence.py",
        str(evidence),
        "--sha",
        _EXACT_SHA,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["exact_sha"] is False
    assert report["release_evidence_ready"] is False
    assert any("stale-or-wrong-sha" in error for error in report["errors"])
