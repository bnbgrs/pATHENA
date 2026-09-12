"""Capability-derived HELP surface for the pATHENA desktop command palette."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from PySide6.QtCore import QEvent, QObject, QSize, Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)

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
        self._saved_inspector_state: tuple[str, str, str] | None = None
        self._saved_inspector_overlay_visible: bool | None = None
        palette.__dict__["_render_help_text"] = self.render
        self._host_help_in_shell()
        self._build_help_hierarchy()
        self._publish_state(self.snapshot())

    def _workspace_host(self) -> QFrame | None:
        """Return the real central workspace frame used by the reference shell."""
        return self.window.findChild(QFrame, "conversation")

    def _host_help_in_shell(self) -> None:
        """Host HELP in the workspace body without adding a primary page."""
        help_surface = self.palette.help_dialog
        help_surface.hide()
        workspace = self._workspace_host()
        if workspace is None:
            return
        help_surface.setParent(workspace)
        help_surface.setWindowFlags(Qt.WindowType.Widget)
        help_surface.setObjectName("helpWorkspace")
        help_surface.setAccessibleName("pATHENA help workspace")
        help_surface.setAccessibleDescription(
            "Read-only capability guide hosted in the current pATHENA workspace body."
        )
        help_surface.setProperty("pathenaShellHosted", True)
        help_surface.installEventFilter(self)
        workspace.installEventFilter(self)

    def _build_help_hierarchy(self) -> None:
        """Replace the flat visual guide with a searchable, capability-derived hierarchy."""
        surface_layout = self.palette.help_dialog.layout()
        if not isinstance(surface_layout, QVBoxLayout):
            return

        for name in ("helpDialogTitle", "helpDialogIntro"):
            widget = self.palette.help_dialog.findChild(QLabel, name)
            if widget is not None:
                widget.hide()
        self.palette.help_text.hide()

        self.help_body = QFrame(self.palette.help_dialog)
        self.help_body.setObjectName("helpBody")
        body_layout = QHBoxLayout(self.help_body)
        body_layout.setContentsMargins(0, 2, 0, 2)
        body_layout.setSpacing(24)

        navigation = QFrame(self.help_body)
        navigation.setObjectName("helpSecondaryNavigation")
        navigation.setFixedWidth(184)
        navigation_layout = QVBoxLayout(navigation)
        navigation_layout.setContentsMargins(0, 0, 0, 0)
        navigation_layout.setSpacing(10)
        navigation_title = QLabel("Help", navigation)
        navigation_title.setObjectName("helpSecondaryTitle")
        navigation_layout.addWidget(navigation_title)

        self.help_sections = QListWidget(navigation)
        self.help_sections.setObjectName("helpSections")
        self.help_sections.setAccessibleName("Help sections")
        self.help_sections.setAccessibleDescription(
            "Filter the live capability guide by capability area."
        )
        self.help_sections.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        navigation_layout.addWidget(self.help_sections, 1)

        content = QFrame(self.help_body)
        content.setObjectName("helpCapabilityContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        headline = QLabel("What can pATHENA do?", content)
        headline.setObjectName("helpHeadline")
        content_layout.addWidget(headline)

        self.help_query = QLineEdit(content)
        self.help_query.setObjectName("helpSearch")
        self.help_query.setPlaceholderText("Search help…")
        self.help_query.setAccessibleName("Search help")
        self.help_query.setAccessibleDescription(
            "Filter the live pATHENA capabilities shown below."
        )
        content_layout.addWidget(self.help_query)

        self.help_summary = QLabel(content)
        self.help_summary.setObjectName("helpSummary")
        self.help_summary.setWordWrap(True)
        content_layout.addWidget(self.help_summary)

        self.help_capabilities = QListWidget(content)
        self.help_capabilities.setObjectName("helpCapabilities")
        self.help_capabilities.setAccessibleName("Live capabilities")
        self.help_capabilities.setAccessibleDescription(
            "Read-only capabilities generated from commands installed in this desktop."
        )
        self.help_capabilities.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.help_capabilities.setSpacing(6)
        content_layout.addWidget(self.help_capabilities, 1)

        body_layout.addWidget(navigation)
        body_layout.addWidget(content, 1)

        insert_at = surface_layout.indexOf(self.palette.help_text)
        if insert_at < 0:
            insert_at = max(0, surface_layout.count() - 1)
        surface_layout.insertWidget(insert_at, self.help_body, 1)

        self.help_query.textChanged.connect(self._apply_help_filter)
        self.help_sections.currentRowChanged.connect(self._apply_help_filter)
        self._refresh_hierarchy(self.snapshot())

    def _build_capability_row(self, capability: ResolvedCapability) -> QFrame:
        """Build one spacious read-only row from a resolved live capability."""
        state = capability.availability.value
        row = QFrame(self.help_capabilities)
        row.setObjectName("helpCapabilityRow")
        row.setProperty("pathenaCapabilityAvailability", state)
        row.setMinimumHeight(76)
        row.setAccessibleName(capability.label)
        row.setAccessibleDescription(
            f"{capability.summary} Availability: {state.replace('_', ' ')}."
        )

        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(14, 10, 14, 10)
        row_layout.setSpacing(5)

        title_line = QHBoxLayout()
        title_line.setContentsMargins(0, 0, 0, 0)
        title_line.setSpacing(12)

        title = QLabel(capability.label, row)
        title.setObjectName("helpCapabilityTitle")
        title_font = title.font()
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAccessibleName(capability.label)
        title_line.addWidget(title, 1)

        availability = QLabel(state.replace("_", " ").upper(), row)
        availability.setObjectName("helpCapabilityState")
        availability.setProperty("pathenaUiState", state)
        availability.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        availability.setAccessibleName(
            f"Availability: {state.replace('_', ' ')}"
        )
        title_line.addWidget(availability)
        row_layout.addLayout(title_line)

        summary = QLabel(capability.summary, row)
        summary.setObjectName("helpCapabilitySummary")
        summary.setWordWrap(True)
        summary.setAccessibleName(f"{capability.label} description")
        row_layout.addWidget(summary)
        return row

    def _fit_help_surface_to_workspace(self) -> None:
        help_surface = self.palette.help_dialog
        workspace = self._workspace_host()
        if workspace is None or help_surface.parent() is not workspace:
            return
        help_surface.setGeometry(workspace.rect())
        help_surface.raise_()

    def _focus_help_search(self) -> None:
        if self.palette.help_dialog.isVisible():
            self.help_query.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.palette.help_dialog:
            if event.type() == QEvent.Type.Show:
                self._fit_help_surface_to_workspace()
                snapshot = self.snapshot()
                self._refresh_hierarchy(snapshot)
                self._publish_help_inspector(snapshot)
                self.window.page_title.setText("Help")
                self.window.page_title.setAccessibleDescription("Current workspace: Help.")
                self.window.setProperty("pathenaHelpWorkspaceVisible", True)
                QTimer.singleShot(0, self._focus_help_search)
            elif event.type() == QEvent.Type.Hide:
                self._restore_inspector()
                sync_navigation = getattr(self.window, "_sync_reference_navigation", None)
                if callable(sync_navigation):
                    sync_navigation(self.window.navigation.currentRow())
                self.window.setProperty("pathenaHelpWorkspaceVisible", False)
        elif watched is self._workspace_host() and event.type() == QEvent.Type.Resize:
            if self.palette.help_dialog.isVisible():
                self._fit_help_surface_to_workspace()
        return super().eventFilter(watched, event)

    def snapshot(self) -> CapabilityCatalogSnapshot:
        return resolve_capability_catalog(self.window, self.palette._commands)

    def _refresh_hierarchy(self, snapshot: CapabilityCatalogSnapshot) -> None:
        current_section = self.help_sections.currentItem()
        current_text = current_section.text() if current_section is not None else "All"
        areas = sorted({capability.area for capability in snapshot.capabilities})

        self.help_sections.blockSignals(True)
        self.help_sections.clear()
        self.help_sections.addItem("All")
        for area in areas:
            self.help_sections.addItem(area)
        matches = self.help_sections.findItems(
            current_text,
            Qt.MatchFlag.MatchExactly,
        )
        self.help_sections.setCurrentItem(matches[0] if matches else self.help_sections.item(0))
        self.help_sections.blockSignals(False)

        self.help_capabilities.clear()
        for capability in snapshot.capabilities:
            state = capability.availability.value
            item = QListWidgetItem(
                f"{capability.label}\n{capability.summary}  ·  {state}"
            )
            item.setData(Qt.ItemDataRole.UserRole, capability.area)
            item.setData(
                Qt.ItemDataRole.UserRole + 1,
                " ".join(
                    (
                        capability.label,
                        capability.summary,
                        capability.area,
                        capability.explanation,
                        state,
                    )
                ).casefold(),
            )
            item.setToolTip(
                capability.summary if state == "available" else capability.explanation
            )
            self.help_capabilities.addItem(item)
            row = self._build_capability_row(capability)
            item.setSizeHint(QSize(0, max(76, row.sizeHint().height())))
            self.help_capabilities.setItemWidget(item, row)

        self.help_summary.setText(
            f"{len(snapshot.capabilities)} live commands · Catalogue {snapshot.version} · "
            f"schema {CAPABILITY_SCHEMA_VERSION}"
        )
        self._apply_help_filter()

    def _apply_help_filter(self, *_args: object) -> None:
        query = self.help_query.text().strip().casefold()
        selected = self.help_sections.currentItem()
        area = selected.text() if selected is not None else "All"
        visible = 0
        for index in range(self.help_capabilities.count()):
            item = self.help_capabilities.item(index)
            item_area = str(item.data(Qt.ItemDataRole.UserRole))
            search_text = str(item.data(Qt.ItemDataRole.UserRole + 1))
            matches = (area == "All" or item_area == area) and (
                not query or query in search_text
            )
            item.setHidden(not matches)
            if matches:
                visible += 1
        self.help_capabilities.setAccessibleDescription(
            f"{visible} visible live capabilities. Read-only; filter with the help search."
        )

    def _publish_help_inspector(self, snapshot: CapabilityCatalogSnapshot) -> None:
        if self._saved_inspector_state is None:
            self._saved_inspector_state = (
                self.window.inspector_object_id.text(),
                self.window.inspector_heading.text(),
                self.window.inspector_provenance.text(),
            )
        route_overlay = self.window.findChild(QFrame, "inspectorRouteContext")
        if route_overlay is not None:
            if self._saved_inspector_overlay_visible is None:
                self._saved_inspector_overlay_visible = route_overlay.isVisible()
            route_overlay.hide()
        available = sum(
            capability.availability.value == "available"
            for capability in snapshot.capabilities
        )
        self.window.inspector_object_id.setText("HELP / LIVE")
        self.window.inspector_heading.setText("Quick shortcuts")
        self.window.inspector_provenance.setText(
            "Ctrl K   Command palette\n"
            "F1       Help\n"
            "Esc      Close help\n\n"
            f"{available} of {len(snapshot.capabilities)} commands currently available.\n"
            f"Catalogue {snapshot.version} · generated from active capabilities."
        )
        self.window.inspector_provenance.setAccessibleDescription(
            "Installed help shortcuts and live capability catalogue status."
        )

    def _restore_inspector(self) -> None:
        if self._saved_inspector_state is None:
            return
        object_id, heading, provenance = self._saved_inspector_state
        self.window.inspector_object_id.setText(object_id)
        self.window.inspector_heading.setText(heading)
        self.window.inspector_provenance.setText(provenance)
        route_overlay = self.window.findChild(QFrame, "inspectorRouteContext")
        if route_overlay is not None and self._saved_inspector_overlay_visible is not None:
            route_overlay.setVisible(self._saved_inspector_overlay_visible)
            if self._saved_inspector_overlay_visible:
                route_overlay.raise_()
        self._saved_inspector_state = None
        self._saved_inspector_overlay_visible = None

    def render(self) -> str:
        snapshot = self.snapshot()
        self._publish_state(snapshot)
        self._refresh_hierarchy(snapshot)
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
