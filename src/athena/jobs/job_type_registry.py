"""Controlled durable job-type registry."""

from __future__ import annotations

from collections.abc import Iterable


class JobTypeRegistry:
    """Track approved durable job types and guarded plugin registrations."""

    def __init__(self, builtin_job_types: Iterable[str] = ()) -> None:
        self._builtin_job_types: set[str] = set()
        self._plugin_job_types: set[str] = set()
        for job_type in builtin_job_types:
            normalized = self._validate_job_type(job_type)
            if normalized in self._builtin_job_types:
                raise ValueError(f"duplicate builtin job type: {normalized}")
            self._builtin_job_types.add(normalized)

    @staticmethod
    def _validate_job_type(job_type: object) -> str:
        if not isinstance(job_type, str):
            raise TypeError("job_type must be a string.")
        if not job_type or job_type != job_type.strip():
            raise ValueError("job_type must be non-empty and trimmed.")
        if any(character.isspace() for character in job_type):
            raise ValueError("job_type must not contain whitespace.")
        return job_type

    @staticmethod
    def _require_plugin_namespace(job_type: str) -> None:
        namespace, separator, local_name = job_type.partition(".")
        if not separator or not namespace or not local_name:
            raise ValueError("plugin job types must be namespaced.")

    def register_plugin(self, job_type: object, *, permission_granted: bool) -> str:
        """Register one namespaced plugin job type when permission is explicit."""
        if permission_granted is not True:
            raise PermissionError("plugin job type registration requires permission.")
        normalized = self._validate_job_type(job_type)
        self._require_plugin_namespace(normalized)
        if normalized in self._builtin_job_types or normalized in self._plugin_job_types:
            raise ValueError(f"job type is already registered: {normalized}")
        self._plugin_job_types.add(normalized)
        return normalized

    def contains(self, job_type: object) -> bool:
        """Return whether the exact validated job type is registered."""
        try:
            normalized = self._validate_job_type(job_type)
        except (TypeError, ValueError):
            return False
        return normalized in self._builtin_job_types or normalized in self._plugin_job_types

    @property
    def job_types(self) -> tuple[str, ...]:
        """Return a deterministic snapshot of all registered job types."""
        return tuple(sorted(self._builtin_job_types | self._plugin_job_types))
