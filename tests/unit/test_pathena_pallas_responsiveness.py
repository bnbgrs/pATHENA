from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QWidget

from athena.desktop.pathena_pallas_responsiveness_5000 import (
    PallasResponsivenessController,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _window() -> tuple[QWidget, QWidget]:
    window = QWidget()
    pallas = QWidget(window)
    pallas.setObjectName("pallasVisualPlaceholder")
    return window, pallas


def test_pallas_keeps_nine_by_sixteen_ratio_and_secondary_role() -> None:
    _app()
    window, pallas = _window()
    window.resize(1660, 980)

    controller = PallasResponsivenessController(window)

    assert pallas.width() == 112
    assert pallas.height() == 199
    assert pallas.property("pathenaPallasAspectRatio") == "9:16"
    assert pallas.property("pathenaPallasProminence") == "secondary"
    assert not pallas.isHidden()
    assert controller.parent() is window


def test_compact_layout_reduces_pallas_without_hiding_it() -> None:
    _app()
    window, pallas = _window()
    window.resize(1400, 900)

    controller = PallasResponsivenessController(window)

    assert pallas.width() == 96
    assert pallas.height() == 171
    assert pallas.property("pathenaPallasMode") == "compact"
    assert not pallas.isHidden()

    window.setProperty("pathenaLayoutMode", "regular")
    controller.sync()

    assert pallas.width() == 112
    assert pallas.height() == 199
    assert pallas.property("pathenaPallasMode") == "regular"
