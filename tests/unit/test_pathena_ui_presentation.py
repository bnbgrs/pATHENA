from __future__ import annotations

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton

from athena.api.contracts import (
    ChatSummaryResponse,
    HealthResponse,
    ModelResponse,
    ProviderHealthResponse,
)
from athena.desktop.api_controller import DesktopApiSnapshot
from athena.desktop.app import create_application
from athena.desktop.pathena_theme import PATHENA_STYLESHEET
from athena.desktop.pathena_window import (
    PathenaMainWindow,
    _humanize_review_heading,
)


def _app() -> QApplication:
    return create_application(["pathena-ui-test"])


def test_pathena_application_uses_quiet_workspace_theme() -> None:
    app = _app()

    assert app.styleSheet() == PATHENA_STYLESHEET
    assert app.applicationDisplayName() == "pATHENA"


def test_pathena_shell_progressively_discloses_destructive_chat_action() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        assert window.windowTitle() == "pATHENA"
        assert window.delete_chat_button.isHidden()

        window.chat_selector.addItem("Existing chat", "chat-1")
        window.chat_selector.setCurrentIndex(0)
        app.processEvents()
        assert window.delete_chat_button.isHidden() is False

        window.chat_selector.clear()
        window.chat_selector.addItem("New chat", None)
        app.processEvents()
        assert window.delete_chat_button.isHidden()
    finally:
        window.close()
        app.processEvents()


def test_pathena_secondary_context_is_grounded_only_and_user_controlled() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        assert inspector.isHidden()
        assert inspector.width() == 340
        assert window.details_button.text() == "Details"
        assert window.details_button.isChecked() is False

        assert window.context_button.text() == "Context"
        assert window.context_button.isHidden()
        assert window.evidence_chain.isHidden()

        window._set_context_available(True)
        app.processEvents()
        assert window.context_button.isHidden() is False
        assert window.context_button.isChecked() is False

        window.context_button.click()
        app.processEvents()
        assert window.evidence_chain.isHidden() is False

        window._set_context_available(False)
        app.processEvents()
        assert window.context_button.isHidden()
        assert window.context_button.isChecked() is False
        assert window.evidence_chain.isHidden()

        window.details_button.click()
        app.processEvents()
        assert inspector.isHidden() is False

        window.navigation.setCurrentRow(1)
        app.processEvents()
        assert window.details_button.isHidden()
        assert window.details_button.isChecked() is False
        assert inspector.isHidden()
    finally:
        window.close()
        app.processEvents()


def test_pathena_hides_unwired_attach_placeholder_and_humanizes_context_copy() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        hidden_labels = {
            label.text(): label
            for label in window.findChildren(QLabel)
            if label.text()
            in {
                "ATTACH",
                "BACKGROUND WORK",
                "Open Jobs for background work status and controls.",
            }
        }
        assert "ATTACH" in hidden_labels
        assert all(label.isHidden() for label in hidden_labels.values())

        visible_copy = {label.text() for label in window.findChildren(QLabel)}
        assert "KNOWLEDGE FROM THIS CHAT" in visible_copy
        assert "SOURCES & EVIDENCE" in visible_copy
        assert "INSPECTOR" not in visible_copy

        window.apply_chat_busy(True)
        assert window.send_button.text() == "Working…"
        window.apply_chat_busy(False)
        assert window.send_button.text() == "Send"
    finally:
        window.close()
        app.processEvents()


def test_pathena_removes_redundant_shell_chrome_and_fake_status_marker() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        breadcrumb = window.findChild(QLabel, "breadcrumb")
        assert breadcrumb is not None
        assert breadcrumb.isHidden()
        assert window.page_title.text() == "Chat"
        assert window.status_text.text() == "Connecting…"

        rail = window.findChild(QFrame, "rail")
        assert rail is not None
        status_square = rail.findChild(QLabel, "statusSquare")
        assert status_square is not None
        assert status_square.isHidden()

        pallas_labels = [
            label for label in rail.findChildren(QLabel) if label.text() == "PALLAS"
        ]
        assert pallas_labels
        assert all(label.isHidden() for label in pallas_labels)

        session_labels = {
            label.text()
            for label in window.findChildren(QLabel, "sessionLabel")
        }
        assert session_labels == {"Conversation", "Model"}
    finally:
        window.close()
        app.processEvents()


def test_pathena_model_settings_hide_inference_jargon() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        settings_page = window.pages.widget(6)
        assert settings_page is not None
        visible_labels = {
            label.text()
            for label in settings_page.findChildren(QLabel)
            if not label.isHidden()
        }
        assert {
            "Model",
            "Context window",
            "Maximum response",
            "Temperature",
            "Reasoning",
        }.issubset(visible_labels)
        assert "CTX" not in visible_labels
        assert "MAX OUTPUT TOKENS" not in visible_labels
        assert "THINKING" not in visible_labels
        assert all("reasoning_effort" not in text for text in visible_labels)
        assert window.thinking_checkbox.text() == "Off"
    finally:
        window.close()
        app.processEvents()


def test_pathena_review_headings_keep_meaning_without_machine_copy() -> None:
    assert _humanize_review_heading("RUN ABCDEF12 / MODEL qwen") == "Extraction summary"
    assert _humanize_review_heading("K01 / FACT / 92%") == "Knowledge 1 · Fact · 92%"
    assert _humanize_review_heading("C03 / OBSERVATION / 81%") == (
        "Claim 3 · Observation · 81%"
    )
    assert _humanize_review_heading(
        "K02 / POSSIBLE CANONICAL DUPLICATE / 89%"
    ) == "Knowledge 2 · Possible duplicate · 89%"
    assert _humanize_review_heading("RELATIONS") == "Relationships"
    assert _humanize_review_heading("CANONICAL PREFLIGHT") == "Deduplication"


def test_pathena_review_states_use_product_language() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        window.knowledge_review_state.setText("EXTRACTING / SELECTED MESSAGE")
        window._humanize_knowledge_review_panel()
        assert window.knowledge_review_state.text() == "Extracting…"

        window.knowledge_review_state.setText("SAVING MERGE DECISION")
        window._humanize_knowledge_review_panel()
        assert window.knowledge_review_state.text() == "Saving…"

        window.apply_api_failure("offline")
        assert window.status_text.text() == "Core unavailable"
    finally:
        window.close()
        app.processEvents()


def test_pathena_message_header_and_actions_stay_humanized_after_state_sync() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        message = window._message_widget(
            role="assistant",
            content="A persisted answer.",
            created_at_us=1_700_000_000_000_000,
            sequence_no=42,
            message_id="message-42",
            revision_id="revision-42",
        )
        window.chat_messages_layout.insertWidget(0, message)

        meta = message.findChild(QLabel, "speaker")
        assert meta is not None
        assert meta.text().startswith("pATHENA · ")
        assert "0042" not in meta.text()
        assert " / " not in meta.text()

        remember = message.findChild(QPushButton, "rememberMessageButton")
        knowledge = message.findChild(QPushButton, "addKnowledgeButton")
        assert remember is not None
        assert knowledge is not None

        window._sync_message_action_buttons()
        assert remember.text() == "Remember"
        assert knowledge.text() == "Add to knowledge"

        window._remembered_message_revisions.add(("message-42", "revision-42"))
        window._sync_message_action_buttons()
        assert remember.text() == "Remembered"
    finally:
        window.close()
        app.processEvents()


def test_pathena_session_controls_hide_machine_metadata() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    chat_id = "01912345-6789-7abc-8def-0123456789ab"
    model_id = "local/model/backend-identifier"
    snapshot = DesktopApiSnapshot(
        health=HealthResponse(
            api_version="v1",
            core_status="ready",
            detail=None,
        ),
        provider=ProviderHealthResponse(
            provider="LM Studio",
            status="ready",
            detail=None,
        ),
        models=(
            ModelResponse(
                provider="LM Studio",
                backend_model_id=model_id,
                display_name="Qwen Local",
                model_type="llm",
                context_capacity=32_768,
                quantization="Q4",
                loaded=True,
                vision=False,
                trained_for_tool_use=False,
                loaded_context_length=16_384,
            ),
        ),
        chats=(
            ChatSummaryResponse(
                chat_id=chat_id,
                started_at_us=1_700_000_000_000_000,
                ended_at_us=None,
                archive_mode="standard",
                lifecycle_state="active",
                message_count=3,
            ),
        ),
    )

    try:
        window._apply_control_snapshot(snapshot)
        app.processEvents()

        assert window.chat_selector.itemText(0) == "New conversation"
        chat_index = window.chat_selector.findData(chat_id)
        assert chat_index >= 0
        chat_label = window.chat_selector.itemText(chat_index)
        assert "3 messages" in chat_label
        assert chat_id[:8].upper() not in chat_label

        model_index = window.model_selector.findData(model_id)
        assert model_index >= 0
        assert window.model_selector.itemText(model_index) == "Qwen Local"
        assert "LOADED" not in window.model_selector.itemText(model_index)
        assert window.settings_model_value.text() == "Qwen Local · Loaded"

        window.thinking_checkbox.setChecked(True)
        app.processEvents()
        assert window.thinking_checkbox.text() == "On"
        window.thinking_checkbox.setChecked(False)
        app.processEvents()
        assert window.thinking_checkbox.text() == "Off"

        network_state = window.findChild(QLabel, "networkState")
        assert network_state is not None
        assert network_state.isHidden()

        window._core_transport_ready = True
        window._provider_ready = True
        window._last_model_error = None
        window._update_ready_state()
        assert window.status_text.text() == "Ready"
    finally:
        window.close()
        app.processEvents()
