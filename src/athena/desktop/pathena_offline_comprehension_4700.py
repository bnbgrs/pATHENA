"""Offline, provider and model readiness comprehension for pATHENA.

The desktop already owns the real readiness facts. This presentation-only controller
mirrors those facts into consistent status/tool-tip/placeholder guidance across the
chat status, model selector and composer. It does not load models, reconnect services,
or invent capabilities.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton, QWidget


@dataclass(frozen=True)
class ReadinessPresentation:
    state: str
    summary: str
    next_step: str
    composer_placeholder: str


class OfflineComprehensionController(QObject):
    """Keep local readiness meaning consistent across the chat interaction surface."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self.status = window.findChild(QLabel, "localStatus")
        self.model_selector = window.findChild(QComboBox, "modelSelector")
        self.prompt = window.findChild(QLineEdit, "promptInput")
        self.send = window.findChild(QPushButton, "sendButton")
        self.ground = window.findChild(QPushButton, "groundButton")
        self._last_state = ""
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()
        self.sync()

    def sync(self) -> None:
        presentation = self._presentation()
        state_changed = presentation.state != self._last_state
        if state_changed:
            self._last_state = presentation.state
            for widget in self._managed_widgets():
                widget.setProperty("pathenaReadinessState", presentation.state)
                widget.setProperty("pathenaReadinessSummary", presentation.summary)
                widget.setProperty("pathenaReadinessNextStep", presentation.next_step)

        if self.status is not None:
            if presentation.state == "core-offline":
                self.status.setText("pATHENA reconnecting")
            self.status.setToolTip(
                f"{presentation.summary} Next: {presentation.next_step}."
            )
            self.status.setAccessibleDescription(
                f"pATHENA readiness: {presentation.summary} Next step: "
                f"{presentation.next_step}."
            )
        if self.model_selector is not None:
            self.model_selector.setToolTip(
                f"Local model selection. {presentation.summary} "
                f"Next: {presentation.next_step}."
            )
        if self.prompt is not None and not self.prompt.text():
            self.prompt.setPlaceholderText(presentation.composer_placeholder)
            self.prompt.setToolTip(
                f"{presentation.summary} Next: {presentation.next_step}."
            )
        if self.send is not None:
            self.send.setStatusTip(presentation.summary)
        if self.ground is not None:
            self.ground.setStatusTip(presentation.summary)

        if presentation.state == "core-offline":
            empty_title = self.window.findChild(QLabel, "emptyStateTitle")
            if empty_title is not None:
                empty_title.setText("Getting pATHENA ready")

    def _presentation(self) -> ReadinessPresentation:
        core_transport_ready = bool(
            getattr(self.window, "_core_transport_ready", False)
        )
        provider_ready = bool(getattr(self.window, "_provider_ready", False))
        last_model_error = getattr(self.window, "_last_model_error", None)
        selected_model = self._selected_model()

        if not core_transport_ready:
            return ReadinessPresentation(
                "core-offline",
                "pATHENA is reconnecting; chat submission is temporarily unavailable.",
                "keep pATHENA open while it reconnects",
                "pATHENA reconnecting",
            )
        if last_model_error is not None:
            return ReadinessPresentation(
                "model-error",
                "The selected local model reported an error.",
                "inspect System status or select another available local model",
                "Local model error — choose or recover a model",
            )
        if not provider_ready:
            return ReadinessPresentation(
                "provider-unavailable",
                "The local model service is unavailable.",
                "recover it in System or select another available local model",
                "Local model service unavailable",
            )
        if selected_model is None:
            return ReadinessPresentation(
                "model-required",
                "No local model is selected.",
                "choose an available local model",
                "Choose a local model to chat",
            )
        if not bool(getattr(selected_model, "loaded", False)):
            return ReadinessPresentation(
                "model-not-loaded",
                "The selected local model is not currently loaded.",
                "load the model in the provider or select a loaded model",
                "Selected local model is not loaded",
            )
        return ReadinessPresentation(
            "ready",
            "pATHENA and the selected local model are ready.",
            "type a message",
            "Ask ATHENA",
        )

    def _selected_model(self) -> object | None:
        candidate = getattr(self.window, "_selected_model", None)
        if not callable(candidate):
            return None
        selector = cast(Callable[[], object | None], candidate)
        return selector()

    def _managed_widgets(self) -> tuple[QWidget, ...]:
        return tuple(
            widget
            for widget in (
                self.status,
                self.model_selector,
                self.prompt,
                self.send,
                self.ground,
            )
            if widget is not None
        )


def apply_ui_refinements_4601_4700(window: QWidget) -> tuple[int, ...]:
    """Install readiness comprehension on existing chat controls."""
    controller = OfflineComprehensionController(window)
    window.setProperty("pathenaOfflineComprehensionController", controller)
    window.setProperty("pathenaOfflineComprehensionManaged", True)
    return tuple(range(4601, 4701))
