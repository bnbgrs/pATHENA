"""Reference secondary navigation for existing routed pATHENA settings content."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, QSize, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL
from athena.desktop.pathena_window import PathenaMainWindow


@dataclass(frozen=True, slots=True)
class SecondarySection:
    """One truthful navigation target already present in the Settings page."""

    key: str
    label: str
    target: QWidget


class SettingsSecondaryNavigation(QObject):
    """Wrap existing Settings content with a stable, keyboard-reachable section rail."""

    def __init__(self, window: PathenaMainWindow) -> None:
        super().__init__(window)
        self.window = window
        settings_page = window.pages.widget(6)
        if settings_page is None:
            raise RuntimeError("pATHENA Settings page is unavailable")
        page_layout = settings_page.layout()
        if not isinstance(page_layout, QVBoxLayout):
            raise RuntimeError("pATHENA Settings page has no vertical layout")

        model_target = getattr(window, "context_spin", None)
        if not isinstance(model_target, QWidget):
            raise RuntimeError("pATHENA Settings model controls are unavailable")

        runtime_target = settings_page.findChild(QWidget, "settingsRuntimePanel")
        sections = [SecondarySection("model", "Model & inference", model_target)]
        if runtime_target is not None:
            sections.append(SecondarySection("runtime", "Local runtime", runtime_target))
        self.sections = tuple(sections)

        self.navigation = QListWidget()
        self.navigation.setObjectName("settingsSecondaryNavigation")
        self.navigation.setAccessibleName("Settings sections")
        self.navigation.setAccessibleDescription(
            "Navigate between available Settings sections"
        )
        self.navigation.setFixedWidth(SHELL.secondary_nav_width)
        self.navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigation.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.navigation.setStyleSheet(
            f"""
            QListWidget#settingsSecondaryNavigation {{
                background: transparent;
                border: none;
                padding: 0 8px 8px 8px;
                color: {PALETTE.text_muted};
            }}
            QListWidget#settingsSecondaryNavigation::item {{
                min-height: 42px;
                padding: 0 14px;
                border-radius: 4px;
            }}
            QListWidget#settingsSecondaryNavigation::item:selected {{
                background: {PALETTE.surface_selected};
                color: {PALETTE.text};
                border-left: 2px solid {PALETTE.accent};
            }}
            QListWidget#settingsSecondaryNavigation::item:hover {{
                background: {PALETTE.surface_hover};
                color: {PALETTE.text};
            }}
            """
        )
        for section in self.sections:
            nav_item = QListWidgetItem(section.label)
            nav_item.setData(Qt.ItemDataRole.UserRole, section.key)
            nav_item.setData(Qt.ItemDataRole.AccessibleTextRole, section.label)
            nav_item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                f"Open {section.label} settings",
            )
            nav_item.setToolTip(f"Open {section.label} settings")
            nav_item.setSizeHint(QSize(SHELL.secondary_nav_width - 34, 42))
            self.navigation.addItem(nav_item)

        self.rail = QFrame()
        self.rail.setObjectName("settingsSecondaryRail")
        self.rail.setAccessibleName("Settings navigation")
        self.rail.setFixedWidth(SHELL.secondary_nav_width)
        rail_layout = QVBoxLayout(self.rail)
        rail_layout.setContentsMargins(0, 14, 0, 0)
        rail_layout.setSpacing(8)

        rail_heading = QLabel("Settings")
        rail_heading.setObjectName("settingsSecondaryTitle")
        rail_heading.setAccessibleName("Settings")
        rail_heading.setContentsMargins(16, 0, 8, 4)
        rail_layout.addWidget(rail_heading)
        rail_layout.addWidget(self.navigation, 1)

        self.content = QWidget()
        self.content.setObjectName("settingsSecondaryContent")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(28, 0, 12, 28)
        content_layout.setSpacing(18)
        while page_layout.count():
            layout_item = page_layout.takeAt(0)
            if layout_item is None:
                continue
            widget: QWidget | None = layout_item.widget()
            nested_layout: QLayout | None = layout_item.layout()
            if widget is not None:
                content_layout.addWidget(widget)
            elif nested_layout is not None:
                content_layout.addLayout(nested_layout)
            else:
                content_layout.addItem(layout_item)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("settingsSecondaryScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.content)

        self.container = QFrame()
        self.container.setObjectName("settingsSecondaryContainer")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.rail)
        container_layout.addWidget(self.scroll, 1)
        page_layout.addWidget(self.container, 1)

        self.navigation.currentRowChanged.connect(self._activate_row)
        self.navigation.setCurrentRow(0)
        self._activate_row(0)

    @property
    def section_names(self) -> tuple[str, ...]:
        return tuple(section.label for section in self.sections)

    def _activate_row(self, row: int) -> None:
        if not 0 <= row < len(self.sections):
            return
        section = self.sections[row]
        self.scroll.ensureWidgetVisible(section.target, 24, 36)
        self.navigation.setAccessibleDescription(f"Selected section: {section.label}")


def install_settings_secondary_navigation(
    window: PathenaMainWindow,
) -> SettingsSecondaryNavigation:
    """Install the reference section rail once without inventing Settings capabilities."""
    existing = getattr(window, "_pathena_settings_secondary_navigation", None)
    if isinstance(existing, SettingsSecondaryNavigation):
        return existing

    dynamic_existing = window.property("pathenaSettingsSecondaryNavigation")
    if isinstance(dynamic_existing, SettingsSecondaryNavigation):
        window.__setattr__(
            "_pathena_settings_secondary_navigation",
            dynamic_existing,
        )
        return dynamic_existing

    controller = SettingsSecondaryNavigation(window)
    window.__setattr__("_pathena_settings_secondary_navigation", controller)
    window.setProperty("pathenaSettingsSecondaryNavigation", controller)
    return controller