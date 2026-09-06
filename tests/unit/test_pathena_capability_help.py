from __future__ import annotations

import os
from dataclasses import dataclass

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from athena.desktop.app import create_application
from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_catalog import (
    CAPABILITY_CATALOG_VERSION,
    CAPABILITY_METADATA,
    CapabilityAvailability,
    resolve_capability_catalog,
)
from athena.desktop.pathena_capability_help import install_capability_help
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-capability-help-test"])


def _surface() -> tuple[QApplication, PathenaMainWindow, CommandPaletteController]:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    palette = CommandPaletteController(window)
    return app, window, palette


def test_versioned_metadata_exactly_covers_the_live_command_catalogue() -> None:
    app, window, palette = _surface()
    try:
        snapshot = resolve_capability_catalog(window, palette._commands)
        live_labels = {command.label for command in palette._commands}

        assert set(CAPABILITY_METADATA) == live_labels
        assert snapshot.version == CAPABILITY_CATALOG_VERSION
        assert snapshot.has_drift is False
        assert len(snapshot.capabilities) == len(palette._commands)
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_help_is_rendered_from_live_commands_and_reports_missing_surfaces() -> None:
    app, window, palette = _surface()
    controller = install_capability_help(palette)
    try:
        snapshot = controller.snapshot()
        knowledge = next(
            item for item in snapshot.capabilities if item.label == "Browse canonical Knowledge"
        )
        assert knowledge.availability is CapabilityAvailability.UNAVAILABLE
        assert "target surface is not installed" in knowledge.explanation

        rendered = controller.render()
        assert rendered.startswith("pATHENA capabilities\n")
        assert f"Catalogue {CAPABILITY_CATALOG_VERSION}" in rendered
        assert f"{len(palette._commands)} live commands" in rendered
        assert "Browse canonical Knowledge · unavailable" in rendered
        assert "Open Chat · available" in rendered
        assert "Catalogue drift" not in rendered
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_help_disambiguates_ctrl_enter_for_chat_and_pallas() -> None:
    app, window, palette = _surface()
    controller = install_capability_help(palette)
    try:
        rendered = controller.render()

        assert "Ctrl+Enter   Send message from the Chat composer" in rendered
        assert (
            "Ctrl+Enter   Open full PALLAS while its semantic canvas is focused" in rendered
        )
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_disabled_real_control_is_context_required_with_existing_reason() -> None:
    app, window, palette = _surface()
    controller = install_capability_help(palette)
    try:
        window.new_chat_button.setEnabled(False)
        window.new_chat_button.setProperty(
            "pathenaEnablementReason",
            "A chat operation is still running.",
        )
        snapshot = controller.snapshot()
        capability = next(
            item for item in snapshot.capabilities if item.label == "New conversation"
        )

        assert capability.availability is CapabilityAvailability.CONTEXT_REQUIRED
        assert capability.explanation == "A chat operation is still running."
        assert "New conversation · context required" in controller.render()
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()


@dataclass(frozen=True)
class _UnknownCommand:
    label: str


def test_catalogue_drift_is_explicit_and_never_lists_stale_metadata_as_live() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        snapshot = resolve_capability_catalog(window, (_UnknownCommand("New live action"),))

        assert snapshot.has_drift is True
        assert snapshot.undocumented_live_commands == ("New live action",)
        assert "Open Chat" in snapshot.stale_metadata
        assert [item.label for item in snapshot.capabilities] == ["New live action"]
        assert snapshot.capabilities[0].documented is False
        assert snapshot.capabilities[0].availability is CapabilityAvailability.UNAVAILABLE
        assert "not verified" in snapshot.capabilities[0].explanation
    finally:
        window.close()
        app.processEvents()


def test_rendered_help_exposes_undocumented_live_command_as_unverified_drift() -> None:
    app, window, palette = _surface()
    palette._commands = (*palette._commands, _UnknownCommand("New live action"))  # type: ignore[assignment]
    controller = install_capability_help(palette)
    try:
        rendered = controller.render()

        assert "New live action · unavailable" in rendered
        assert "Availability is not verified" in rendered
        assert "Catalogue drift" in rendered
        assert "Undocumented live commands: New live action" in rendered
        assert palette.help_text.property("pathenaCapabilityCatalogDrift") is True
        assert palette.help_text.property("pathenaUiState") == "error"
    finally:
        palette.deleteLater()
        window.close()
        app.processEvents()


def test_open_help_re_resolves_runtime_state_and_publishes_accessible_metadata() -> None:
    app, window, palette = _surface()
    install_capability_help(palette)
    try:
        window.show()
        app.processEvents()
        window.new_chat_button.setEnabled(False)
        palette.open_help()
        app.processEvents()

        assert palette.help_dialog.isVisible()
        assert "New conversation · context required" in palette.help_text.toPlainText()
        assert palette.help_text.property("pathenaCapabilityCatalogVersion") == (
            CAPABILITY_CATALOG_VERSION
        )
        assert palette.help_text.property("pathenaCapabilityCatalogDrift") is False
        assert "live commands" in palette.help_text.accessibleDescription()
    finally:
        palette.help_dialog.hide()
        palette.deleteLater()
        window.close()
        app.processEvents()
