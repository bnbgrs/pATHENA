from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.pathena_quiet_success_decay_6400 import QuietSuccessDecayController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_success_starts_fresh_without_changing_semantic_state() -> None:
    _app()
    window = QWidget()
    label = QLabel(window)
    label.setProperty("pathenaUiState", "success")
    controller = QuietSuccessDecayController(window)

    controller.register(label, "Status")

    assert label.property("pathenaUiState") == "success"
    assert label.property("pathenaSuccessEmphasis") == "fresh"
    assert label.property("pathenaSuccessDecayPending") is True


def test_decay_quiets_emphasis_but_preserves_success_truth() -> None:
    _app()
    window = QWidget()
    label = QLabel(window)
    label.setProperty("pathenaUiState", "success")
    controller = QuietSuccessDecayController(window)
    controller.register(label, "Status")
    generation = controller._generation[label]

    controller._decay(label, generation)

    assert label.property("pathenaUiState") == "success"
    assert label.property("pathenaSuccessEmphasis") == "quiet"
    assert label.property("pathenaSuccessSemanticsPreserved") is True


def test_state_change_invalidates_pending_decay() -> None:
    _app()
    window = QWidget()
    label = QLabel(window)
    label.setProperty("pathenaUiState", "success")
    controller = QuietSuccessDecayController(window)
    controller.register(label, "Status")
    stale_generation = controller._generation[label]

    label.setProperty("pathenaUiState", "error")
    controller._sync(label)
    controller._decay(label, stale_generation)

    assert label.property("pathenaUiState") == "error"
    assert label.property("pathenaSuccessEmphasis") == "none"


def test_non_success_state_never_gets_success_emphasis() -> None:
    _app()
    window = QWidget()
    label = QLabel(window)
    label.setProperty("pathenaUiState", "busy")
    controller = QuietSuccessDecayController(window)

    controller.register(label, "Status")

    assert label.property("pathenaSuccessEmphasis") == "none"
    assert label.property("pathenaSuccessDecayPending") is False
