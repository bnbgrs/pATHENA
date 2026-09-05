from __future__ import annotations

from dataclasses import replace

from athena.knowledge.deduplication import (
    CanonicalDeduplicationService,
    DedupAction,
    DedupDecision,
    DeduplicationPlan,
)
from athena.knowledge.extraction_models import ProposalEntityType
from athena.knowledge.models import (
    ClaimDraft,
    ClaimKind,
    EpistemicStatus,
    KnowledgeKind,
    KnowledgeUnitDraft,
)
from tests.unit.test_proposal_acceptance import _extracted


def test_acceptance_attribution_gate_suppresses_distinct_speakers(
    tmp_path,
    monkeypatch,
) -> None:
    database, result, knowledge, claims, acceptance = _extracted(tmp_path)
    try:
        actor_id = acceptance.chat.ensure_local_user()
        left_speaker = knowledge.create_knowledge_unit(
            actor_id=actor_id,
            draft=KnowledgeUnitDraft(
                knowledge_kind=KnowledgeKind.CONCEPT,
                title="Speaker Alice",
                body="Canonical attribution identity for Alice.",
            ),
            reason="attribution contradiction speaker fixture",
        )
        right_speaker = knowledge.create_knowledge_unit(
            actor_id=actor_id,
            draft=KnowledgeUnitDraft(
                knowledge_kind=KnowledgeKind.CONCEPT,
                title="Speaker Bob",
                body="Canonical attribution identity for Bob.",
            ),
            reason="attribution contradiction speaker fixture",
        )
        left = claims.create_claim(
            actor_id=actor_id,
            draft=ClaimDraft(
                claim_kind=ClaimKind.ATTRIBUTED_OPINION,
                statement="Berlin is the best capital city.",
                epistemic_status=EpistemicStatus.ASSERTED,
                attributed_to_entity_id=left_speaker.knowledge_id,
            ),
            reason="attribution contradiction composition fixture",
        )
        right = claims.create_claim(
            actor_id=actor_id,
            draft=ClaimDraft(
                claim_kind=ClaimKind.ATTRIBUTED_OPINION,
                statement="Munich is the best capital city.",
                epistemic_status=EpistemicStatus.ASSERTED,
                attributed_to_entity_id=right_speaker.knowledge_id,
            ),
            reason="attribution contradiction composition fixture",
        )
        gated_result = replace(
            result,
            proposals=replace(result.proposals, knowledge_units=()),
        )
        plan = DeduplicationPlan(
            knowledge=(),
            claims=(
                DedupDecision(
                    proposal_type=ProposalEntityType.CLAIM,
                    proposal_index=0,
                    action=DedupAction.REUSE_CANONICAL,
                    existing_entity_id=left.claim_id,
                    existing_revision_id=left.revision_id,
                ),
                DedupDecision(
                    proposal_type=ProposalEntityType.CLAIM,
                    proposal_index=1,
                    action=DedupAction.REUSE_CANONICAL,
                    existing_entity_id=right.claim_id,
                    existing_revision_id=right.revision_id,
                ),
            ),
            merge_candidates=(),
        )
        monkeypatch.setattr(
            CanonicalDeduplicationService,
            "plan",
            staticmethod(lambda connection, carrier: plan),
        )

        accepted = acceptance.accept_all(gated_result, expected_plan=plan)

        assert accepted.claim_ids == (left.claim_id, right.claim_id)
        assert accepted.contradiction_review_ids == ()
        review_count = database.connection.execute(
            "SELECT COUNT(*) FROM semantic_review_items WHERE review_type = 'contradiction'"
        ).fetchone()[0]
        assert review_count == 0
    finally:
        database.stop()
