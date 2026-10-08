"""Read-only, payload-free recovery issue projection (no Qt or Core mutation)."""
from __future__ import annotations

from collections.abc import Mapping


def project_recovery_issue_details(payload: Mapping[str, object]) -> str:
    """Format all issues, failing closed on malformed or contradictory diagnoses."""
    status = payload.get("status")
    canonical = payload.get("canonical_database")
    issues = payload.get("issues")
    if status not in {"healthy", "degraded-derived", "recovery-required"}:
        raise ValueError("Recovery issue details require a recognized status.")
    if not isinstance(canonical, str) or not canonical.strip():
        raise ValueError("Recovery issue details require canonical database state.")
    if not isinstance(issues, list):
        raise ValueError("Recovery issue details require a list of issues.")
    if status in {"healthy", "degraded-derived"} and canonical != "healthy":
        raise ValueError("Healthy/derived diagnosis contradicts canonical state.")

    lines = [
        f"Diagnosis: {status}",
        f"Canonical database: {canonical}",
        f"Issues: {len(issues)}",
    ]
    has_recovery_required = False
    if not issues:
        lines.append("No recovery issues reported.")
    for index, issue in enumerate(issues, start=1):
        if not isinstance(issue, Mapping):
            raise ValueError(f"Recovery issue {index} must be an object.")
        fields = (issue.get("code"), issue.get("layer"), issue.get("severity"), issue.get("action"))
        if not all(isinstance(value, str) and value.strip() for value in fields):
            raise ValueError(f"Recovery issue {index} is missing typed fields.")
        code, layer, severity, action = fields
        if severity not in {"rebuild-required", "recovery-required"}:
            raise ValueError(f"Recovery issue {index} has unsupported severity.")
        count = issue.get("count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"Recovery issue {index} has invalid count.")
        has_recovery_required |= severity == "recovery-required"
        lines.extend([
            "",
            f"{index}. {code} ({severity})",
            f"Layer: {layer} | Affected: {count}",
            f"Suggested action: {action}",
        ])

    if status == "healthy" and issues:
        raise ValueError("Healthy diagnosis cannot contain recovery issues.")
    if status == "degraded-derived" and (not issues or has_recovery_required):
        raise ValueError("Derived degradation requires rebuild-only issues.")
    if status == "recovery-required" and not has_recovery_required:
        raise ValueError("Recovery-required diagnosis needs a recovery issue.")
    return "\n".join(lines)
