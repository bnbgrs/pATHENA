from __future__ import annotations

from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-pallas-lifecycle-test"])


def test_pallas_binding_stays_owned_by_each_window_across_context_changes() -> None:
    app = _app()
    first = PathenaMainWindow(api_controller=None)
    second = PathenaMainWindow(api_controller=None)
    first.show()
    second.show()
    app.processEvents()

    try:
        first.ascii_panel.set_context("knowledge")
        second.ascii_panel.set_context("research")
        app.processEvents()

        assert first.ascii_panel._pallas_target is first.pallas_visual
        assert second.ascii_panel._pallas_target is second.pallas_visual
        assert first.ascii_panel._pallas_target is not second.pallas_visual
        assert second.ascii_panel._pallas_target is not first.pallas_visual

        for row in range(first.navigation.count()):
            first.navigation.setCurrentRow(row)
            first.ascii_panel.set_context(first.page_title.text())
            app.processEvents()
            assert first.ascii_panel._pallas_target is first.pallas_visual

        second.close()
        app.processEvents()
        first.ascii_panel.set_context("chat")
        app.processEvents()
        assert first.ascii_panel._pallas_target is first.pallas_visual
    finally:
        first.close()
        second.close()
        app.processEvents()


def test_pallas_semantic_sampling_does_not_cross_window_boundaries() -> None:
    app = _app()
    first = PathenaMainWindow(api_controller=None)
    second = PathenaMainWindow(api_controller=None)
    first.show()
    second.show()
    app.processEvents()

    try:
        first.prompt_input.setText("first-window-marker")
        second.prompt_input.setText("second-window-marker")
        app.processEvents()

        first_sample = first.ascii_panel._semantic_snapshot()
        second_sample = second.ascii_panel._semantic_snapshot()

        assert "first-window-marker" in first_sample
        assert "second-window-marker" not in first_sample
        assert "second-window-marker" in second_sample
        assert "first-window-marker" not in second_sample
    finally:
        first.close()
        second.close()
        app.processEvents()
