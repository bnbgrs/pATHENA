from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.desktop.pathena_disclosure_consistency_4800 import (
    DisclosureConsistencyController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_toggle_state_is_mirrored_to_disclosure_surface() -> None:
    _app()
    window = QWidget()
    control = QPushButton(window)
    control.setCheckable(True)
    control.setObjectName("detailsToggle")
    surface = QWidget(window)
    surface.setObjectName("inspector")

    controller = DisclosureConsistencyController(window)
    controller.register(control, surface, "Inspector")

    assert control.property("pathenaDisclosureState") == "closed"
    assert surface.property("pathenaDisclosureState") == "closed"
    assert control.toolTip() == "Show inspector"

    control.setChecked(True)

    assert control.property("pathenaDisclosureState") == "open"
    assert surface.property("pathenaDisclosureState") == "open"
    assert control.toolTip() == "Hide inspector"


def test_review_panel_semantics_follow_existing_visibility() -> None:
    _app()
    window = QWidget()
    panel = QWidget(window)
    panel.setObjectName("knowledgeReviewPanel")
    close = QPushButton(window)
    close.setObjectName("knowledgeReviewCloseButton")

    controller = DisclosureConsistencyController(window)
    controller.register_review_panel()

    assert panel.property("pathenaDisclosureState") == "closed"
    assert close.property("pathenaDisclosureState") == "closed"

    window.show()
    panel.show()
    QApplication.processEvents()

    assert panel.property("pathenaDisclosureState") == "open"
    assert close.property("pathenaDisclosureState") == "open"
    assert "without changing decisions" in close.accessibleDescription()
