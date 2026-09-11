"""Accessible current-workspace semantics for pATHENA navigation."""

from __future__ import annotations

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QWidget,
)

_PRIMARY_TOP_NAVIGATION = (
    (0, "Chat"),
    (1, "Knowledge"),
    (2, "Research"),
    (3, "Jobs"),
    (4, "Sources"),
)


def _workspace_label(item: QListWidgetItem) -> str:
    """Resolve the human workspace name when navigation renders icon glyphs."""
    tooltip = item.toolTip().strip()
    return tooltip or item.text().strip()


class NavigationContextAccessibility(QObject):
    """Mirror the existing selected workspace into visible and assistive navigation."""

    def __init__(self, window: QWidget) -> None:
        super().__init__(window)
        navigation = window.findChild(QListWidget, "navigation")
        page_title = window.findChild(QLabel, "pageTitle")
        pages = getattr(window, "pages", None)
        top_bar = window.findChild(QWidget, "topBar")
        top_layout = top_bar.layout() if top_bar is not None else None
        if (
            navigation is None
            or page_title is None
            or not isinstance(pages, QStackedWidget)
            or not isinstance(top_layout, QHBoxLayout)
        ):
            raise RuntimeError("pATHENA navigation context is unavailable")

        self.navigation = navigation
        self.page_title = page_title
        self.pages = pages
        self.top_buttons: dict[int, QPushButton] = {}

        navigation.setAccessibleName("Workspaces")
        navigation.setAccessibleDescription(
            "Primary pATHENA workspace navigation. Use the focused list to choose a workspace."
        )
        page_title.setAccessibleName("Current workspace")

        for position, (row, label) in enumerate(_PRIMARY_TOP_NAVIGATION, start=1):
            button = QPushButton(label)
            button.setObjectName("topNavButton")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setToolTip(f"Open {label}")
            button.setAccessibleName(label)
            button.clicked.connect(
                lambda _checked=False, index=row: self.navigation.setCurrentRow(index)
            )
            top_layout.insertWidget(position, button)
            self.top_buttons[row] = button

        navigation.currentRowChanged.connect(self.sync)
        self.sync(navigation.currentRow())

    def sync(self, index: int) -> None:
        if not 0 <= index < self.navigation.count() or index >= self.pages.count():
            return

        current_item = self.navigation.item(index)
        current_label = _workspace_label(current_item)
        self.navigation.setProperty("pathenaCurrentWorkspace", current_label)
        self.navigation.setProperty("pathenaCurrentWorkspaceIndex", index)
        self.page_title.setAccessibleDescription(f"Current workspace: {current_label}.")
        self.page_title.setProperty("pathenaCurrentWorkspace", current_label)

        for row, button in self.top_buttons.items():
            current = row == index
            button.setChecked(current)
            button.setAccessibleDescription(
                f"{button.text()}; current workspace"
                if current
                else f"{button.text()}; workspace"
            )

        for row in range(self.navigation.count()):
            item = self.navigation.item(row)
            label = _workspace_label(item)
            current = row == index
            item.setData(Qt.ItemDataRole.AccessibleTextRole, label)
            item.setData(
                Qt.ItemDataRole.AccessibleDescriptionRole,
                f"{label}; current workspace" if current else f"{label}; workspace",
            )
            item.setData(Qt.ItemDataRole.StatusTipRole, "Current workspace" if current else "")

        page = self.pages.widget(index)
        if page is not None:
            page.setAccessibleName(current_label)
            page.setAccessibleDescription(f"{current_label} workspace content.")
            page.setProperty("pathenaCurrentWorkspace", True)
        for row in range(self.pages.count()):
            if row == index:
                continue
            other_page = self.pages.widget(row)
            if other_page is not None:
                other_page.setProperty("pathenaCurrentWorkspace", False)


def install_navigation_context_accessibility(
    window: QWidget,
) -> NavigationContextAccessibility:
    """Install visible and accessible navigation without introducing a second router."""
    return NavigationContextAccessibility(window)
