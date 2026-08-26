from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QMainWindow, QWidget

from athena.desktop.app import create_application
from athena.desktop.ascii_panel import AsciiPanel
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-ascii-root-contract-test"])


def _root(marker: str) -> tuple[QMainWindow, QWidget, QLineEdit]:
    root = QMainWindow()
    body = QWidget(root)
    root.setCentralWidget(body)

    target = QWidget(body)
    target.setObjectName("pallasVisualPlaceholder")
    target.resize(260, 420)

    prompt = QLineEdit(marker, body)
    prompt.setObjectName("promptInput")
    prompt.show()
    QLabel(f"label-{marker}", body).show()
    root.show()
    return root, target, prompt


def test_explicit_roots_keep_binding_and_sampling_window_local() -> None:
    app = _app()
    first_root, first_target, _first_prompt = _root("first-window-marker")
    second_root, second_target, _second_prompt = _root("second-window-marker")
    first_panel = AsciiPanel()
    second_panel = AsciiPanel()
    app.processEvents()

    try:
        first_panel.bind_semantic_root(first_root)
        second_panel.bind_semantic_root(second_root)
        app.processEvents()

        assert first_panel._pallas_target is first_target
        assert second_panel._pallas_target is second_target
        assert "first-window-marker" in first_panel._semantic_snapshot()
        assert "second-window-marker" not in first_panel._semantic_snapshot()
        assert "second-window-marker" in second_panel._semantic_snapshot()
        assert "first-window-marker" not in second_panel._semantic_snapshot()
    finally:
        first_panel.close()
        second_panel.close()
        first_root.close()
        second_root.close()
        app.processEvents()


def test_rebind_and_unbind_release_the_previous_target() -> None:
    app = _app()
    first_root, first_target, _first_prompt = _root("first")
    second_root, second_target, _second_prompt = _root("second")
    panel = AsciiPanel()
    app.processEvents()

    try:
        panel.bind_semantic_root(first_root)
        assert panel._pallas_target is first_target

        panel.bind_semantic_root(second_root)
        assert panel._pallas_target is second_target
        assert "second" in panel._semantic_snapshot()
        assert "first" not in panel._semantic_snapshot()

        panel.bind_semantic_root(None)
        assert panel._pallas_target is None
        assert panel._semantic_snapshot() == "idle"
    finally:
        panel.close()
        first_root.close()
        second_root.close()
        app.processEvents()


def test_destroyed_root_clears_weak_binding_without_touching_a_new_root() -> None:
    app = _app()
    old_root, _old_target, _old_prompt = _root("old")
    new_root, new_target, _new_prompt = _root("new")
    panel = AsciiPanel()
    app.processEvents()

    try:
        panel.bind_semantic_root(old_root)
        panel.bind_semantic_root(new_root)
        old_root.deleteLater()
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()

        assert panel._semantic_root() is new_root
        assert panel._pallas_target is new_target

        new_root.deleteLater()
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
        assert panel._semantic_root() is None
        assert panel._pallas_target is None
    finally:
        panel.close()
        app.processEvents()


def test_binding_rejects_a_child_widget_as_semantic_root() -> None:
    app = _app()
    root, _target, _prompt = _root("marker")
    panel = AsciiPanel()
    app.processEvents()

    try:
        child = QWidget(root)
        with pytest.raises(ValueError, match="top-level"):
            panel.bind_semantic_root(child)
    finally:
        panel.close()
        root.close()
        app.processEvents()


def test_pathena_window_contract_restores_legacy_lifecycle_when_shell_calls_it() -> None:
    app = _app()
    first = PathenaMainWindow(api_controller=None)
    second = PathenaMainWindow(api_controller=None)
    first.show()
    second.show()
    app.processEvents()

    try:
        first.ascii_panel.bind_semantic_root(first)
        second.ascii_panel.bind_semantic_root(second)
        first.prompt_input.setText("first-shell-marker")
        second.prompt_input.setText("second-shell-marker")
        app.processEvents()

        assert first.ascii_panel._pallas_target is first.pallas_visual
        assert second.ascii_panel._pallas_target is second.pallas_visual
        assert "first-shell-marker" in first.ascii_panel._semantic_snapshot()
        assert "second-shell-marker" not in first.ascii_panel._semantic_snapshot()
        assert "second-shell-marker" in second.ascii_panel._semantic_snapshot()
        assert "first-shell-marker" not in second.ascii_panel._semantic_snapshot()
    finally:
        first.close()
        second.close()
        app.processEvents()
