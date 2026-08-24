"""Proxy-free HTTP transport for loopback-only local model adapters."""

from __future__ import annotations

from typing import Any
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


class _RejectRedirects(HTTPRedirectHandler):
    """Prevent a local-only provider request from escaping through a redirect."""

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        del req, fp, code, msg, headers, newurl
        return None


def open_local_request(request: Request, *, timeout: float) -> Any:
    """Open a local-provider request without proxies or redirect traversal.

    ATHENA's local model providers are restricted to loopback endpoints by
    configuration. Explicitly installing an empty ``ProxyHandler`` keeps those
    requests local even when HTTP_PROXY, HTTPS_PROXY, ALL_PROXY or platform
    proxy settings are present in the process environment. Redirects are also
    rejected so a loopback service cannot move a request onto an external URL.
    """
    opener = build_opener(ProxyHandler({}), _RejectRedirects())
    return opener.open(request, timeout=timeout)
