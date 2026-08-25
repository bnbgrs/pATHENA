"""Versioned capability metadata resolved against real desktop commands and surfaces.

The command palette remains the executable source of truth. This catalogue adds
versioned human-facing metadata only for commands that are actually registered by
that palette, then resolves availability from the same live target widgets. A
catalogue drift is explicit and never turns a missing action into a capability claim.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, Protocol

from PySide6.QtWidgets import QListWidget, QWidget

CAPABILITY_SCHEMA_VERSION: Final = 1
CAPABILITY_CATALOG_VERSION: Final = "2026.08.25.1"


class CommandLike(Protocol):
    @property
    def label(self) -> str: ...


class CapabilityAvailability(StrEnum):
    AVAILABLE = "available"
    CONTEXT_REQUIRED = "context required"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class CapabilityMetadata:
    label: str
    area: str
    summary: str
    workspace_row: int | None = None
    target_attribute: str | None = None
    target_object_name: str | None = None

    def __post_init__(self) -> None:
        if not self.label.strip() or not self.area.strip() or not self.summary.strip():
            raise ValueError("Capability metadata text must not be empty.")
        target_count = sum(
            value is not None
            for value in (
                self.workspace_row,
                self.target_attribute,
                self.target_object_name,
            )
        )
        if target_count > 1:
            raise ValueError("A capability must use at most one availability target.")


@dataclass(frozen=True, slots=True)
class ResolvedCapability:
    label: str
    area: str
    summary: str
    availability: CapabilityAvailability
    explanation: str
    documented: bool


@dataclass(frozen=True, slots=True)
class CapabilityCatalogSnapshot:
    version: str
    capabilities: tuple[ResolvedCapability, ...]
    undocumented_live_commands: tuple[str, ...]
    stale_metadata: tuple[str, ...]

    @property
    def has_drift(self) -> bool:
        return bool(self.undocumented_live_commands or self.stale_metadata)


_CAPABILITIES: Final = (
    CapabilityMetadata(
        "Open Chat",
        "Workspaces",
        "Persistent local conversations and the existing grounded/direct chat controls.",
        workspace_row=0,
    ),
    CapabilityMetadata(
        "Open Knowledge",
        "Workspaces",
        "Canonical Knowledge, Claims, decisions and their persisted provenance.",
        workspace_row=1,
    ),
    CapabilityMetadata(
        "Open Research",
        "Workspaces",
        "Durable research jobs, results and explicit review paths.",
        workspace_row=2,
    ),
    CapabilityMetadata(
        "Open Jobs",
        "Workspaces",
        "Persistent background work and its supported lifecycle controls.",
        workspace_row=3,
    ),
    CapabilityMetadata(
        "Open Files",
        "Workspaces",
        "Captured local sources, processing readiness and real import paths.",
        workspace_row=4,
    ),
    CapabilityMetadata(
        "Open System",
        "Workspaces",
        "Local Core/provider state and verified backup/recovery surfaces.",
        workspace_row=5,
    ),
    CapabilityMetadata(
        "Open Settings",
        "Workspaces",
        "Existing local model context, output, temperature and reasoning controls.",
        workspace_row=6,
    ),
    CapabilityMetadata(
        "New conversation",
        "Chat",
        "Invoke the existing new-conversation control.",
        target_attribute="new_chat_button",
    ),
    CapabilityMetadata(
        "Focus message field",
        "Chat",
        "Move keyboard focus to the existing message composer without sending.",
        target_attribute="prompt_input",
    ),
    CapabilityMetadata(
        "Use sources for next response",
        "Chat",
        "Toggle the existing evidence-grounding control for the next response.",
        target_attribute="ground_button",
    ),
    CapabilityMetadata(
        "Browse canonical Knowledge",
        "Knowledge",
        "Open the installed canonical Knowledge browser.",
        target_object_name="canonicalMemoryTabs",
    ),
    CapabilityMetadata(
        "Browse canonical Claims",
        "Knowledge",
        "Open the installed canonical Claim browser.",
        target_object_name="canonicalMemoryTabs",
    ),
    CapabilityMetadata(
        "Review contradiction decisions",
        "Knowledge",
        "Open persisted contradiction decisions; no decision is applied automatically.",
        target_object_name="semanticDecisionMode",
    ),
    CapabilityMetadata(
        "Review canonical merge candidates",
        "Knowledge",
        "Open persisted near-duplicate decisions for explicit review.",
        target_object_name="semanticDecisionMode",
    ),
    CapabilityMetadata(
        "Browse selected Claim relations",
        "Knowledge",
        "Focus the installed relation list for the selected persisted Claim.",
        target_object_name="claimRelationList",
    ),
    CapabilityMetadata(
        "Open current knowledge review",
        "Knowledge",
        "Open the existing session proposal review before canonical acceptance.",
        target_object_name="canonicalMemoryTabs",
    ),
    CapabilityMetadata(
        "Filter canonical memory",
        "Knowledge",
        "Focus the installed canonical-memory filter.",
        target_object_name="knowledgeSearchInput",
    ),
    CapabilityMetadata(
        "Open Research result & promotion",
        "Research",
        "Open immutable ResearchResult proposals for explicit accept/reject decisions.",
        target_object_name="researchProposalList",
    ),
    CapabilityMetadata(
        "Open Backup & Recovery",
        "System",
        "Open the existing verified backup and isolated-restore surface.",
        target_object_name="systemOperationsTabs",
    ),
    CapabilityMetadata(
        "Open model settings",
        "Settings",
        "Navigate to the existing local model controls.",
        workspace_row=6,
    ),
    CapabilityMetadata(
        "Open help",
        "Help",
        "Open this read-only capability view.",
    ),
)

CAPABILITY_METADATA: Final = {item.label: item for item in _CAPABILITIES}
EXTENSION_CAPABILITY_METADATA: Final = {
    "Open ComfyUI": CapabilityMetadata(
        "Open ComfyUI",
        "ComfyUI",
        "Open the local-only ComfyUI bridge for endpoint checks and explicit API-workflow queueing.",
        target_object_name="comfyUiDialog",
    )
}


def _property_text(widget: QWidget, name: str) -> str:
    value = widget.property(name)
    return " ".join(str(value).split()) if value else ""


def _widget_availability(widget: QWidget) -> tuple[CapabilityAvailability, str]:
    if widget.isEnabled():
        return CapabilityAvailability.AVAILABLE, "Available in this desktop."
    reason = _property_text(widget, "pathenaEnablementReason")
    restore = _property_text(widget, "pathenaEnablementRestoreCondition")
    explanation = " ".join(part for part in (reason, restore) if part)
    return (
        CapabilityAvailability.CONTEXT_REQUIRED,
        explanation or "The existing target control is currently disabled.",
    )


def _resolve_metadata(
    window: QWidget,
    metadata: CapabilityMetadata,
) -> tuple[CapabilityAvailability, str]:
    if metadata.workspace_row is not None:
        navigation = getattr(window, "navigation", None)
        pages = getattr(window, "pages", None)
        if not isinstance(navigation, QListWidget) or not isinstance(pages, QWidget):
            return (
                CapabilityAvailability.UNAVAILABLE,
                "The workspace navigation surface is not installed.",
            )
        row = metadata.workspace_row
        page_count = pages.count() if hasattr(pages, "count") else 0
        if row >= navigation.count() or row >= page_count:
            return (
                CapabilityAvailability.UNAVAILABLE,
                "The referenced workspace is not installed in this desktop.",
            )
        return CapabilityAvailability.AVAILABLE, "Available in this desktop."

    if metadata.target_attribute is not None:
        target = getattr(window, metadata.target_attribute, None)
        if not isinstance(target, QWidget):
            return (
                CapabilityAvailability.UNAVAILABLE,
                "The executable target control is not installed.",
            )
        return _widget_availability(target)

    if metadata.target_object_name is not None:
        target = window.findChild(QWidget, metadata.target_object_name)
        if target is None:
            return (
                CapabilityAvailability.UNAVAILABLE,
                "The executable target surface is not installed.",
            )
        return _widget_availability(target)

    return CapabilityAvailability.AVAILABLE, "Available in this desktop."


def resolve_capability_catalog(
    window: QWidget,
    commands: Iterable[CommandLike],
) -> CapabilityCatalogSnapshot:
    """Resolve only live commands and report metadata drift explicitly."""
    live_commands = tuple(commands)
    live_labels = tuple(command.label for command in live_commands)
    if len(live_labels) != len(set(live_labels)):
        raise ValueError("Live command labels must be unique.")

    resolved: list[ResolvedCapability] = []
    undocumented: list[str] = []
    for label in live_labels:
        metadata = CAPABILITY_METADATA.get(label) or EXTENSION_CAPABILITY_METADATA.get(label)
        if metadata is None:
            undocumented.append(label)
            resolved.append(
                ResolvedCapability(
                    label=label,
                    area="Other",
                    summary="Live command registered by the current desktop.",
                    availability=CapabilityAvailability.UNAVAILABLE,
                    explanation=(
                        "Availability is not verified because catalogue metadata is missing."
                    ),
                    documented=False,
                )
            )
            continue
        availability, explanation = _resolve_metadata(window, metadata)
        resolved.append(
            ResolvedCapability(
                label=metadata.label,
                area=metadata.area,
                summary=metadata.summary,
                availability=availability,
                explanation=explanation,
                documented=True,
            )
        )

    live_label_set = set(live_labels)
    stale = tuple(label for label in CAPABILITY_METADATA if label not in live_label_set)
    return CapabilityCatalogSnapshot(
        version=CAPABILITY_CATALOG_VERSION,
        capabilities=tuple(resolved),
        undocumented_live_commands=tuple(undocumented),
        stale_metadata=stale,
    )
