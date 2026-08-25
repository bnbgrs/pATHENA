"""pATHENA presentation shell layered over the existing desktop behaviour."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QSize, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from athena.api.contracts import ChatThreadResponse, GroundedChatResponse
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


def _humanize_review_heading(text: str) -> str:
    """Translate proposal codes into compact readable review headings."""
    if text.startswith("RUN "):
        return "Extraction summary"
    if text == "RELATIONS":
        return "Relationships"
    if text == "EXTRACTOR MERGE CANDIDATES / BLOCKING":
        return "Possible duplicates"
    if text == "CANONICAL PREFLIGHT":
        return "Deduplication"

    parts = [part.strip() for part in text.split("/")]
    if len(parts) >= 3 and len(parts[0]) >= 2:
        code = parts[0]
        prefix = code[0]
        index = code[1:]
        if prefix in {"K", "C"} and index.isdigit():
            noun = "Knowledge" if prefix == "K" else "Claim"
            raw_kind = parts[1].replace("_", " ")
            kind = (
                "Possible duplicate"
                if raw_kind == "POSSIBLE CANONICAL DUPLICATE"
                else raw_kind.title()
            )
            confidence = parts[2]
            return f"{noun} {int(index)} · {kind} · {confidence}"
    return text


class PathenaMainWindow(AthenaMainWindow):
    """Apply pATHENA's quiet shell without changing ATHENA-derived behaviour."""

    def __init__(self, api_controller: DesktopApiController | None = None) -> None:
        super().__init__(api_controller=api_controller)
        bind_semantic_root = getattr(self.ascii_panel, "bind_semantic_root", None)
        if callable(bind_semantic_root):
            bind_semantic_root(self)
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

            for metric in rail.findChildren(MetricRow):
                metric.hide()

            status_square = rail.findChild(QLabel, "statusSquare")
            if status_square is not None:
                status_square.hide()

            network_state = rail.findChild(QLabel, "networkState")
            if network_state is not None:
                network_state.hide()
            rail_rules = rail.findChildren(QFrame, "rule")
            for rule in rail_rules[-2:]:
                rule.hide()

            for child_label in rail.findChildren(QLabel):
                if child_label.text() == "PALLAS":
                    child_label.hide()

        if self.status_text.text() == "LOCAL / CORE DISCONNECTED":
            self.status_text.setText("Connecting…")

        center = self.findChild(QFrame, "conversation")
        if center is not None:
            center_layout = center.layout()
            if isinstance(center_layout, QVBoxLayout):
                center_layout.setContentsMargins(30, 24, 30, 18)

        wordmark = self.findChild(QLabel, "wordmark")
        if wordmark is not None:
            wordmark.setText("pATHENA")

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
        self._apply_settings_presentation()
        self._hide_nonfunctional_placeholders()
        self._humanize_knowledge_review_panel()

    def _install_progressive_disclosure(self) -> None:
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
                    header_layout.insertWidget(
                        max(0, header_layout.count() - 1),
                        self.details_button,
                    )

        self.context_button = QPushButton("Context")
        self.context_button.setObjectName("contextToggle")
        self.context_button.setCheckable(True)
        self.context_button.setToolTip(
            "Show source and evidence context for the latest grounded response"
        )
        self.context_button.setMaximumWidth(90)
        self.context_button.hide()
        self.evidence_chain.hide()
        self.context_button.toggled.connect(self.evidence_chain.setVisible)

        chat_page = self.pages.widget(0)
        if chat_page is not None:
            chat_layout = chat_page.layout()
            if isinstance(chat_layout, QVBoxLayout):
                evidence_index = chat_layout.indexOf(self.evidence_chain)
                if evidence_index >= 0:
                    chat_layout.insertWidget(evidence_index, self.context_button)

    def bind_pallas_context_inspector(self, selection_source: object) -> object:
        """Bind Core's selection signal to the one shared Context Inspector."""
        from athena.desktop.pathena_pallas_inspector import (
            install_pallas_context_inspector,
        )

        return install_pallas_context_inspector(self, selection_source)

    def _set_context_available(self, available: bool) -> None:
        button = getattr(self, "context_button", None)
        if not isinstance(button, QPushButton):
            return
        button.setVisible(available)
        if not available:
            button.setChecked(False)
            self.evidence_chain.hide()

    def _sync_progressive_chat_actions(self, _index: int | None = None) -> None:
        """Expose secondary chat chrome only for an actual persisted conversation."""
        has_selected_chat = self.chat_selector.currentData() is not None
        is_chat_page = self.navigation.currentRow() == 0
        self.delete_chat_button.setVisible(has_selected_chat)

        details_button = getattr(self, "details_button", None)
        if isinstance(details_button, QPushButton):
            details_button.setVisible(has_selected_chat and is_chat_page)
            if not has_selected_chat or not is_chat_page:
                details_button.setChecked(False)

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

        for label in self.findChildren(QLabel, "sessionLabel"):
            if label.text() == "CHAT":
                label.setText("Conversation")
            elif label.text() == "MODEL":
                label.setText("Model")

    def _apply_settings_presentation(self) -> None:
        settings_page = self.pages.widget(6)
        if settings_page is None:
            return

        label_replacements = {
            "MODEL": "Model",
            "CTX": "Context window",
            "MAX OUTPUT TOKENS": "Maximum response",
            "TEMPERATURE": "Temperature",
            "THINKING": "Reasoning",
        }
        for label in settings_page.findChildren(QLabel):
            if label.text() == "LOCAL MODEL / INFERENCE SETTINGS":
                label.hide()
                continue
            if label.text().startswith("Per-model session controls."):
                label.setText(
                    "Tune how the selected local model uses context and generates "
                    "responses. Settings are kept per model for this session."
                )
                continue
            if label.text().startswith("THINKING OFF sends reasoning_effort=none."):
                label.setText(
                    "Reasoning is used only when enabled and supported by the selected "
                    "model. Maximum response stays within the current context budget."
                )
                continue
            replacement = label_replacements.get(label.text())
            if replacement is not None:
                label.setText(replacement)

        self.context_slider.setToolTip("Adjust the request context window")
        self.context_spin.setToolTip("Enter the exact context window in tokens")
        self.max_output_slider.setToolTip("Adjust the maximum response length")
        self.max_output_spin.setToolTip("Enter the maximum response length in tokens")
        self.temperature_spin.setToolTip("Adjust sampling temperature")
        self.thinking_checkbox.setToolTip(
            "Allow model reasoning when the selected model supports it"
        )
        self._humanize_model_settings_state()

    def _humanize_model_settings_state(self) -> None:
        model = self._selected_model()
        if model is None:
            self.settings_model_value.setText("—")
        else:
            state = "Loaded" if model.loaded else "Not loaded"
            self.settings_model_value.setText(f"{model.display_name} · {state}")
        self.thinking_checkbox.setText(
            "On" if self.thinking_checkbox.isChecked() else "Off"
        )

    def _humanize_knowledge_review_panel(self) -> None:
        self.knowledge_review_close_button.setText("Close")

        state_replacements = {
            "IDLE": "Idle",
            "EXTRACTING / SELECTED MESSAGE": "Extracting…",
            "PREFLIGHT / PENDING": "Checking for duplicates…",
            "REVIEW COMPLETE / READY": "Ready to add",
            "DECISION REQUIRED / CANONICAL MERGE": "Decision required",
            "BLOCKED / EXTRACTOR MERGE": "Needs review",
            "BLOCKED / REVIEW REQUIRED": "Needs review",
            "SAVING MERGE DECISION": "Saving…",
            "MERGE DECISION SAVED / REFRESHING PREFLIGHT": "Checking again…",
        }
        state = self.knowledge_review_state.text()
        if state.startswith("ERROR /"):
            self.knowledge_review_state.setText("Review failed")
        else:
            replacement = state_replacements.get(state)
            if replacement is not None:
                self.knowledge_review_state.setText(replacement)

        for label in self.knowledge_review_panel.findChildren(
            QLabel,
            "knowledgeReviewItemTitle",
        ):
            original = label.text()
            humanized = _humanize_review_heading(original)
            if humanized != original:
                label.setToolTip(original)
                label.setText(humanized)

        for button in self.knowledge_review_panel.findChildren(
            QPushButton,
            "knowledgeMergeButton",
        ):
            decision = button.property("decision")
            if decision == "merge":
                button.setText("Merge")
            elif decision == "keep_separate":
                button.setText("Keep separate")

    def _hide_nonfunctional_placeholders(self) -> None:
        hidden_copy = {
            "ATTACH",
            "BACKGROUND WORK",
            "Open Jobs for background work status and controls.",
        }
        for label in self.findChildren(QLabel):
            if label.text() in hidden_copy:
                label.hide()

    def _apply_control_snapshot(self, snapshot: DesktopApiSnapshot) -> None:
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

        self._humanize_model_settings_state()
        self._sync_progressive_chat_actions()

    def _configure_context_for_selected_model(self) -> None:
        super()._configure_context_for_selected_model()
        self._humanize_model_settings_state()

    def _on_thinking_changed(self, checked: bool) -> None:
        super()._on_thinking_changed(checked)
        self._humanize_model_settings_state()

    def _enter_new_chat_state(
        self,
        *,
        clear_transient: bool,
        message: str = "New persistent conversation. Type below to send the first message.",
    ) -> None:
        super()._enter_new_chat_state(
            clear_transient=clear_transient,
            message=message,
        )
        self._set_context_available(False)
        self._sync_progressive_chat_actions()

    def _extract_message_knowledge(self, message_id: str, revision_id: str) -> None:
        super()._extract_message_knowledge(message_id, revision_id)
        self._humanize_knowledge_review_panel()

    def _resolve_knowledge_merge(self, review_id: str, decision: str) -> None:
        super()._resolve_knowledge_merge(review_id, decision)
        self._humanize_knowledge_review_panel()

    @Slot(object)
    def apply_chat_loaded(self, thread: object) -> None:
        super().apply_chat_loaded(thread)
        if (
            isinstance(thread, ChatThreadResponse)
            and self.current_chat_id == thread.chat_id
            and self.pending_chat_id is None
        ):
            self._set_context_available(False)
        self._sync_progressive_chat_actions()

    @Slot(object)
    def apply_chat_sent(self, thread: object) -> None:
        super().apply_chat_sent(thread)
        if isinstance(thread, ChatThreadResponse) and self.current_chat_id == thread.chat_id:
            self._set_context_available(False)
        self._sync_progressive_chat_actions()

    @Slot(object)
    def apply_grounded_chat_sent(self, response: object) -> None:
        super().apply_grounded_chat_sent(response)
        if (
            isinstance(response, GroundedChatResponse)
            and self.current_chat_id == response.thread.chat_id
        ):
            self._set_context_available(True)
        self._sync_progressive_chat_actions()

    @Slot(object)
    def apply_knowledge_merge_review_ready(self, response: object) -> None:
        super().apply_knowledge_merge_review_ready(response)
        self._humanize_knowledge_review_panel()

    @Slot(str)
    def apply_api_failure(self, message: str) -> None:
        super().apply_api_failure(message)
        self.status_text.setText("Core unavailable")

    @Slot(str, str)
    def apply_chat_operation_failure(self, operation: str, message: str) -> None:
        super().apply_chat_operation_failure(operation, message)
        self.status_text.setText("Chat error")
        self._humanize_knowledge_review_panel()

    def _render_knowledge_review_panel(self) -> None:
        super()._render_knowledge_review_panel()
        self._humanize_knowledge_review_panel()

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

    def _sync_message_action_buttons(self) -> None:
        super()._sync_message_action_buttons()
        for button in self.chat_messages_widget.findChildren(
            QPushButton,
            "rememberMessageButton",
        ):
            button.setText(
                "Remembered" if button.text() == "REMEMBERED" else "Remember"
            )
        for button in self.chat_messages_widget.findChildren(
            QPushButton,
            "addKnowledgeButton",
        ):
            button.setText("Add to knowledge")
        self._humanize_knowledge_review_panel()

    def _update_ready_state(self) -> None:
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
        super()._select_page(index)
        if 0 <= index < len(_DISPLAY_NAVIGATION):
            self.page_title.setText(_DISPLAY_NAVIGATION[index])
        self._sync_progressive_chat_actions()

    def apply_chat_busy(self, busy: bool) -> None:
        super().apply_chat_busy(busy)
        self.send_button.setText("Working…" if busy else "Send")
