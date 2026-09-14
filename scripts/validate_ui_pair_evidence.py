"""Validate visual evidence against the authoritative pATHENA 11-screen set.

The validator is intentionally independent of rendering. It decides whether a
human visual verdict is evidence-eligible: every slot must identify the canonical
original state, and substantive verdicts require an opened exact-SHA runtime render
of that same state.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_ALLOWED_VERDICTS = frozenset({"MATCH", "CLOSE", "GAP", "UNVERIFIED"})
_SUBSTANTIVE_VERDICTS = frozenset({"MATCH", "CLOSE", "GAP"})


@dataclass(frozen=True, slots=True)
class AuthoritativeReference:
    slot: str
    reference_id: str
    filename: str
    state: str


AUTHORITATIVE_REFERENCES = (
    AuthoritativeReference(
        "01",
        "comfyui-integration",
        "ComfyUI Integration für KI-Workflows.png",
        "comfyui-shell",
    ),
    AuthoritativeReference(
        "02",
        "pallas-knowledge-structure",
        "PALLAS Wissensstruktur-Visualisierung.png",
        "pallas-full",
    ),
    AuthoritativeReference(
        "03",
        "settings-models-local-ai",
        "Settings Modelle und lokale KI.png",
        "settings-models-local-ai",
    ),
    AuthoritativeReference(
        "04",
        "help-capabilities",
        "Hilfe und Fähigkeiten von pATHENA.png",
        "help-capabilities",
    ),
    AuthoritativeReference(
        "05",
        "dark-workspace-evidence",
        "pATHENA im eleganten Dunkelmodus.png",
        "dark-workspace-evidence",
    ),
    AuthoritativeReference(
        "06",
        "jobs-active",
        "Jobs und Hintergrundprozesse.png",
        "jobs-active",
    ),
    AuthoritativeReference(
        "07",
        "command-palette-workspace",
        "Schnelle Navigation mit Command Palette.png",
        "command-palette-workspace",
    ),
    AuthoritativeReference(
        "08",
        "system-healthy",
        "Systemstatus und lokale Dienste.png",
        "system-healthy",
    ),
    AuthoritativeReference(
        "09",
        "research-populated",
        "pATHENA – Dunkles Studio für Wissensforschung.png",
        "research-populated",
    ),
    AuthoritativeReference(
        "10",
        "light-workspace",
        "pATHENA: Intelligenzstudio für lokales Wissen.png",
        "light-workspace",
    ),
    AuthoritativeReference(
        "11",
        "local-memory-populated",
        "Lokale Gedächtnisbildung mit voller Nachvollziehbarkeit.png",
        "local-memory-populated",
    ),
)


def _normalized(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _nonblank_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_gap_descriptions(value: object) -> bool:
    return isinstance(value, list) and all(_nonblank_text(item) for item in value)


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
    expected_slots = [reference.slot for reference in AUTHORITATIVE_REFERENCES]
    actual_slots = [str(row.get("slot", "")) for row in rows]
    if actual_slots != expected_slots:
        errors.append(f"expected slots {expected_slots}, found {actual_slots}")

    verified_pairs = 0
    verdict_counts = {name: 0 for name in sorted(_ALLOWED_VERDICTS)}

    for index, reference in enumerate(AUTHORITATIVE_REFERENCES):
        if index >= len(rows):
            break
        row = rows[index]
        slot = reference.slot
        verdict = row.get("verdict")
        if verdict not in _ALLOWED_VERDICTS:
            errors.append(f"slot {slot}: invalid verdict {verdict!r}")
            continue
        verdict_counts[str(verdict)] += 1

        reference_id = row.get("reference_id")
        reference_file = row.get("reference_file")
        reference_state = row.get("reference_state")
        reference_id_matches = reference_id == reference.reference_id
        reference_file_matches = (
            isinstance(reference_file, str)
            and _normalized(reference_file) == _normalized(reference.filename)
        )
        reference_state_matches = reference_state == reference.state

        if not reference_id_matches:
            errors.append(
                f"slot {slot}: reference_id {reference_id!r} != "
                f"{reference.reference_id!r}"
            )
        if not reference_file_matches:
            errors.append(
                f"slot {slot}: reference_file does not identify authoritative original"
            )
        if not reference_state_matches:
            errors.append(
                f"slot {slot}: reference_state {reference_state!r} != "
                f"{reference.state!r}"
            )

        reference_opened = row.get("reference_opened") is True
        render_opened = row.get("render_opened") is True
        render_id = row.get("render_id")
        render_sha = row.get("render_sha")
        render_state = row.get("render_state")
        exact_sha = isinstance(render_sha, str) and _SHA_RE.fullmatch(render_sha) is not None
        render_id_valid = _nonblank_text(render_id)
        same_state = reference_state_matches and render_state == reference.state

        if render_opened and not render_id_valid:
            errors.append(f"slot {slot}: opened render requires non-blank render_id")
        if render_opened and not exact_sha:
            errors.append(
                f"slot {slot}: opened render requires exact lowercase 40-char SHA"
            )

        identity_matches = (
            reference_id_matches and reference_file_matches and reference_state_matches
        )
        pair_verified = (
            identity_matches
            and reference_opened
            and render_opened
            and render_id_valid
            and exact_sha
            and same_state
        )
        if pair_verified:
            verified_pairs += 1

        if verdict in _SUBSTANTIVE_VERDICTS:
            if not reference_opened:
                errors.append(f"slot {slot}: {verdict} requires opened original reference")
            if not render_opened:
                errors.append(f"slot {slot}: {verdict} requires opened exact runtime render")
            if not render_id_valid:
                errors.append(f"slot {slot}: {verdict} requires non-blank render_id")
            if not exact_sha:
                errors.append(f"slot {slot}: {verdict} requires exact runtime SHA")
            if not same_state:
                errors.append(
                    f"slot {slot}: {verdict} requires canonical same-state render "
                    f"{reference.state!r}"
                )

        visible_gaps = row.get("visible_gaps")
        if visible_gaps is not None and not _valid_gap_descriptions(visible_gaps):
            errors.append(
                f"slot {slot}: visible_gaps must be a list of non-blank strings"
            )
        if verdict == "MATCH" and visible_gaps not in ([], None):
            errors.append(f"slot {slot}: MATCH cannot carry visible_gaps")
        if verdict in {"CLOSE", "GAP"} and (
            not _valid_gap_descriptions(visible_gaps) or not visible_gaps
        ):
            errors.append(f"slot {slot}: {verdict} requires visible_gaps")

    visual_ready = (
        not errors
        and len(rows) == len(AUTHORITATIVE_REFERENCES)
        and verified_pairs == len(AUTHORITATIVE_REFERENCES)
        and verdict_counts["MATCH"] == len(AUTHORITATIVE_REFERENCES)
    )
    return {
        "slots": len(rows),
        "verified_pairs": verified_pairs,
        "verdict_counts": verdict_counts,
        "visual_ready_11_of_11": visual_ready,
        "errors": errors,
    }


def evidence_exit_code(
    report: dict[str, object],
    *,
    require_ready: bool = False,
) -> int:
    """Separate evidence-shape validity from an explicit 11/11 release gate."""
    if report.get("errors"):
        return 1
    if require_ready and report.get("visual_ready_11_of_11") is not True:
        return 2
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit non-zero unless all eleven authoritative same-state pairs are MATCH.",
    )
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
    return evidence_exit_code(report, require_ready=args.require_ready)


if __name__ == "__main__":
    raise SystemExit(main())
