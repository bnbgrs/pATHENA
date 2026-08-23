from __future__ import annotations

import pytest

pathena_theme = pytest.importorskip(
    "athena.desktop.pathena_theme",
    reason="pATHENA desktop presentation tests require the optional desktop dependency",
)
pathena_window = pytest.importorskip(
    "athena.desktop.pathena_window",
    reason="pATHENA desktop presentation tests require the optional desktop dependency",
)
base_window = pytest.importorskip(
    "athena.desktop.window",
    reason="pATHENA desktop presentation tests require the optional desktop dependency",
)


def test_pathena_window_is_presentation_only_subclass() -> None:
    assert issubclass(pathena_window.PathenaMainWindow, base_window.AthenaMainWindow)


def test_pathena_theme_layers_on_existing_desktop_theme() -> None:
    stylesheet = pathena_theme.PATHENA_STYLESHEET

    assert "QFrame#rail" in stylesheet
    assert "QListWidget#navigation::item:selected" in stylesheet
    assert "QPushButton#sendButton" in stylesheet
    assert "border-right: 1px solid #262b30" in stylesheet


def test_pathena_shell_keeps_all_primary_workspaces_visible() -> None:
    assert pathena_window._DISPLAY_NAVIGATION == (
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Files",
        "System",
        "Settings",
    )
