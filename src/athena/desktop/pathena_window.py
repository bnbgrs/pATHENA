"""pATHENA presentation shell layered over the existing desktop behaviour."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.desktop.api_controller import DesktopApiController, DesktopApiSnapshot
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


def _conversation_label(started_at_us: int, message_count: int) -> str:
    """Render a durable chat identity as quiet human-facing session metadata."""
    started = datetime.fromtimestamp(started_at_us / 1_000_000)
    message_word = "message" if message_count == 1 else "messages"
    return f"{started:%d %b, %H:%M} · {message_count} {message_word}"


def _message_time(created_at_us: int) -> str:
    try:
        return datetime.fromtimestamp(created_at_us / 1_000_000).strftime("%H:%M")
    except (OverflowError, OSError, ValueError):
        return "—"


class PathenaMainWindow(AthenaMainWindow):
    """Apply pATHENA's quiet shell without changing ATHENA-derived behaviour.

    The base window remains the functional implementation. This subclass only
    changes visible labels, spacing, sizing and progressive disclosure so that
    future functional work can continue independently of the presentation layer.
    """

    def __init__(self, api_controller: DesktopApiController | None = None) -> None:
        super().__init__(api_controller=api_controller)
        self._apply_quiet_cognitive_workspace()
        self._install_progressive_disclosure()
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

            # Runtime metrics remain available in System/Details. Keeping them
            # permanently visible in the primary rail makes the application read
            # like a monitoring dashboard instead of a cognitive workspace.
            for metric in rail.findChildren(MetricRow):
                metric.hide()

            # The inherited network copy is a static placeholder rather than a
            # live network-control surface. Do not present it as current state.
            network_state = rail.findChild(QLabel, "networkState")
            if network_state is not None:
                network_state.hide()
            rail_rules = rail.findChildren(QFrame, "rule")
            for rule in rail_rules[-2:]:
                rule.hide()

            # The live PALLAS canvas already identifies itself. A second heading
            # directly above it adds noise without adding navigation information.
            for child_label in rail.findChildren(QLabel):
                if child_label.text() == "PALLAS":
                    child_label.hide()

        center = self.findChild(QFrame, "conversation")
        if center is not None:
            center_layout = center.layout()
            if isinstance(center_layout, QVBoxLayout):
                center_layout.setContentsMargins(30, 24, 30, 18)

        wordmark = self.findChild(QLabel, "wordmark")
        if wordmark is not None:
            wordmark.setText("pATHENA")

        # The product name is already anchored in the navigation rail. Keep the
        # content header focused on the current workspace instead of repeating it.
        breadcrumb = self.findChild(QLabel, "breadcrumb")
        if breadcrumb is not None:
            breadcrumb.hide()

        keyboard_hint = self.findChild(QLabel, "keyboardHint")
        if keyboard_hint is not None:
            keyboard_hint.setText("Ctrl K")
            keyboard_hint.setToolTip("Open command palette")

        for index, navigation_label in enumerate(_DISPLAY_NAVIGATION):
            if index >= self.navigation.count():
                break
            item = self.navigation.item(index)
            item.setText(navigation_label)
            item.setSizeHint(QSize(176, 36))

        current_page = self.navigation.currentRow()
        if 0 <= current_page < len(_DISPLAY_NAVIGATION):
            self.page_title.setText(_DISPLAY_NAVIGATION[current_page])

        # PALLAS has a live semantic ASCII controller. Reduce its visual
        # dominance while preserving the intended 9:16 reactive surface.
        self.pallas_visual.setFixedSize(126, 224)
        self.pallas_visual.setToolTip(
            "PALLAS — local reactive view of the current workspace context"
        )

        self.chat_selector.setMinimumWidth(250)
        self.chat_selector.setToolTip("Choose a conversation")
        self.model_selector.setMinimumWidth(210)
        self.model_selector.setMaximumWidth(320)
        self.model_selector.setToolTip("Choose a local model")

        self.prompt_input.setObjectName("promptInput")
        self.prompt_input.setPlaceholderText("Ask, explore, or work with your knowledge…")

        self.ground_button.setObjectName("groundButton")
        self.ground_button.setText("Sources")
        self.ground_button.setToolTip("Ground this message in available sources")

        self.send_button.setObjectName("sendButton")
        self.send_button.setText("Send")
        self.send_button.setToolTip("Send message (Ctrl+Enter)")

        self.new_chat_button.setText("New")
        self.new_chat_button.setToolTip("Start a new conversation")
        self.delete_chat_button.setText("Delete")
        self.delete_chat_button.setToolTip("Delete the selected conversation")

        self._replace_visible_copy()
        self._hide_nonfunctional_placeholders()

    def _install_progressive_disclosure(self) -> None:
        """Keep secondary evidence machinery out of the default reading flow."""
        self.details_button = QPushButton("Details")
        self.details_button.setObjectName("detailsToggle")
        self.details_button.setCheckable(True)
        self.details_button.setToolTip("Show conversation details and provenance")
        self.details_button.setMaximumWidth(84)

        inspector = self.findChild(QFrame, "inspector")
        if inspector is not None:
            inspector.setFixedWidth(340)
            inspector.hide()
            self.details_button.toggled.connect(inspector.setVisible)

        center = self.findChild(QFrame, "conversation")
        if center is not None:
            center_layout = center.layout()
            if isinstance(center_layout, QVBoxLayout):
                header_item = center_layout.itemAt(0)
                header_layout = header_item.layout() if header_item is not None else None
                if isinstance(header_layout, QHBoxLayout):
                    # Insert immediately before the keyboard shortcut hint.
                    header_layout.insertWidget(
                        max(0, header_layout.count() - 1),
                        self.details_button,
                    )

        self.context_button = QPushButton("Context")
        self.context_button.setObjectName("contextToggle")
        self.context_button.setCheckable(True)
        self.context_button.setToolTip(
            "Show source and evidence context for this conversation"
        )
        self.context_button.setMaximumWidth(90)
        self.evidence_chain.hide()
        self.context_button.toggled.connect(self.evidence_chain.setVisible)

        chat_page = self.pages.widget(0)
        if chat_page is not None:
            chat_layout = chat_page.layout()
            if isinstance(chat_layout, QVBoxLayout):
                evidence_index = chat_layout.indexOf(self.evidence_chain)
                if evidence_index >= 0:
                    chat_layout.insertWidget(evidence_index, self.context_button)

    def _sync_progressive_chat_actions(self, _index: int | None = None) -> None:
        """Reveal destructive chat controls only when they are actionable."""
        has_selected_chat = self.chat_selector.currentData() is not None
        self.delete_chat_button.setVisible(has_selected_chat)

    def _replace_visible_copy(self) -> None:
        replacements = {
            "Connect to ATHENA Core to load a conversation.": (
                "Connect to the local core to load a conversation."
            ),
            "INSPECTOR": "DETAILS",
            "PROVENANCE": "SOURCES & KNOWLEDGE",
            "KNOWLEDGE REVIEW": "KNOWLEDGE FROM THIS CHAT",
            "EVIDENCE CHAIN": "SOURCES & EVIDENCE",
            "DIRECT / PROVENANCE NOT ATTACHED": "No sources attached",
            "JOBS / API NOT CONNECTED": "BACKGROUND WORK",
            (
                "Autonomous job state will appear here when the desktop jobs API "
                "is available."
            ): "Open Jobs for background work status and controls.",
        }
        for label in self.findChildren(QLabel):
            replacement = replacements.get(label.text())
            if replacement is not None:
                label.setText(replacement)

        # Only humanize the compact Chat toolbar labels. Do not rewrite workspace
        # titles or technical labels inside Settings/System by matching text alone.
        for label in self.findChildren(QLabel, "sessionLabel"):
            if label.text() == "CHAT":
                label.setText("Conversation")
            elif label.text() == "MODEL":
                label.setText("Model")

    def _hide_nonfunctional_placeholders(self) -> None:
        """Do not advertise affordances that are not wired to an action yet."""
        hidden_copy = {
            "ATTACH",
            "BACKGROUND WORK",
            "Open Jobs for background work status and controls.",
        }
        for label in self.findChildren(QLabel):
            if label.text() in hidden_copy:
                label.hide()

    def _apply_control_snapshot(self, snapshot: DesktopApiSnapshot) -> None:
        """Keep controller identities intact while presenting readable selectors."""
        super()._apply_control_snapshot(snapshot)

        models = {
            model.backend_model_id: model
            for model in snapshot.models
            if model.model_type == "llm"
        }
        for index in range(self.model_selector.count()):
            model_id = self.model_selector.itemData(index)
            if not isinstance(model_id, str):
                continue
            model = models.get(model_id)
            if model is not None:
                self.model_selector.setItemText(index, model.display_name)

        chats = {chat.chat_id: chat for chat in snapshot.chats}
        for index in range(self.chat_selector.count()):
            chat_id = self.chat_selector.itemData(index)
            if chat_id is None:
                self.chat_selector.setItemText(index, "New conversation")
                continue
            if not isinstance(chat_id, str):
                continue
            chat = chats.get(chat_id)
            if chat is not None:
                self.chat_selector.setItemText(
                    index,
                    _conversation_label(chat.started_at_us, chat.message_count),
                )
            elif chat_id == self.pending_chat_id:
                self.chat_selector.setItemText(index, "Loading conversation…")
            else:
                self.chat_selector.setItemText(index, "Current conversation")

    def _message_widget(
        self,
        *,
        role: str,
        content: str | None,
        created_at_us: int,
        sequence_no: int,
        message_id: str,
        revision_id: str,
    ) -> QWidget:
        """Render the mature message actions with quieter pATHENA presentation."""
        container = super()._message_widget(
            role=role,
            content=content,
            created_at_us=created_at_us,
            sequence_no=sequence_no,
            message_id=message_id,
            revision_id=revision_id,
        )

        meta_name = "userMeta" if role == "user" else "speaker"
        meta = container.findChild(QLabel, meta_name)
        if meta is not None:
            display_role = (
                "You"
                if role == "user"
                else "pATHENA"
                if role == "assistant"
                else role.replace("_", " ").title()
            )
            meta.setText(f"{display_role} · {_message_time(created_at_us)}")

        remember_button = container.findChild(QPushButton, "rememberMessageButton")
        if remember_button is not None:
            remember_button.setText("Remember")

        knowledge_button = container.findChild(QPushButton, "addKnowledgeButton")
        if knowledge_button is not None:
            knowledge_button.setText("Add to knowledge")

        return container

    def _update_ready_state(self) -> None:
        """Translate machine-oriented readiness copy into quiet product status."""
        super()._update_ready_state()
        replacements = {
            "LOCAL / READY": "Ready",
            "LOCAL / MODEL ERROR": "Model error",
            "LOCAL / PROVIDER UNAVAILABLE": "Model service unavailable",
            "LOCAL / MODEL REQUIRED": "Choose a model",
            "LOCAL / MODEL NOT LOADED": "Model not loaded",
        }
        replacement = replacements.get(self.status_text.text())
        if replacement is not None:
            self.status_text.setText(replacement)

    def _select_page(self, index: int) -> None:
        """Keep functional routing but present human-readable page titles."""
        super()._select_page(index)
        if 0 <= index < len(_DISPLAY_NAVIGATION):
            self.page_title.setText(_DISPLAY_NAVIGATION[index])

        # The legacy inspector is chat-specific. Never leave stale chat metadata
        # open beside Knowledge, Research, Jobs, Files, System, or Settings.
        details_button = getattr(self, "details_button", None)
        if isinstance(details_button, QPushButton):
            is_chat = index == 0
            details_button.setVisible(is_chat)
            if not is_chat:
                details_button.setChecked(False)

    def apply_chat_busy(self, busy: bool) -> None:
        """Preserve the quiet pATHENA copy when base chat state changes."""
        super().apply_chat_busy(busy)
        self.send_button.setText("Working…" if busy else "Send")
