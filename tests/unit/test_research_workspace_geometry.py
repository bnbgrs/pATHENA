from __future__ import annotations

import os

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from athena.desktop.research_workspace import ResearchWorkspace


def _app() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    return QApplication.instance() or QApplication([])


def test_research_splitter_geometry_round_trips_through_injected_settings(
    tmp_path,
    monkeypatch,
) -> None:
    app = _app()
    monkeypatch.setattr(ResearchWorkspace, "refresh", lambda self: None)
    settings_path = str(tmp_path / "research-ui.ini")

    first_settings = QSettings(settings_path, QSettings.Format.IniFormat)
    first = ResearchWorkspace(settings=first_settings)
    try:
        first.resize(960, 640)
        first.show()
        app.processEvents()
        first.splitter.setSizes([240, 640])
        first._persist_splitter_state()
        saved_state = bytes(first.splitter.saveState())
        assert saved_state
    finally:
        first.close()

    second_settings = QSettings(settings_path, QSettings.Format.IniFormat)
    second = ResearchWorkspace(settings=second_settings)
    try:
        second.resize(960, 640)
        second.show()
        app.processEvents()
        assert bytes(second.splitter.saveState()) == saved_state
        sizes = second.splitter.sizes()
        assert len(sizes) == 2
        assert sizes[0] > 0
        assert sizes[1] > sizes[0]
    finally:
        second.close()
