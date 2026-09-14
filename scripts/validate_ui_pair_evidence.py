"""Validate exact-state visual evidence for the canonical pATHENA references.

Visual readiness is fail-closed. Each slot is bound to one human-reviewed
reference identity, and a runtime render can only be paired with that same
identity and state on an exact commit SHA.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_VERDICTS = {"MATCH", "CLOSE", "GAP", "UNVERIFIED"}
_REFERENCE_IDENTITIES = {
    "01": "ComfyUI",
    "02": "PALLAS",
    "03": "Settings",
    "04": "Help",
    "05": "Dark Workspace / Evidence",
    "06": "Jobs",
    "07": "Command Palette",
    "08": "System",
    "09": "Research",
    "10": "Light Workspace",
    "11": "Local Memory",
}


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
    expected_slots = list(_REFERENCE_IDENTITIES)
    slots = [str(row.get("slot", "")) for row in rows]
    if slots != expected_slots:
        errors.append(f"expected slots {expected_slots}, found {slots}")

    verified_pairs = 0
    identity_bound_slots = 0
    verdict_counts = {name: 0 for name in sorted(_ALLOWED_VERDICTS)}

    for row in rows:
        slot = str(row.get("slot", "?"))
        expected_identity = _REFERENCE_IDENTITIES.get(slot)
        reference_identity = row.get("reference_identity")
        render_identity = row.get("render_identity")

        if expected_identity is None:
            errors.append(f"slot {slot}: unknown canonical reference slot")
        elif reference_identity != expected_identity:
            errors.append(
                f"slot {slot}: expected reference identity {expected_identity!r}, "
                f"found {reference_identity!r}"
            )
        else:
            identity_bound_slots += 1

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
        if render_opened and not (
            isinstance(render_sha, str) and _SHA_RE.fullmatch(render_sha)
        ):
            errors.append(f"slot {slot}: opened render requires exact 40-char SHA")
        if render_opened and render_identity != expected_identity:
            errors.append(
                f"slot {slot}: render identity must be {expected_identity!r}, "
                f"found {render_identity!r}"
            )

        same_state = (
            isinstance(reference_state, str)
            and reference_state != ""
            and reference_state == render_state
        )
        same_identity = (
            expected_identity is not None
            and reference_identity == expected_identity
            and render_identity == expected_identity
        )
        pair_verified = reference_opened and render_opened and same_state and same_identity
        if pair_verified:
            verified_pairs += 1

        if verdict in {"MATCH", "CLOSE", "GAP"}:
            if not reference_opened:
                errors.append(f"slot {slot}: {verdict} requires opened original reference")
            if not render_opened:
                errors.append(f"slot {slot}: {verdict} requires opened exact runtime render")
            if not same_identity:
                errors.append(f"slot {slot}: {verdict} requires canonical identity pairing")
            if not same_state:
                errors.append(f"slot {slot}: {verdict} requires same reference/runtime state")
            if not (
                isinstance(render_sha, str) and _SHA_RE.fullmatch(render_sha)
            ):
                errors.append(f"slot {slot}: {verdict} requires exact runtime SHA")

        if verdict == "MATCH" and row.get("visible_gaps") not in ([], None):
            errors.append(f"slot {slot}: MATCH cannot carry visible_gaps")
        if verdict == "GAP" and not row.get("visible_gaps"):
            errors.append(f"slot {slot}: GAP requires at least one visible_gaps entry")

    return {
        "slots": len(rows),
        "identity_bound_slots": identity_bound_slots,
        "verified_pairs": verified_pairs,
        "verdict_counts": verdict_counts,
        "visual_ready_11_of_11": (
            not errors
            and identity_bound_slots == 11
            and verified_pairs == 11
            and verdict_counts["GAP"] == 0
            and verdict_counts["UNVERIFIED"] == 0
        ),
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
            "identity_bound_slots": 0,
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
