from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings  # type: ignore[import-untyped]
from athena.core.application import AthenaApplication  # type: ignore[import-untyped]
from athena.knowledge.models import KnowledgeKind  # type: ignore[import-untyped]


def test_application_exposes_truthful_knowledge_reads_through_core_api(
    tmp_path: Path,
) -> None:
    app = AthenaApplication(
        settings=AthenaSettings(local_root=tmp_path.absolute()),
    )
    app.start(run_startup_maintenance=False)
    try:
        chat_id = app.chat.create_chat()
        message = app.chat.add_user_message(
            chat_id=chat_id,
            content="Canonical knowledge keeps its recorded source.",
        )
        first = app.knowledge.promote_chat_message(
            chat_id=chat_id,
            sequence_no=message.sequence_no,
            knowledge_kind=KnowledgeKind.FACT,
            title="Recorded source",
        )

        capabilities = app.api.capabilities().features
        assert "knowledge.read.why_known" in capabilities
        assert "knowledge.read.revision_history" in capabilities
        assert app.api._knowledge_read is app.knowledge_read

        explanation = app.api.why_known(str(first.knowledge_id))
        assert explanation.knowledge_id == str(first.knowledge_id)
        assert explanation.revision_id == str(first.revision_id)
        assert explanation.actor_id == str(first.created_by_actor_id)
        assert len(explanation.inputs) == 1
        source = explanation.inputs[0]
        assert source.entity_id == str(message.message_id)
        assert source.revision_id == str(message.revision_id)
        assert source.role == "chat_message_source"
        assert source.ordinal == 0

        second = app.knowledge.revise(
            knowledge_id=first.knowledge_id,
            title="Recorded source",
            body="Canonical knowledge keeps its recorded source and revision history.",
        )
        history = app.api.knowledge_revision_history(str(first.knowledge_id))
        assert history.knowledge_id == str(first.knowledge_id)
        assert [entry.revision_id for entry in history.entries] == [
            str(first.revision_id),
            str(second.revision_id),
        ]
        assert history.entries[0].changes_from_previous == ()
        changes = history.entries[1].changes_from_previous
        assert any(
            change.field == "body"
            and change.previous == "Canonical knowledge keeps its recorded source."
            and change.current
            == "Canonical knowledge keeps its recorded source and revision history."
            for change in changes
        )
    finally:
        app.stop()
