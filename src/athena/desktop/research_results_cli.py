"""Short-lived desktop boundary for immutable ResearchResult promotion workflows."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Sequence

from athena.core.application import AthenaApplication
from athena.research.promotion import ResearchProposalRecord


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-research-results-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    result = commands.add_parser("result")
    result.add_argument("identifier", type=uuid.UUID)

    proposals = commands.add_parser("proposals")
    proposals.add_argument("identifier", type=uuid.UUID)

    propose = commands.add_parser("propose")
    propose.add_argument("identifier", type=uuid.UUID)

    accept = commands.add_parser("accept")
    accept.add_argument("proposal_id", type=uuid.UUID)
    accept.add_argument("--keep-separate-near-duplicates", action="store_true")

    reject = commands.add_parser("reject")
    reject.add_argument("proposal_id", type=uuid.UUID)
    return parser


def _result_id(app: AthenaApplication, identifier: uuid.UUID) -> uuid.UUID:
    view = app.research_promotion.result_view(identifier)
    value = view.get("result_id")
    if not isinstance(value, str):
        raise ValueError("ResearchResult view has no durable result_id")
    return uuid.UUID(value)


def _proposal_line(item: ResearchProposalRecord) -> str:
    return "\t".join(
        (
            str(item.proposal_id),
            str(item.ordinal),
            item.proposal_type.value,
            item.state.value,
            item.evidence_kind,
            str(item.evidence_ordinal) if item.evidence_ordinal is not None else "-",
            str(item.accepted_entity_id or "-"),
            item.payload_json.replace("\t", " ").replace("\r", " ").replace("\n", " "),
        )
    )


def _print_proposals(app: AthenaApplication, result_id: uuid.UUID) -> None:
    proposals = app.research_promotion.proposals_for_result(result_id)
    print(f"RESULT {result_id}")
    print(f"PROPOSAL_COUNT {len(proposals)}")
    for item in proposals:
        print("PROPOSAL\t" + _proposal_line(item))


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "result":
        view = app.research_promotion.result_view(args.identifier)
        print(json.dumps(view, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "proposals":
        _print_proposals(app, _result_id(app, args.identifier))
        return 0

    if args.command == "propose":
        result_id = _result_id(app, args.identifier)
        proposal_set = app.research_promotion.create_proposals(result_id)
        print(f"PROPOSAL_SET {proposal_set.proposal_set_id}")
        _print_proposals(app, result_id)
        return 0

    if args.command == "accept":
        accepted = app.research_promotion.accept(
            args.proposal_id,
            keep_separate_near_duplicates=args.keep_separate_near_duplicates,
        )
        print(f"ACCEPTED {accepted.proposal_id}")
        print(f"ENTITY {accepted.entity_id}")
        print(f"REVISION {accepted.revision_id}")
        print(f"COMMIT {accepted.commit_id}")
        return 0

    if args.command == "reject":
        rejected = app.research_promotion.reject(args.proposal_id)
        print(f"REJECTED {rejected.proposal_id}")
        print(f"STATE {rejected.state.value}")
        return 0

    raise RuntimeError(f"Unsupported ResearchResult desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"RESEARCH_RESULT_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
