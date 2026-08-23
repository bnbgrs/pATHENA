"""Model-settings comprehension for the existing pATHENA inference controls.

The settings page already stores per-model CTX, output, temperature and thinking
choices. This presentation-only controller explains the currently selected model and
the meaning of each existing control without changing ranges, values, enabled state,
provider behavior or request construction.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QWidget


class SettingsComprehensionController(QObject):
    """Mirror selected-model facts into concise, truthful settings guidance."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        self.window = window
        self._last_signature: tuple[object, ...] | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self.sync)
        self._timer.start()
        self.sync()

    def sync(self) -> None:
        model = self._selected_model()
        loaded = bool(getattr(model, "loaded", False)) if model is not None else False
        capacity = self._runtime_capacity(model)
        context_value = self._value("context_spin")
        output_value = self._value("max_output_spin")
        thinking = self._checked("thinking_checkbox")
        signature = (id(model), loaded, capacity, context_value, output_value, thinking)
        if signature == self._last_signature:
            return
        self._last_signature = signature

        model_state = (
            "no-model"
            if model is None
            else "loaded"
            if loaded
            else "available-not-loaded"
        )
        context_mode = "auto" if model is not None and capacity is None else "exact"

        for widget in self._controls():
            widget.setProperty("pathenaSettingsModelState", model_state)
            widget.setProperty("pathenaSettingsContextMode", context_mode)
            widget.setProperty("pathenaSettingsPerModel", True)

        self._set_tip(
            "context_slider",
            self._context_tip(model_state, capacity),
        )
        self._set_tip(
            "context_spin",
            self._context_tip(model_state, capacity),
        )
        self._set_tip(
            "max_output_slider",
            self._output_tip(model_state, context_value),
        )
        self._set_tip(
            "max_output_spin",
            self._output_tip(model_state, context_value),
        )
        self._set_tip(
            "temperature_spin",
            "Sampling temperature for the selected model. This value is remembered "
            "per model and does not change model loading state.",
        )
        self._set_tip(
            "thinking_checkbox",
            "OFF sends reasoning_effort=none. ON allows reasoning when the selected "
            "model/provider supports it; ON does not guarantee reasoning support.",
        )

        settings_value = getattr(self.window, "settings_model_value", None)
        if isinstance(settings_value, QWidget):
            settings_value.setProperty("pathenaSettingsModelState", model_state)
            settings_value.setAccessibleDescription(
                self._model_description(model, model_state, capacity)
            )

    def _selected_model(self) -> object | None:
        candidate = getattr(self.window, "_selected_model", None)
        if not callable(candidate):
            return None
        selector = cast(Callable[[], object | None], candidate)
        return selector()

    @staticmethod
    def _runtime_capacity(model: object | None) -> int | None:
        if model is None:
            return None
        loaded = getattr(model, "loaded_context_length", None)
        capacity = getattr(model, "context_capacity", None)
        value = loaded or capacity
        return value if isinstance(value, int) and value > 0 else None

    def _value(self, attribute_name: str) -> int | None:
        widget = getattr(self.window, attribute_name, None)
        value_method = getattr(widget, "value", None)
        if not callable(value_method):
            return None
        result = value_method()
        return result if isinstance(result, int) else None

    def _checked(self, attribute_name: str) -> bool | None:
        widget = getattr(self.window, attribute_name, None)
        checked = getattr(widget, "isChecked", None)
        if not callable(checked):
            return None
        result = checked()
        return result if isinstance(result, bool) else None

    def _controls(self) -> tuple[QWidget, ...]:
        names = (
            "context_slider",
            "context_spin",
            "max_output_slider",
            "max_output_spin",
            "temperature_spin",
            "thinking_checkbox",
        )
        return tuple(
            widget
            for name in names
            if isinstance((widget := getattr(self.window, name, None)), QWidget)
        )

    def _set_tip(self, attribute_name: str, text: str) -> None:
        widget = getattr(self.window, attribute_name, None)
        if not isinstance(widget, QWidget):
            return
        widget.setToolTip(text)
        widget.setStatusTip(text)
        widget.setAccessibleDescription(text)

    @staticmethod
    def _context_tip(model_state: str, capacity: int | None) -> str:
        if model_state == "no-model":
            return "CTX is per model. Choose a local model before a model-specific context can apply."
        if capacity is None:
            return (
                "CTX capacity is not reported separately by the provider, so pATHENA "
                "shows AUTO rather than inventing an exact model ceiling."
            )
        return (
            f"Total request context for the selected model. Current discovered ceiling: "
            f"{capacity:,} tokens."
        )

    @staticmethod
    def _output_tip(model_state: str, context_value: int | None) -> str:
        if model_state == "no-model":
            return "MAX OUTPUT is per model and becomes meaningful after selecting a model."
        if context_value is None:
            return "MAX OUTPUT is bounded by the effective context and pATHENA safety reserve."
        return (
            f"Maximum response budget for the selected model. It remains bounded by "
            f"CTX {context_value:,} minus pATHENA's safety reserve."
        )

    @staticmethod
    def _model_description(
        model: object | None,
        model_state: str,
        capacity: int | None,
    ) -> str:
        if model is None:
            return "No local model selected. Per-model inference settings are not active."
        display_name = str(getattr(model, "display_name", "selected local model"))
        state = "loaded and ready for requests" if model_state == "loaded" else "available but not loaded"
        capacity_text = (
            f" Discovered context capacity: {capacity:,} tokens."
            if capacity is not None
            else " Exact context capacity is not reported; CTX uses AUTO semantics."
        )
        return f"{display_name}: {state}.{capacity_text}"


def apply_ui_refinements_5001_5100(window: QWidget) -> tuple[int, ...]:
    """Install model-settings comprehension without changing inference behavior."""
    controller = SettingsComprehensionController(window)
    window.setProperty("pathenaSettingsComprehensionController", controller)
    window.setProperty("pathenaSettingsComprehensionManaged", True)
    return tuple(range(5001, 5101))
