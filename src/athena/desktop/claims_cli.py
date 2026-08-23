"""Short-lived process boundary for persistent desktop Claim operations."""

from __future__ import annotations

import argparse
import sys
import uuid
from collections.abc import Sequence

from athena.core.application import AthenaApplication
from athena.knowledge.models import ClaimRevision, ClaimSnapshot


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-claims-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=150)

    show = commands.add_parser("show")
    show.add_argument("claim_id", type=uuid.UUID)

    history = commands.add_parser("history")
    history.add_argument("claim_id", type=uuid.UUID)
    return parser


def _safe(value: object | None, *, fallback: str = "-") -> str:
    if value is None:
        return fallback
    text = str(value)
    if not text:
        return fallback
    return text.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _summary(snapshot: ClaimSnapshot) -> str:
    compact = " ".join(snapshot.revision.payload.statement.split())
    if len(compact) > 140:
        compact = compact[:137].rstrip() + "..."
    return compact or "<empty>"


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    for snapshot in app.claims.list(limit=limit):
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
                    _summary(snapshot),
                )
            )
        )


def _print_revision(revision: ClaimRevision) -> None:
    payload = revision.payload
    print(f"REVISION {revision.revision_no} {revision.revision_id}")
    print(f"CREATED_AT_US {revision.created_at_us}")
    print(f"KIND {payload.claim_kind.value}")
    print(f"STATUS {payload.epistemic_status.value}")
    print(f"SUBJECT {_safe(payload.subject_entity_id)}")
    print(f"PREDICATE {_safe(payload.predicate)}")
    print(f"OBJECT {_safe(payload.object_entity_id)}")
    print(f"ATTRIBUTED_TO {_safe(payload.attributed_to_entity_id)}")
    print(f"VALID_FROM_US {payload.valid_from_us if payload.valid_from_us is not None else '-'}")
    print(f"VALID_TO_US {payload.valid_to_us if payload.valid_to_us is not None else '-'}")
    print("STATEMENT")
    print(payload.statement)


def _print_show(app: AthenaApplication, claim_id: uuid.UUID) -> None:
    snapshot = app.claims.load(claim_id)
    revision = snapshot.revision
    print(f"CLAIM {snapshot.claim_id}")
    print(f"LIFECYCLE {snapshot.lifecycle_state}")
    _print_revision(revision)

    provenance = app.claims.provenance_inputs(revision.provenance_id)
    print(f"PROVENANCE_INPUTS {len(provenance)}")
    for input_ref in provenance:
        print(
            "PROVENANCE "
            f"{input_ref.ordinal} "
            f"role={input_ref.input_role} "
            f"entity={input_ref.input_entity_id} "
            f"revision={input_ref.input_revision_id or '-'}"
        )

    evidence = app.claims.evidence(claim_id)
    print(f"EVIDENCE {len(evidence)}")
    for evidence_ref in evidence:
        print(
            "EVIDENCE_REF "
            f"role={evidence_ref.evidence_role.value} "
            f"anchor={evidence_ref.anchor_id or '-'} "
            f"message={evidence_ref.message_id or '-'} "
            f"entity={evidence_ref.evidence_entity_id or '-'} "
            f"revision={evidence_ref.evidence_revision_id or '-'}"
        )


def _print_history(app: AthenaApplication, claim_id: uuid.UUID) -> None:
    revisions = app.claims.history(claim_id)
    print(f"CLAIM {claim_id}")
    print(f"HISTORY {len(revisions)}")
    for index, revision in enumerate(revisions):
        if index:
            print("---")
        _print_revision(revision)


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0
    if args.command == "show":
        _print_show(app, args.claim_id)
        return 0
    if args.command == "history":
        _print_history(app, args.claim_id)
        return 0
    raise RuntimeError(f"Unsupported claims desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"CLAIMS_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
