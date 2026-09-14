from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QWidget

from athena.desktop.pathena_offline_comprehension_4700 import OfflineComprehensionController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_offline_readiness_preserves_reference_welcome_and_neutral_composer_copy() -> None:
    _app()
    window = QWidget()
    window._core_transport_ready = False
    window._provider_ready = False
    window._last_model_error = None

    status = QLabel(window)
    status.setObjectName("localStatus")
    prompt = QLineEdit(window)
    prompt.setObjectName("promptInput")
    send = QPushButton(window)
    send.setObjectName("sendButton")
    ground = QPushButton(window)
    ground.setObjectName("groundButton")
    title = QLabel("Hello, Commander.", window)
    title.setObjectName("emptyStateTitle")

    controller = OfflineComprehensionController(window)
    controller.sync()

    assert status.text() == "pATHENA reconnecting"
    assert "reconnecting" in status.toolTip().casefold()
    assert prompt.placeholderText() == "Ask anything…"
    assert title.text() == "Hello, Commander."
    assert window.property("pathenaReferenceWelcomePreserved") is True

    controller.deleteLater()
    window.close()
