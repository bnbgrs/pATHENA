"""Capability-derived HELP surface for the pATHENA desktop command palette."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, Qt

from athena.desktop.command_palette import CommandPaletteController
from athena.desktop.pathena_capability_catalog import (
    CAPABILITY_SCHEMA_VERSION,
    CapabilityCatalogSnapshot,
    ResolvedCapability,
    resolve_capability_catalog,
)


class CapabilityHelpController(QObject):
    """Render F1 HELP from live commands and host it inside the pATHENA shell."""

    def __init__(self, palette: CommandPaletteController) -> None:
        super().__init__(palette)
        self.palette = palette
        self.window = palette.window
        self._original_render: Callable[[], str] = palette._render_help_text
        palette.__dict__["_render_help_text"] = self.render
        self._host_help_in_shell()
        self._publish_state(self.snapshot())

    def _host_help_in_shell(self) -> None:
        """Host HELP as a transient shell surface without adding a primary page."""
        help_surface = self.palette.help_dialog
        help_surface.hide()
        shell = self.window.centralWidget()
        if shell is None:
            return
        help_surface.setParent(shell)
        help_surface.setWindowFlags(Qt.WindowType.Widget)
        help_surface.setObjectName("helpWorkspace")
        help_surface.setAccessibleName("pATHENA help workspace")
        help_surface.setAccessibleDescription(
            "Read-only capability guide hosted in the current pATHENA workspace shell."
        )
        help_surface.setProperty("pathenaShellHosted", True)
        help_surface.installEventFilter(self)
        shell.installEventFilter(self)

    def _fit_help_surface_to_shell(self) -> None:
        help_surface = self.palette.help_dialog
        shell = self.window.centralWidget()
        if shell is None or help_surface.parent() is not shell:
            return
        help_surface.setGeometry(shell.rect())
        help_surface.raise_()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.palette.help_dialog:
            if event.type() == QEvent.Type.Show:
                self._fit_help_surface_to_shell()
                self.window.page_title.setText("Help")
                self.window.page_title.setAccessibleDescription("Current workspace: Help.")
                self.window.setProperty("pathenaHelpWorkspaceVisible", True)
            elif event.type() == QEvent.Type.Hide:
                sync_navigation = getattr(self.window, "_sync_reference_navigation", None)
                if callable(sync_navigation):
                    sync_navigation(self.window.navigation.currentRow())
                self.window.setProperty("pathenaHelpWorkspaceVisible", False)
        elif watched is self.window.centralWidget() and event.type() == QEvent.Type.Resize:
            if self.palette.help_dialog.isVisible():
                self._fit_help_surface_to_shell()
        return super().eventFilter(watched, event)

    def snapshot(self) -> CapabilityCatalogSnapshot:
        return resolve_capability_catalog(self.window, self.palette._commands)

    def render(self) -> str:
        snapshot = self.snapshot()
        self._publish_state(snapshot)
        grouped: dict[str, list[ResolvedCapability]] = defaultdict(list)
        for capability in snapshot.capabilities:
            grouped[capability.area].append(capability)

        lines = [
            "pATHENA capabilities",
            f"Catalogue {snapshot.version} · schema {CAPABILITY_SCHEMA_VERSION}",
            f"{len(snapshot.capabilities)} live commands",
            "",
        ]
        for area, capabilities in grouped.items():
            lines.extend((area, ""))
            for capability in capabilities:
                state = capability.availability.value
                lines.append(f"{capability.label} · {state}")
                lines.append(f"  {capability.summary}")
                if state != "available":
                    lines.append(f"  {capability.explanation}")
                lines.append("")

        lines.extend(
            (
                "Keyboard",
                "",
                "Ctrl K       Commands",
                "Ctrl+Enter   Send message",
                "Ctrl+F       Filter canonical memory while Knowledge is active",
                "F1           Help",
                "Esc          Close commands or help",
                "",
                "Availability",
                "",
                "Availability is resolved from the same live command list and target "
                "controls used by this desktop. Context-required actions remain governed "
                "by their existing readiness and safety checks.",
            )
        )
        if snapshot.has_drift:
            lines.extend(("", "Catalogue drift", ""))
            if snapshot.undocumented_live_commands:
                lines.append(
                    "Undocumented live commands: "
                    + ", ".join(snapshot.undocumented_live_commands)
                )
            if snapshot.stale_metadata:
                lines.append(
                    "Metadata without a live command: " + ", ".join(snapshot.stale_metadata)
                )
        return "\n".join(lines)

    def _publish_state(self, snapshot: CapabilityCatalogSnapshot) -> None:
        state = "error" if snapshot.has_drift else "success"
        self.palette.help_text.setProperty("pathenaUiState", state)
        self.palette.help_text.setProperty(
            "pathenaCapabilityCatalogVersion",
            snapshot.version,
        )
        self.palette.help_text.setProperty(
            "pathenaCapabilitySchemaVersion",
            CAPABILITY_SCHEMA_VERSION,
        )
        self.palette.help_text.setProperty(
            "pathenaCapabilityLiveCommandCount",
            len(snapshot.capabilities),
        )
        self.palette.help_text.setProperty(
            "pathenaCapabilityCatalogDrift",
            snapshot.has_drift,
        )
        self.palette.help_text.setAccessibleDescription(
            "Read-only versioned guide generated from the live commands and target "
            "controls installed in this pATHENA desktop."
        )


def install_capability_help(
    palette: CommandPaletteController,
) -> CapabilityHelpController:
    """Install live capability HELP in the existing pATHENA workspace shell."""
    controller = CapabilityHelpController(palette)
    palette.window.setProperty("pathenaCapabilityHelpController", controller)
    palette.window.setProperty("pathenaCapabilityHelpManaged", True)
    return controller
