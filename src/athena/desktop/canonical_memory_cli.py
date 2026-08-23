"""Short-lived process boundary for advanced canonical-memory desktop actions.

This helper deliberately reuses the existing canonical Claim and Review services.
It contains no GUI-side semantic state and performs no model calls.
"""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from athena.core.application import AthenaApplication
from athena.knowledge.claim_repository import ClaimNotFoundError
from athena.knowledge.extraction_models import ProposalEntityType
from athena.knowledge.review_service import MergeReviewDetails, ReviewItem


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-canonical-memory-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    merge_list = commands.add_parser("merge-list")
    merge_list.add_argument("--limit", type=int, default=100)

    merge_show = commands.add_parser("merge-show")
    merge_show.add_argument("review_id", type=uuid.UUID)

    merge = commands.add_parser("merge")
    merge.add_argument("review_id", type=uuid.UUID)

    keep_separate = commands.add_parser("keep-separate")
    keep_separate.add_argument("review_id", type=uuid.UUID)

    relations = commands.add_parser("claim-relations")
    relations.add_argument("claim_id", type=uuid.UUID)
    return parser


def _safe(value: str | None, *, fallback: str = "-") -> str:
    if not value:
        return fallback
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _compact(value: str, *, limit: int = 180) -> str:
    compact = " ".join(value.split())
    if len(compact) > limit:
        compact = compact[: limit - 3].rstrip() + "..."
    return compact or "<empty>"


def _merge_row(item: ReviewItem, details: MergeReviewDetails) -> str:
    return "\t".join(
        (
            str(item.review_id),
            details.proposal_type.value,
            str(details.proposal_index),
            f"{details.similarity:.6f}",
            str(details.existing_entity_id),
            details.proposal_kind,
            details.proposal_epistemic_status,
            _safe(_compact(details.proposal_text)),
        )
    )


def _print_merge_list(app: AthenaApplication, *, limit: int) -> None:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    for item in app.reviews.list_pending(review_type="merge_candidate", limit=limit):
        print(_merge_row(item, app.reviews.merge_details(item.review_id)))


def _print_merge_target(app: AthenaApplication, details: MergeReviewDetails) -> None:
    print(f"TARGET_ENTITY {details.existing_entity_id}")
    print(f"TARGET_REVISION {details.existing_revision_id}")
    if details.proposal_type is ProposalEntityType.KNOWLEDGE:
        knowledge_snapshot = app.knowledge.load(details.existing_entity_id)
        knowledge_payload = knowledge_snapshot.revision.payload
        print("TARGET_TYPE knowledge")
        print(f"TARGET_KIND {knowledge_payload.knowledge_kind.value}")
        print(f"TARGET_STATUS {knowledge_payload.epistemic_status.value}")
        print(f"TARGET_TITLE {_safe(knowledge_payload.title)}")
        print("TARGET_TEXT")
        print(knowledge_payload.body)
        return

    claim_snapshot = app.claim_repository.load_current(details.existing_entity_id)
    claim_payload = claim_snapshot.revision.payload
    print("TARGET_TYPE claim")
    print(f"TARGET_KIND {claim_payload.claim_kind.value}")
    print(f"TARGET_STATUS {claim_payload.epistemic_status.value}")
    print("TARGET_TEXT")
    print(claim_payload.statement)


def _print_merge_show(app: AthenaApplication, review_id: uuid.UUID) -> None:
    item = app.reviews.get(review_id)
    if item.review_type != "merge_candidate":
        raise ValueError(f"Review {review_id} is not a merge candidate")
    details = app.reviews.merge_details(review_id)
    print(f"REVIEW {review_id}")
    print(f"STATUS {item.status.value}")
    print(f"PROPOSAL_TYPE {details.proposal_type.value}")
    print(f"PROPOSAL_INDEX {details.proposal_index}")
    print(f"PROPOSAL_KIND {details.proposal_kind}")
    print(f"PROPOSAL_STATUS {details.proposal_epistemic_status}")
    print(f"SIMILARITY {details.similarity:.6f}")
    print(f"DECISION {details.decision or '-'}")
    print("PROPOSAL_TEXT")
    print(details.proposal_text)
    _print_merge_target(app, details)


def _resolve_merge(app: AthenaApplication, *, review_id: uuid.UUID, decision: str) -> None:
    actor_id = app.chat.ensure_local_user()
    item = app.reviews.resolve_merge(review_id, actor_id=actor_id, decision=decision)
    details = app.reviews.merge_details(review_id)
    print(f"MERGE_REVIEW_RESOLVED {item.review_id} {decision}")
    print(f"STATUS {item.status.value}")
    print(f"TARGET_ENTITY {details.existing_entity_id}")


def _claim_relation_row(app: AthenaApplication, claim_id: uuid.UUID) -> tuple[str, ...]:
    rows: list[str] = []
    for evidence in app.claim_repository.list_evidence(claim_id):
        # Preserve the most specific provenance identity first. Chat-origin evidence
        # also carries the message entity in evidence_entity_id, but presenting that
        # generic entity before message_id would make ORIGINATES look like an unknown
        # semantic relation instead of an exact source-message reference.
        if evidence.message_id is not None:
            rows.append(
                "\t".join(
                    (
                        evidence.evidence_role.value,
                        str(evidence.message_id),
                        str(evidence.evidence_revision_id or "-"),
                        "message",
                        "-",
                        "-",
                        "Chat-message provenance source",
                    )
                )
            )
            continue

        if evidence.anchor_id is not None:
            rows.append(
                "\t".join(
                    (
                        evidence.evidence_role.value,
                        str(evidence.anchor_id),
                        str(evidence.evidence_revision_id or "-"),
                        "anchor",
                        "-",
                        "-",
                        "Source anchor evidence",
                    )
                )
            )
            continue

        target_id = evidence.evidence_entity_id
        target_revision = evidence.evidence_revision_id
        if target_id is None:
            continue
        try:
            target = app.claim_repository.load_current(target_id)
        except ClaimNotFoundError:
            rows.append(
                "\t".join(
                    (
                        evidence.evidence_role.value,
                        str(target_id),
                        str(target_revision or "-"),
                        "entity",
                        "-",
                        "-",
                        "<non-Claim semantic target>",
                    )
                )
            )
        else:
            payload = target.revision.payload
            rows.append(
                "\t".join(
                    (
                        evidence.evidence_role.value,
                        str(target.claim_id),
                        str(target.revision.revision_id),
                        "claim",
                        payload.claim_kind.value,
                        payload.epistemic_status.value,
                        _safe(_compact(payload.statement)),
                    )
                )
            )
    return tuple(rows)


def _print_claim_relations(app: AthenaApplication, claim_id: uuid.UUID) -> None:
    app.claim_repository.load_current(claim_id)
    rows = _claim_relation_row(app, claim_id)
    print(f"CLAIM {claim_id}")
    print(f"RELATION_COUNT {len(rows)}")
    for row in rows:
        print("RELATION\t" + row)


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "merge-list":
        _print_merge_list(app, limit=args.limit)
        return 0
    if args.command == "merge-show":
        _print_merge_show(app, args.review_id)
        return 0
    if args.command == "merge":
        _resolve_merge(app, review_id=args.review_id, decision="merge")
        return 0
    if args.command == "keep-separate":
        _resolve_merge(app, review_id=args.review_id, decision="keep_separate")
        return 0
    if args.command == "claim-relations":
        _print_claim_relations(app, args.claim_id)
        return 0
    raise RuntimeError(f"Unsupported canonical-memory desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"CANONICAL_MEMORY_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
