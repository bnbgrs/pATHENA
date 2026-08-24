"""Proxy-free HTTP transport for loopback-only local model adapters."""

from __future__ import annotations

from typing import Any
from urllib.request import ProxyHandler, Request, build_opener


def open_local_request(request: Request, *, timeout: float) -> Any:
    """Open a local-provider request without consulting ambient proxy settings.

    ATHENA's local model providers are restricted to loopback endpoints by
    configuration. Explicitly installing an empty ``ProxyHandler`` keeps those
    requests local even when HTTP_PROXY, HTTPS_PROXY, ALL_PROXY or platform
    proxy settings are present in the process environment.
    """
    opener = build_opener(ProxyHandler({}))
    return opener.open(request, timeout=timeout)
