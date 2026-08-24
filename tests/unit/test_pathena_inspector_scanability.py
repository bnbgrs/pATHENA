from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy, QWidget

from athena.desktop.pathena_inspector_scanability_6700 import (
    InspectorScanTarget,
    _harden_label,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_hardened_provenance_yields_to_inspector_width() -> None:
    _app()
    label = QLabel("very-long-provenance-token" * 20)
    target = InspectorScanTarget("inspectorBody", "Inspector provenance", True)

    _harden_label(label, target)

    assert label.minimumWidth() == 0
    assert label.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Ignored
    assert label.wordWrap() is True
    assert label.property("pathenaInspectorFullTextPreserved") is True


def test_hardened_label_preserves_plain_selectable_text() -> None:
    _app()
    text = "ctx-1234567890 source-name evidence excerpt"
    label = QLabel(text)
    target = InspectorScanTarget("chainState", "Evidence chain summary", True)

    _harden_label(label, target)

    assert label.text() == text
    assert label.textFormat() == Qt.TextFormat.PlainText
    flags = label.textInteractionFlags()
    assert flags & Qt.TextInteractionFlag.TextSelectableByMouse
    assert flags & Qt.TextInteractionFlag.TextSelectableByKeyboard


def test_scan_role_is_diagnostic_only() -> None:
    _app()
    label = QLabel("Grounded provenance")
    target = InspectorScanTarget("inspectorBody", "Inspector provenance", True)

    _harden_label(label, target)

    assert label.property("pathenaInspectorScanRole") == "inspector provenance"
    assert "Full text is preserved" in label.accessibleDescription()


def test_hardening_does_not_change_parent_geometry_contract() -> None:
    _app()
    parent = QWidget()
    parent.setFixedWidth(300)
    label = QLabel("Source " + "x" * 500, parent)
    target = InspectorScanTarget("inspectorBody", "Inspector provenance", True)

    _harden_label(label, target)

    assert parent.minimumWidth() == 300
    assert parent.maximumWidth() == 300
