from __future__ import annotations

from PySide6.QtWidgets import QApplication

from athena.api.contracts import (
    ChatMessageResponse,
    ChatThreadResponse,
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundedMemoryResponse,
    GroundingResponse,
)
from athena.desktop.app import create_application
from athena.desktop.pathena_pallas_field import (
    PallasSelection,
    PallasSemanticField,
    install_pallas_grounded_field,
)
from athena.desktop.pathena_pallas_semantic import (
    PallasNodeKind,
    deterministic_layout,
    graph_from_grounded_response,
)
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-pallas-semantic-test"])


def _evidence(
    *,
    context_id: str,
    evidence_class: str,
    entity_type: str,
    entity_id: str,
    title: str,
    text: str,
    cited: bool,
    epistemic_status: str | None = None,
) -> GroundedEvidenceResponse:
    is_source = evidence_class == "source"
    return GroundedEvidenceResponse(
        context_id=context_id,
        evidence_class=evidence_class,
        entity_type=entity_type,
        entity_id=entity_id,
        revision_id=f"revision-{entity_id}",
        title=title,
        text=text,
        cited=cited,
        epistemic_status=epistemic_status,
        source_id=entity_id if is_source else None,
        representation_id="representation-1" if is_source else None,
        source_name=title if is_source else None,
        source_uri="file:///real/source.pdf" if is_source else None,
        start_offset=10 if is_source else None,
        end_offset=42 if is_source else None,
        page_start=1 if is_source else None,
        page_end=1 if is_source else None,
        quoted_sha256="a" * 64 if is_source else None,
        truncated=False,
    )


def _response(
    evidence: tuple[GroundedEvidenceResponse, ...],
    memory: tuple[GroundedMemoryResponse, ...] = (),
) -> GroundedChatResponse:
    user = ChatMessageResponse(
        message_id="message-user",
        chat_id="chat-1",
        sequence_no=1,
        message_type="user",
        actor_id=None,
        created_at_us=1,
        revision_id="message-user-revision",
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
        revision_id="message-assistant-revision",
        content="A grounded answer.",
        content_format="text/plain",
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
        assistant_text="A grounded answer.",
        evidence=evidence,
        personal_memory=memory,
        grounding=GroundingResponse(
            cited_context_ids=tuple(item.context_id for item in evidence if item.cited),
            canonical_context_ids=tuple(
                item.context_id for item in evidence if item.evidence_class == "canonical"
            ),
            user_statement_context_ids=(),
            conversation_context_ids=(),
            source_context_ids=tuple(
                item.context_id for item in evidence if item.evidence_class == "source"
            ),
            research_context_ids=tuple(
                item.context_id for item in evidence if item.evidence_class == "research"
            ),
            news_context_ids=(),
            invalid_context_ids=(),
            uses_inference=False,
            uses_model_prior=False,
            uses_unknown=False,
            has_provenance_marker=True,
        ),
        processing_run_id="run-real-1",
        model_id="local-model",
        embedding_model_id="local-embedding",
    )


def _semantic_response() -> GroundedChatResponse:
    return _response(
        (
            _evidence(
                context_id="ctx-source",
                evidence_class="source",
                entity_type="source_anchor",
                entity_id="source-1",
                title="Stored paper",
                text="Exact source quotation.",
                cited=True,
            ),
            _evidence(
                context_id="ctx-claim",
                evidence_class="canonical",
                entity_type="canonical_claim",
                entity_id="claim-1",
                title="Supported claim",
                text="A canonical claim persisted by Core.",
                cited=True,
                epistemic_status="supported",
            ),
            _evidence(
                context_id="ctx-research",
                evidence_class="research",
                entity_type="research_result",
                entity_id="research-1",
                title="Research result",
                text="A durable research result.",
                cited=False,
                epistemic_status="hypothesis",
            ),
            _evidence(
                context_id="ctx-conflict",
                evidence_class="canonical",
                entity_type="canonical_claim",
                entity_id="claim-conflict",
                title="Conflicting claim",
                text="A conflict reported by Core.",
                cited=False,
                epistemic_status="contradicted",
            ),
        ),
        (
            GroundedMemoryResponse(
                context_id="ctx-memory",
                memory_id="memory-1",
                revision_id="memory-revision-1",
                memory_kind="user_preference",
                scope_kind="global",
                scope_entity_id=None,
                content="A real persisted preference.",
            ),
        ),
    )


def test_adapter_preserves_real_entity_ids_and_semantic_glyphs() -> None:
    snapshot = graph_from_grounded_response(_semantic_response())

    assert snapshot.status == "ready"
    assert snapshot.focus_id == "focus:run-real-1"
    assert [node.node_id for node in snapshot.nodes] == [
        "canonical_claim:claim-1",
        "canonical_claim:claim-conflict",
        "focus:run-real-1",
        "memory:memory-1",
        "research_result:research-1",
        "source_anchor:source-1",
    ]
    assert snapshot.node("source_anchor:source-1").kind is PallasNodeKind.SOURCE  # type: ignore[union-attr]
    assert snapshot.node("canonical_claim:claim-1").glyph == "◆"  # type: ignore[union-attr]
    assert snapshot.node("research_result:research-1").kind is PallasNodeKind.HYPOTHESIS  # type: ignore[union-attr]
    assert snapshot.node("canonical_claim:claim-conflict").glyph == "×"  # type: ignore[union-attr]
    assert snapshot.node("memory:memory-1").summary == "A real persisted preference."  # type: ignore[union-attr]
    assert len(snapshot.edges) == 5
    assert {edge.relation for edge in snapshot.edges} == {
        "cites",
        "includes_context",
        "uses_personal_memory",
    }


def test_layout_is_deterministic_when_core_evidence_order_changes() -> None:
    response = _semantic_response()
    reversed_response = _response(tuple(reversed(response.evidence)), response.personal_memory)

    first = graph_from_grounded_response(response)
    second = graph_from_grounded_response(reversed_response)

    assert first.nodes == second.nodes
    assert first.edges == second.edges
    assert deterministic_layout(first) == deterministic_layout(second)


def test_adapter_reports_an_honest_empty_state() -> None:
    snapshot = graph_from_grounded_response(_response(()))

    assert snapshot.status == "empty"
    assert snapshot.nodes == ()
    assert snapshot.edges == ()
    assert snapshot.focus_id is None
    assert "no evidence" in snapshot.status_detail


def test_field_publishes_selection_for_context_inspector_handoff() -> None:
    _app()
    field = PallasSemanticField()
    selections: list[object] = []
    field.selection_changed.connect(selections.append)
    try:
        field.resize(760, 520)
        field.set_snapshot(graph_from_grounded_response(_semantic_response()))

        assert field.property("pathenaUiState") == "ready"
        assert field.property("pathenaPallasNodeCount") == 6
        assert field.focus_node("canonical_claim:claim-1")
        assert field.property("pathenaPallasSelectionId") == "canonical_claim:claim-1"
        assert selections
        assert isinstance(selections[-1], PallasSelection)
        selection = selections[-1]
        assert selection.node.entity_id == "claim-1"
        assert selection.node.summary == "A canonical claim persisted by Core."

        field.set_error("Core unavailable")
        assert field.snapshot is None
        assert field.property("pathenaPallasGraphId") == ""
        assert field.property("pathenaPallasNodeCount") == 0
    finally:
        field.close()


def test_installer_mounts_reversibly_and_keeps_legacy_pallas_widget() -> None:
    app = _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        window.show()
        app.processEvents()
        legacy_target = window.pallas_visual

        controller = install_pallas_grounded_field(window)
        controller.apply_grounded_response(_semantic_response())
        app.processEvents()

        assert controller.target is legacy_target
        assert window.pallas_visual is legacy_target
        assert not legacy_target.isHidden()
        assert controller.field.parentWidget() is legacy_target
        assert controller.field.property("pathenaUiState") == "ready"
        assert controller.field.property("pathenaPallasMode") == "compact"
        assert controller.field.selection_label.isHidden()
        assert legacy_target.property("pathenaPallasRenderer") == "grounded-semantic-v1"
        assert legacy_target.property("pathenaUiState") == "ready"
    finally:
        window.close()


def test_installer_exposes_loading_and_grounded_failure_without_fake_data() -> None:
    _app()
    window = PathenaMainWindow(api_controller=None)
    try:
        controller = install_pallas_grounded_field(window)
        window.ground_button.setChecked(True)
        controller.apply_chat_busy(True)
        assert controller.field.property("pathenaUiState") == "loading"
        assert controller.field.snapshot is None

        controller.apply_chat_operation_failure("send_grounded", "Provider unavailable")
        assert controller.field.property("pathenaUiState") == "error"
        assert "Provider unavailable" in controller.field.state_label.text()
        assert controller.field.snapshot is None
    finally:
        window.close()
