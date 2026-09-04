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
pathena_design_tokens = pytest.importorskip(
    "athena.desktop.pathena_design_tokens",
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
    assert f"border-right: 1px solid {pathena_design_tokens.PALETTE.border}" in stylesheet


def test_pathena_shell_keeps_all_primary_workspaces_visible() -> None:
    assert pathena_window._DISPLAY_NAVIGATION == (
        "Workspace",
        "Library",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    )
