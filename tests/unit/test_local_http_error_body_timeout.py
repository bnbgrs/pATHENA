from __future__ import annotations

from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from athena.model.adapters import local_http


def test_http_error_body_inherits_total_timeout() -> None:
    error = HTTPError(
        "http://127.0.0.1:1234/v1/models",
        500,
        "provider error",
        {},
        BytesIO(b"error body"),
    )

    with patch.object(local_http, "monotonic", return_value=100.0):
        local_http._bound_http_error_body(
            error,
            total_timeout_seconds=1.0,
        )

    with patch.object(local_http, "monotonic", return_value=101.0):
        with pytest.raises(
            TimeoutError,
            match="exceeded the configured total timeout",
        ):
            error.fp.read()
