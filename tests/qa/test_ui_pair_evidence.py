from __future__ import annotations

import copy

from scripts.validate_ui_pair_evidence import (
    AUTHORITATIVE_REFERENCES,
    evidence_exit_code,
    validate_pair_evidence,
)

_EXACT_SHA = "1" * 40


def _rows() -> list[dict[str, object]]:
    return [
        {
            "slot": reference.slot,
            "reference_id": reference.reference_id,
            "reference_file": reference.filename,
            "reference_state": reference.state,
            "reference_opened": False,
            "render_opened": False,
            "verdict": "UNVERIFIED",
        }
        for reference in AUTHORITATIVE_REFERENCES
    ]


def _open_pair(row: dict[str, object], *, verdict: str = "MATCH") -> None:
    row["reference_opened"] = True
    row["render_opened"] = True
    row["render_id"] = f"runtime-{row['slot']}"
    row["render_sha"] = _EXACT_SHA
    row["render_state"] = row["reference_state"]
    row["verdict"] = verdict
    row["visible_gaps"] = [] if verdict == "MATCH" else ["visible composition gap"]


def test_unverified_authoritative_inventory_is_truthful_but_not_visual_ready() -> None:
    report = validate_pair_evidence(_rows())

    assert report["errors"] == []
    assert report["slots"] == 11
    assert report["verified_pairs"] == 0
    assert report["verdict_counts"]["UNVERIFIED"] == 11
    assert report["visual_ready_11_of_11"] is False
    assert evidence_exit_code(report) == 0
    assert evidence_exit_code(report, require_ready=True) == 2


def test_exact_same_state_gap_is_evidence_eligible_but_not_visual_ready() -> None:
    rows = _rows()
    _open_pair(rows[0], verdict="GAP")

    report = validate_pair_evidence(rows)

    assert report["errors"] == []
    assert report["verified_pairs"] == 1
    assert report["verdict_counts"]["GAP"] == 1
    assert report["visual_ready_11_of_11"] is False
    assert evidence_exit_code(report) == 0
    assert evidence_exit_code(report, require_ready=True) == 2


def test_light_workspace_slot_rejects_files_capture_identity() -> None:
    rows = _rows()
    light = rows[9]
    _open_pair(light)
    light["reference_id"] = "sources-files"
    light["reference_file"] = "Sources and Files.png"
    light["reference_state"] = "files-workspace"
    light["render_state"] = "files-workspace"

    report = validate_pair_evidence(rows)

    assert report["visual_ready_11_of_11"] is False
    errors = report["errors"]
    assert any("slot 10: reference_id" in error for error in errors)
    assert any("slot 10: reference_file" in error for error in errors)
    assert any("slot 10: reference_state" in error for error in errors)
    assert any("slot 10: MATCH requires canonical same-state render 'light-workspace'" in error for error in errors)
    assert evidence_exit_code(report) == 1
    assert evidence_exit_code(report, require_ready=True) == 1


def test_cross_state_match_fails_closed() -> None:
    rows = _rows()
    _open_pair(rows[4])
    rows[4]["render_state"] = "chat-empty"

    report = validate_pair_evidence(rows)

    assert report["visual_ready_11_of_11"] is False
    assert any("slot 05: MATCH requires canonical same-state render" in error for error in report["errors"])


def test_opened_render_requires_exact_lowercase_sha() -> None:
    rows = _rows()
    _open_pair(rows[0])
    rows[0]["render_sha"] = "A" * 40

    report = validate_pair_evidence(rows)

    assert report["visual_ready_11_of_11"] is False
    assert any("exact lowercase 40-char SHA" in error for error in report["errors"])


def test_unicode_normalization_does_not_break_authoritative_filename_identity() -> None:
    rows = _rows()
    rows[3]["reference_file"] = "Hilfe und Fa\u0308higkeiten von pATHENA.png"

    report = validate_pair_evidence(rows)

    assert report["errors"] == []


def test_all_eleven_exact_same_state_matches_are_required_for_visual_ready() -> None:
    rows = _rows()
    for row in rows:
        _open_pair(row)

    report = validate_pair_evidence(rows)

    assert report["errors"] == []
    assert report["verified_pairs"] == 11
    assert report["verdict_counts"]["MATCH"] == 11
    assert report["visual_ready_11_of_11"] is True
    assert evidence_exit_code(report) == 0
    assert evidence_exit_code(report, require_ready=True) == 0

    close_rows = copy.deepcopy(rows)
    close_rows[0]["verdict"] = "CLOSE"
    close_rows[0]["visible_gaps"] = ["minor spacing difference"]
    close_report = validate_pair_evidence(close_rows)
    assert close_report["errors"] == []
    assert close_report["visual_ready_11_of_11"] is False
    assert evidence_exit_code(close_report) == 0
    assert evidence_exit_code(close_report, require_ready=True) == 2
