"""Storage-health extension for the local authenticated desktop API client."""

from __future__ import annotations

from athena.api.client import (
    CoreApiClient,
    CoreApiClientError,
    _optional_int,
    _optional_str,
    _required_bool,
    _required_int,
    _required_str,
)
from athena.api.contracts import StorageHealthResponse


class StorageAwareCoreApiClient(CoreApiClient):
    """Core API client with the read-only storage-health endpoint exposed."""

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
        if response.status not in {"available", "unavailable", "error"}:
            raise CoreApiClientError(
                "ATHENA Core returned an invalid storage-health status.",
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
        if response.observed_at_us < 0:
            raise CoreApiClientError(
                "ATHENA Core returned an invalid storage observation time.",
                code="invalid_response",
            )
        return response
