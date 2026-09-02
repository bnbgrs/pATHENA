"""Fail-closed durable-job execution capability classification."""

from __future__ import annotations

# Only jobs proven not to call the local model/provider belong here.
# Any new/unknown job type remains provider-isolated until explicitly reviewed.
CONTROL_LANE_JOB_TYPES = frozenset(
    {
        "source.process",
        "backup.create",
        "archive.replicate",
    }
)


def requires_provider_isolation(job_type: object) -> bool:
    """Return True unless a durable job is explicitly classified control-safe."""
    if not isinstance(job_type, str) or not job_type or job_type != job_type.strip():
        return True
    return job_type not in CONTROL_LANE_JOB_TYPES
