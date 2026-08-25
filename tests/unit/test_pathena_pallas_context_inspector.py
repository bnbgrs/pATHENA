from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import QApplication, QFrame, QLabel
from shiboken6 import isValid

from athena.desktop.pathena_pallas_inspector import (
    PallasContextInspectorController,
    install_pallas_context_inspector,
)
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import PathenaMainWindow


class _Kind(StrEnum):
    CLAIM = "claim"


@dataclass(frozen=True)
class _Node:
    node_id: str = "claim:claim-7"
    kind: _Kind = _Kind.CLAIM
    entity_type: str = "claim"
    entity_id: str = "claim-7"
    revision_id: str = "revision-3"
    title: str = "Local evidence remains attributable"
    summary: str = "The persisted claim keeps its source identity."
    epistemic_status: str = "supported"
    cited: bool = True
    confidence: float = 0.875

    @property
    def glyph(self) -> str:
        return "◆"


@dataclass(frozen=True)
class _Selection:
    graph_id: str = "grounded-run:run-4"
    node: _Node = _Node()


class _SelectionSource(QObject):
    selection_changed = Signal(object)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        if not existing.styleSheet():
            existing.setStyleSheet(PATHENA_STYLESHEET)
        existing.setApplicationDisplayName("pATHENA")
        return existing
    app = QApplication([])
    app.setStyleSheet(PATHENA_STYLESHEET)
    app.setApplicationDisplayName("pATHENA")
    return app


def _surface() -> tuple[QApplication, PathenaMainWindow, _SelectionSource]:
    app = _app()
    window = PathenaMainWindow()
    source = _SelectionSource()
    window.resize(1480, 900)
    window.show()
    app.processEvents()
    return app, window, source


def test_selection_projects_only_real_payload_fields() -> None:
    app, window, source = _surface()
    controller = install_pallas_context_inspector(window, source)

    source.selection_changed.emit(_Selection())
    app.processEvents()

    panel = window.findChild(QFrame, "inspector")
    object_id = window.findChild(QLabel, "objectId")
    heading = window.findChild(QLabel, "inspectorHeading")
    body = window.findChild(QLabel, "inspectorBody")
    assert panel is not None and panel.isVisible()
    assert object_id is not None and object_id.text() == "PALLAS / CLAIM / claim:claim-7"
    assert heading is not None and heading.text() == "◆ Local evidence remains attributable"
    assert body is not None
    assert "Entity: claim / claim-7" in body.text()
    assert "Revision: revision-3" in body.text()
    assert "Graph: grounded-run:run-4" in body.text()
    assert "Confidence: 0.88" in body.text()
    assert panel.property("pathenaPallasSelectionId") == "claim:claim-7"
    assert not window.inspector_message_count.isVisible()
    controller.dispose()
    window.close()


def test_clear_restores_previous_screen_context_and_visibility() -> None:
    app, window, source = _surface()
    panel = window.findChild(QFrame, "inspector")
    object_id = window.findChild(QLabel, "objectId")
    assert panel is not None and object_id is not None
    panel.hide()
    object_id.setText("CHAT / durable-chat")
    controller = install_pallas_context_inspector(window, source)

    source.selection_changed.emit(_Selection())
    source.selection_changed.emit(None)
    app.processEvents()

    assert object_id.text() == "CHAT / durable-chat"
    assert not panel.isVisible()
    assert panel.property("pathenaPallasSelectionId") is None
    controller.dispose()
    window.close()


def test_invalid_payload_clears_without_inventing_content() -> None:
    app, window, source = _surface()
    controller = install_pallas_context_inspector(window, source)
    original = window.inspector_heading.text()

    source.selection_changed.emit(object())
    app.processEvents()

    assert window.inspector_heading.text() == original
    assert window.findChild(QFrame, "inspector").property("pathenaPallasSelectionId") is None
    controller.dispose()
    window.close()


def test_inspector_is_keyboard_focusable_without_stealing_canvas_focus() -> None:
    app, window, source = _surface()
    window.prompt_input.setFocus()
    app.processEvents()
    controller = install_pallas_context_inspector(window, source)

    source.selection_changed.emit(_Selection())
    app.processEvents()

    panel = window.findChild(QFrame, "inspector")
    assert panel is not None
    assert panel.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert panel.accessibleName() == "PALLAS Context Inspector"
    assert QApplication.focusWidget() is not panel
    panel.setFocus()
    app.processEvents()
    assert QApplication.focusWidget() is panel
    controller.dispose()
    window.close()


def test_destroyed_window_disconnects_long_lived_source_safely() -> None:
    app, window, source = _surface()
    controller = install_pallas_context_inspector(window, source)
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    assert not isValid(window)
    assert not isValid(controller)
    source.selection_changed.emit(_Selection())
    app.processEvents()


def test_window_exposes_single_rebindable_shared_slot() -> None:
    _app_instance, window, source = _surface()
    first = window.bind_pallas_context_inspector(source)
    second = window.bind_pallas_context_inspector(source)

    assert isinstance(first, PallasContextInspectorController)
    assert isinstance(second, PallasContextInspectorController)
    assert first is not second
    source.selection_changed.emit(_Selection())
    assert (
        window.findChild(QFrame, "inspector").property("pathenaPallasSelectionId")
        == "claim:claim-7"
    )
    second.dispose()
    window.close()
