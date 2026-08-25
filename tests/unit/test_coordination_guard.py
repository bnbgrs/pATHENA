from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "coordination_guard.py"
BASE_SHA = "a" * 40
CANDIDATE_SHA = "b" * 40
COMPLETED_SHA = "c" * 40


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def _ledger(*, last_known: str = BASE_SHA) -> dict[str, Any]:
    return {
        "last_known_candidate_sha": last_known,
        "claims": [
            {
                "task_id": "TASK-ACTIVE",
                "status": "CLAIMED",
                "paths": ["src/athena/storage/", "tests/unit/test_storage.py"],
            }
        ],
        "completed": [
            {
                "task_id": "TASK-DONE",
                "status": "COMPLETED",
                "result_candidate_sha": COMPLETED_SHA,
                "paths": ["src/athena/desktop/view.py"],
            }
        ],
    }


def _diff(commits: list[dict[str, object]]) -> dict[str, object]:
    return {
        "base_sha": BASE_SHA,
        "candidate_sha": CANDIDATE_SHA,
        "commits": commits,
    }


def _run_guard(
    tmp_path: Path,
    *,
    ledger: dict[str, Any],
    diff: dict[str, object],
) -> subprocess.CompletedProcess[str]:
    ledger_path = tmp_path / "ledger.json"
    diff_path = tmp_path / "diff.json"
    _write_json(ledger_path, ledger)
    _write_json(diff_path, diff)
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--ledger",
            str(ledger_path),
            "--diff",
            str(diff_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def test_active_and_matching_completed_claims_cover_multi_agent_diff(
    tmp_path: Path,
) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(),
        diff=_diff(
            [
                {
                    "sha": "d" * 40,
                    "paths": [
                        "src/athena/storage/wal_maintenance.py",
                        "tests/unit/test_storage.py",
                    ],
                },
                {
                    "sha": COMPLETED_SHA,
                    "paths": ["src/athena/desktop/view.py"],
                },
            ]
        ),
    )

    assert result.returncode == 0
    assert "coordination guard: PASS" in result.stdout
    assert "covered=3" in result.stdout


def test_single_uncovered_product_path_fails_closed(tmp_path: Path) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(),
        diff=_diff(
            [
                {
                    "sha": "d" * 40,
                    "paths": [
                        "src/athena/storage/wal_maintenance.py",
                        "src/athena/api/unclaimed.py",
                    ],
                }
            ]
        ),
    )

    assert result.returncode == 1
    assert "uncovered product mutation" in result.stdout
    assert "src/athena/api/unclaimed.py" in result.stdout


def test_stale_ledger_sha_fails_closed(tmp_path: Path) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(last_known="f" * 40),
        diff=_diff([]),
    )

    assert result.returncode == 1
    assert "stale ledger candidate SHA" in result.stdout


def test_candidate_already_recorded_requires_empty_diff(tmp_path: Path) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(last_known=CANDIDATE_SHA),
        diff=_diff([{"sha": "d" * 40, "paths": ["src/athena/storage/x.py"]}]),
    )

    assert result.returncode == 1
    assert "already names candidate SHA" in result.stdout


@pytest.mark.parametrize(
    ("classification", "path"),
    [
        ("COORDINATION_METADATA", ".pathena/agent-ledger.json"),
        ("COORDINATION_METADATA", ".pathena/AGENT_COORDINATION.md"),
        ("NON_PRODUCT_EVIDENCE", ".github/windows-candidate-request.txt"),
    ],
)
def test_explicit_non_product_classifications_are_separate_and_bounded(
    tmp_path: Path,
    classification: str,
    path: str,
) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(),
        diff=_diff(
            [
                {
                    "sha": "d" * 40,
                    "classification": classification,
                    "paths": [path],
                }
            ]
        ),
    )

    assert result.returncode == 0
    assert "coordination guard: PASS" in result.stdout


@pytest.mark.parametrize(
    ("classification", "path"),
    [
        ("COORDINATION_METADATA", "src/athena/core.py"),
        ("NON_PRODUCT_EVIDENCE", "src/athena/core.py"),
    ],
)
def test_non_product_classification_cannot_hide_product_path(
    tmp_path: Path,
    classification: str,
    path: str,
) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(),
        diff=_diff(
            [
                {
                    "sha": "d" * 40,
                    "classification": classification,
                    "paths": [path],
                }
            ]
        ),
    )

    assert result.returncode == 1
    assert path in result.stdout


def test_old_completed_claim_does_not_authorize_future_mutation(tmp_path: Path) -> None:
    result = _run_guard(
        tmp_path,
        ledger=_ledger(),
        diff=_diff(
            [
                {
                    "sha": "d" * 40,
                    "paths": ["src/athena/desktop/view.py"],
                }
            ]
        ),
    )

    assert result.returncode == 1
    assert "src/athena/desktop/view.py" in result.stdout


def test_malformed_diff_fails_closed(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.json"
    diff_path = tmp_path / "diff.json"
    _write_json(ledger_path, _ledger())
    _write_json(diff_path, {"base_sha": BASE_SHA, "candidate_sha": CANDIDATE_SHA})

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--ledger",
            str(ledger_path),
            "--diff",
            str(diff_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "diff.commits" in result.stdout
