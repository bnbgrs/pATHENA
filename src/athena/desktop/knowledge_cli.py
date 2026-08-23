"""Short-lived process boundary for persistent desktop Knowledge operations."""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from athena.api.service import _dedup_plan_digest
from athena.core.application import AthenaApplication
from athena.knowledge.models import KnowledgeUnitRevision, KnowledgeUnitSnapshot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-knowledge-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=150)

    show = commands.add_parser("show")
    show.add_argument("knowledge_id", type=uuid.UUID)

    history = commands.add_parser("history")
    history.add_argument("knowledge_id", type=uuid.UUID)

    accept = commands.add_parser("accept")
    accept.add_argument("processing_run_id", type=uuid.UUID)
    accept.add_argument("preflight_digest")
    return parser


def _safe(value: str | None, *, fallback: str = "-") -> str:
    if not value:
        return fallback
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _summary(snapshot: KnowledgeUnitSnapshot) -> str:
    payload = snapshot.revision.payload
    if payload.title:
        return _safe(payload.title)
    compact = " ".join(payload.body.split())
    if len(compact) > 120:
        compact = compact[:117].rstrip() + "..."
    return compact or "<empty>"


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
