from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _run(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts" / script), "--json"],
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
    ]


def test_ui_reference_manifest_obeys_fail_closed_claim_rules() -> None:
    result = _run("validate_ui_reference_evidence.py")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["slots"] == 11
    assert report["errors"] == []
    assert report["match_claims"] == 0


def test_windows_release_contract_has_required_guards() -> None:
    result = _run("validate_windows_release_contract.py")
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["windows_runner"] is True
    assert report["two_exe_contract"] is True
    assert report["pypdf_locked"] is True
    assert report["desktop_runtime_locked"] is True
    assert report["missing"] == []
