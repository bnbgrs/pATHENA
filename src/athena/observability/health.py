"""Core health model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RECOVERY_REQUIRED = "recovery_required"
    OK = "ok"
    STOPPING = "stopping"
    FAILED = "failed"


def _health_detail(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("ATHENA health detail must be non-empty text.")
    return value


@dataclass(frozen=True, slots=True)
class HealthSnapshot:
    status: HealthStatus
    detail: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, HealthStatus):
            raise ValueError("ATHENA health status must be a HealthStatus value.")
        if self.detail is not None:
            _health_detail(self.detail)


class HealthService:
    """In-memory bootstrap health service."""

    def __init__(self) -> None:
        self._status = HealthStatus.STOPPED
        self._detail: str | None = None

    def mark_starting(self) -> None:
        self._set(HealthStatus.STARTING)

    def mark_ok(self) -> None:
        self._set(HealthStatus.OK)

    def mark_recovery_required(self, detail: str) -> None:
        self._set(HealthStatus.RECOVERY_REQUIRED, _health_detail(detail))

    def mark_stopping(self) -> None:
        self._set(HealthStatus.STOPPING)

    def mark_stopped(self) -> None:
        self._set(HealthStatus.STOPPED)

    def mark_failed(self, detail: str) -> None:
        self._set(HealthStatus.FAILED, _health_detail(detail))

    def snapshot(self) -> HealthSnapshot:
        return HealthSnapshot(status=self._status, detail=self._detail)

    def _set(self, status: HealthStatus, detail: str | None = None) -> None:
        if not isinstance(status, HealthStatus):
            raise ValueError("ATHENA health status must be a HealthStatus value.")
        if detail is not None:
            _health_detail(detail)
        self._status = status
        self._detail = detail
