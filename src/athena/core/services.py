"""Service lifecycle primitives for the ATHENA Core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from athena.core.errors import ShutdownError, StartupError


@runtime_checkable
class LifecycleService(Protocol):
    """Minimal contract for a service managed by the ATHENA Core."""

    @property
    def name(self) -> str:
        """Stable diagnostic name for the service."""
        ...

    def start(self) -> None:
        """Start the service."""
        ...

    def stop(self) -> None:
        """Stop the service."""
        ...


def _canonical_service_name(service: LifecycleService) -> str:
    name = service.name
    if not isinstance(name, str):
        raise TypeError("Lifecycle service name must be text.")
    normalized = name.strip()
    if not normalized:
        raise ValueError("Lifecycle service name must not be empty.")
    if normalized != name:
        raise ValueError("Lifecycle service name must use canonical trimmed text.")
    return normalized


@dataclass(frozen=True, slots=True)
class ServiceFailure:
    """A service plus the exception raised by a lifecycle operation."""

    service_name: str
    error: Exception

    def __post_init__(self) -> None:
        if not isinstance(self.service_name, str) or not self.service_name.strip():
            raise ValueError("ServiceFailure service_name must be non-empty text.")
        if self.service_name != self.service_name.strip():
            raise ValueError("ServiceFailure service_name must be canonical trimmed text.")
        if not isinstance(self.error, Exception):
            raise TypeError("ServiceFailure error must be an Exception.")


class ServiceManager:
    """Starts services in order and stops them in reverse order.

    Startup is transactional at the service-lifecycle level: if service N
    fails, every service successfully started before it is stopped again.
    """

    def __init__(self, services: tuple[LifecycleService, ...] = ()) -> None:
        if not isinstance(services, tuple):
            raise TypeError("services must be a tuple of LifecycleService values.")
        names: list[str] = []
        for service in services:
            if not isinstance(service, LifecycleService):
                raise TypeError("services must contain LifecycleService values only.")
            names.append(_canonical_service_name(service))
        if len(set(names)) != len(names):
            raise ValueError("Lifecycle service names must be unique.")
        self._services = services
        self._service_names = tuple(names)
        self._started: list[tuple[LifecycleService, str]] = []

    @property
    def started_service_names(self) -> tuple[str, ...]:
        return tuple(name for _service, name in self._started)

    def start_all(self) -> None:
        if self._started:
            return

        for service, service_name in zip(self._services, self._service_names, strict=True):
            try:
                service.start()
            except Exception as exc:
                rollback_failures = self._stop_started_best_effort()
                suffix = ""
                if rollback_failures:
                    failed_names = ", ".join(
                        failure.service_name for failure in rollback_failures
                    )
                    suffix = f" Rollback also failed for: {failed_names}."
                raise StartupError(
                    f"Failed to start service {service_name!r}.{suffix}"
                ) from exc
            self._started.append((service, service_name))

    def stop_all(self) -> None:
        failures = self._stop_started_best_effort()
        if failures:
            failed_names = ", ".join(
                failure.service_name for failure in failures
            )
            raise ShutdownError(
                f"Failed to stop one or more services: {failed_names}."
            )

    def _stop_started_best_effort(self) -> tuple[ServiceFailure, ...]:
        failures: list[ServiceFailure] = []

        while self._started:
            service, service_name = self._started.pop()
            try:
                service.stop()
            except Exception as exc:
                failures.append(
                    ServiceFailure(service_name=service_name, error=exc)
                )

        return tuple(failures)
