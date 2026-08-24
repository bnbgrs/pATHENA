from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_layout_resilience_4000 import LayoutResilienceController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _flush_deferred_delete() -> None:
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    QCoreApplication.processEvents()


def test_layout_resilience_drops_destroyed_registered_widget() -> None:
    _app()
    window = QWidget()
    window.resize(1400, 800)
    target = QWidget(window)
    controller = LayoutResilienceController(window)
    controller.register(target)

    target.deleteLater()
    _flush_deferred_delete()

    controller.sync()

    assert controller._widgets == []


def test_layout_resilience_keeps_live_widgets_synchronized() -> None:
    _app()
    window = QWidget()
    window.resize(1400, 800)
    target = QWidget(window)
    controller = LayoutResilienceController(window)
    controller.register(target)

    controller.sync()

    assert controller._widgets == [target]
    assert target.property("pathenaCompactLayout") is True
    assert target.property("pathenaLayoutMode") == "compact"

    window.resize(1600, 800)
    controller.sync()

    assert target.property("pathenaCompactLayout") is False
    assert target.property("pathenaLayoutMode") == "regular"
