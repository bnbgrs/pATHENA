from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget

from athena.desktop.pathena_cancellation_comprehension_5900 import (
    CancellationComprehensionController,
    CancellationTarget,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


class _Workspace(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._operation = ""
        self._selected_state: str | None = None
        self.jobs = QListWidget(self)


def _register(workspace: _Workspace) -> tuple[CancellationComprehensionController, QWidget]:
    window = QWidget()
    surface = QWidget(workspace)
    target = CancellationTarget("jobsWorkspace", "status", "Jobs status")
    controller = CancellationComprehensionController(window)
    controller.register(workspace, surface, target)
    return controller, surface


def test_cancel_operation_is_requesting_not_terminal() -> None:
    _app()
    workspace = _Workspace()
    workspace._operation = "cancel"
    workspace._selected_state = "running"
    controller, surface = _register(workspace)

    controller.sync()

    assert surface.property("pathenaCancellationPhase") == "requesting"
    assert surface.property("pathenaCancellationRequestPending") is True
    assert surface.property("pathenaCancellationTerminal") is False


def test_cancel_requested_remains_pending_not_cancelled() -> None:
    _app()
    workspace = _Workspace()
    workspace._selected_state = "cancel_requested"
    controller, surface = _register(workspace)

    controller.sync()

    assert surface.property("pathenaCancellationPhase") == "requested"
    assert surface.property("pathenaCancellationRequestPending") is True
    assert surface.property("pathenaCancellationTerminal") is False
    assert "terminal cancellation is still pending" in surface.accessibleDescription()


def test_cancelled_is_terminal() -> None:
    _app()
    workspace = _Workspace()
    workspace._selected_state = "cancelled"
    controller, surface = _register(workspace)

    controller.sync()

    assert surface.property("pathenaCancellationPhase") == "cancelled"
    assert surface.property("pathenaCancellationRequestPending") is False
    assert surface.property("pathenaCancellationTerminal") is True


def test_research_style_list_text_can_supply_selected_state() -> None:
    _app()
    workspace = _Workspace()
    workspace._selected_state = None
    item = QListWidgetItem("CANCEL_REQUESTED   72.0%  Research question")
    workspace.jobs.addItem(item)
    workspace.jobs.setCurrentItem(item)
    controller, surface = _register(workspace)

    controller.sync()

    assert surface.property("pathenaCancellationSelectedState") == "cancel_requested"
    assert surface.property("pathenaCancellationPhase") == "requested"
