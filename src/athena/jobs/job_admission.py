"""Registry-backed admission routing for durable jobs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from athena.jobs.job_type_registry import JobTypeRegistry
from athena.jobs.models import JobPriority, JobRecord


class JobAdmissionError(ValueError):
    """Raised when a durable job type cannot be admitted safely."""


class UnboundPluginJobTypeError(JobAdmissionError):
    """Raised when a registered plugin type has no explicit admission handler."""


class BuiltinJobAdmission(Protocol):
    """Minimal built-in durable-job admission surface."""

    BUILTIN_JOB_TYPES: frozenset[str]

    def create(
        self,
        *,
        job_type: str,
        priority: JobPriority = JobPriority.NORMAL,
        requested_scope: Mapping[str, Any] | None = None,
        pinned_configuration: Mapping[str, Any] | None = None,
        next_run_at_us: int | None = None,
    ) -> JobRecord: ...


class PluginJobAdmissionHandler(Protocol):
    """Plugin-owned validation and persistence boundary for one job type."""

    def create(
        self,
        *,
        job_type: str,
        priority: JobPriority = JobPriority.NORMAL,
        requested_scope: Mapping[str, Any] | None = None,
        pinned_configuration: Mapping[str, Any] | None = None,
        next_run_at_us: int | None = None,
    ) -> JobRecord: ...


class RegistryBackedJobAdmission:
    """Route durable job creation only through registered, explicitly bound types."""

    def __init__(
        self,
        *,
        registry: JobTypeRegistry,
        builtin_service: BuiltinJobAdmission,
    ) -> None:
        self.registry = registry
        self.builtin_service = builtin_service
        self._builtin_job_types = frozenset(builtin_service.BUILTIN_JOB_TYPES)
        missing = sorted(
            job_type
            for job_type in self._builtin_job_types
            if not registry.contains(job_type)
        )
        if missing:
            raise JobAdmissionError(
                "builtin service exposes job types absent from registry: "
                + ", ".join(missing)
            )
        self._plugin_handlers: dict[str, PluginJobAdmissionHandler] = {}

    def bind_plugin_handler(
        self,
        job_type: object,
        handler: PluginJobAdmissionHandler,
    ) -> None:
        """Bind a handler only after the plugin type is permission-registered."""
        if not isinstance(job_type, str) or not self.registry.contains(job_type):
            raise JobAdmissionError("plugin job type is not registered.")
        if job_type in self._builtin_job_types:
            raise JobAdmissionError("builtin job types cannot bind plugin handlers.")
        if job_type in self._plugin_handlers:
            raise JobAdmissionError("plugin job type already has an admission handler.")
        self._plugin_handlers[job_type] = handler

    def create(
        self,
        *,
        job_type: object,
        priority: JobPriority = JobPriority.NORMAL,
        requested_scope: Mapping[str, Any] | None = None,
        pinned_configuration: Mapping[str, Any] | None = None,
        next_run_at_us: int | None = None,
    ) -> JobRecord:
        """Admit one job through its registered built-in or plugin boundary."""
        if not isinstance(job_type, str) or not self.registry.contains(job_type):
            raise JobAdmissionError("job type is not registered.")

        kwargs = {
            "job_type": job_type,
            "priority": priority,
            "requested_scope": requested_scope,
            "pinned_configuration": pinned_configuration,
            "next_run_at_us": next_run_at_us,
        }
        if job_type in self._builtin_job_types:
            return self.builtin_service.create(**kwargs)

        handler = self._plugin_handlers.get(job_type)
        if handler is None:
            raise UnboundPluginJobTypeError(
                f"registered plugin job type {job_type!r} has no admission handler."
            )
        return handler.create(**kwargs)
