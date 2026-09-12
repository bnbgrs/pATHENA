"""Fail-closed release-readiness assessment for exact pATHENA build evidence."""

from __future__ import annotations

from dataclasses import dataclass

_REQUIRED_GUARDS = (
    "canonical_quality",
    "windows_runtime",
    "packaging",
    "frozen_argv",
    "two_exe_topology",
    "single_desktop_bounded_workers",
    "adaptive_2048_context_reserve",
    "windows_lane_lock",
    "storage_regressions",
)


@dataclass(frozen=True, slots=True)
class ReleaseReadinessEvidence:
    """Exact-SHA evidence for the release guards required before promotion."""

    exact_sha: str
    canonical_quality: bool | None
    windows_runtime: bool | None
    packaging: bool | None
    frozen_argv: bool | None
    two_exe_topology: bool | None
    single_desktop_bounded_workers: bool | None
    adaptive_2048_context_reserve: bool | None
    windows_lane_lock: bool | None
    storage_regressions: bool | None


@dataclass(frozen=True, slots=True)
class ReleaseReadiness:
    """Deterministic promotion decision and the guards that still block it."""

    exact_sha: str
    ready: bool
    blockers: tuple[str, ...]


def assess_release_readiness(evidence: ReleaseReadinessEvidence) -> ReleaseReadiness:
    """Return READY only when every required guard is explicitly green."""
    if not isinstance(evidence, ReleaseReadinessEvidence):
        raise TypeError("evidence must be ReleaseReadinessEvidence.")
    _validate_exact_sha(evidence.exact_sha)

    blockers = tuple(
        guard for guard in _REQUIRED_GUARDS if getattr(evidence, guard) is not True
    )
    return ReleaseReadiness(
        exact_sha=evidence.exact_sha,
        ready=not blockers,
        blockers=blockers,
    )


def _validate_exact_sha(value: object) -> None:
    if not isinstance(value, str):
        raise TypeError("exact_sha must be a 40-character hexadecimal Git SHA.")
    if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
        raise ValueError("exact_sha must be a lowercase 40-character hexadecimal Git SHA.")
