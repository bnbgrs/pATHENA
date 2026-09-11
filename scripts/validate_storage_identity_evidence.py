"""Validate exact-SHA adversarial evidence for BE-046 and BE-052 closure.

This validator does not implement Storage fixes. It defines the minimum evidence
packet Backend must produce before Integrator/Error can call the identity gaps
closed. Evidence is fail-closed, exact-SHA-bound and case-complete.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED_CASES = {
    "BE046_POSIX_RELEASE_SAME_PARENT_TARGET_REPLACEMENT": "posix",
    "BE046_POSIX_FAILURE_CLEANUP_TARGET_REPLACEMENT": "posix",
    "BE046_WINDOWS_RELEASE_SAME_PARENT_TARGET_REPLACEMENT": "windows",
    "BE046_WINDOWS_FAILURE_CLEANUP_TARGET_REPLACEMENT": "windows",
    "BE046_WINDOWS_PARENT_DIRECTORY_SUBSTITUTION": "windows",
    "BE052_WAL_APPEARS_AFTER_PREFLIGHT": "all",
    "BE052_SHM_REPLACED_AFTER_PREFLIGHT": "all",
    "BE052_PRIMARY_REPLACED_AFTER_PREFLIGHT": "all",
}
_BE046_CASES = {case for case in _REQUIRED_CASES if case.startswith("BE046_")}
_BE052_CASES = {case for case in _REQUIRED_CASES if case.startswith("BE052_")}


def validate_storage_evidence(payload: dict[str, Any], expected_sha: str) -> dict[str, object]:
    errors: list[str] = []
    if not _SHA_RE.fullmatch(expected_sha):
        errors.append("expected SHA must be exactly 40 lowercase hex characters")

    actual_sha = payload.get("head_sha")
    if actual_sha != expected_sha:
        errors.append(f"stale-or-wrong-sha: expected {expected_sha}, got {actual_sha}")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        errors.append("cases must be a list")
        raw_cases = []

    by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            errors.append("every case must be an object")
            continue
        case_id = raw_case.get("id")
        if not isinstance(case_id, str):
            errors.append("every case requires string id")
            continue
        if case_id in by_id:
            duplicate_ids.append(case_id)
        by_id[case_id] = raw_case

    if duplicate_ids:
        errors.append("duplicate cases: " + ", ".join(sorted(set(duplicate_ids))))

    missing = sorted(set(_REQUIRED_CASES) - set(by_id))
    unexpected = sorted(set(by_id) - set(_REQUIRED_CASES))
    if missing:
        errors.append("missing cases: " + ", ".join(missing))
    if unexpected:
        errors.append("unexpected cases: " + ", ".join(unexpected))

    failing: list[str] = []
    for case_id, required_platform in _REQUIRED_CASES.items():
        case = by_id.get(case_id)
        if case is None:
            continue
        if case.get("status") != "completed" or case.get("conclusion") != "success":
            failing.append(case_id)
            continue
        if case.get("platform") != required_platform:
            errors.append(
                f"{case_id}: platform must be {required_platform!r}, got {case.get('platform')!r}"
            )
        if case_id in _BE046_CASES:
            if case.get("foreign_or_replacement_object_preserved") is not True:
                errors.append(f"{case_id}: must prove foreign/replacement object preserved")
            if case.get("released_original_object_only") is not True:
                errors.append(f"{case_id}: must prove only the originally bound object was released")
        if case_id in _BE052_CASES:
            if case.get("writer_started") is not False:
                errors.append(f"{case_id}: writer must not start after post-preflight substitution")
            if case.get("failed_closed") is not True:
                errors.append(f"{case_id}: must prove fail-closed writer startup")

    if failing:
        errors.append("non-success cases: " + ", ".join(sorted(failing)))

    return {
        "expected_sha": expected_sha,
        "actual_sha": actual_sha,
        "exact_sha": actual_sha == expected_sha,
        "required_cases": len(_REQUIRED_CASES),
        "present_cases": len(set(by_id) & set(_REQUIRED_CASES)),
        "missing_cases": missing,
        "unexpected_cases": unexpected,
        "failing_cases": sorted(failing),
        "be046_evidence_ready": not any(
            case in missing or case in failing for case in _BE046_CASES
        )
        and not any(case in error for error in errors for case in _BE046_CASES),
        "be052_evidence_ready": not any(
            case in missing or case in failing for case in _BE052_CASES
        )
        and not any(case in error for error in errors for case in _BE052_CASES),
        "closure_evidence_ready": not errors,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Storage evidence root must be a JSON object.")
        report = validate_storage_evidence(payload, args.sha)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "closure_evidence_ready": False,
            "errors": [str(exc)],
        }
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"closure_evidence_ready={report['closure_evidence_ready']}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
