from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.desktop.pathena_decision_context_3600 import DecisionContextController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QApplication, QWidget, QPushButton, QPushButton]:
    app = _app()
    window = QWidget()
    action = QPushButton("Run", window)
    anchor = QPushButton("Context", window)
    action.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    anchor.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    window.resize(320, 180)
    window.show()
    app.processEvents()
    return app, window, action, anchor


def _delete(widget: QWidget, app: QApplication) -> None:
    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


def test_deleted_action_is_dropped_from_deferred_focus_restore() -> None:
    app, window, action, anchor = _surface()
    controller = DecisionContextController(window)
    controller.register(action, anchor)

    _delete(action, app)

    controller._restore_context_if_needed(action)

    assert action not in controller._anchors


def test_deleted_anchor_is_dropped_without_invalid_qt_access() -> None:
    app, window, action, anchor = _surface()
    controller = DecisionContextController(window)
    controller.register(action, anchor)
    action.setEnabled(False)

    _delete(anchor, app)

    controller._restore_context_if_needed(action)

    assert action not in controller._anchors


def test_live_anchor_keeps_existing_focus_restore_behavior() -> None:
    app, window, action, anchor = _surface()
    controller = DecisionContextController(window)
    controller.register(action, anchor)
    action.setEnabled(False)

    controller._restore_context_if_needed(action)
    app.processEvents()

    assert QApplication.focusWidget() is anchor
    assert anchor.property("pathenaDecisionFocusReturned") is True
