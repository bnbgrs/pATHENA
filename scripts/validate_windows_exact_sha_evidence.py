"""Validate exact-SHA Windows release evidence exported from GitHub Actions.

This does not trigger a workflow and does not build pATHENA.  It fail-closes on
stale SHAs, incomplete runs, missing Windows release-guard steps, or non-success
outcomes so Integrator/Backend can distinguish repository contracts from actual
native-Windows evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED_STEPS = (
    "Probe native active-state locality",
    "Run deterministic Windows locality regressions",
    "Run Windows storage path regressions",
    "Run Windows durable filesystem regressions",
    "Run API runtime path-boundary regressions",
    "Run Windows Core/API ownership lifecycle regressions",
    "Run Windows packaged runtime contract regressions",
    "Run Windows adaptive chat reserve contract",
    "Run Windows Core/API restart smoke",
    "Verify Windows pypdf packaging metadata",
    "Enforce Windows release-guard result",
)


def validate_windows_evidence(payload: dict[str, Any], expected_sha: str) -> dict[str, object]:
    errors: list[str] = []
    if not _SHA_RE.fullmatch(expected_sha):
        errors.append("expected SHA must be exactly 40 lowercase hex characters")

    actual_sha = payload.get("head_sha")
    if actual_sha != expected_sha:
        errors.append(f"stale-or-wrong-sha: expected {expected_sha}, got {actual_sha}")
    if payload.get("status") != "completed":
        errors.append(f"workflow-not-completed: {payload.get('status')!r}")
    if payload.get("conclusion") != "success":
        errors.append(f"workflow-not-success: {payload.get('conclusion')!r}")

    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        errors.append("jobs must be a list")
        jobs = []

    windows_jobs = [job for job in jobs if isinstance(job, dict) and job.get("name") == "Windows path safety"]
    if len(windows_jobs) != 1:
        errors.append(f"expected exactly one Windows path safety job, found {len(windows_jobs)}")
        steps: list[dict[str, Any]] = []
        job_conclusion = None
    else:
        windows_job = windows_jobs[0]
        job_conclusion = windows_job.get("conclusion")
        if job_conclusion != "success":
            errors.append(f"Windows path safety job not successful: {job_conclusion!r}")
        raw_steps = windows_job.get("steps")
        if not isinstance(raw_steps, list):
            errors.append("Windows path safety steps must be a list")
            steps = []
        else:
            steps = [step for step in raw_steps if isinstance(step, dict)]

    by_name = {str(step.get("name")): step for step in steps}
    missing_steps: list[str] = []
    failing_steps: list[str] = []
    for name in _REQUIRED_STEPS:
        step = by_name.get(name)
        if step is None:
            missing_steps.append(name)
            continue
        if step.get("status") != "completed" or step.get("conclusion") != "success":
            failing_steps.append(name)

    if missing_steps:
        errors.append("missing Windows steps: " + ", ".join(missing_steps))
    if failing_steps:
        errors.append("non-success Windows steps: " + ", ".join(failing_steps))

    return {
        "expected_sha": expected_sha,
        "actual_sha": actual_sha,
        "exact_sha": actual_sha == expected_sha,
        "workflow_success": payload.get("status") == "completed"
        and payload.get("conclusion") == "success",
        "windows_job_success": job_conclusion == "success",
        "required_steps": len(_REQUIRED_STEPS),
        "missing_steps": missing_steps,
        "failing_steps": failing_steps,
        "release_evidence_ready": not errors,
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
            raise ValueError("Windows evidence root must be a JSON object.")
        report = validate_windows_evidence(payload, args.sha)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        report = {
            "release_evidence_ready": False,
            "errors": [str(exc)],
        }
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(f"release_evidence_ready={report['release_evidence_ready']}")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
