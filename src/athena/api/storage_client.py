"""Storage-health extension for the local authenticated desktop API client."""

from __future__ import annotations

from typing import Self, cast

from athena.api.client import CoreApiClient, CoreApiClientError
from athena.api.contracts import JsonValue, StorageHealthResponse


class StorageAwareCoreApiClient(CoreApiClient):
    """Core API client with the read-only storage-health endpoint exposed."""

    @classmethod
    def from_environment(
        cls,
        *,
        timeout_seconds: float = 5.0,
    ) -> Self:
        """Preserve the concrete storage-aware client type at desktop bootstrap."""
        return cast(
            Self,
            super().from_environment(timeout_seconds=timeout_seconds),
        )

    def storage_health(self) -> StorageHealthResponse:
        payload = self._get("/api/v1/storage/health")
        response = StorageHealthResponse(
            api_version=_required_str(payload, "api_version"),
            status=_required_str(payload, "status"),
            database_open=_required_bool(payload, "database_open"),
            database_path=_optional_str(payload, "database_path"),
            database_size_bytes=_optional_int(payload, "database_size_bytes"),
            wal_size_bytes=_optional_int(payload, "wal_size_bytes"),
            observed_at_us=_required_int(payload, "observed_at_us"),
            detail=_optional_str(payload, "detail"),
        )
        _validate_storage_health(response)
        return response


def _required_str(payload: dict[str, JsonValue], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str):
        raise _invalid_field(key)
    return value


def _optional_str(payload: dict[str, JsonValue], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise _invalid_field(key)
    return value


def _required_int(payload: dict[str, JsonValue], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise _invalid_field(key)
    return value


def _optional_int(payload: dict[str, JsonValue], key: str) -> int | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise _invalid_field(key)
    return value


def _required_bool(payload: dict[str, JsonValue], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise _invalid_field(key)
    return value


def _invalid_field(key: str) -> CoreApiClientError:
    return CoreApiClientError(
        f"ATHENA Core response field {key!r} is invalid.",
        code="invalid_response",
    )


def _validate_storage_health(response: StorageHealthResponse) -> None:
    if response.status not in {"available", "unavailable", "error"}:
        raise CoreApiClientError(
            "ATHENA Core returned an invalid storage-health status.",
            code="invalid_response",
        )
    if response.observed_at_us <= 0:
        raise CoreApiClientError(
            "ATHENA Core returned an invalid storage observation time.",
            code="invalid_response",
        )
    if response.database_size_bytes is not None and response.database_size_bytes < 0:
        raise CoreApiClientError(
            "ATHENA Core returned an invalid database size.",
            code="invalid_response",
        )
    if response.wal_size_bytes is not None and response.wal_size_bytes < 0:
        raise CoreApiClientError(
            "ATHENA Core returned an invalid WAL size.",
            code="invalid_response",
        )
    if response.status == "available" and not response.database_open:
        raise CoreApiClientError(
            "ATHENA Core returned available storage without an open database.",
            code="invalid_response",
        )
    if response.status == "unavailable" and response.database_open:
        raise CoreApiClientError(
            "ATHENA Core returned unavailable storage for an open database.",
            code="invalid_response",
        )
    if response.status == "error" and not response.database_open:
        raise CoreApiClientError(
            "ATHENA Core returned a storage probe error without a live database.",
            code="invalid_response",
        )
    measured_sizes = (
        response.database_size_bytes,
        response.wal_size_bytes,
    )
    if response.status == "available" and any(value is None for value in measured_sizes):
        raise CoreApiClientError(
            "ATHENA Core returned incomplete available storage measurements.",
            code="invalid_response",
        )
    if response.status != "available" and any(value is not None for value in measured_sizes):
        raise CoreApiClientError(
            "ATHENA Core returned measured storage sizes for a non-available state.",
            code="invalid_response",
        )
