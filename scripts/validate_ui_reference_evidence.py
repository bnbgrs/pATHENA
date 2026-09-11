"""Validate fail-closed evidence rules for the canonical 11-screen UI manifest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_SLOT_RE = re.compile(r"^\|\s*(\d{2})\s*\|")


def validate_manifest(path: Path) -> dict[str, object]:
    rows: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _SLOT_RE.match(line)
        if match:
            rows.append((match.group(1), line))

    expected = [f"{index:02d}" for index in range(1, 12)]
    slots = [slot for slot, _line in rows]
    errors: list[str] = []
    if slots != expected:
        errors.append(f"expected slots {expected}, found {slots}")

    opened = 0
    pending = 0
    matches = 0
    for slot, row in rows:
        columns = [part.strip() for part in row.strip().strip("|").split("|")]
        if len(columns) < 6:
            errors.append(f"slot {slot}: malformed manifest row")
            continue
        reference = columns[2]
        status = columns[4]
        if "AVAILABLE_OPENED" in reference:
            opened += 1
        if "VISUAL_REFERENCE_PENDING" in reference:
            pending += 1
        if "`MATCH`" in status or status == "MATCH":
            matches += 1
            if "AVAILABLE_OPENED" not in reference:
                errors.append(f"slot {slot}: MATCH without opened original reference")
            if "VISUAL_REFERENCE_PENDING" in reference:
                errors.append(f"slot {slot}: MATCH while reference is pending")

    return {
        "slots": len(rows),
        "opened_references": opened,
        "pending_references": pending,
        "match_claims": matches,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs/ui/11_SCREEN_REFERENCE_MANIFEST.md",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_manifest(args.manifest)
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(
            f"slots={report['slots']} opened={report['opened_references']} "
            f"pending={report['pending_references']} matches={report['match_claims']}"
        )
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
