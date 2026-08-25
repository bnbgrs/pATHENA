from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from athena.api.contracts import (
    ChatMessageResponse,
    ChatThreadResponse,
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundingResponse,
)
from athena.desktop.chat_grounding_extension import (
    ChatGroundingController,
    project_chat_evidence,
)


@pytest.fixture(scope="module")
def qapp() -> Iterator[QApplication]:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app


def _evidence(
    *,
    context_id: str,
    entity_type: str = "source",
    entity_id: str = "source-1",
    title: str | None = "Durable source",
    source_name: str | None = "Archive A",
    cited: bool = True,
    page_start: int | None = 3,
    page_end: int | None = 4,
) -> GroundedEvidenceResponse:
    return GroundedEvidenceResponse(
        context_id=context_id,
        evidence_class="canonical",
        entity_type=entity_type,
        entity_id=entity_id,
        revision_id="revision-1",
        title=title,
        text="Persisted evidence text.",
        cited=cited,
        epistemic_status="verified",
        source_id="source-id-1",
        representation_id="representation-1",
        source_name=source_name,
        source_uri=None,
        start_offset=0,
        end_offset=24,
        page_start=page_start,
        page_end=page_end,
        quoted_sha256="a" * 64,
        truncated=False,
    )


def _response(
    evidence: tuple[GroundedEvidenceResponse, ...],
    *,
    chat_id: str = "chat-1",
    run_id: str = "run-1",
    user_text: str | None = None,
) -> GroundedChatResponse:
    messages: list[ChatMessageResponse] = []
    if user_text is not None:
        messages.append(
            ChatMessageResponse(
                message_id="user-1",
                chat_id=chat_id,
                sequence_no=1,
                message_type="user",
                actor_id="user",
                created_at_us=1,
                revision_id="message-revision-user",
                content=user_text,
                content_format="text/plain",
            )
        )
    messages.append(
        ChatMessageResponse(
            message_id="assistant-1",
            chat_id=chat_id,
            sequence_no=2,
            message_type="assistant",
            actor_id="athena",
            created_at_us=2,
            revision_id="message-revision-1",
            content="Grounded answer",
            content_format="text/plain",
        )
    )
    return GroundedChatResponse(
        thread=ChatThreadResponse(
            chat_id=chat_id,
            started_at_us=1,
            ended_at_us=None,
            archive_mode="durable",
            lifecycle_state="active",
            messages=tuple(messages),
        ),
        assistant_text="Grounded answer",
        evidence=evidence,
        personal_memory=(),
        grounding=GroundingResponse(
            cited_context_ids=tuple(item.context_id for item in evidence if item.cited),
            canonical_context_ids=tuple(item.context_id for item in evidence),
            user_statement_context_ids=(),
            conversation_context_ids=(),
            source_context_ids=tuple(
                item.context_id for item in evidence if item.entity_type == "source"
            ),
            research_context_ids=(),
            news_context_ids=(),
            invalid_context_ids=(),
            uses_inference=False,
            uses_model_prior=False,
            uses_unknown=False,
            has_provenance_marker=True,
        ),
        processing_run_id=run_id,
        model_id="local-model",
        embedding_model_id=None,
    )


def _window(chat_id: str = "chat-1") -> tuple[QWidget, QWidget]:
    window = QWidget()
    window.current_chat_id = chat_id  # type: ignore[attr-defined]
    document = QWidget(window)
    document.setObjectName("chatMessages")
    window.chat_messages_widget = document  # type: ignore[attr-defined]
    document_layout = QVBoxLayout(document)

    message = QWidget(document)
    message.setObjectName("chatMessage")
    message.setProperty("messageId", "assistant-1")
    message_layout = QVBoxLayout(message)
    message_layout.addWidget(QLabel("Grounded answer", message))
    message_layout.addWidget(QWidget(message))
    document_layout.addWidget(message)

    inspector_title = QLabel("INSPECTOR", window)
    inspector_title.setObjectName("inspectorTitle")
    inspector_content = QWidget(window)
    inspector_content.setObjectName("inspectorScrollContent")
    inspector_layout = QVBoxLayout(inspector_content)
    inspector_layout.addWidget(QLabel("Existing provenance", inspector_content))
    inspector_layout.addStretch(1)
    return window, message


def test_projection_preserves_real_provenance_and_deduplicates_context() -> None:
    item = _evidence(context_id="ctx-1")
    response = _response((item, item))

    references = project_chat_evidence(response)

    assert len(references) == 1
    reference = references[0]
    assert reference.context_id == "ctx-1"
    assert reference.node_id == "source:source-1"
    assert reference.entity_id == "source-1"
    assert reference.title == "Durable source"
    assert reference.source_name == "Archive A"
    assert reference.location == "pages 3–4"
    assert reference.epistemic_status == "verified"
    assert reference.cited is True


def test_grounded_panel_separates_title_from_compact_provenance_metadata(
    qapp: QApplication,
) -> None:
    window, message = _window()
    controller = ChatGroundingController(window, None)
    try:
        controller.apply_grounded_response(_response((_evidence(context_id="ctx-1"),)))
        qapp.processEvents()

        assert controller.last_state == "ready"
        panel = message.findChild(QWidget, "groundedEvidenceSummary")
        assert panel is not None
        heading = panel.findChild(QLabel, "groundedEvidenceHeading")
        title = panel.findChild(QLabel, "groundedEvidenceTitle")
        metadata = panel.findChild(QLabel, "groundedEvidenceMeta")
        action = panel.findChild(QPushButton, "openPallasEvidenceButton")
        assert heading is not None
        assert heading.text() == "Grounded evidence · 1 cited · 1 available"
        assert title is not None
        assert title.text() == "Durable source"
        assert title.toolTip() == "Persisted evidence text."
        assert metadata is not None
        assert metadata.text() == (
            "CITED · SOURCE · source-1 · Archive A · pages 3–4 · verified"
        )
        assert action is not None
        assert action.isEnabled() is False
        assert action.toolTip() == "PALLAS is not installed for this window."
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_grounded_response_mirrors_real_evidence_and_activity_into_inspector(
    qapp: QApplication,
) -> None:
    window, _message = _window()
    controller = ChatGroundingController(window, None)
    try:
        controller.apply_grounded_response(_response((_evidence(context_id="ctx-1"),)))
        qapp.processEvents()

        inspector_title = window.findChild(QLabel, "inspectorTitle")
        panel = window.findChild(QWidget, "groundedInspectorPanel")
        assert inspector_title is not None
        assert inspector_title.text() == "Evidence & Activity"
        assert panel is not None
        evidence_title = panel.findChild(QLabel, "inspectorEvidenceTitle")
        evidence_meta = panel.findChild(QLabel, "inspectorEvidenceMeta")
        activity = panel.findChild(QLabel, "inspectorActivityItem")
        assert evidence_title is not None
        assert evidence_title.text() == "Durable source"
        assert evidence_title.toolTip() == "Persisted evidence text."
        assert evidence_meta is not None
        assert evidence_meta.text().startswith("CITED · SOURCE · source-1")
        assert activity is not None
        assert activity.text() == "Latest grounded response · 1 cited · 1 evidence"
        assert activity.property("groundedRunId") == "run-1"
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_repeated_grounding_replaces_inspector_projection_instead_of_stacking(
    qapp: QApplication,
) -> None:
    window, _message = _window()
    controller = ChatGroundingController(window, None)
    try:
        controller.apply_grounded_response(_response((_evidence(context_id="ctx-1"),)))
        controller.apply_grounded_response(
            _response((_evidence(context_id="ctx-2", entity_id="source-2"),), run_id="run-2")
        )
        qapp.processEvents()

        panels = window.findChildren(QWidget, "groundedInspectorPanel")
        assert len(panels) == 1
        activity = panels[0].findChild(QLabel, "inspectorActivityItem")
        assert activity is not None
        assert activity.property("groundedRunId") == "run-2"
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_empty_grounded_response_is_honest_and_non_mutating(qapp: QApplication) -> None:
    window, message = _window()
    controller = ChatGroundingController(window, None)
    try:
        controller.apply_grounded_response(_response(()))
        qapp.processEvents()

        assert controller.last_state == "empty"
        panel = message.findChild(QWidget, "groundedEvidenceSummary")
        assert panel is not None
        empty = panel.findChild(QLabel, "groundedEvidenceEmpty")
        assert empty is not None
        assert empty.text() == "No evidence entities were returned for this grounded run."
        assert panel.findChildren(QPushButton) == []
        inspector_empty = window.findChild(QLabel, "inspectorEvidenceEmpty")
        assert inspector_empty is not None
        assert inspector_empty.text() == "No evidence returned for this grounded response."
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_stale_grounded_response_does_not_attach_to_current_chat(
    qapp: QApplication,
) -> None:
    window, message = _window(chat_id="chat-current")
    controller = ChatGroundingController(window, None)
    try:
        controller.apply_grounded_response(
            _response((_evidence(context_id="ctx-1"),), chat_id="chat-stale")
        )
        qapp.processEvents()

        assert controller.last_state == "stale"
        assert message.findChild(QWidget, "groundedEvidenceSummary") is None
        assert window.findChild(QWidget, "groundedInspectorPanel") is None
        assert message.property("pathenaGroundedRunId") is None
    finally:
        window.deleteLater()
        qapp.processEvents()


def test_reference_falls_back_to_real_source_name_without_synthetic_title() -> None:
    response = _response(
        (
            _evidence(
                context_id="ctx-source-name",
                title=None,
                source_name="Imported report",
                page_start=None,
                page_end=None,
            ),
        )
    )

    reference = project_chat_evidence(response)[0]

    assert reference.title == "Imported report"
    assert reference.source_name == "Imported report"
    assert reference.location is None
