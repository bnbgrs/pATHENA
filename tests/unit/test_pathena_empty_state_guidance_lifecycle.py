from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QListWidget, QPushButton, QWidget

from athena.desktop.pathena_empty_state_guidance_3400 import (
    EmptyStateGuidanceController,
    EmptyStateTarget,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QApplication, QWidget, QListWidget, QPushButton]:
    app = _app()
    window = QWidget()
    target = QListWidget(window)
    action = QPushButton("Refresh", window)
    window.resize(320, 180)
    window.show()
    app.processEvents()
    return app, window, target, action


def _target() -> EmptyStateTarget:
    return EmptyStateTarget(
        "testList",
        "test list",
        None,
        "Refresh",
        "No items are available.",
    )


def _delete(widget: QWidget, app: QApplication) -> None:
    widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


def test_deleted_target_is_dropped_during_deferred_sync() -> None:
    app, window, target, action = _surface()
    controller = EmptyStateGuidanceController(window)
    controller.register(target, _target(), action)

    _delete(target, app)

    controller.sync()

    assert target not in controller._targets
    assert target not in controller._actions


def test_deleted_action_does_not_break_live_target_sync() -> None:
    app, window, target, action = _surface()
    controller = EmptyStateGuidanceController(window)
    controller.register(target, _target(), action)

    _delete(action, app)

    controller.sync()

    assert target in controller._targets
    assert controller._actions[target] is None
    assert target.property("pathenaEmptyStateActive") is True
    assert target.property("pathenaContentState") == "empty"


def test_live_action_keeps_existing_empty_state_behavior() -> None:
    app, window, target, action = _surface()
    controller = EmptyStateGuidanceController(window)
    controller.register(target, _target(), action)

    controller.sync()
    app.processEvents()

    assert target.property("pathenaEmptyStateActive") is True
    assert action.property("pathenaEmptyStatePrimary") is True

    target.addItem("one")
    controller.sync()
    app.processEvents()

    assert target.property("pathenaEmptyStateActive") is False
    assert target.property("pathenaContentState") == "populated"
    assert action.property("pathenaEmptyStatePrimary") is False
