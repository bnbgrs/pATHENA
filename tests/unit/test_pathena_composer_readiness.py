from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_composer_readiness_6000 import ComposerReadinessController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


@dataclass
class _Model:
    loaded: bool


class _Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.api_controller: object | None = object()
        self._core_transport_ready = True
        self._last_model_error: str | None = None
        self._provider_ready = True
        self.pending_chat_id: str | None = None
        self._chat_busy = False
        self.model: _Model | None = _Model(loaded=True)

    def _selected_model(self) -> _Model | None:
        return self.model


def test_controller_unavailable_has_highest_priority() -> None:
    _app()
    window = _Window()
    window.api_controller = None
    window._core_transport_ready = False
    window._provider_ready = False
    window._chat_busy = True
    surface = QWidget(window)

    controller = ComposerReadinessController(window)
    controller.register(surface, "Send")

    assert surface.property("pathenaComposerReadinessState") == "controller-unavailable"
    assert surface.property("pathenaComposerReadinessPriority") == 1


def test_provider_block_wins_before_model_and_conversation_conditions() -> None:
    _app()
    window = _Window()
    window._provider_ready = False
    window.model = None
    window.pending_chat_id = "chat-loading"
    window._chat_busy = True
    surface = QWidget(window)

    controller = ComposerReadinessController(window)
    controller.register(surface, "Chat composer")

    assert surface.property("pathenaComposerReadinessState") == "provider-unavailable"
    assert surface.property("pathenaComposerProviderBlocked") is True
    assert surface.property("pathenaComposerConversationBlocked") is False


def test_pending_conversation_precedes_chat_busy() -> None:
    _app()
    window = _Window()
    window.pending_chat_id = "chat-loading"
    window._chat_busy = True
    surface = QWidget(window)

    controller = ComposerReadinessController(window)
    controller.register(surface, "Conversation selector")

    assert surface.property("pathenaComposerReadinessState") == "conversation-loading"
    assert surface.property("pathenaComposerReadinessPriority") == 7


def test_every_registered_widget_receives_initial_snapshot() -> None:
    _app()
    window = _Window()
    first = QWidget(window)
    second = QWidget(window)

    controller = ComposerReadinessController(window)
    controller.register(first, "First")
    controller.register(second, "Second")

    assert first.property("pathenaComposerReadinessState") == "ready"
    assert second.property("pathenaComposerReadinessState") == "ready"
    assert first.property("pathenaComposerReadinessObservedOnly") is True
    assert second.property("pathenaComposerReadinessObservedOnly") is True


def test_sync_changes_readiness_without_changing_enablement() -> None:
    _app()
    window = _Window()
    surface = QWidget(window)
    surface.setEnabled(False)
    controller = ComposerReadinessController(window)
    controller.register(surface, "Send")

    window._chat_busy = True
    controller.sync()

    assert surface.isEnabled() is False
    assert surface.property("pathenaComposerReadinessState") == "chat-busy"
