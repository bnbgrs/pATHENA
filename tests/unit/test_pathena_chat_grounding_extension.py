from __future__ import annotations

from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from athena.api.contracts import (
    ChatMessageResponse,
    ChatThreadResponse,
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundingResponse,
)
from athena.desktop.app import create_application
from athena.desktop.chat_grounding_extension import (
    install_chat_grounding_extension,
    project_chat_evidence,
)
from athena.desktop.pathena_pallas_field import install_pallas_grounded_field
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-chat-grounding-extension-test"])


def _evidence(
    context_id: str,
    entity_type: str,
    entity_id: str,
    *,
    cited: bool,
    page: int | None = None,
) -> GroundedEvidenceResponse:
    is_source = entity_type == "source_anchor"
    return GroundedEvidenceResponse(
        context_id=context_id,
        evidence_class="source" if is_source else "canonical",
        entity_type=entity_type,
        entity_id=entity_id,
        revision_id=f"revision-{entity_id}",
        title="Stored source" if is_source else "Supported claim",
        text="Persisted evidence text.",
        cited=cited,
        epistemic_status=None if is_source else "supported",
        source_id=entity_id if is_source else None,
        representation_id="representation-1" if is_source else None,
        source_name="Stored source" if is_source else None,
        source_uri="file:///stored.pdf" if is_source else None,
        start_offset=10 if is_source else None,
        end_offset=30 if is_source else None,
        page_start=page,
        page_end=page,
        quoted_sha256="a" * 64 if is_source else None,
        truncated=False,
    )


def _response() -> GroundedChatResponse:
    user = ChatMessageResponse(
        message_id="message-user",
        chat_id="chat-1",
        sequence_no=1,
        message_type="user",
        actor_id=None,
        created_at_us=1,
        revision_id="revision-user",
        content="What is supported?",
        content_format="text/plain",
    )
    assistant = ChatMessageResponse(
        message_id="message-assistant",
        chat_id="chat-1",
        sequence_no=2,
        message_type="assistant",
        actor_id="local-model",
        created_at_us=2,
        revision_id="revision-assistant",
        content="A grounded response.",
        content_format="text/plain",
    )
    evidence = (
        _evidence("ctx-source", "source_anchor", "source-1", cited=True, page=4),
        _evidence("ctx-claim", "canonical_claim", "claim-1", cited=True),
    )
    return GroundedChatResponse(
        thread=ChatThreadResponse(
            chat_id="chat-1",
            started_at_us=1,
            ended_at_us=None,
            archive_mode="active",
            lifecycle_state="active",
            messages=(user, assistant),
        ),
        assistant_text="A grounded response.",
        evidence=evidence,
        personal_memory=(),
        grounding=GroundingResponse(
            cited_context_ids=("ctx-source", "ctx-claim"),
            canonical_context_ids=("ctx-claim",),
            user_statement_context_ids=(),
            conversation_context_ids=(),
            source_context_ids=("ctx-source",),
            research_context_ids=(),
            news_context_ids=(),
            invalid_context_ids=(),
            uses_inference=False,
            uses_model_prior=False,
            uses_unknown=False,
            has_provenance_marker=True,
        ),
        processing_run_id="run-1",
        model_id="local-model",
        embedding_model_id="local-embedding",
    )


def _render_grounded(window: PathenaMainWindow, response: GroundedChatResponse) -> None:
    window.apply_grounded_chat_sent(response)


def test_projection_preserves_source_claim_ids_and_location() -> None:
    references = project_chat_evidence(_response())

    assert [item.node_id for item in references] == [
        "source_anchor:source-1",
        "canonical_claim:claim-1",
    ]
    assert references[0].location == "page 4"
    assert references[1].entity_id == "claim-1"
    assert all(item.cited for item in references)


def test_grounded_response_renders_inline_references_on_exact_assistant() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    extension = install_chat_grounding_extension(window)
    response = _response()
    try:
        window.show()
        _render_grounded(window, response)
        extension.apply_grounded_response(response)
        app.processEvents()

        assistant = next(
            item
            for item in window.chat_messages_widget.findChildren(QWidget, "chatMessage")
            if item.property("messageId") == "message-assistant"
        )
        panel = assistant.findChild(QWidget, "groundedEvidenceSummary")
        assert panel is not None
        assert panel.property("groundedRunId") == "run-1"
        assert assistant.property("pathenaGroundedEvidenceCount") == 2
        buttons = panel.findChildren(QPushButton, "openPallasEvidenceButton")
        assert len(buttons) == 2
        assert all(not button.isEnabled() for button in buttons)
        assert extension.last_state == "ready"
    finally:
        window.close()
        app.processEvents()


def test_pallas_action_focuses_only_exact_graph_entity() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    pallas = install_pallas_grounded_field(window)
    extension = install_chat_grounding_extension(window)
    response = _response()
    try:
        window.show()
        _render_grounded(window, response)
        pallas.apply_grounded_response(response)
        extension.apply_grounded_response(response)
        app.processEvents()

        button = next(
            item
            for item in window.findChildren(QPushButton, "openPallasEvidenceButton")
            if item.property("pallasNodeId") == "canonical_claim:claim-1"
        )
        assert button.isEnabled()
        button.click()
        app.processEvents()

        assert pallas.field.property("pathenaPallasSelectionId") == (
            "canonical_claim:claim-1"
        )
    finally:
        window.close()
        app.processEvents()


def test_foreign_chat_response_is_rejected_without_mutating_document() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    extension = install_chat_grounding_extension(window)
    response = _response()
    try:
        window.show()
        window.current_chat_id = "another-chat"
        extension.apply_grounded_response(response)
        app.processEvents()

        assert extension.last_state == "stale"
        assert window.findChild(QWidget, "groundedEvidenceSummary") is None
    finally:
        window.close()
        app.processEvents()
