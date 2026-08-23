"""pATHENA presentation shell layered over the existing desktop behaviour."""

from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QFrame, QLabel

from athena.desktop.api_controller import DesktopApiController
from athena.desktop.window import AthenaMainWindow, MetricRow

_DISPLAY_NAVIGATION = (
    "Chat",
    "Knowledge",
    "Research",
    "Jobs",
    "Files",
    "System",
    "Settings",
)


class PathenaMainWindow(AthenaMainWindow):
    """Apply pATHENA's quiet shell without changing ATHENA-derived behaviour.

    The base window remains the functional implementation. This subclass only
    changes visible labels, spacing, sizing and progressive disclosure so that
    future functional work can continue independently of the presentation layer.
    """

    def __init__(self, api_controller: DesktopApiController | None = None) -> None:
        super().__init__(api_controller=api_controller)
        self._apply_quiet_cognitive_workspace()
        self.chat_selector.currentIndexChanged.connect(
            self._sync_progressive_chat_actions
        )
        self._sync_progressive_chat_actions()

    def _apply_quiet_cognitive_workspace(self) -> None:
        self.setWindowTitle("pATHENA")
        self.resize(1480, 900)
        self.setMinimumSize(1180, 720)

        rail = self.findChild(QFrame, "rail")
        if rail is not None:
            rail.setFixedWidth(218)
            rail_layout = rail.layout()
            if rail_layout is not None:
                rail_layout.setContentsMargins(18, 20, 16, 18)
                rail_layout.setSpacing(11)

            # Runtime metrics remain available in System/Inspector. Keeping them
            # permanently visible in the primary rail makes the application read
            # like a monitoring dashboard instead of a cognitive workspace.
            for metric in rail.findChildren(MetricRow):
                metric.hide()

        wordmark = self.findChild(QLabel, "wordmark")
        if wordmark is not None:
            wordmark.setText("pATHENA")

        breadcrumb = self.findChild(QLabel, "breadcrumb")
        if breadcrumb is not None:
            breadcrumb.setText("pATHENA  /")

        keyboard_hint = self.findChild(QLabel, "keyboardHint")
        if keyboard_hint is not None:
            keyboard_hint.setText("Ctrl K")
            keyboard_hint.setToolTip("Open command palette")

        network_state = self.findChild(QLabel, "networkState")
        if network_state is not None:
            network_state.setText("Internet   Online\nTor        Off")
            network_state.setToolTip(
                "Network state. Detailed controls remain in the system workspace."
            )

        for index, label in enumerate(_DISPLAY_NAVIGATION):
            item = self.navigation.item(index)
            if item is None:
                continue
            item.setText(label)
            item.setSizeHint(QSize(176, 36))

        # PALLAS already has a live semantic ASCII controller. Reduce its visual
        # dominance while preserving the intended 9:16 reactive surface.
        self.pallas_visual.setFixedSize(126, 224)
        self.pallas_visual.setToolTip(
            "PALLAS — local reactive view of the current workspace context"
        )

        self.prompt_input.setObjectName("promptInput")
        self.prompt_input.setPlaceholderText("Ask, explore, or work with your knowledge…")

        self.ground_button.setObjectName("groundButton")
        self.ground_button.setText("Sources")
        self.ground_button.setToolTip("Ground this message in available sources")

        self.send_button.setObjectName("sendButton")
        self.send_button.setText("Send")
        self.send_button.setToolTip("Send message (Ctrl+Enter)")

        self.new_chat_button.setText("New")
        self.new_chat_button.setToolTip("Start a new chat")
        self.delete_chat_button.setText("Delete")
        self.delete_chat_button.setToolTip("Delete the selected chat")

        self._replace_visible_copy()

    def _sync_progressive_chat_actions(self, _index: int | None = None) -> None:
        """Reveal destructive chat controls only when they are actionable."""
        has_selected_chat = self.chat_selector.currentData() is not None
        self.delete_chat_button.setVisible(has_selected_chat)

    def _replace_visible_copy(self) -> None:
        replacements = {
            "Connect to ATHENA Core to load a conversation.": (
                "Connect to the local core to load a conversation."
            ),
            "ATHENA  >  ": "pATHENA  /",
        }
        for label in self.findChildren(QLabel):
            replacement = replacements.get(label.text())
            if replacement is not None:
                label.setText(replacement)

    def _select_page(self, index: int) -> None:
        """Keep functional routing but present human-readable page titles."""
        super()._select_page(index)
        if 0 <= index < len(_DISPLAY_NAVIGATION):
            self.page_title.setText(_DISPLAY_NAVIGATION[index])
