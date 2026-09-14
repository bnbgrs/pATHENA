from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "validate_ui_pair_evidence.py"
_SHA = "1" * 40
_IDENTITIES = (
    "ComfyUI",
    "PALLAS",
    "Settings",
    "Help",
    "Dark Workspace / Evidence",
    "Jobs",
    "Command Palette",
    "System",
    "Research",
    "Light Workspace",
    "Local Memory",
)


def _rows() -> list[dict[str, object]]:
    return [
        {
            "slot": f"{index:02d}",
            "reference_identity": identity,
            "reference_opened": False,
            "render_opened": False,
            "verdict": "UNVERIFIED",
        }
        for index, identity in enumerate(_IDENTITIES, start=1)
    ]


def _run(tmp_path: Path, rows: list[dict[str, object]]) -> tuple[int, dict[str, object]]:
    evidence = tmp_path / "ui-pair-evidence.json"
    evidence.write_text(json.dumps(rows), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(evidence), "--json"],
        cwd=_REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode, json.loads(result.stdout)


def test_reference_slots_are_bound_even_before_pair_verification(tmp_path: Path) -> None:
    returncode, report = _run(tmp_path, _rows())

    assert returncode == 0
    assert report["slots"] == 11
    assert report["identity_bound_slots"] == 11
    assert report["verified_pairs"] == 0
    assert report["visual_ready_11_of_11"] is False
    assert report["errors"] == []


def test_slot_10_rejects_files_as_light_workspace_reference(tmp_path: Path) -> None:
    rows = _rows()
    rows[9]["reference_identity"] = "Files"

    returncode, report = _run(tmp_path, rows)

    assert returncode == 1
    assert report["identity_bound_slots"] == 10
    assert report["visual_ready_11_of_11"] is False
    assert any(
        "slot 10: expected reference identity 'Light Workspace'" in error
        for error in report["errors"]
    )


def test_match_requires_same_canonical_identity_state_and_exact_sha(
    tmp_path: Path,
) -> None:
    rows = _rows()
    rows[9].update(
        {
            "reference_opened": True,
            "reference_id": "human-reference-10",
            "render_opened": True,
            "render_id": "runtime-render-10",
            "render_identity": "Files",
            "render_sha": _SHA,
            "reference_state": "light-workspace-empty",
            "render_state": "light-workspace-empty",
            "verdict": "MATCH",
            "visible_gaps": [],
        }
    )

    returncode, report = _run(tmp_path, rows)

    assert returncode == 1
    assert report["verified_pairs"] == 0
    assert report["visual_ready_11_of_11"] is False
    assert any("canonical identity pairing" in error for error in report["errors"])
