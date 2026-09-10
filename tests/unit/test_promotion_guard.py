from __future__ import annotations

import os
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


def _run_guard(
    root: Path, *, actual_ref: str = CANDIDATE_REF
) -> subprocess.CompletedProcess[str]:
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


def _symlink_or_skip(
    target: str | Path,
    link: Path,
    *,
    target_is_directory: bool = False,
) -> None:
    try:
        link.symlink_to(target, target_is_directory=target_is_directory)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")


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


def test_required_quality_workflow_symlink_fails_closed(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "quality.yml"
    workflow.parent.mkdir(parents=True)
    real_workflow = tmp_path / "quality-real.yml"
    real_workflow.write_text("name: quality\n", encoding="utf-8")
    _symlink_or_skip(real_workflow, workflow)

    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert "non-symlink regular file" in result.stdout


def test_broken_forbidden_symlink_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)
    forbidden = tmp_path / ".github" / "workflows" / "pathena-bootstrap.yml"
    _symlink_or_skip("missing-target.yml", forbidden)
    assert os.path.lexists(forbidden)
    assert not forbidden.exists()

    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert "pathena-bootstrap.yml" in result.stdout


def test_broken_forbidden_tree_symlink_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)
    forbidden_tree = tmp_path / ".pathena" / "bootstrap"
    forbidden_tree.parent.mkdir(parents=True)
    _symlink_or_skip("missing-tree", forbidden_tree, target_is_directory=True)
    assert os.path.lexists(forbidden_tree)
    assert not forbidden_tree.exists()

    result = _run_guard(tmp_path)

    assert result.returncode == 1
    assert ".pathena/bootstrap" in result.stdout
