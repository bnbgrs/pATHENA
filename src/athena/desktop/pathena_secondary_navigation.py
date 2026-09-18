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

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SHELL, SPACE, TYPE
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
        sections = [SecondarySection("model", "Models & inference", model_target)]
        if runtime_target is not None:
            sections.append(SecondarySection("runtime", "System status", runtime_target))
        self.sections = tuple(sections)
        self.runtime_target = runtime_target

        self.navigation = QListWidget()
        self.navigation.setObjectName("settingsSecondaryNavigation")
        self.navigation.setProperty("referenceFamily", "11-screen-2026-08-24")
        self.navigation.setAccessibleName("Settings sections")
        self.navigation.setAccessibleDescription(
            "Navigate between the Settings sections implemented in this desktop"
        )
        self.navigation.setFixedWidth(SHELL.secondary_nav_width)
        self.navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navigation.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.navigation.setStyleSheet(
            f"""
            QListWidget#settingsSecondaryNavigation {{
                background: {PALETTE.surface};
                border: 0;
                border-right: 1px solid {PALETTE.border};
                border-radius: 0;
                padding: {SPACE.md}px {SPACE.sm}px;
                color: {PALETTE.text_subtle};
                outline: 0;
            }}
            QListWidget#settingsSecondaryNavigation::item {{
                min-height: 34px;
                padding: 0 10px;
                border-radius: 3px;
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
            nav_item.setSizeHint(QSize(SHELL.secondary_nav_width - 24, 36))
            self.navigation.addItem(nav_item)

        self.content = QWidget()
        self.content.setObjectName("settingsSecondaryContent")
        self.content.setStyleSheet(
            f"""
            QWidget#settingsSecondaryContent {{
                background: {PALETTE.canvas};
            }}
            """
        )
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(SPACE.xl, SPACE.sm, SPACE.lg, SPACE.xl)
        content_layout.setSpacing(SPACE.md)
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

        self.status_panel: QFrame | None = None
        if runtime_target is not None:
            self.status_panel = QFrame()
            self.status_panel.setObjectName("settingsStatusPanel")
            self.status_panel.setAccessibleName("System status")
            self.status_panel.setFixedWidth(SHELL.inspector_width)
            self.status_panel.setStyleSheet(
                f"""
                QFrame#settingsStatusPanel {{
                    background: {PALETTE.surface};
                    border: 0;
                    border-left: 1px solid {PALETTE.border};
                }}
                QLabel#settingsStatusTitle {{
                    color: {PALETTE.text};
                    font-family: {TYPE.display_family};
                    font-size: {TYPE.section_px}px;
                    font-weight: 500;
                }}
                QWidget#settingsRuntimePanel {{
                    background: {PALETTE.surface_raised};
                    border: 1px solid {PALETTE.border};
                    border-radius: {RADII.panel}px;
                    color: {PALETTE.text_muted};
                }}
                QWidget#settingsRuntimePanel QLabel {{
                    background: transparent;
                }}
                """
            )
            status_layout = QVBoxLayout(self.status_panel)
            status_layout.setContentsMargins(SPACE.lg, SPACE.lg, SPACE.lg, SPACE.xl)
            status_layout.setSpacing(SPACE.md)
            status_title = QLabel("System status")
            status_title.setObjectName("settingsStatusTitle")
            status_layout.addWidget(status_title)
            status_layout.addWidget(runtime_target)
            status_layout.addStretch(1)

        self.container = QFrame()
        self.container.setObjectName("settingsSecondaryContainer")
        self.container.setProperty("referenceFamily", "11-screen-2026-08-24")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.navigation)
        container_layout.addWidget(self.scroll, 1)
        if self.status_panel is not None:
            container_layout.addWidget(self.status_panel)
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
        if section.key == "model":
            self.scroll.ensureWidgetVisible(section.target, 24, 36)
        elif section.key == "runtime" and self.status_panel is not None:
            self.status_panel.setAccessibleDescription("Selected section: System status")
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
