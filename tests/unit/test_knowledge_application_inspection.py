from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings  # type: ignore[import-untyped]
from athena.core.application import AthenaApplication  # type: ignore[import-untyped]
from athena.knowledge.models import ClaimKind  # type: ignore[import-untyped]


def test_application_exposes_real_claim_inspection_through_core_api(
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
            content="The local archive preserves canonical evidence.",
        )
        revision = app.claims.promote_chat_message(
            chat_id=chat_id,
            sequence_no=message.sequence_no,
            claim_kind=ClaimKind.FACTUAL_ASSERTION,
        )
        actor_id = app.chat.ensure_local_user()

        capabilities = app.api.capabilities().features
        assert "knowledge.claim.inspect" in capabilities
        assert "knowledge.review.contradiction" in capabilities
        assert app.api._knowledge_inspection is app.knowledge_inspection

        claims = app.api.list_claims(limit=10)
        assert len(claims) == 1
        listed = claims[0]
        assert listed.claim_id == str(revision.claim_id)
        assert listed.revision.revision_id == str(revision.revision_id)
        assert listed.revision.created_by_actor_id == str(actor_id)
        assert listed.revision.statement == (
            "The local archive preserves canonical evidence."
        )

        assert len(listed.provenance_inputs) == 1
        provenance = listed.provenance_inputs[0]
        assert provenance.input_entity_id == str(message.message_id)
        assert provenance.input_revision_id == str(message.revision_id)
        assert provenance.input_role == "chat_message_source"

        assert len(listed.evidence) == 1
        evidence = listed.evidence[0]
        assert evidence.evidence_role == "originates"
        assert evidence.message_id == str(message.message_id)
        assert evidence.evidence_entity_id == str(message.message_id)
        assert evidence.evidence_revision_id == str(message.revision_id)

        loaded = app.api.load_claim(str(revision.claim_id))
        assert loaded == listed

        history = app.api.claim_history(str(revision.claim_id))
        assert len(history) == 1
        assert history[0].revision_id == str(revision.revision_id)
        assert history[0].statement == listed.revision.statement
    finally:
        app.stop()
