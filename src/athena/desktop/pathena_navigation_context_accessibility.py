"""Accessible current-workspace semantics for pATHENA navigation."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

_PRIMARY_TOP_NAVIGATION = (
    (0, "Chat"),
    (1, "Knowledge"),
    (2, "Research"),
    (3, "Jobs"),
    (4, "Sources"),
)

_CONTEXTUAL_INSPECTOR_COPY = {
    3: (
        "JOB / NONE",
        "No job selected",
        "EXECUTION\nSelect a job in the Jobs workspace to inspect its reported execution state.\n\n"
        "RESOURCES\nResource details appear only for a selected reported job.",
    ),
    6: (
        "SETTINGS / LOCAL",
        "System status",
        "Runtime and model availability are reported by the local pATHENA core. "
        "No synthetic health state is shown here.",
    ),
}


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

        self.window = window
        self.navigation = navigation
        self.page_title = page_title
        self.pages = pages
        self.top_buttons: dict[int, QPushButton] = {}
        self.inspector = window.findChild(QFrame, "inspector")
        self.inspector_context: QFrame | None = None
        self.inspector_context_id: QLabel | None = None
        self.inspector_context_heading: QLabel | None = None
        self.inspector_context_body: QLabel | None = None

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

        self._install_contextual_inspector_overlay()
        navigation.currentRowChanged.connect(self.sync)
        self.sync(navigation.currentRow())

    def _install_contextual_inspector_overlay(self) -> None:
        inspector = self.inspector
        if inspector is None:
            return

        panel = QFrame(inspector)
        panel.setObjectName("inspectorRouteContext")
        panel.setAutoFillBackground(True)
        panel.setPalette(inspector.palette())
        panel.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        panel.setVisible(False)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(10)

        title = QLabel("EVIDENCE & ACTIVITY")
        title.setObjectName("inspectorTitle")
        context_id = QLabel()
        context_id.setObjectName("objectId")
        heading = QLabel()
        heading.setObjectName("inspectorHeading")
        heading.setWordWrap(True)
        body = QLabel()
        body.setObjectName("inspectorBody")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(title)
        layout.addSpacing(8)
        layout.addWidget(context_id)
        layout.addWidget(heading)
        layout.addSpacing(8)
        layout.addWidget(body, 1)

        panel.setAccessibleName("Workspace context")
        inspector.installEventFilter(self)
        self.inspector_context = panel
        self.inspector_context_id = context_id
        self.inspector_context_heading = heading
        self.inspector_context_body = body
        self._resize_contextual_inspector()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.inspector and event.type() == QEvent.Type.Resize:
            self._resize_contextual_inspector()
        return super().eventFilter(watched, event)

    def _resize_contextual_inspector(self) -> None:
        if self.inspector is None or self.inspector_context is None:
            return
        self.inspector_context.setGeometry(self.inspector.rect())
        self.inspector_context.raise_()

    def _sync_contextual_inspector(self, index: int) -> None:
        panel = self.inspector_context
        context_id = self.inspector_context_id
        heading = self.inspector_context_heading
        body = self.inspector_context_body
        if panel is None or context_id is None or heading is None or body is None:
            return

        copy = _CONTEXTUAL_INSPECTOR_COPY.get(index)
        if copy is None:
            panel.setVisible(False)
            return

        object_id, heading_text, body_text = copy
        if index == 6:
            status_text = getattr(self.window, "status_text", None)
            status = status_text.text().strip() if isinstance(status_text, QLabel) else ""
            if status:
                body_text = f"Core status: {status}\n\n{body_text}"

        context_id.setText(object_id)
        heading.setText(heading_text)
        body.setText(body_text)
        panel.setAccessibleDescription(f"{heading_text}. {body_text}")
        panel.setVisible(True)
        self._resize_contextual_inspector()

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

        self._sync_contextual_inspector(index)


def install_navigation_context_accessibility(
    window: QWidget,
) -> NavigationContextAccessibility:
    """Install visible and accessible navigation without introducing a second router."""
    return NavigationContextAccessibility(window)
