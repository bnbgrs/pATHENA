"""Short-lived desktop boundary for pending contradiction reviews."""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from athena.core.application import AthenaApplication
from athena.knowledge.models import ClaimRevision
from athena.knowledge.review_service import ReviewItem


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-contradiction-reviews-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=100)

    show = commands.add_parser("show")
    show.add_argument("review_id", type=uuid.UUID)

    accept = commands.add_parser("accept")
    accept.add_argument("review_id", type=uuid.UUID)

    reject = commands.add_parser("reject")
    reject.add_argument("review_id", type=uuid.UUID)
    return parser


def _single_line(value: str, *, limit: int = 120) -> str:
    compact = " ".join(value.split())
    if len(compact) > limit:
        compact = compact[: limit - 3].rstrip() + "..."
    return compact or "<empty>"


def _claim_revision(
    app: AthenaApplication,
    *,
    claim_id: uuid.UUID,
    revision_id: uuid.UUID,
) -> ClaimRevision:
    for revision in app.claims.history(claim_id):
        if revision.revision_id == revision_id:
            return revision
    raise LookupError(f"Claim revision not found: {claim_id} / {revision_id}")


def _require_contradiction(item: ReviewItem) -> ReviewItem:
    if item.review_type != "contradiction":
        raise ValueError("Review item is not a contradiction review")
    if (
        item.left_entity_id is None
        or item.left_revision_id is None
        or item.right_entity_id is None
        or item.right_revision_id is None
    ):
        raise ValueError("Contradiction review is missing canonical Claim references")
    return item


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    for item in app.reviews.list_pending(review_type="contradiction", limit=limit):
        item = _require_contradiction(item)
        assert item.left_entity_id is not None
        assert item.left_revision_id is not None
        assert item.right_entity_id is not None
        assert item.right_revision_id is not None
        left = _claim_revision(
            app,
            claim_id=item.left_entity_id,
            revision_id=item.left_revision_id,
        )
        right = _claim_revision(
            app,
            claim_id=item.right_entity_id,
            revision_id=item.right_revision_id,
        )
        print(
            "\t".join(
                (
                    str(item.review_id),
                    f"{item.confidence:.6f}",
                    str(item.created_at_us),
                    str(item.left_entity_id),
                    str(item.right_entity_id),
                    _single_line(left.payload.statement),
                    _single_line(right.payload.statement),
                )
            )
        )


def _print_show(app: AthenaApplication, review_id: uuid.UUID) -> None:
    item = _require_contradiction(app.reviews.get(review_id))
    assert item.left_entity_id is not None
    assert item.left_revision_id is not None
    assert item.right_entity_id is not None
    assert item.right_revision_id is not None
    left = _claim_revision(
        app,
        claim_id=item.left_entity_id,
        revision_id=item.left_revision_id,
    )
    right = _claim_revision(
        app,
        claim_id=item.right_entity_id,
        revision_id=item.right_revision_id,
    )

    print(f"REVIEW {item.review_id}")
    print(f"TYPE {item.review_type}")
    print(f"STATUS {item.status.value}")
    print(f"CONFIDENCE {item.confidence:.6f}")
    print(f"CREATED_AT_US {item.created_at_us}")
    print(f"PROCESSING_RUN {item.processing_run_id}")
    print(f"MODEL_SIGNATURE {item.model_signature_id}")
    print(f"REASON {item.reason}")
    print(f"LEFT_CLAIM {item.left_entity_id}")
    print(f"LEFT_REVISION {item.left_revision_id}")
    print("LEFT_STATEMENT")
    print(left.payload.statement)
    print(f"RIGHT_CLAIM {item.right_entity_id}")
    print(f"RIGHT_REVISION {item.right_revision_id}")
    print("RIGHT_STATEMENT")
    print(right.payload.statement)


def _resolve(app: AthenaApplication, *, review_id: uuid.UUID, accept: bool) -> None:
    actor_id = app.chat.ensure_local_user()
    item = (
        app.reviews.accept(review_id, actor_id=actor_id)
        if accept
        else app.reviews.reject(review_id, actor_id=actor_id)
    )
    print(f"RESOLVED {item.review_id} {item.status.value}")


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0
    if args.command == "show":
        _print_show(app, args.review_id)
        return 0
    if args.command == "accept":
        _resolve(app, review_id=args.review_id, accept=True)
        return 0
    if args.command == "reject":
        _resolve(app, review_id=args.review_id, accept=False)
        return 0
    raise RuntimeError(f"Unsupported contradiction review command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"REVIEW_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
