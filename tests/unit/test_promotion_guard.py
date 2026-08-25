from __future__ import annotations

from pathlib import Path

import pytest

from scripts.promotion_guard import CANDIDATE_REF, inspect_promotion_tree


def _valid_tree(root: Path) -> None:
    workflow = root / ".github" / "workflows" / "quality.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: quality\n", encoding="utf-8")


def test_valid_candidate_tree_passes(tmp_path: Path) -> None:
    _valid_tree(tmp_path)

    result = inspect_promotion_tree(tmp_path, actual_ref=CANDIDATE_REF)

    assert result.ok
    assert result.errors == ()


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

    result = inspect_promotion_tree(tmp_path, actual_ref=CANDIDATE_REF)

    assert not result.ok
    assert any(legacy_path in error for error in result.errors)


def test_legacy_bootstrap_payload_tree_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)
    payload = tmp_path / ".pathena" / "bootstrap" / "000.b64"
    payload.parent.mkdir(parents=True)
    payload.write_text("legacy\n", encoding="utf-8")

    result = inspect_promotion_tree(tmp_path, actual_ref=CANDIDATE_REF)

    assert not result.ok
    assert any(".pathena/bootstrap" in error for error in result.errors)


def test_missing_quality_workflow_fails_closed(tmp_path: Path) -> None:
    result = inspect_promotion_tree(tmp_path, actual_ref=CANDIDATE_REF)

    assert not result.ok
    assert any("quality.yml" in error for error in result.errors)


def test_unexpected_ref_fails_closed(tmp_path: Path) -> None:
    _valid_tree(tmp_path)

    result = inspect_promotion_tree(tmp_path, actual_ref="refs/heads/main")

    assert not result.ok
    assert any("expected ref" in error for error in result.errors)
