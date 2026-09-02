"""Short-lived process boundary for persistent desktop Knowledge operations."""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from athena.api.service import _dedup_plan_digest
from athena.core.application import AthenaApplication
from athena.knowledge.models import (
    ClaimRevision,
    ClaimSnapshot,
    KnowledgeUnitRevision,
    KnowledgeUnitSnapshot,
)
from athena.knowledge.review_service import ReviewItem


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-knowledge-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=150)

    show = commands.add_parser("show")
    show.add_argument("knowledge_id", type=uuid.UUID)

    history = commands.add_parser("history")
    history.add_argument("knowledge_id", type=uuid.UUID)

    claims_listing = commands.add_parser("claims-list")
    claims_listing.add_argument("--limit", type=int, default=150)

    claim_show = commands.add_parser("claim-show")
    claim_show.add_argument("claim_id", type=uuid.UUID)

    claim_history = commands.add_parser("claim-history")
    claim_history.add_argument("claim_id", type=uuid.UUID)

    reviews_listing = commands.add_parser("reviews-list")
    reviews_listing.add_argument(
        "--type",
        dest="review_type",
        choices=("contradiction", "merge_candidate"),
        default="contradiction",
    )
    reviews_listing.add_argument("--limit", type=int, default=100)

    review_show = commands.add_parser("review-show")
    review_show.add_argument("review_id", type=uuid.UUID)

    review_accept = commands.add_parser("review-accept")
    review_accept.add_argument("review_id", type=uuid.UUID)

    review_reject = commands.add_parser("review-reject")
    review_reject.add_argument("review_id", type=uuid.UUID)

    accept = commands.add_parser("accept")
    accept.add_argument("processing_run_id", type=uuid.UUID)
    accept.add_argument("preflight_digest")
    return parser


def _safe(value: str | None, *, fallback: str = "-") -> str:
    if not value:
        return fallback
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _compact(value: str, *, limit: int = 120) -> str:
    compact = " ".join(value.split())
    if len(compact) > limit:
        compact = compact[: limit - 3].rstrip() + "..."
    return compact or "<empty>"


def _summary(snapshot: KnowledgeUnitSnapshot) -> str:
    payload = snapshot.revision.payload
    if payload.title:
        return _safe(payload.title)
    return _compact(payload.body)


def _claim_summary(snapshot: ClaimSnapshot) -> str:
    return _compact(snapshot.revision.payload.statement)


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    for snapshot in app.knowledge.list(limit=limit):
        revision = snapshot.revision
        payload = revision.payload
        print(
            "\t".join(
                (
                    str(snapshot.knowledge_id),
                    str(revision.revision_no),
                    payload.knowledge_kind.value,
                    payload.epistemic_status.value,
                    snapshot.lifecycle_state,
                    _summary(snapshot),
                )
            )
        )


def _print_revision(revision: KnowledgeUnitRevision) -> None:
    payload = revision.payload
    print(f"REVISION {revision.revision_no} {revision.revision_id}")
    print(f"CREATED_AT_US {revision.created_at_us}")
    print(f"KIND {payload.knowledge_kind.value}")
    print(f"STATUS {payload.epistemic_status.value}")
    print(f"TITLE {_safe(payload.title)}")
    print(f"VALID_FROM_US {payload.valid_from_us if payload.valid_from_us is not None else '-'}")
    print(f"VALID_TO_US {payload.valid_to_us if payload.valid_to_us is not None else '-'}")
    print("BODY")
    print(payload.body)


def _print_show(app: AthenaApplication, knowledge_id: uuid.UUID) -> None:
    snapshot = app.knowledge.load(knowledge_id)
    revision = snapshot.revision
    print(f"KNOWLEDGE {snapshot.knowledge_id}")
    print(f"LIFECYCLE {snapshot.lifecycle_state}")
    _print_revision(revision)
    provenance = app.knowledge.provenance_inputs(revision.provenance_id)
    print(f"PROVENANCE_INPUTS {len(provenance)}")
    for item in provenance:
        print(
            "PROVENANCE "
            f"{item.ordinal} "
            f"role={item.input_role} "
            f"entity={item.input_entity_id} "
            f"revision={item.input_revision_id or '-'}"
        )


def _print_history(app: AthenaApplication, knowledge_id: uuid.UUID) -> None:
    revisions = app.knowledge.history(knowledge_id)
    print(f"KNOWLEDGE {knowledge_id}")
    print(f"HISTORY {len(revisions)}")
    for index, revision in enumerate(revisions):
        if index:
            print("---")
        _print_revision(revision)


def _print_claims_list(app: AthenaApplication, *, limit: int) -> None:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    for snapshot in app.claim_repository.list_current(limit=limit):
        revision = snapshot.revision
        payload = revision.payload
        print(
            "\t".join(
                (
                    str(snapshot.claim_id),
                    str(revision.revision_no),
                    payload.claim_kind.value,
                    payload.epistemic_status.value,
                    snapshot.lifecycle_state,
                    _claim_summary(snapshot),
                )
            )
        )


def _print_claim_revision(revision: ClaimRevision) -> None:
    payload = revision.payload
    print(f"REVISION {revision.revision_no} {revision.revision_id}")
    print(f"CREATED_AT_US {revision.created_at_us}")
    print(f"KIND {payload.claim_kind.value}")
    print(f"STATUS {payload.epistemic_status.value}")
    print(f"SUBJECT {payload.subject_entity_id or '-'}")
    print(f"PREDICATE {_safe(payload.predicate)}")
    print(f"OBJECT {payload.object_entity_id or '-'}")
    print(f"ATTRIBUTED_TO {payload.attributed_to_entity_id or '-'}")
    print(f"VALID_FROM_US {payload.valid_from_us if payload.valid_from_us is not None else '-'}")
    print(f"VALID_TO_US {payload.valid_to_us if payload.valid_to_us is not None else '-'}")
    print("STATEMENT")
    print(payload.statement)


def _print_claim_show(app: AthenaApplication, claim_id: uuid.UUID) -> None:
    snapshot = app.claim_repository.load_current(claim_id)
    revision = snapshot.revision
    print(f"CLAIM {snapshot.claim_id}")
    print(f"LIFECYCLE {snapshot.lifecycle_state}")
    _print_claim_revision(revision)

    provenance = app.claim_repository.list_provenance_inputs(revision.provenance_id)
    print(f"PROVENANCE_INPUTS {len(provenance)}")
    for provenance_ref in provenance:
        print(
            "PROVENANCE "
            f"{provenance_ref.ordinal} "
            f"role={provenance_ref.input_role} "
            f"entity={provenance_ref.input_entity_id} "
            f"revision={provenance_ref.input_revision_id or '-'}"
        )

    evidence = app.claim_repository.list_evidence(claim_id)
    print(f"EVIDENCE {len(evidence)}")
    for evidence_ref in evidence:
        print(
            "EVIDENCE_REF "
            f"role={evidence_ref.evidence_role.value} "
            f"anchor={evidence_ref.anchor_id or '-'} "
            f"message={evidence_ref.message_id or '-'} "
            f"entity={evidence_ref.evidence_entity_id or '-'} "
            f"revision={evidence_ref.evidence_revision_id or '-'} "
            f"provenance={evidence_ref.provenance_id}"
        )


def _print_claim_history(app: AthenaApplication, claim_id: uuid.UUID) -> None:
    revisions = app.claim_repository.list_revisions(claim_id)
    print(f"CLAIM {claim_id}")
    print(f"HISTORY {len(revisions)}")
    for index, revision in enumerate(revisions):
        if index:
            print("---")
        _print_claim_revision(revision)


def _review_line(item: ReviewItem) -> str:
    return "\t".join(
        (
            str(item.review_id),
            item.review_type,
            item.status.value,
            f"{item.confidence:.6f}",
            str(item.left_entity_id or "-"),
            str(item.right_entity_id or "-"),
            _safe(item.reason),
        )
    )


def _print_reviews_list(
    app: AthenaApplication,
    *,
    review_type: str,
    limit: int,
) -> None:
    for item in app.reviews.list_pending(review_type=review_type, limit=limit):
        print(_review_line(item))


def _print_review(app: AthenaApplication, item: ReviewItem) -> None:
    print(f"REVIEW {item.review_id}")
    print(f"TYPE {item.review_type}")
    print(f"STATUS {item.status.value}")
    print(f"CONFIDENCE {item.confidence:.6f}")
    print(f"CREATED_AT_US {item.created_at_us}")
    print(f"RESOLVED_AT_US {item.resolved_at_us if item.resolved_at_us is not None else '-'}")
    print(f"PROCESSING_RUN {item.processing_run_id}")
    print(f"MODEL_SIGNATURE {item.model_signature_id}")
    print(f"LEFT_ENTITY {item.left_entity_id or '-'}")
    print(f"LEFT_REVISION {item.left_revision_id or '-'}")
    print(f"RIGHT_ENTITY {item.right_entity_id or '-'}")
    print(f"RIGHT_REVISION {item.right_revision_id or '-'}")
    print(f"REASON {item.reason}")
    print(f"DECISION_ACTOR {item.decision_actor_id or '-'}")
    print(f"DECISION_REASON {_safe(item.decision_reason)}")

    if item.review_type == "contradiction":
        for label, claim_id in (("LEFT", item.left_entity_id), ("RIGHT", item.right_entity_id)):
            if claim_id is None:
                continue
            snapshot = app.claim_repository.load_current(claim_id)
            print(f"{label}_CLAIM_KIND {snapshot.revision.payload.claim_kind.value}")
            print(f"{label}_CLAIM_STATUS {snapshot.revision.payload.epistemic_status.value}")
            print(f"{label}_CLAIM_STATEMENT {snapshot.revision.payload.statement}")
    elif item.review_type == "merge_candidate":
        details = app.reviews.merge_details(item.review_id)
        print(f"PROPOSAL_TYPE {details.proposal_type.value}")
        print(f"PROPOSAL_INDEX {details.proposal_index}")
        print(f"PROPOSAL_KIND {details.proposal_kind}")
        print(f"PROPOSAL_STATUS {details.proposal_epistemic_status}")
        print(f"SIMILARITY {details.similarity:.6f}")
        print(f"PROPOSAL_TEXT {details.proposal_text}")
        print(f"MERGE_DECISION {details.decision or '-'}")


def _print_review_show(app: AthenaApplication, review_id: uuid.UUID) -> None:
    _print_review(app, app.reviews.get(review_id))


def _resolve_contradiction_review(
    app: AthenaApplication,
    *,
    review_id: uuid.UUID,
    accept: bool,
) -> None:
    actor_id = app.chat.ensure_local_user()
    item = (
        app.reviews.accept(review_id, actor_id=actor_id)
        if accept
        else app.reviews.reject(review_id, actor_id=actor_id)
    )
    action = "ACCEPTED" if accept else "REJECTED"
    print(f"REVIEW_{action} {item.review_id}")
    _print_review(app, item)


def _accept_review(
    app: AthenaApplication,
    *,
    processing_run_id: uuid.UUID,
    preflight_digest: str,
) -> None:
    try:
        digest_bytes = bytes.fromhex(preflight_digest)
    except ValueError as exc:
        raise ValueError("preflight_digest must be valid SHA-256 hexadecimal") from exc
    if len(preflight_digest) != 64 or len(digest_bytes) != 32:
        raise ValueError("preflight_digest must be a SHA-256 hexadecimal digest")

    result = app.extraction_snapshots.load(processing_run_id)
    if result.processing_run.processing_run_id != processing_run_id:
        raise RuntimeError("Frozen extraction returned another ProcessingRun")
    if result.proposals.merge_candidates:
        raise ValueError("Extractor merge candidates must be resolved before acceptance")

    plan = app.proposal_acceptance.preflight(result)
    if plan.merge_candidates:
        raise ValueError("Canonical merge candidates must be resolved before acceptance")

    current_digest = _dedup_plan_digest(plan)
    if current_digest != preflight_digest:
        raise ValueError(
            "Knowledge preflight is stale; review the proposals again before acceptance"
        )

    accepted = app.proposal_acceptance.accept_all(result, expected_plan=plan)
    print(f"ACCEPTED {accepted.processing_run_id} {accepted.commit_id}")
    print(f"KNOWLEDGE_TOTAL {len(accepted.knowledge_ids)}")
    print(f"KNOWLEDGE_CREATED {len(accepted.knowledge_created_ids)}")
    print(f"KNOWLEDGE_REUSED {len(accepted.knowledge_reused_ids)}")
    print(f"CLAIMS_TOTAL {len(accepted.claim_ids)}")
    print(f"CLAIMS_CREATED {len(accepted.claim_created_ids)}")
    print(f"CLAIMS_REUSED {len(accepted.claim_reused_ids)}")
    print(f"CONTRADICTION_REVIEWS {len(accepted.contradiction_review_ids)}")


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0
    if args.command == "show":
        _print_show(app, args.knowledge_id)
        return 0
    if args.command == "history":
        _print_history(app, args.knowledge_id)
        return 0
    if args.command == "claims-list":
        _print_claims_list(app, limit=args.limit)
        return 0
    if args.command == "claim-show":
        _print_claim_show(app, args.claim_id)
        return 0
    if args.command == "claim-history":
        _print_claim_history(app, args.claim_id)
        return 0
    if args.command == "reviews-list":
        _print_reviews_list(
            app,
            review_type=args.review_type,
            limit=args.limit,
        )
        return 0
    if args.command == "review-show":
        _print_review_show(app, args.review_id)
        return 0
    if args.command == "review-accept":
        _resolve_contradiction_review(app, review_id=args.review_id, accept=True)
        return 0
    if args.command == "review-reject":
        _resolve_contradiction_review(app, review_id=args.review_id, accept=False)
        return 0
    if args.command == "accept":
        _accept_review(
            app,
            processing_run_id=args.processing_run_id,
            preflight_digest=args.preflight_digest,
        )
        return 0
    raise RuntimeError(f"Unsupported knowledge desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"KNOWLEDGE_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
