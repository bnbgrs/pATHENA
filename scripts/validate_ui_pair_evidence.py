"""Validate exact-state visual evidence for the canonical eleven pATHENA screens.

The UI worker owns rendering and product changes.  This independent validator
only defines when a visual verdict is evidence-eligible: the original reference
and the exact runtime render must both have been opened, the render must be tied
to a full commit SHA, and both artifacts must describe the same state.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_VERDICTS = {"MATCH", "CLOSE", "GAP", "UNVERIFIED"}


def _load(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("UI pair evidence must be a JSON list.")
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"UI pair evidence row {index} must be an object.")
        rows.append(item)
    return rows


def validate_pair_evidence(rows: list[dict[str, Any]]) -> dict[str, object]:
    errors: list[str] = []
    expected = [f"{index:02d}" for index in range(1, 12)]
    slots = [str(row.get("slot", "")) for row in rows]
    if slots != expected:
        errors.append(f"expected slots {expected}, found {slots}")

    verified_pairs = 0
    verdict_counts = {name: 0 for name in sorted(_ALLOWED_VERDICTS)}

    for row in rows:
        slot = str(row.get("slot", "?"))
        verdict = row.get("verdict")
        if verdict not in _ALLOWED_VERDICTS:
            errors.append(f"slot {slot}: invalid verdict {verdict!r}")
            continue
        verdict_counts[str(verdict)] += 1

        reference_opened = row.get("reference_opened") is True
        render_opened = row.get("render_opened") is True
        reference_id = row.get("reference_id")
        render_id = row.get("render_id")
        render_sha = row.get("render_sha")
        reference_state = row.get("reference_state")
        render_state = row.get("render_state")

        if reference_opened and not isinstance(reference_id, str):
            errors.append(f"slot {slot}: opened reference requires reference_id")
        if render_opened and not isinstance(render_id, str):
            errors.append(f"slot {slot}: opened render requires render_id")
        if render_opened and not (isinstance(render_sha, str) and _SHA_RE.fullmatch(render_sha)):
            errors.append(f"slot {slot}: opened render requires exact 40-char SHA")

        same_state = (
            isinstance(reference_state, str)
            and reference_state != ""
            and reference_state == render_state
        )
        pair_verified = reference_opened and render_opened and same_state
        if pair_verified:
            verified_pairs += 1

        if verdict in {"MATCH", "CLOSE", "GAP"}:
            if not reference_opened:
                errors.append(f"slot {slot}: {verdict} requires opened original reference")
            if not render_opened:
                errors.append(f"slot {slot}: {verdict} requires opened exact runtime render")
            if not same_state:
                errors.append(f"slot {slot}: {verdict} requires same reference/runtime state")
            if not (isinstance(render_sha, str) and _SHA_RE.fullmatch(render_sha)):
                errors.append(f"slot {slot}: {verdict} requires exact runtime SHA")

        if verdict == "MATCH" and row.get("visible_gaps") not in ([], None):
            errors.append(f"slot {slot}: MATCH cannot carry visible_gaps")
        if verdict == "GAP" and not row.get("visible_gaps"):
            errors.append(f"slot {slot}: GAP requires at least one visible_gaps entry")

    return {
        "slots": len(rows),
        "verified_pairs": verified_pairs,
        "verdict_counts": verdict_counts,
        "visual_ready_11_of_11": verified_pairs == 11
        and verdict_counts["GAP"] == 0
        and verdict_counts["UNVERIFIED"] == 0,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        rows = _load(args.evidence)
        report = validate_pair_evidence(rows)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "slots": 0,
            "verified_pairs": 0,
            "verdict_counts": {},
            "visual_ready_11_of_11": False,
            "errors": [str(exc)],
        }
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(
            f"slots={report['slots']} verified_pairs={report['verified_pairs']} "
            f"visual_ready={report['visual_ready_11_of_11']}"
        )
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
