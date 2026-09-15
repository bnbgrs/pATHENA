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

from athena.desktop.pathena_design_tokens import PALETTE, RADII, SHELL
from athena.desktop.pathena_window import PathenaMainWindow


@dataclass(frozen=True, slots=True)
class SecondarySection:
    """One truthful navigation target already present in the Settings page."""

    key: str
    label: str
    target: QWidget


class SettingsSecondaryNavigation(QObject):
    """Wrap real Settings content with the three-column reference composition."""

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
        self.runtime_target = runtime_target

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
                background: {PALETTE.surface};
                border: 0;
                border-right: 1px solid {PALETTE.border};
                padding: 8px 12px 8px 0;
                color: {PALETTE.text_muted};
            }}
            QListWidget#settingsSecondaryNavigation::item {{
                min-height: 40px;
                padding: 0 10px;
                border: 0;
                border-left: 2px solid transparent;
                border-radius: {RADII.control}px;
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
            nav_item.setSizeHint(QSize(SHELL.secondary_nav_width - 34, 40))
            self.navigation.addItem(nav_item)

        # Preserve every existing Settings widget. Runtime is separated only at
        # presentation level so the reference's right-hand status column can be
        # built from real snapshot-backed facts rather than fabricated controls.
        moved_items: list[QWidget | QLayout] = []
        while page_layout.count():
            layout_item = page_layout.takeAt(0)
            if layout_item is None:
                continue
            widget = layout_item.widget()
            nested_layout = layout_item.layout()
            if widget is not None:
                moved_items.append(widget)
            elif nested_layout is not None:
                moved_items.append(nested_layout)
            else:
                moved_items.append(layout_item)  # type: ignore[arg-type]

        self.content = QWidget()
        self.content.setObjectName("settingsSecondaryContent")
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(4, 0, 12, 28)
        content_layout.setSpacing(18)
        for item in moved_items:
            if isinstance(item, QWidget):
                if item is runtime_target:
                    continue
                content_layout.addWidget(item)
            elif isinstance(item, QLayout):
                content_layout.addLayout(item)
            else:
                content_layout.addItem(item)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("settingsSecondaryScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(self.content)

        self.runtime_column: QFrame | None = None
        if runtime_target is not None:
            # The original runtime rows were built for a full-width form. Once
            # placed in the reference's narrow right status column, values must
            # wrap rather than elide or push the row beyond the column boundary.
            for object_name in (
                "settingsProviderState",
                "settingsNetworkState",
                "settingsPersistenceState",
                "settingsRuntimeDetail",
            ):
                value = runtime_target.findChild(QLabel, object_name)
                if value is None:
                    continue
                value.setWordWrap(True)
                value.setAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
                )
                value.setMinimumWidth(130)
                value.setMaximumWidth(176)

            runtime_column = QFrame()
            runtime_column.setObjectName("settingsRuntimeColumn")
            runtime_column.setAccessibleName("System status")
            runtime_column.setFixedWidth(310)
            runtime_layout = QVBoxLayout(runtime_column)
            runtime_layout.setContentsMargins(20, 4, 4, 24)
            runtime_layout.setSpacing(12)
            runtime_heading = QLabel("System status")
            runtime_heading.setObjectName("settingsStatusColumnTitle")
            runtime_layout.addWidget(runtime_heading)
            runtime_layout.addWidget(runtime_target)
            runtime_layout.addStretch(1)
            runtime_column.setStyleSheet(
                f"""
                QFrame#settingsRuntimeColumn {{
                    background: {PALETTE.surface};
                    border: 0;
                    border-left: 1px solid {PALETTE.border};
                }}
                QLabel#settingsStatusColumnTitle {{
                    color: {PALETTE.text};
                    font-size: 18px;
                    font-weight: 600;
                }}
                QWidget#settingsRuntimePanel {{
                    background: transparent;
                    border: 0;
                }}
                """
            )
            self.runtime_column = runtime_column

        self.container = QFrame()
        self.container.setObjectName("settingsSecondaryContainer")
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(24)
        container_layout.addWidget(self.navigation)
        container_layout.addWidget(self.scroll, 1)
        if self.runtime_column is not None:
            container_layout.addWidget(self.runtime_column)
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
        if section.key == "runtime" and self.runtime_column is not None:
            self.runtime_column.setFocus(Qt.FocusReason.OtherFocusReason)
        else:
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
