"""Deny-by-default capability contracts for future plugin hosts.

This module defines the official Core-side policy boundary only. It does not load or
execute plugin code and must not be described as an OS sandbox.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from athena.plugins.manifest import PluginManifest


class PluginPermission(StrEnum):
    """Coarse permissions a plugin must disclose before activation."""

    READ_SOURCES = "sources.read"
    PROPOSE_IMPORT = "imports.propose"
    REQUEST_SEARCH = "search.request"
    REQUEST_NETWORK = "network.request"
    READ_PROJECTS = "projects.read"
    WRITE_PROJECTION = "projection.write"
    REGISTER_UI = "ui.register"
    SCHEDULE_JOBS = "jobs.schedule"
    REQUEST_SECRET_HANDLE = "secrets.handle"


class PluginCapability(StrEnum):
    """Fine-grained official capabilities exposed by the v1 Core boundary."""

    READ_SELECTED_SOURCES = "read_selected_sources"
    CREATE_IMPORT_CANDIDATE = "create_import_candidate"
    REQUEST_SEARCH = "request_search"
    REQUEST_EXTERNAL_ACCESS = "request_external_access"
    READ_PROJECT_SCOPE = "read_project_scope"
    WRITE_PROJECTION = "write_projection"
    REGISTER_UI_PANEL = "register_ui_panel"
    SCHEDULE_JOB = "schedule_job"
    REQUEST_SECRET_HANDLE = "request_secret_handle"


_CAPABILITY_PERMISSION: dict[PluginCapability, PluginPermission] = {
    PluginCapability.READ_SELECTED_SOURCES: PluginPermission.READ_SOURCES,
    PluginCapability.CREATE_IMPORT_CANDIDATE: PluginPermission.PROPOSE_IMPORT,
    PluginCapability.REQUEST_SEARCH: PluginPermission.REQUEST_SEARCH,
    PluginCapability.REQUEST_EXTERNAL_ACCESS: PluginPermission.REQUEST_NETWORK,
    PluginCapability.READ_PROJECT_SCOPE: PluginPermission.READ_PROJECTS,
    PluginCapability.WRITE_PROJECTION: PluginPermission.WRITE_PROJECTION,
    PluginCapability.REGISTER_UI_PANEL: PluginPermission.REGISTER_UI,
    PluginCapability.SCHEDULE_JOB: PluginPermission.SCHEDULE_JOBS,
    PluginCapability.REQUEST_SECRET_HANDLE: PluginPermission.REQUEST_SECRET_HANDLE,
}


def required_permission(capability: PluginCapability) -> PluginPermission:
    """Return the coarse manifest permission required for one capability."""

    if not isinstance(capability, PluginCapability):
        raise TypeError("Plugin capability must be a PluginCapability value.")
    return _CAPABILITY_PERMISSION[capability]


class PluginCapabilityDenied(PermissionError):
    """Raised when an official plugin capability request is denied."""

    def __init__(
        self,
        *,
        plugin_id: str,
        capability: PluginCapability,
        reason_code: str,
        scope: str | None,
    ) -> None:
        self.plugin_id = plugin_id
        self.capability = capability
        self.reason_code = reason_code
        self.scope = scope
        suffix = "" if scope is None else f" scope={scope!r}"
        super().__init__(
            f"Plugin {plugin_id!r} is denied capability {capability.value!r}: "
            f"{reason_code}{suffix}"
        )


@dataclass(frozen=True, slots=True)
class PluginCapabilityGrant:
    """One explicit runtime grant for one plugin capability.

    ``scopes=None`` is an intentionally unscoped grant. A non-empty scope set limits
    the grant to exact opaque Core-issued scope identifiers. Wildcard syntax is not
    interpreted by this boundary.
    """

    plugin_id: str
    capability: PluginCapability
    scopes: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.plugin_id, str) or not self.plugin_id.strip():
            raise ValueError("Plugin capability grant requires a non-empty plugin_id.")
        if not isinstance(self.capability, PluginCapability):
            raise TypeError("Plugin capability grant capability is invalid.")
        if self.scopes is None:
            return
        if not isinstance(self.scopes, frozenset) or not self.scopes:
            raise ValueError(
                "Scoped plugin capability grants require a non-empty frozenset."
            )
        for scope in self.scopes:
            if not isinstance(scope, str) or not scope.strip():
                raise ValueError("Plugin capability grant scopes must be non-empty strings.")
            if scope == "*":
                raise ValueError("Plugin capability grants do not interpret wildcard scopes.")


@dataclass(frozen=True, slots=True)
class PluginCapabilityDecision:
    """Payload-free authorization result for an official plugin capability request."""

    plugin_id: str
    capability: PluginCapability
    allowed: bool
    reason_code: str
    scope: str | None


class PluginCapabilityBoundary:
    """Evaluate manifest disclosure plus explicit runtime grants, deny by default."""

    def __init__(
        self,
        *,
        manifest: PluginManifest,
        grants: tuple[PluginCapabilityGrant, ...] = (),
    ) -> None:
        from athena.plugins.manifest import PluginManifest

        if not isinstance(manifest, PluginManifest):
            raise TypeError("Plugin capability boundary requires a PluginManifest.")
        self.manifest = manifest

        by_capability: dict[PluginCapability, list[PluginCapabilityGrant]] = {}
        for grant in grants:
            if not isinstance(grant, PluginCapabilityGrant):
                raise TypeError("Plugin capability boundary grants are invalid.")
            if grant.plugin_id != manifest.plugin_id:
                raise ValueError(
                    "Plugin capability grant belongs to a different plugin_id."
                )
            by_capability.setdefault(grant.capability, []).append(grant)
        self._grants = {
            capability: tuple(items)
            for capability, items in by_capability.items()
        }

    def evaluate(
        self,
        capability: PluginCapability,
        *,
        scope: str | None = None,
    ) -> PluginCapabilityDecision:
        if not isinstance(capability, PluginCapability):
            raise TypeError("Plugin capability request must use PluginCapability.")
        if scope is not None and (not isinstance(scope, str) or not scope.strip()):
            raise ValueError("Plugin capability request scope must be non-empty or None.")

        plugin_id = self.manifest.plugin_id
        if capability not in self.manifest.capabilities:
            return PluginCapabilityDecision(
                plugin_id=plugin_id,
                capability=capability,
                allowed=False,
                reason_code="capability_not_declared",
                scope=scope,
            )

        permission = required_permission(capability)
        if permission not in self.manifest.permissions:
            return PluginCapabilityDecision(
                plugin_id=plugin_id,
                capability=capability,
                allowed=False,
                reason_code="permission_not_declared",
                scope=scope,
            )

        grants = self._grants.get(capability, ())
        if not grants:
            return PluginCapabilityDecision(
                plugin_id=plugin_id,
                capability=capability,
                allowed=False,
                reason_code="capability_not_granted",
                scope=scope,
            )

        for grant in grants:
            if grant.scopes is None:
                return PluginCapabilityDecision(
                    plugin_id=plugin_id,
                    capability=capability,
                    allowed=True,
                    reason_code="allowed",
                    scope=scope,
                )
            if scope is not None and scope in grant.scopes:
                return PluginCapabilityDecision(
                    plugin_id=plugin_id,
                    capability=capability,
                    allowed=True,
                    reason_code="allowed",
                    scope=scope,
                )

        return PluginCapabilityDecision(
            plugin_id=plugin_id,
            capability=capability,
            allowed=False,
            reason_code="scope_not_granted",
            scope=scope,
        )

    def require(
        self,
        capability: PluginCapability,
        *,
        scope: str | None = None,
    ) -> PluginCapabilityDecision:
        decision = self.evaluate(capability, scope=scope)
        if not decision.allowed:
            raise PluginCapabilityDenied(
                plugin_id=decision.plugin_id,
                capability=decision.capability,
                reason_code=decision.reason_code,
                scope=decision.scope,
            )
        return decision
