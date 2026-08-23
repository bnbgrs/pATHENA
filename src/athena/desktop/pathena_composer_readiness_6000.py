"""Deterministic chat-composer readiness hierarchy for pATHENA.

Several real prerequisites can block chat at once. This presentation-only controller
chooses one truthful highest-priority reason from the existing controller/Core/provider/
model/conversation/busy state and mirrors it across composer-adjacent surfaces. It does
not change enablement, load a model, reconnect a provider, or start a chat operation.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class ReadinessTarget:
    attribute_name: str
    label: str


_TARGETS: tuple[ReadinessTarget, ...] = (
    ReadinessTarget("prompt_input", "Chat composer"),
    ReadinessTarget("ground_button", "Grounding"),
    ReadinessTarget("send_button", "Send"),
    ReadinessTarget("model_selector", "Model selector"),
    ReadinessTarget("chat_selector", "Conversation selector"),
    ReadinessTarget("delete_chat_button", "Delete conversation"),
    ReadinessTarget("new_chat_button", "New conversation"),
    ReadinessTarget("status_text", "Local readiness status"),
    ReadinessTarget("connection_detail", "Connection detail"),
    ReadinessTarget("settings_model_value", "Settings model state"),
)

_DIMENSIONS: tuple[str, ...] = (
    "readiness priority",
    "primary blocking reason",
    "readiness recovery condition",
    "composer readiness state",
    "assistive readiness description",
    "tooltip readiness guidance",
    "readiness diagnostic metadata",
    "provider-model distinction",
    "conversation-busy distinction",
    "readiness synchronization",
)

UI_REFINEMENT_TASKS_5901_6000: tuple[str, ...] = tuple(
    f"{dimension}: {target.label}"
    for target in _TARGETS
    for dimension in _DIMENSIONS
)


@dataclass(frozen=True)
class ReadinessSnapshot:
    state: str
    priority: int
    reason: str
    recovery: str


class ComposerReadinessController(QObject):
    """Mirror one authoritative readiness reason across existing chat surfaces."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._widgets: list[tuple[QWidget, str]] = []
        self._last: ReadinessSnapshot | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()

    def register(self, widget: QWidget, label: str) -> None:
        self._widgets.append((widget, label))
        widget.setProperty("pathenaComposerReadinessObservedOnly", True)
        self.sync()

    def sync(self) -> None:
        snapshot = self._snapshot()
        if snapshot == self._last:
            return
        self._last = snapshot
        for widget, label in self._widgets:
            self._apply(widget, label, snapshot)
        self.window.setProperty("pathenaComposerReadinessState", snapshot.state)
        self.window.setProperty("pathenaComposerReadinessPriority", snapshot.priority)
        self.window.setProperty("pathenaComposerBlockingReason", snapshot.reason)

    def _snapshot(self) -> ReadinessSnapshot:
        if getattr(self.window, "api_controller", None) is None:
            return ReadinessSnapshot(
                "controller-unavailable",
                1,
                "The desktop API controller is unavailable.",
                "Chat returns when the local desktop controller is connected.",
            )
        if not bool(getattr(self.window, "_core_transport_ready", False)):
            return ReadinessSnapshot(
                "core-offline",
                2,
                "The local Core transport is not ready.",
                "Chat returns when the existing Core connection reports ready.",
            )
        model_error = getattr(self.window, "_last_model_error", None)
        if isinstance(model_error, str) and model_error:
            return ReadinessSnapshot(
                "model-error",
                3,
                "Local model discovery reported an error.",
                "Chat returns after model discovery succeeds on a later status refresh.",
            )
        if not bool(getattr(self.window, "_provider_ready", False)):
            return ReadinessSnapshot(
                "provider-unavailable",
                4,
                "The local model provider is unavailable or stale.",
                "Chat returns when provider status and model discovery are fresh and ready.",
            )
        model = self._selected_model()
        if model is None:
            return ReadinessSnapshot(
                "model-required",
                5,
                "No local language model is selected or available.",
                "Chat returns when model discovery provides a selectable local model.",
            )
        if not bool(getattr(model, "loaded", False)):
            return ReadinessSnapshot(
                "model-not-loaded",
                6,
                "The selected local model is available but not loaded.",
                "Chat returns when the provider reports the selected model as loaded.",
            )
        if getattr(self.window, "pending_chat_id", None) is not None:
            return ReadinessSnapshot(
                "conversation-loading",
                7,
                "The selected conversation is still loading.",
                "Chat returns when the selected conversation finishes loading.",
            )
        if bool(getattr(self.window, "_chat_busy", False)):
            return ReadinessSnapshot(
                "chat-busy",
                8,
                "A chat operation is currently running.",
                "Chat input returns when the current chat operation finishes.",
            )
        return ReadinessSnapshot(
            "ready",
            9,
            "Chat is ready for local interaction.",
            "No readiness prerequisite is currently blocking the composer.",
        )

    def _selected_model(self) -> object | None:
        selector = getattr(self.window, "_selected_model", None)
        return selector() if callable(selector) else None

    @staticmethod
    def _apply(widget: QWidget, label: str, snapshot: ReadinessSnapshot) -> None:
        widget.setProperty("pathenaComposerReadinessState", snapshot.state)
        widget.setProperty("pathenaComposerReadinessPriority", snapshot.priority)
        widget.setProperty("pathenaComposerBlockingReason", snapshot.reason)
        widget.setProperty("pathenaComposerRecoveryCondition", snapshot.recovery)
        widget.setProperty("pathenaComposerProviderBlocked", snapshot.state == "provider-unavailable")
        widget.setProperty(
            "pathenaComposerModelBlocked",
            snapshot.state in {"model-error", "model-required", "model-not-loaded"},
        )
        widget.setProperty(
            "pathenaComposerConversationBlocked",
            snapshot.state in {"conversation-loading", "chat-busy"},
        )
        widget.setProperty("pathenaComposerReadinessSynchronized", True)

        explanation = f"{snapshot.reason} {snapshot.recovery}"
        widget.setAccessibleDescription(
            ComposerReadinessController._with_suffix(
                widget.accessibleDescription(),
                " Readiness: ",
                explanation,
            )
        )
        widget.setToolTip(
            ComposerReadinessController._with_suffix(
                widget.toolTip(),
                "\nReadiness: ",
                explanation,
            )
        )
        widget.setStatusTip(f"{label} readiness: {explanation}")

    @staticmethod
    def _with_suffix(current: str, marker: str, suffix: str) -> str:
        base = current.split(marker, 1)[0].rstrip()
        if not base:
            return f"Readiness: {suffix}"
        return f"{base}{marker}{suffix}"


def apply_ui_refinements_5901_6000(window: QWidget) -> tuple[int, ...]:
    """Install deterministic readiness guidance without owning chat enablement."""
    controller = ComposerReadinessController(window)
    applied: list[int] = []
    for index, target in enumerate(_TARGETS):
        widget = getattr(window, target.attribute_name, None)
        if not isinstance(widget, QWidget):
            continue
        controller.register(widget, target.label)
        start = 5901 + index * len(_DIMENSIONS)
        applied.extend(range(start, start + len(_DIMENSIONS)))

    window.setProperty("pathenaComposerReadinessController", controller)
    window.setProperty("pathenaComposerReadinessManaged", True)
    return tuple(applied)
