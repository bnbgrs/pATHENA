from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QLabel,
    QSlider,
    QSpinBox,
    QWidget,
)

from athena.desktop.pathena_settings_comprehension_5100 import (
    SettingsComprehensionController,
)


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._model: object | None = None
        self.context_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.context_spin = QSpinBox(self)
        self.max_output_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.max_output_spin = QSpinBox(self)
        self.temperature_spin = QDoubleSpinBox(self)
        self.thinking_checkbox = QCheckBox(self)
        self.settings_model_value = QLabel(self)
        self.context_spin.setRange(1, 131_072)
        self.context_spin.setValue(16_384)
        self.max_output_spin.setRange(1, 131_072)
        self.max_output_spin.setValue(4_096)

    def _selected_model(self) -> object | None:
        return self._model


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_settings_explain_no_model_without_changing_values() -> None:
    _app()
    window = _Window()
    context_before = window.context_spin.value()
    output_before = window.max_output_spin.value()

    SettingsComprehensionController(window)

    assert window.context_spin.value() == context_before
    assert window.max_output_spin.value() == output_before
    assert window.context_spin.property("pathenaSettingsModelState") == "no-model"
    assert "Choose a local model" in window.context_spin.toolTip()


def test_settings_distinguish_auto_capacity_and_loaded_model() -> None:
    _app()
    window = _Window()
    window._model = SimpleNamespace(
        loaded=True,
        loaded_context_length=None,
        context_capacity=None,
        display_name="Local Model",
    )

    controller = SettingsComprehensionController(window)

    assert window.context_spin.property("pathenaSettingsContextMode") == "auto"
    assert "AUTO" in window.context_spin.toolTip()
    assert "loaded and ready" in window.settings_model_value.accessibleDescription()

    window._model = SimpleNamespace(
        loaded=False,
        loaded_context_length=32_768,
        context_capacity=65_536,
        display_name="Known Model",
    )
    controller.sync()

    assert window.context_spin.property("pathenaSettingsContextMode") == "exact"
    assert "32,768" in window.context_spin.toolTip()
    assert "available but not loaded" in window.settings_model_value.accessibleDescription()


def test_settings_controls_have_distinct_assistive_names() -> None:
    _app()
    window = _Window()

    SettingsComprehensionController(window)

    assert window.context_slider.accessibleName() == "Context size slider"
    assert window.context_spin.accessibleName() == "Context size exact value"
    assert window.max_output_slider.accessibleName() == "Maximum output slider"
    assert window.max_output_spin.accessibleName() == "Maximum output exact value"
    assert window.temperature_spin.accessibleName() == "Sampling temperature"
    assert window.thinking_checkbox.accessibleName() == "Thinking and reasoning"
    assert window.settings_model_value.accessibleName() == "Selected local model"


def test_settings_visible_labels_point_to_exact_controls() -> None:
    _app()
    window = _Window()
    page = QWidget(window)
    page.setObjectName("pageSettings")
    labels = {
        text: QLabel(text, page)
        for text in ("CTX", "MAX OUTPUT TOKENS", "TEMPERATURE", "THINKING")
    }

    SettingsComprehensionController(window)

    assert labels["CTX"].buddy() is window.context_spin
    assert labels["MAX OUTPUT TOKENS"].buddy() is window.max_output_spin
    assert labels["TEMPERATURE"].buddy() is window.temperature_spin
    assert labels["THINKING"].buddy() is window.thinking_checkbox
    assert labels["CTX"].property("pathenaSettingsBuddyControl") == "context_spin"
