from __future__ import annotations

import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from athena.desktop.pathena_offline_comprehension_4700 import (
    OfflineComprehensionController,
)


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._core_transport_ready = False
        self._provider_ready = False
        self._last_model_error: str | None = None
        self._model: object | None = None

        self.status = QLabel(self)
        self.status.setObjectName("localStatus")
        self.model_selector = QComboBox(self)
        self.model_selector.setObjectName("modelSelector")
        self.prompt = QLineEdit(self)
        self.prompt.setObjectName("promptInput")
        self.send = QPushButton(self)
        self.send.setObjectName("sendButton")
        self.ground = QPushButton(self)
        self.ground.setObjectName("groundButton")

    def _selected_model(self) -> object | None:
        return self._model


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_readiness_copy_tracks_real_local_state() -> None:
    _app()
    window = _Window()
    controller = OfflineComprehensionController(window)

    assert window.prompt.property("pathenaReadinessState") == "core-offline"
    assert "offline" in window.prompt.placeholderText().casefold()

    window._core_transport_ready = True
    window._provider_ready = False
    controller.sync()
    assert window.prompt.property("pathenaReadinessState") == "provider-unavailable"

    window._provider_ready = True
    controller.sync()
    assert window.prompt.property("pathenaReadinessState") == "model-required"

    window._model = SimpleNamespace(loaded=False)
    controller.sync()
    assert window.prompt.property("pathenaReadinessState") == "model-not-loaded"

    window._model = SimpleNamespace(loaded=True)
    controller.sync()
    assert window.prompt.property("pathenaReadinessState") == "ready"
    assert window.prompt.placeholderText() == "Ask ATHENA"


def test_model_error_has_precedence_after_core_connects() -> None:
    _app()
    window = _Window()
    window._core_transport_ready = True
    window._provider_ready = True
    window._model = SimpleNamespace(loaded=True)
    window._last_model_error = "provider model failed"

    controller = OfflineComprehensionController(window)

    assert window.status.property("pathenaReadinessState") == "model-error"
    assert "model" in window.status.toolTip().casefold()
    assert "system" in window.model_selector.toolTip().casefold()
