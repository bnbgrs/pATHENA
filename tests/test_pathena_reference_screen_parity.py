from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QFrame,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QWidget,
)

from athena.desktop.pathena_design_tokens import PALETTE, SHELL  # noqa: E402
from athena.desktop.pathena_reference_screen_parity import (  # noqa: E402
    COMPOSER_PLACEHOLDER,
    PAGE_LABELS,
    PAGE_TITLES,
    REFERENCE_FAMILY,
    SEARCH_PLACEHOLDER,
    TOP_NAV_LABELS,
    install_reference_screen_parity,
)


class _ReferenceWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._core_transport_ready = False
        self.navigation = QListWidget(self)
        self.navigation.setObjectName("navigation")
        for label in (
            "Chat",
            "Knowledge",
            "Research",
            "Jobs",
            "Sources",
            "System",
            "Settings",
        ):
            self.navigation.addItem(label)
        self.navigation.setCurrentRow(0)

        self.page_title = QLabel("Chat", self)
        self.prompt_input = QLineEdit(self)
        self.prompt_input.setPlaceholderText("Ask, explore, or work with your knowledge…")
        self.send_button = QPushButton("→", self)

        self.top_bar = QFrame(self)
        self.top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.addWidget(QLabel("pATHENA", self.top_bar))

        self.reference_top_nav_buttons: list[QPushButton] = []
        for index, label in enumerate(
            ("WORKSPACE", "LIBRARY", "RESEARCH", "JOBS", "SOURCES")
        ):
            button = QPushButton(label, self.top_bar)
            button.setObjectName("topNavButton")
            button.setCheckable(True)
            button.setProperty("pageIndex", index)
            self.reference_top_nav_buttons.append(button)
            top_layout.addWidget(button)

        top_layout.addStretch(1)
        top_layout.addWidget(QPushButton("◎", self.top_bar))
        top_layout.addWidget(QPushButton("⚙", self.top_bar))
        top_layout.addWidget(QLabel("●", self.top_bar))
        self.local_status = QLabel("LOCAL / PRIVATE", self.top_bar)
        self.local_status.setObjectName("localPrivateStatus")
        top_layout.addWidget(self.local_status)

        self.icon_rail = QFrame(self)
        self.icon_rail.setObjectName("iconRail")
        self.inspector = QFrame(self)
        self.inspector.setObjectName("inspector")
        self.inspector_title = QLabel("DETAILS", self.inspector)
        self.inspector_title.setObjectName("inspectorTitle")

        self.empty_eyebrow = QLabel("LOCAL-FIRST WORKSPACE", self)
        self.empty_eyebrow.setObjectName("emptyStateEyebrow")
        self.empty_title = QLabel("Waiting for the local core", self)
        self.empty_title.setObjectName("emptyStateTitle")
        self.empty_body = QLabel("Reconnecting…", self)
        self.empty_body.setObjectName("emptyStateBody")

        self.pallas_canvas = QGraphicsView(self)
        self.pallas_canvas.setObjectName("pallasSemanticCanvas")

        self.jobs_workspace = QWidget(self)
        self.jobs_workspace.setObjectName("jobsWorkspace")
        self.jobs_workspace.setStyleSheet(
            "QLineEdit#jobsFilter:focus { border-color: #F26A21; }"
        )


class _CommandPalette:
    def __init__(self, parent: QWidget) -> None:
        self.query = QLineEdit(parent)
        self.open_count = 0

    def open(self) -> None:
        self.open_count += 1


def _application() -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication([])


def test_reference_contract_matches_selected_eleven_screen_family() -> None:
    assert REFERENCE_FAMILY == "11-screen-2026-08-24"
    assert PAGE_LABELS == (
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    )
    assert PAGE_TITLES == (
        "Chat",
        "Library",
        "Research",
        "Jobs",
        "Sources",
        "System",
        "Settings",
    )
    assert TOP_NAV_LABELS == {
        0: "Chat",
        1: "Knowledge",
        2: "Research",
        3: "Jobs",
        4: "Sources",
    }
    assert COMPOSER_PLACEHOLDER == "Ask, explore, or build…"
    assert SEARCH_PLACEHOLDER == "Search commands or workspaces…"


def test_parity_adapter_normalizes_live_shell_copy_and_navigation() -> None:
    app = _application()
    window = _ReferenceWindow()
    parity = install_reference_screen_parity(window)
    app.processEvents()

    assert window.property("referenceFamily") == REFERENCE_FAMILY
    assert [button.text() for button in window.reference_top_nav_buttons] == [
        "Chat",
        "Knowledge",
        "Research",
        "Jobs",
        "Sources",
    ]
    assert window.prompt_input.placeholderText() == COMPOSER_PLACEHOLDER
    assert window.prompt_input.accessibleName() == "Ask pATHENA"
    assert window.send_button.text() == "→"
    assert window.local_status.text() == "Local · Private"
    assert window.page_title.text() == "Chat"
    assert window.inspector_title.text() == "KNOWLEDGE"
    assert window.empty_eyebrow.text() == "LOCAL CORE · CONNECTING"
    assert window.empty_title.text() == "Getting pATHENA ready"
    assert window.empty_body.text() == "What shall we explore today?"

    # Screen 01 uses its own wide, full-height navigation treatment while the
    # local core is unavailable. This must collapse back to the shared shell as
    # soon as another workbench destination is selected.
    assert window.top_bar.isHidden()
    assert window.icon_rail.width() == 248
    assert window.navigation.item(0).text() == "›  CHAT"
    assert window.navigation.item(4).text() == "▱  SOURCES"
    assert window.navigation.item(5).isHidden()
    assert window.navigation.item(6).isHidden()

    window.navigation.setCurrentRow(1)
    app.processEvents()
    assert window.page_title.text() == "Library"
    assert window.inspector_title.text() == "EVIDENCE & ACTIVITY"
    assert window.reference_top_nav_buttons[1].isChecked()
    assert not window.reference_top_nav_buttons[0].isChecked()
    assert not window.top_bar.isHidden()
    assert window.icon_rail.width() == SHELL.icon_rail_width
    assert window.navigation.item(0).text() == "Chat"
    assert not window.navigation.item(5).isHidden()

    window.navigation.setCurrentRow(5)
    app.processEvents()
    assert window.page_title.text() == "System"
    assert not any(button.isChecked() for button in window.reference_top_nav_buttons)

    assert (
        window.pallas_canvas.backgroundBrush().color().name().casefold()
        == PALETTE.canvas.casefold()
    )
    jobs_style = window.jobs_workspace.styleSheet()
    assert "/* 11-screen jobs parity */" in jobs_style
    assert f"border-color: {PALETTE.accent};" in jobs_style
    shell_style = window.styleSheet()
    assert "/* 11-screen shell parity */" in shell_style
    assert f"border-left: 2px solid {PALETTE.accent};" in shell_style

    parity.deleteLater()
    window.deleteLater()
    app.processEvents()


def test_reference_search_button_opens_real_palette_action() -> None:
    app = _application()
    window = _ReferenceWindow()
    parity = install_reference_screen_parity(window)
    command_palette = _CommandPalette(window)

    search_button = parity.bind_command_palette(command_palette)

    assert isinstance(search_button, QPushButton)
    assert search_button.text() == "⌕"
    assert search_button.property("referenceRole") == "globalSearch"
    assert search_button.accessibleName() == "Search and commands"
    assert command_palette.query.placeholderText() == SEARCH_PLACEHOLDER

    search_button.click()
    assert command_palette.open_count == 1

    # Rebinding is idempotent and must not duplicate the global utility.
    assert parity.bind_command_palette(command_palette) is search_button
    global_search_buttons = [
        button
        for button in window.top_bar.findChildren(QPushButton)
        if button.property("referenceRole") == "globalSearch"
    ]
    assert global_search_buttons == [search_button]

    parity.deleteLater()
    window.deleteLater()
    app.processEvents()
