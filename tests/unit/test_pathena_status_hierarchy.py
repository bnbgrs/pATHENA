from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel, QWidget

from athena.desktop.pathena_status_hierarchy_5300 import StatusHierarchyController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_status_hierarchy_keeps_distinct_primary_and_secondary_visible() -> None:
    _app()
    window = QWidget()
    primary = QLabel("Refreshing durable jobs", window)
    secondary = QLabel("Scheduler active", window)

    controller = StatusHierarchyController(window)
    controller.register(primary, secondary, "Jobs")

    assert primary.property("pathenaStatusPriority") == "primary"
    assert secondary.property("pathenaStatusPriority") == "secondary"
    assert secondary.property("pathenaStatusRedundant") is False
    assert not primary.isHidden()
    assert not secondary.isHidden()


def test_exact_duplicate_secondary_status_is_marked_not_hidden() -> None:
    _app()
    window = QWidget()
    primary = QLabel("Ready", window)
    secondary = QLabel("  READY  ", window)

    controller = StatusHierarchyController(window)
    controller.register(primary, secondary, "Jobs")

    assert secondary.property("pathenaStatusRedundant") is True
    assert not secondary.isHidden()
    assert "Duplicates the primary status" in secondary.accessibleDescription()
