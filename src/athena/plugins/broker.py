"""Core-side capability broker contract for a future out-of-process plugin host.

The broker consumes already validated IPC requests and delegates authorization to the
existing manifest+grant boundary. It executes no plugin code and performs no external
operation itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from athena.plugins.capabilities import PluginCapabilityBoundary
from athena.plugins.protocol import PluginCapabilityRequest


@dataclass(frozen=True, slots=True)
class PluginBrokerDecision:
    """Payload-free broker response suitable for a future IPC response encoder."""

    request_id: str
    plugin_id: str
    allowed: bool
    reason_code: str


class PluginCapabilityBroker:
    """Authorize validated plugin capability requests, deny by default."""

    def __init__(self, *, boundary: PluginCapabilityBoundary) -> None:
        if not isinstance(boundary, PluginCapabilityBoundary):
            raise TypeError("Plugin capability broker requires PluginCapabilityBoundary.")
        self._boundary = boundary

    def authorize(self, request: PluginCapabilityRequest) -> PluginBrokerDecision:
        if not isinstance(request, PluginCapabilityRequest):
            raise TypeError("Plugin capability broker requires a validated request.")
        decision = self._boundary.evaluate(
            request.capability,
            scope=request.scope,
        )
        return PluginBrokerDecision(
            request_id=request.request_id,
            plugin_id=decision.plugin_id,
            allowed=decision.allowed,
            reason_code=decision.reason_code,
        )
