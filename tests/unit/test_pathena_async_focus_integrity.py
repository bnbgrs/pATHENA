from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QEvent, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.desktop.pathena_async_focus_integrity_6200 import (
    AsyncFocusIntegrityController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _surface() -> tuple[QApplication, QWidget, QWidget, QPushButton, QPushButton]:
    app = _app()
    window = QWidget()
    workspace = QWidget(window)
    first = QPushButton("First", window)
    second = QPushButton("Second", window)
    first.setObjectName("first")
    second.setObjectName("second")
    first.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    second.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    window.resize(320, 180)
    window.show()
    app.processEvents()
    return app, window, workspace, first, second


def test_newer_focus_wins_over_stale_completion_restore() -> None:
    app, window, workspace, first, second = _surface()
    controller = AsyncFocusIntegrityController(window)
    controller._busy[workspace] = True

    second.setFocus()
    app.processEvents()
    controller._focus_changed(first, second)

    # Simulate a stale programmatic restore from another completion controller.
    # It must not be reclassified as newer user-selected focus by this arbiter.
    controller._reasserting = True
    try:
        first.setFocus()
        app.processEvents()
    finally:
        controller._reasserting = False
    assert QApplication.focusWidget() is first

    controller._settle_completion(workspace)
    app.processEvents()

    assert QApplication.focusWidget() is second
    assert second.property("pathenaAsyncFocusPreserved") is True
    assert workspace.property("pathenaAsyncFocusCompletion") == "newer-focus-restored"


def test_unavailable_preferred_focus_is_not_forced() -> None:
    app, window, workspace, first, second = _surface()
    controller = AsyncFocusIntegrityController(window)
    controller._preferred_focus[workspace] = second
    second.setEnabled(False)
    first.setFocus()
    app.processEvents()

    controller._settle_completion(workspace)
    app.processEvents()

    assert QApplication.focusWidget() is first
    assert workspace.property("pathenaAsyncFocusCompletion") == "preferred-unavailable"


def test_deleted_preferred_focus_is_treated_as_unavailable() -> None:
    app, window, workspace, first, second = _surface()
    controller = AsyncFocusIntegrityController(window)
    controller._preferred_focus[workspace] = second
    first.setFocus()
    app.processEvents()

    second.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()

    controller._settle_completion(workspace)
    app.processEvents()

    assert QApplication.focusWidget() is first
    assert workspace.property("pathenaAsyncFocusCompletion") == "preferred-unavailable"


def test_no_newer_focus_leaves_existing_focus_untouched() -> None:
    app, window, workspace, first, _second = _surface()
    controller = AsyncFocusIntegrityController(window)
    first.setFocus()
    app.processEvents()

    controller._settle_completion(workspace)

    assert QApplication.focusWidget() is first
    assert workspace.property("pathenaAsyncFocusCompletion") == "no-newer-focus"


def test_registered_surface_is_marked_as_managed() -> None:
    _app, window, workspace, first, _second = _surface()
    controller = AsyncFocusIntegrityController(window)

    controller.register(workspace, first)

    assert first.property("pathenaAsyncFocusIntegrityManaged") is True
