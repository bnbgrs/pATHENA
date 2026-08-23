"""Compose dynamic UI guidance without cross-layer suffix loss.

Readiness, enablement, mutation-boundary, cancellation and accessibility controllers
own different facts about the same widgets. This presentation-only pass composes those
facts from their existing properties so one later state update cannot erase guidance
owned by another layer. Tooltips stay deliberately brief; assistive descriptions keep
all distinct relevant facts. No control state or domain behavior is changed.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDynamicPropertyChangeEvent, QEvent, QObject, QTimer
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class GuidanceTarget:
    workspace_name: str | None
    attribute_name: str
    label: str


_TARGETS: tuple[GuidanceTarget, ...] = (
    GuidanceTarget(None, "prompt_input", "Chat composer"),
    GuidanceTarget(None, "ground_button", "Grounding"),
    GuidanceTarget(None, "send_button", "Send"),
    GuidanceTarget(None, "model_selector", "Model selector"),
    GuidanceTarget(None, "chat_selector", "Conversation selector"),
    GuidanceTarget(None, "delete_chat_button", "Delete conversation"),
    GuidanceTarget(None, "new_chat_button", "New conversation"),
    GuidanceTarget(None, "status_text", "Local readiness status"),
    GuidanceTarget(None, "connection_detail", "Connection detail"),
    GuidanceTarget(None, "settings_model_value", "Settings model state"),
    GuidanceTarget("researchWorkspace", "status", "Research status"),
    GuidanceTarget("researchWorkspace", "jobs", "Research jobs"),
    GuidanceTarget("researchWorkspace", "details", "Research details"),
    GuidanceTarget("researchWorkspace", "cancel_button", "Research cancel"),
    GuidanceTarget("jobsWorkspace", "status", "Jobs status"),
    GuidanceTarget("jobsWorkspace", "jobs", "Durable jobs"),
    GuidanceTarget("jobsWorkspace", "details", "Job details"),
    GuidanceTarget("jobsWorkspace", "cancel_button", "Job cancel"),
    GuidanceTarget("filesWorkspace", "process_button", "Process Source"),
    GuidanceTarget("backupWorkspace", "restore_button", "Restore isolated"),
)

_DIMENSIONS: tuple[str, ...] = (
    "stable guidance base",
    "cross-layer guidance composition",
    "bounded tooltip guidance",
    "complete assistive guidance",
    "dynamic guidance recomposition",
)

UI_REFINEMENT_TASKS_6001_6100: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)

_TRACKED_PROPERTIES = frozenset(
    {
        b"pathenaAccessibleUiState",
        b"pathenaAccessibleSelectionIdentity",
        b"pathenaEnablementReason",
        b"pathenaEnablementRestoreCondition",
        b"pathenaBoundaryExplanation",
        b"pathenaCancellationPhase",
        b"pathenaCancellationSelectedState",
        b"pathenaComposerBlockingReason",
        b"pathenaComposerRecoveryCondition",
    }
)
_GUIDANCE_MARKERS = (
    "Availability:",
    "Interaction boundary:",
    "Cancellation:",
    "Readiness:",
)


class GuidanceCompositionController(QObject):
    """Recompose guidance from semantic properties after any owner updates."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._labels: dict[QWidget, str] = {}
        self._accessible_base: dict[QWidget, str] = {}
        self._tooltip_base: dict[QWidget, str] = {}
        self._pending: set[QWidget] = set()

    def register(self, widget: QWidget, label: str) -> None:
        self._labels[widget] = label
        self._accessible_base[widget] = self._strip_dynamic_guidance(
            widget.accessibleDescription()
        )
        self._tooltip_base[widget] = self._strip_dynamic_guidance(widget.toolTip())
        widget.installEventFilter(self)
        widget.setProperty("pathenaGuidanceCompositionManaged", True)
        self._compose(widget, refresh_base=False)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            isinstance(watched, QWidget)
            and watched in self._labels
            and isinstance(event, QDynamicPropertyChangeEvent)
            and bytes(event.propertyName().data()) in _TRACKED_PROPERTIES
        ):
            self._schedule(watched)
        return super().eventFilter(watched, event)

    def _schedule(self, widget: QWidget) -> None:
        if widget in self._pending:
            return
        self._pending.add(widget)
        QTimer.singleShot(0, lambda target=widget: self._run_scheduled(target))

    def _run_scheduled(self, widget: QWidget) -> None:
        self._pending.discard(widget)
        if widget not in self._labels:
            return
        self._compose(widget, refresh_base=True)

    def _compose(self, widget: QWidget, *, refresh_base: bool) -> None:
        if refresh_base:
            accessible_base = self._strip_dynamic_guidance(widget.accessibleDescription())
            tooltip_base = self._strip_dynamic_guidance(widget.toolTip())
            if accessible_base:
                self._accessible_base[widget] = accessible_base
            if tooltip_base:
                self._tooltip_base[widget] = tooltip_base

        overlays = self._overlays(widget)
        accessible_parts = [self._accessible_base.get(widget, "")]
        accessible_parts.extend(text for _name, text in overlays)
        accessible = self._deduplicated_join(accessible_parts, separator=" ")
        widget.setAccessibleDescription(accessible)

        tooltip_parts = [self._tooltip_base.get(widget, "")]
        tooltip_parts.extend(f"{name}: {text}" for name, text in overlays[:2])
        tooltip = self._deduplicated_join(tooltip_parts, separator="\n")
        widget.setToolTip(tooltip)

        widget.setProperty("pathenaGuidanceOverlayCount", len(overlays))
        widget.setProperty("pathenaGuidanceTooltipOverlayCount", min(2, len(overlays)))
        widget.setProperty("pathenaGuidanceComposed", True)

    @classmethod
    def _overlays(cls, widget: QWidget) -> list[tuple[str, str]]:
        overlays: list[tuple[str, str]] = []

        readiness_reason = cls._property_text(widget, "pathenaComposerBlockingReason")
        readiness_recovery = cls._property_text(widget, "pathenaComposerRecoveryCondition")
        if readiness_reason:
            overlays.append(
                ("Readiness", cls._combine(readiness_reason, readiness_recovery))
            )

        cancellation = cls._cancellation_text(widget)
        if cancellation:
            overlays.append(("Cancellation", cancellation))

        availability_reason = cls._property_text(widget, "pathenaEnablementReason")
        availability_restore = cls._property_text(
            widget,
            "pathenaEnablementRestoreCondition",
        )
        availability = cls._combine(availability_reason, availability_restore)
        if availability and not cls._duplicates_existing(availability, overlays):
            overlays.append(("Availability", availability))

        boundary = cls._property_text(widget, "pathenaBoundaryExplanation")
        if boundary and not cls._duplicates_existing(boundary, overlays):
            overlays.append(("Interaction boundary", boundary))

        return overlays

    @classmethod
    def _cancellation_text(cls, widget: QWidget) -> str:
        phase = cls._property_text(widget, "pathenaCancellationPhase")
        state = cls._property_text(widget, "pathenaCancellationSelectedState")
        if not phase or phase == "no-selection":
            return ""
        if phase == "requesting":
            return "A cancellation request is being persisted; terminal cancellation has not occurred yet."
        if phase == "requested":
            return "Cancellation is requested and persisted; terminal cancellation is still pending."
        if phase == "cancelled":
            return "The selected job is terminally cancelled."
        if phase == "terminal-other":
            return f"The selected job is terminal with state {state}; cancellation is not pending."
        if phase == "requestable":
            return f"The selected job is {state}; cancelling would persist a request first."
        return ""

    @staticmethod
    def _property_text(widget: QWidget, name: str) -> str:
        value = widget.property(name)
        return " ".join(str(value).split()) if value else ""

    @staticmethod
    def _combine(first: str, second: str) -> str:
        if not first:
            return second
        if not second:
            return first
        return f"{first} {second}"

    @staticmethod
    def _duplicates_existing(text: str, overlays: list[tuple[str, str]]) -> bool:
        normalized = " ".join(text.casefold().split())
        for _name, existing in overlays:
            other = " ".join(existing.casefold().split())
            if normalized == other or normalized in other or other in normalized:
                return True
        return False

    @staticmethod
    def _deduplicated_join(parts: list[str], *, separator: str) -> str:
        result: list[str] = []
        seen: set[str] = set()
        for part in parts:
            normalized_part = " ".join(part.split())
            if not normalized_part:
                continue
            key = normalized_part.casefold()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized_part)
        return separator.join(result)

    @staticmethod
    def _strip_dynamic_guidance(text: str) -> str:
        if not text:
            return ""
        earliest = len(text)
        for marker in _GUIDANCE_MARKERS:
            index = text.find(marker)
            if index >= 0:
                earliest = min(earliest, index)
        return text[:earliest].rstrip(" \n")


def _resolve(window: QWidget, target: GuidanceTarget) -> QWidget | None:
    workspace = window
    if target.workspace_name is not None:
        found = window.findChild(QWidget, target.workspace_name)
        if found is None:
            return None
        workspace = found
    candidate = getattr(workspace, target.attribute_name, None)
    return candidate if isinstance(candidate, QWidget) else None


def apply_ui_refinements_6001_6100(window: QWidget) -> tuple[int, ...]:
    """Install cross-layer guidance composition on dynamic UI surfaces."""
    controller = GuidanceCompositionController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = _resolve(window, target)
        if widget is None:
            continue
        controller.register(widget, target.label)
        start = 6001 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaGuidanceCompositionController", controller)
    window.setProperty("pathenaGuidanceCompositionManaged", True)
    return tuple(applied)
