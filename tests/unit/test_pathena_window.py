from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFrame, QLabel, QPushButton, QWidget

from athena.api.contracts import (
    ChatMessageResponse,
    ChatOperationRecoveryResponse,
    ChatThreadResponse,
    GroundedChatResponse,
    GroundedEvidenceResponse,
    GroundingResponse,
)

from athena.desktop import window as window_module
from athena.desktop.app import create_application
from athena.desktop.pathena_design_tokens import PALETTE, SHELL
from athena.desktop.pathena_v3_theme import V3_COMPOSER_ACTION_SIZE
from athena.desktop.pathena_window import PathenaMainWindow


def _app() -> QApplication:
    return create_application(["pathena-window-test"])


def _assert_inspector_width(inspector: QFrame) -> None:
    assert inspector.width() in {
        SHELL.inspector_width,
        SHELL.inspector_width + inspector.frameWidth(),
    }
    assert inspector.minimumWidth() == SHELL.inspector_width
    assert inspector.maximumWidth() == SHELL.inspector_width


def test_reference_shell_owns_icon_rail_without_rewiring_navigation() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        assert shell.objectName() == "referenceShell"

        top_bar = shell.findChild(QFrame, "topBar")
        assert top_bar is not None
        assert top_bar.height() == SHELL.top_bar_height
        assert top_bar.accessibleName() == "Status and utilities"

        body = shell.findChild(QFrame, "referenceBody")
        assert body is not None
        icon_rail = body.findChild(QFrame, "iconRail")
        assert icon_rail is not None
        assert icon_rail.width() == SHELL.icon_rail_width
        assert icon_rail.accessibleName() == "Primary navigation"
        assert window.navigation.parentWidget() is icon_rail
        assert window.navigation.width() <= SHELL.icon_rail_width
        assert window.navigation.item(0).text() != "Workspace"
        assert window.navigation.item(0).toolTip() == "Workspace"

        legacy_host = shell.findChild(QWidget, "legacyShellHost")
        assert legacy_host is not None
        legacy_rail = legacy_host.findChild(QFrame, "rail")
        assert legacy_rail is not None
        assert legacy_host.isHidden()
        assert legacy_rail.isHidden()
        assert not icon_rail.isAncestorOf(window.pallas_visual)
        assert window.pallas_visual.isHidden()

        window.navigation.setCurrentRow(3)
        assert window.pages.currentIndex() == 3
        assert window.page_title.text() == "Jobs"
    finally:
        window.close()


def test_reference_shell_owns_orange_navigation_selection() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        stylesheet = window.navigation.styleSheet()
        assert PALETTE.accent in stylesheet
        assert PALETTE.surface_selected in stylesheet
        assert "#377DFF" not in stylesheet.upper()
    finally:
        window.close()


def test_reference_body_directly_owns_workspace_and_contextual_inspector() -> None:
    app = _app()
    window = PathenaMainWindow()
    app.processEvents()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        body = shell.findChild(QFrame, "referenceBody")
        assert body is not None

        center = body.findChild(QFrame, "conversation")
        inspector = body.findChild(QFrame, "inspector")
        assert center is not None
        assert inspector is not None
        assert center.parentWidget() is body
        assert inspector.parentWidget() is body
        _assert_inspector_width(inspector)
        assert inspector.accessibleName() == "Evidence & Activity"
        assert any(
            label.text() == "EVIDENCE & ACTIVITY"
            for label in inspector.findChildren(QLabel)
        )
        assert inspector.isHidden()
    finally:
        window.close()


def test_reference_shell_keeps_primary_navigation_in_rail_and_private_status_in_top_bar() -> None:
    _app()
    window = PathenaMainWindow()
    try:
        shell = window.centralWidget()
        assert isinstance(shell, QWidget)
        top_bar = shell.findChild(QFrame, "topBar")
        assert top_bar is not None
        assert top_bar.accessibleName() == "Status and utilities"
        assert window.findChildren(QPushButton, "topNavButton") == []

        utilities = window.findChildren(QPushButton, "topUtilityButton")
        assert [button.accessibleName() for button in utilities] == ["System", "Settings"]

        window.navigation.setCurrentRow(1)
        assert window.pages.currentIndex() == 1
        assert window.page_title.text() == "Library"

        status = window.findChild(QLabel, "localPrivateStatus")
        assert status is not None
        assert status.text() == "Local · Private"
    finally:
        window.close()


def test_reference_composer_uses_large_work_surface_and_send_target() -> None:
    app = _app()
    window = PathenaMainWindow()
    app.processEvents()
    try:
        composer = window.findChild(QFrame, "composer")
        assert composer is not None
        assert composer.accessibleName() == "Message composer"
        assert composer.height() == 88
        assert window.prompt_input.minimumHeight() == 44
        assert window.ground_button.minimumHeight() == 36
        assert window.send_button.width() == V3_COMPOSER_ACTION_SIZE
        assert window.send_button.height() == V3_COMPOSER_ACTION_SIZE
        assert window.send_button.minimumWidth() == V3_COMPOSER_ACTION_SIZE
        assert window.send_button.maximumWidth() == V3_COMPOSER_ACTION_SIZE
        assert window.send_button.minimumHeight() == V3_COMPOSER_ACTION_SIZE
        assert window.send_button.maximumHeight() == V3_COMPOSER_ACTION_SIZE
    finally:
        window.close()


def test_reference_inspector_follows_grounding_and_non_chat_navigation() -> None:
    app = _app()
    window = PathenaMainWindow()
    app.processEvents()
    try:
        inspector = window.findChild(QFrame, "inspector")
        assert inspector is not None
        _assert_inspector_width(inspector)
        assert inspector.isHidden()
        assert window.details_button.isHidden()

        window._set_context_available(True)
        assert inspector.isHidden()
        assert not window.context_button.isHidden()

        window.context_button.click()
        assert not inspector.isHidden()

        window._enter_new_chat_state(clear_transient=True)
        assert inspector.isHidden()

        window.navigation.setCurrentRow(2)
        assert not inspector.isHidden()

        window._set_context_available(False)
        assert not inspector.isHidden()

        window.navigation.setCurrentRow(0)
        assert inspector.isHidden()

        assert window.send_button.text() == "→"
        assert window.send_button.accessibleName() == "Send message"
        assert window.prompt_input.objectName() == "promptInput"
    finally:
        window.close()


class _CancelControllerStub:
    def __init__(self) -> None:
        self.can_cancel_active_chat = True
        self.chat_cancel_pending = False
        self.cancel_calls = 0

    def cancel_active_chat_operation(self) -> bool:
        self.cancel_calls += 1
        self.chat_cancel_pending = True
        return True


def test_reference_composer_exposes_stop_only_for_real_direct_send() -> None:
    app = _app()
    window = PathenaMainWindow()
    controller = _CancelControllerStub()
    try:
        window.api_controller = controller  # type: ignore[assignment]
        window._core_ready = True
        window._chat_busy = True
        window.pending_chat_id = None

        window._sync_composer_enabled()
        app.processEvents()

        assert window.prompt_input.isEnabled() is False
        assert window.ground_button.isEnabled() is False
        assert window.send_button.isEnabled() is True
        assert window.send_button.text() == "■"
        assert window.send_button.accessibleName() == "Stop response"

        window.send_button.click()
        assert controller.cancel_calls == 1

        window._sync_composer_enabled()
        assert window.send_button.isEnabled() is False
        assert window.send_button.text() == "…"
        assert window.send_button.accessibleName() == "Cancellation requested"

        controller.chat_cancel_pending = False
        controller.can_cancel_active_chat = False
        window._sync_composer_enabled()

        assert window.send_button.isEnabled() is False
        assert window.send_button.text() == "…"
        assert window.send_button.accessibleName() == "Chat operation in progress"

        window._chat_busy = False
        window._sync_composer_enabled()

        assert window.send_button.text() == "→"
        assert window.send_button.accessibleName() == "Send message"
    finally:
        window.close()


class _EditForkControllerStub:
    def __init__(self) -> None:
        self.edit_calls: list[tuple[str, str, str, str]] = []
        self.fork_calls: list[tuple[str, str, str]] = []

    def edit_message(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
        content: str,
    ) -> None:
        self.edit_calls.append((chat_id, message_id, revision_id, content))

    def fork_chat_from_message(
        self,
        *,
        chat_id: str,
        message_id: str,
        revision_id: str,
    ) -> None:
        self.fork_calls.append((chat_id, message_id, revision_id))


def test_message_actions_expose_real_edit_and_fork_controls(
    monkeypatch,
) -> None:
    app = _app()
    window = PathenaMainWindow()
    controller = _EditForkControllerStub()
    chat_id = "11111111-1111-1111-1111-111111111111"
    message_id = "22222222-2222-2222-2222-222222222222"
    revision_id = "33333333-3333-3333-3333-333333333333"

    try:
        window.api_controller = controller  # type: ignore[assignment]
        window.current_chat_id = chat_id
        window.pending_chat_id = None
        window._chat_busy = False
        window._core_ready = True
        monkeypatch.setattr(
            window_module.QInputDialog,
            "getMultiLineText",
            staticmethod(
                lambda *args, **kwargs: ("revised persisted text", True)
            ),
        )

        user_message = window._message_widget(
            role="user",
            content="original persisted text",
            created_at_us=1,
            sequence_no=1,
            message_id=message_id,
            revision_id=revision_id,
        )
        edit_button = user_message.findChild(QPushButton, "editMessageButton")
        fork_button = user_message.findChild(QPushButton, "forkMessageButton")

        assert edit_button is not None
        assert edit_button.text() == "Edit"
        assert edit_button.accessibleName() == "Edit message"
        assert fork_button is not None
        assert fork_button.text() == "New chat"
        assert fork_button.accessibleName() == "New chat from here"

        edit_button.click()
        fork_button.click()
        app.processEvents()

        assert controller.edit_calls == [
            (
                chat_id,
                message_id,
                revision_id,
                "revised persisted text",
            )
        ]
        assert controller.fork_calls == [
            (chat_id, message_id, revision_id)
        ]

        assistant_message = window._message_widget(
            role="assistant",
            content="answer",
            created_at_us=2,
            sequence_no=2,
            message_id="44444444-4444-4444-4444-444444444444",
            revision_id="55555555-5555-5555-5555-555555555555",
        )
        assert (
            assistant_message.findChild(QPushButton, "editMessageButton")
            is None
        )
        assert (
            assistant_message.findChild(QPushButton, "forkMessageButton")
            is not None
        )
    finally:
        window.close()


class _RecoveryControllerStub:
    def __init__(self) -> None:
        self.inspect_calls: list[tuple[str, str]] = []
        self.continue_calls: list[tuple[str, str]] = []
        self.can_cancel_active_chat = False
        self.chat_cancel_pending = False

    def inspect_chat_recovery(
        self,
        *,
        chat_id: str,
        operation_id: str,
    ) -> None:
        self.inspect_calls.append((chat_id, operation_id))

    def continue_chat_operation(
        self,
        *,
        chat_id: str,
        operation_id: str,
    ) -> None:
        self.continue_calls.append((chat_id, operation_id))


def _recovery_thread(
    *,
    chat_id: str,
    operation_id: str,
    include_assistant: bool = False,
) -> ChatThreadResponse:
    messages = [
        ChatMessageResponse(
            message_id=operation_id,
            chat_id=chat_id,
            sequence_no=1,
            message_type="user",
            actor_id="33333333-3333-4333-8333-333333333333",
            created_at_us=1,
            revision_id="44444444-4444-4444-8444-444444444444",
            content="persisted interrupted request",
            content_format="text/plain",
        )
    ]
    if include_assistant:
        messages.append(
            ChatMessageResponse(
                message_id="55555555-5555-4555-8555-555555555555",
                chat_id=chat_id,
                sequence_no=2,
                message_type="assistant",
                actor_id="66666666-6666-4666-8666-666666666666",
                created_at_us=2,
                revision_id="77777777-7777-4777-8777-777777777777",
                content="complete answer",
                content_format="text/plain",
            )
        )
    return ChatThreadResponse(
        chat_id=chat_id,
        started_at_us=1,
        ended_at_us=None,
        archive_mode="standard",
        lifecycle_state="active",
        messages=tuple(messages),
    )


def test_recovery_continue_is_exposed_only_after_core_confirmation() -> None:
    app = _app()
    window = PathenaMainWindow()
    controller = _RecoveryControllerStub()
    chat_id = "11111111-1111-4111-8111-111111111111"
    operation_id = "22222222-2222-4222-8222-222222222222"

    try:
        window.api_controller = controller  # type: ignore[assignment]
        window.apply_chat_loaded(
            _recovery_thread(
                chat_id=chat_id,
                operation_id=operation_id,
            )
        )
        app.processEvents()

        assert controller.inspect_calls == [(chat_id, operation_id)]
        assert window.recovery_bar.isHidden()

        window.apply_chat_recovery(
            ChatOperationRecoveryResponse(
                operation_id=operation_id,
                chat_id=chat_id,
                mode="grounded",
                state="resumable",
                can_continue=True,
                processing_run_id=(
                    "88888888-8888-4888-8888-888888888888"
                ),
            )
        )

        assert not window.recovery_bar.isHidden()
        assert not window.recovery_continue_button.isHidden()
        assert window.recovery_continue_button.isEnabled()
        assert "persisted checkpoint" in window.recovery_state_label.text()

        window.recovery_continue_button.click()

        assert controller.continue_calls == [(chat_id, operation_id)]
        assert not window.recovery_continue_button.isEnabled()
        assert "Continuing" in window.recovery_state_label.text()
    finally:
        window.close()


def test_ambiguous_recovery_never_exposes_continue_button() -> None:
    _app()
    window = PathenaMainWindow()
    controller = _RecoveryControllerStub()
    chat_id = "11111111-1111-4111-8111-111111111111"
    operation_id = "22222222-2222-4222-8222-222222222222"

    try:
        window.api_controller = controller  # type: ignore[assignment]
        window.current_chat_id = chat_id
        window._recovery_chat_id = chat_id
        window._recovery_operation_id = operation_id

        window.apply_chat_recovery(
            ChatOperationRecoveryResponse(
                operation_id=operation_id,
                chat_id=chat_id,
                mode="grounded",
                state="ambiguous",
                can_continue=False,
                processing_run_id=(
                    "88888888-8888-4888-8888-888888888888"
                ),
            )
        )

        assert not window.recovery_bar.isHidden()
        assert window.recovery_continue_button.isHidden()
        assert "will not repeat" in window.recovery_state_label.text()
        assert controller.continue_calls == []
    finally:
        window.close()


def test_completed_chat_does_not_probe_recovery() -> None:
    app = _app()
    window = PathenaMainWindow()
    controller = _RecoveryControllerStub()
    chat_id = "11111111-1111-4111-8111-111111111111"
    operation_id = "22222222-2222-4222-8222-222222222222"

    try:
        window.api_controller = controller  # type: ignore[assignment]
        window.apply_chat_loaded(
            _recovery_thread(
                chat_id=chat_id,
                operation_id=operation_id,
                include_assistant=True,
            )
        )
        app.processEvents()

        assert controller.inspect_calls == []
        assert window.recovery_bar.isHidden()
        assert window._recovery_operation_id is None
    finally:
        window.close()



def test_grounded_evidence_hover_previews_use_persisted_evidence() -> None:
    app = _app()
    window = PathenaMainWindow()
    response = GroundedChatResponse(
        thread=ChatThreadResponse(
            chat_id="11111111-1111-1111-1111-111111111111",
            started_at_us=1,
            ended_at_us=None,
            archive_mode="standard",
            lifecycle_state="active",
            messages=(),
        ),
        assistant_text="grounded answer",
        evidence=(
            GroundedEvidenceResponse(
                context_id="ctx-source-1",
                evidence_class="source",
                entity_type="source_representation",
                entity_id="22222222-2222-2222-2222-222222222222",
                revision_id="33333333-3333-3333-3333-333333333333",
                title="Source excerpt",
                text=(
                    "This persisted excerpt is the exact evidence behind "
                    "the grounded answer."
                ),
                cited=True,
                epistemic_status="supported",
                source_id="44444444-4444-4444-4444-444444444444",
                representation_id="55555555-5555-5555-5555-555555555555",
                source_name="Local report.pdf",
                source_uri="file:///archive/local-report.pdf",
                start_offset=120,
                end_offset=260,
                page_start=4,
                page_end=5,
                quoted_sha256="a" * 64,
                truncated=False,
            ),
            GroundedEvidenceResponse(
                context_id="ctx-claim-1",
                evidence_class="canonical",
                entity_type="claim",
                entity_id="66666666-6666-6666-6666-666666666666",
                revision_id="77777777-7777-7777-7777-777777777777",
                title="Persisted supported claim",
                text="Canonical claim evidence from the local knowledge graph.",
                cited=False,
                epistemic_status="supported",
                source_id=None,
                representation_id=None,
                source_name=None,
                source_uri=None,
                start_offset=None,
                end_offset=None,
                page_start=None,
                page_end=None,
                quoted_sha256=None,
                truncated=False,
            ),
        ),
        personal_memory=(),
        grounding=GroundingResponse(
            cited_context_ids=("ctx-source-1",),
            canonical_context_ids=("ctx-claim-1",),
            user_statement_context_ids=(),
            conversation_context_ids=(),
            source_context_ids=("ctx-source-1",),
            research_context_ids=(),
            news_context_ids=(),
            invalid_context_ids=(),
            uses_inference=False,
            uses_model_prior=False,
            uses_unknown=False,
            has_provenance_marker=True,
        ),
        processing_run_id="88888888-8888-8888-8888-888888888888",
        model_id="local-model",
        embedding_model_id=None,
    )

    try:
        window._render_evidence_previews(response)
        app.processEvents()

        chips = window.evidence_preview_host.findChildren(
            QLabel,
            "evidencePreviewChip",
        )
        assert len(chips) == 2

        source_chip = chips[0]
        assert source_chip.property("contextId") == "ctx-source-1"
        assert source_chip.property("cited") is True
        assert "Local report.pdf" in source_chip.text()
        assert "file:///archive/local-report.pdf" in source_chip.toolTip()
        assert "pages 4–5" in source_chip.toolTip()
        assert "offsets 120–260" in source_chip.toolTip()
        assert "exact evidence" in source_chip.toolTip()
        assert source_chip.accessibleDescription() == source_chip.toolTip()

        claim_chip = chips[1]
        assert claim_chip.property("contextId") == "ctx-claim-1"
        assert claim_chip.property("cited") is False
        assert "Persisted supported claim" in claim_chip.text()
        assert "Canonical claim evidence" in claim_chip.toolTip()

        assert not window.evidence_preview_host.isHidden()
        assert "Local report.pdf" in window.evidence_chain_state.toolTip()

        window._clear_evidence_previews()
        app.processEvents()
        assert window.evidence_preview_layout.count() == 0
        assert window.evidence_preview_host.isHidden()
        assert window.evidence_chain_state.toolTip() == ""
    finally:
        window.close()
