from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.layout_state import DesktopLayoutStateController


def _app() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication(["pathena-layout-state-test"])


def _settings(path: Path) -> QSettings:
    return QSettings(str(path), QSettings.Format.IniFormat)


def _window() -> tuple[QMainWindow, list[QSplitter]]:
    window = QMainWindow()
    window.setObjectName("athenaMainWindow")
    window.resize(1000, 720)

    root = QWidget(window)
    layout = QVBoxLayout(root)
    splitters: list[QSplitter] = []

    research = QWidget(root)
    research.setObjectName("researchWorkspace")
    research_layout = QVBoxLayout(research)
    research_splitter = QSplitter(research)
    research_splitter.addWidget(QLabel("Research list"))
    research_splitter.addWidget(QLabel("Research detail"))
    research_layout.addWidget(research_splitter)
    layout.addWidget(research)
    splitters.append(research_splitter)

    knowledge = QWidget(root)
    knowledge.setObjectName("knowledgeWorkspace")
    knowledge_layout = QVBoxLayout(knowledge)
    for label in ("Knowledge", "Claims", "Reviews"):
        splitter = QSplitter(knowledge)
        splitter.setObjectName("canonicalMemorySplit")
        splitter.addWidget(QLabel(f"{label} list"))
        splitter.addWidget(QLabel(f"{label} detail"))
        knowledge_layout.addWidget(splitter)
        splitters.append(splitter)
    layout.addWidget(knowledge)

    window.setCentralWidget(root)
    return window, splitters


def _show(window: QMainWindow) -> QApplication:
    app = _app()
    window.show()
    app.processEvents()
    return app


def test_layout_state_round_trip_restores_window_and_splitters(tmp_path: Path) -> None:
    first, first_splitters = _window()
    app = _show(first)
    first.move(80, 110)
    first.resize(1120, 760)
    expected_sizes = ([180, 700], [220, 660], [260, 620], [300, 580])
    for splitter, sizes in zip(first_splitters, expected_sizes, strict=True):
        splitter.setSizes(sizes)
    app.processEvents()

    expected_geometry = first.saveGeometry()
    expected_states = tuple(splitter.saveState() for splitter in first_splitters)

    settings_path = tmp_path / "layout.ini"
    saver = DesktopLayoutStateController(first, settings=_settings(settings_path))
    saver.save()
    first.close()
    app.processEvents()

    second, second_splitters = _window()
    _show(second)
    second.move(300, 320)
    second.resize(760, 540)
    for splitter in second_splitters:
        splitter.setSizes([700, 180])
    app.processEvents()

    restorer = DesktopLayoutStateController(second, settings=_settings(settings_path))
    restorer.restore()
    app.processEvents()

    try:
        assert second.saveGeometry() == expected_geometry
        assert tuple(splitter.saveState() for splitter in second_splitters) == expected_states
    finally:
        second.close()
        app.processEvents()


def test_duplicate_named_knowledge_splitters_keep_independent_state(tmp_path: Path) -> None:
    first, first_splitters = _window()
    app = _show(first)
    knowledge_splitters = first_splitters[1:]
    for splitter, sizes in zip(
        knowledge_splitters,
        ([120, 760], [320, 560], [520, 360]),
        strict=True,
    ):
        splitter.setSizes(sizes)
    app.processEvents()
    expected = tuple(splitter.saveState() for splitter in knowledge_splitters)

    settings_path = tmp_path / "duplicate-splitters.ini"
    DesktopLayoutStateController(first, settings=_settings(settings_path)).save()
    first.close()
    app.processEvents()

    second, second_splitters = _window()
    _show(second)
    for splitter in second_splitters[1:]:
        splitter.setSizes([440, 440])
    app.processEvents()

    DesktopLayoutStateController(second, settings=_settings(settings_path)).restore()
    app.processEvents()

    try:
        assert tuple(splitter.saveState() for splitter in second_splitters[1:]) == expected
    finally:
        second.close()
        app.processEvents()


def test_corrupt_or_incompatible_layout_state_is_ignored(tmp_path: Path) -> None:
    window, splitters = _window()
    app = _show(window)
    window.move(140, 160)
    window.resize(900, 620)
    splitters[0].setSizes([250, 550])
    app.processEvents()
    baseline_geometry = window.saveGeometry()
    baseline_splitter = splitters[0].saveState()

    settings = _settings(tmp_path / "corrupt-layout.ini")
    controller = DesktopLayoutStateController(window, settings=settings)
    identity = controller._splitter_entries()[0].identity

    settings.beginGroup("desktop/layout/v1")
    settings.setValue("version", 1)
    settings.setValue("window_geometry", QByteArray(b"not-a-window-geometry"))
    settings.setValue("splitters/count", 1)
    settings.setValue("splitters/0/identity", identity)
    settings.setValue("splitters/0/state", QByteArray(b"not-a-splitter-state"))
    settings.endGroup()
    settings.sync()

    controller.restore()
    app.processEvents()

    try:
        assert window.saveGeometry() == baseline_geometry
        assert splitters[0].saveState() == baseline_splitter
    finally:
        window.close()
        app.processEvents()

    incompatible, incompatible_splitters = _window()
    _show(incompatible)
    incompatible_splitters[0].setSizes([330, 470])
    app.processEvents()
    incompatible_geometry = incompatible.saveGeometry()
    incompatible_state = incompatible_splitters[0].saveState()

    versioned = _settings(tmp_path / "future-layout.ini")
    versioned.beginGroup("desktop/layout/v1")
    versioned.setValue("version", 999)
    versioned.setValue("window_geometry", QByteArray(b"future"))
    versioned.setValue("splitters/count", 0)
    versioned.endGroup()
    versioned.sync()

    DesktopLayoutStateController(incompatible, settings=versioned).restore()
    app.processEvents()

    try:
        assert incompatible.saveGeometry() == incompatible_geometry
        assert incompatible_splitters[0].saveState() == incompatible_state
    finally:
        incompatible.close()
        app.processEvents()
