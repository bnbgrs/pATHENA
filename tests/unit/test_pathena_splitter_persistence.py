from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QByteArray, QSettings
from PySide6.QtWidgets import QApplication, QLabel, QSplitter, QVBoxLayout, QWidget

from athena.desktop.pathena_splitter_persistence import (
    SplitterPersistenceController,
    install_splitter_persistence,
)


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def _settings(path: Path) -> QSettings:
    return QSettings(str(path), QSettings.Format.IniFormat)


def _root_with_splitter(
    *,
    key: str,
) -> tuple[QWidget, QSplitter]:
    root = QWidget()
    root.resize(900, 500)
    layout = QVBoxLayout(root)
    splitter = QSplitter()
    splitter.setProperty("pathenaSplitterPersistenceKey", key)
    splitter.addWidget(QLabel("left"))
    splitter.addWidget(QLabel("right"))
    layout.addWidget(splitter)
    root.show()
    _app().processEvents()
    return root, splitter


def test_splitter_geometry_round_trips_through_versioned_qsettings(
    tmp_path: Path,
) -> None:
    app = _app()
    settings = _settings(tmp_path / "splitters.ini")
    first_root, first = _root_with_splitter(key="research-main")
    first_controller = install_splitter_persistence(
        first_root,
        settings=settings,
    )

    try:
        first.setSizes([250, 650])
        first.moveSplitter(280, 1)
        app.processEvents()
        first_controller.dispose()

        settings.beginGroup("desktop/splitters/v1")
        try:
            stored = settings.value("research-main")
        finally:
            settings.endGroup()
        assert isinstance(stored, QByteArray)
        assert not stored.isEmpty()

        second_root, second = _root_with_splitter(key="research-main")
        try:
            second_controller = install_splitter_persistence(
                second_root,
                settings=settings,
            )
            app.processEvents()

            assert second_controller.keys == ("research-main",)
            assert second.saveState() == stored
            assert second_root.property("pathenaSplitterPersistenceEnabled") is True
            assert second_root.property("pathenaSplitterPersistenceCount") == 1
            second_controller.dispose()
        finally:
            second_root.close()
    finally:
        first_root.close()
        settings.clear()
        settings.sync()


def test_invalid_splitter_state_is_ignored_without_replacing_defaults(
    tmp_path: Path,
) -> None:
    _app()
    settings = _settings(tmp_path / "invalid.ini")
    settings.beginGroup("desktop/splitters/v1")
    try:
        settings.setValue("jobs-main", "not-a-qbytearray")
    finally:
        settings.endGroup()
    settings.sync()

    root, splitter = _root_with_splitter(key="jobs-main")
    before = splitter.saveState()
    controller = SplitterPersistenceController(root, settings=settings)

    try:
        assert splitter.saveState() == before
        assert controller.keys == ("jobs-main",)
    finally:
        controller.dispose()
        root.close()


def test_duplicate_persistence_keys_fail_closed(tmp_path: Path) -> None:
    _app()
    settings = _settings(tmp_path / "duplicate.ini")
    root = QWidget()
    layout = QVBoxLayout(root)
    for _index in range(2):
        splitter = QSplitter()
        splitter.setProperty("pathenaSplitterPersistenceKey", "duplicate")
        splitter.addWidget(QLabel("left"))
        splitter.addWidget(QLabel("right"))
        layout.addWidget(splitter)

    with pytest.raises(RuntimeError, match="Duplicate persistent splitter key"):
        SplitterPersistenceController(root, settings=settings)

    root.close()
