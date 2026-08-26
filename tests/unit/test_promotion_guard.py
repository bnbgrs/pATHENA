from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CANDIDATE_REF = "refs/heads/bot/pathena-candidate"
SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "promotion_guard.py"


def _valid_tree(root: Path) -> None:
    workflow = root / ".github" / "workflows" / "quality.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: quality\n", encoding="utf-8")


def _run_guard(root: Path, *, actual_ref: str = CANDIDATE_REF) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(root),
            "--actual-ref",
            actual_ref,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_valid_candidate_tree_passes(tmp_path: Path) -> None:
    _valid_tree(tmp_path)

    result = _run_guard(tmp_path)

    assert result.returncode == 0
    assert "promotion guard: PASS" in result.stdout


@pytest.mark.parametrize(
    "legacy_path",
    [
        ".github/workflows/pathena-bootstrap.yml",
        ".github/workflows/pathena-slice-gate.yml",
        ".pathena-bootstrap",
    ],
)
def test_legacy_files_fail_closed(tmp_path: Path, legacy_path: str) -> None:
    _valid_tree(tmp_path)
    target = tmp_path / legacy_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("legacy\n", encoding="utf-8")

    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert legacy_path in result.stdout


def test_legacy_bootstrap_payload_tree_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)
    payload = tmp_path / ".pathena" / "bootstrap" / "000.b64"
    payload.parent.mkdir(parents=True)
    payload.write_text("legacy\n", encoding="utf-8")

    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert ".pathena/bootstrap" in result.stdout


def test_missing_quality_workflow_fails_closed(tmp_path: Path) -> None:
    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert "quality.yml" in result.stdout


def test_unexpected_ref_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)

    result = _run_guard(tmp_path, actual_ref="refs/heads/main")

    assert result.returncode == 1
    assert "expected ref" in result.stdout
