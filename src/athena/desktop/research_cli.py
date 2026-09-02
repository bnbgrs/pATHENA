"""Small process boundary used by the native RESEARCH workspace.

The desktop keeps long-running database and model work out of Qt's GUI thread.  This
module deliberately calls the existing :class:`ResearchService` and durable job
repositories instead of reimplementing research semantics in the GUI.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Sequence

from athena.core.application import AthenaApplication
from athena.jobs.models import JobPriority


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-research-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    enqueue = commands.add_parser("enqueue")
    enqueue.add_argument("query")

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=100)

    show = commands.add_parser("show")
    show.add_argument("job_id", type=uuid.UUID)

    cancel = commands.add_parser("cancel")
    cancel.add_argument("job_id", type=uuid.UUID)
    return parser


def _query_for_job(job: object) -> str:
    raw = getattr(job, "requested_scope_json", None)
    if not raw:
        return ""
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if not isinstance(value, dict):
        return ""
    query = value.get("query")
    return query.strip() if isinstance(query, str) else ""


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")
    research_jobs = [
        job
        for job in app.jobs.list(limit=500)
        if job.job_type == "research.exhaustive"
    ][:limit]
    for job in research_jobs:
        scope = app.research_repository.get_scope_for_job(job.job_id)
        coverage = "-"
        if scope is not None:
            coverage = f"{scope.coverage_ratio:.3f}"
        query = _query_for_job(job).replace("\t", " ").replace("\n", " ")
        print(
            "\t".join(
                (
                    str(job.job_id),
                    job.state.value,
                    job.current_stage or "-",
                    coverage,
                    query,
                )
            )
        )


def _print_show(app: AthenaApplication, job_id: uuid.UUID) -> None:
    job = app.jobs.get(job_id)
    if job.job_type != "research.exhaustive":
        raise ValueError(f"Job {job_id} is not an exhaustive research job")

    print(f"JOB {job.job_id}")
    print(f"STATE {job.state.value}")
    print(f"STAGE {job.current_stage or '-'}")
    print(f"QUERY {_query_for_job(job) or '-'}")
    print(f"RETRIES {job.retry_count}")
    print(f"BLOCKED {job.blocked_reason or '-'}")

    scope = app.research_repository.get_scope_for_job(job_id)
    if scope is None:
        print("SCOPE pending initialization")
        return

    coverage = app.research_repository.coverage(scope.scope_id)
    print(f"SCOPE {scope.scope_id}")
    print(f"SCOPE_STATE {scope.state.value}")
    print(f"SNAPSHOT_COMMIT {scope.snapshot_commit_seq}")
    print(f"MODEL {scope.model_id or '-'}")
    print(f"COVERAGE {coverage.coverage_ratio:.3f}")
    print(
        "COUNTS "
        f"eligible={coverage.eligible_count} "
        f"processed={coverage.processed_count} "
        f"successful={coverage.successful_count} "
        f"irrelevant={coverage.irrelevant_count} "
        f"failed={coverage.failed_count} "
        f"unavailable={coverage.unavailable_count} "
        f"excluded={coverage.excluded_count}"
    )

    work_items = app.research_repository.list_work_items(scope.scope_id)
    print(f"WORK_ITEMS {len(work_items)}")
    for work in work_items:
        print(
            "WORK "
            f"{work.work_item_id} "
            f"state={work.state.value} "
            f"attempts={work.attempt_count} "
            f"processing={work.source_processing_job_id or '-'} "
            f"analysis={work.source_analysis_job_id or '-'}"
        )


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "enqueue":
        job = app.research.enqueue_local(
            query=args.query,
            priority=JobPriority.NORMAL,
        )
        print(f"JOB_QUEUED {job.job_id}")
        print(f"QUERY {_query_for_job(job)}")
        return 0

    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0

    if args.command == "show":
        _print_show(app, args.job_id)
        return 0

    if args.command == "cancel":
        job = app.research.cancel(args.job_id)
        print(f"JOB_CANCEL {job.job_id} {job.state.value}")
        return 0

    raise RuntimeError(f"Unsupported research desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"RESEARCH_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            # The command's original failure is more useful than a secondary
            # best-effort shutdown failure from a short-lived helper process.
            pass


if __name__ == "__main__":
    raise SystemExit(main())
