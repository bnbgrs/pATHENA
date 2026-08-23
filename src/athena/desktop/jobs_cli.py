"""Process boundary for the native JOBS workspace.

The Qt desktop observes and controls the canonical durable job repository from a
short-lived helper process so SQLite work never blocks the GUI thread.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Sequence
from typing import Any

from athena.core.application import AthenaApplication


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-jobs-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=150)

    for command in ("show", "pause", "resume", "cancel", "wake"):
        subparser = commands.add_parser(command)
        subparser.add_argument("job_id", type=uuid.UUID)

    return parser


def _scope_summary(raw: str | None) -> str:
    if not raw:
        return "-"
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return raw.replace("\t", " ").replace("\n", " ")[:120]

    if not isinstance(value, dict):
        return str(value).replace("\t", " ").replace("\n", " ")[:120]

    preferred_keys = (
        "query",
        "source_id",
        "analysis_id",
        "backup_id",
        "archive_root",
        "scope_id",
    )
    parts: list[str] = []
    for key in preferred_keys:
        item = value.get(key)
        if item is None:
            continue
        rendered = str(item).replace("\t", " ").replace("\n", " ").strip()
        if rendered:
            parts.append(f"{key}={rendered}")
        if len(parts) >= 2:
            break

    if not parts:
        parts = [
            f"{key}={str(item).replace(chr(9), ' ').replace(chr(10), ' ')}"
            for key, item in list(value.items())[:2]
        ]

    summary = " ".join(parts).strip() or "-"
    return summary[:160]


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    if limit < 1 or limit > 500:
        raise ValueError("limit must be between 1 and 500")

    for job in app.jobs.list(limit=limit):
        print(
            "\t".join(
                (
                    str(job.job_id),
                    job.state.value,
                    str(int(job.priority)),
                    job.job_type,
                    job.current_stage or "-",
                    str(job.retry_count),
                    str(job.updated_at_us),
                    _scope_summary(job.requested_scope_json),
                )
            )
        )


def _print_json_field(label: str, raw: str | None) -> None:
    if not raw:
        print(f"{label} -")
        return
    try:
        value: Any = json.loads(raw)
    except json.JSONDecodeError:
        print(f"{label} {raw}")
        return
    print(f"{label} {json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)}")


def _print_show(app: AthenaApplication, job_id: uuid.UUID) -> None:
    job = app.jobs.get(job_id)
    print(f"JOB {job.job_id}")
    print(f"TYPE {job.job_type}")
    print(f"STATE {job.state.value}")
    print(f"PRIORITY {int(job.priority)} ({job.priority.name})")
    print(f"STAGE {job.current_stage or '-'}")
    print(f"RETRIES {job.retry_count}")
    print(f"BLOCKED {job.blocked_reason or '-'}")
    print(f"CREATED_AT_US {job.created_at_us}")
    print(f"UPDATED_AT_US {job.updated_at_us}")
    print(f"NEXT_RUN_AT_US {job.next_run_at_us or '-'}")
    print(f"WORKER {job.worker_id or '-'}")
    print(f"LEASE_ACQUIRED_AT_US {job.lease_acquired_at_us or '-'}")
    print(f"LEASE_EXPIRES_AT_US {job.lease_expires_at_us or '-'}")
    print(f"HEARTBEAT_AT_US {job.heartbeat_at_us or '-'}")
    print(f"FENCING_SEQUENCE {job.fencing_sequence}")
    print(f"PROCESSING_RUN {job.processing_run_id or '-'}")
    print(f"LAST_CHECKPOINT {job.last_checkpoint_id or '-'}")
    print(f"PROTECTION_SCOPE {job.protection_scope_id or '-'}")
    print(f"PROTECTED_PAYLOAD {job.protected_payload_id or '-'}")
    _print_json_field("REQUESTED_SCOPE", job.requested_scope_json)
    _print_json_field("PINNED_CONFIGURATION", job.pinned_configuration_json)

    checkpoints = app.jobs.checkpoints(job_id)
    print(f"CHECKPOINTS {len(checkpoints)}")
    for checkpoint in checkpoints[-10:]:
        print(
            "CHECKPOINT "
            f"{checkpoint.checkpoint_id} "
            f"created_at_us={checkpoint.created_at_us} "
            f"fence={checkpoint.fencing_sequence} "
            f"commit={checkpoint.commit_id or '-'}"
        )
        if checkpoint.progress_state_json:
            print(f"  PROGRESS {checkpoint.progress_state_json}")
        if checkpoint.resume_metadata_json:
            print(f"  RESUME {checkpoint.resume_metadata_json}")


def _print_transition(label: str, job: object) -> None:
    job_id = getattr(job, "job_id")
    state = getattr(job, "state").value
    print(f"{label} {job_id} {state}")


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0
    if args.command == "show":
        _print_show(app, args.job_id)
        return 0
    if args.command == "pause":
        _print_transition("JOB_PAUSE", app.jobs.pause(args.job_id))
        return 0
    if args.command == "resume":
        _print_transition("JOB_RESUME", app.jobs.resume(args.job_id))
        return 0
    if args.command == "cancel":
        _print_transition("JOB_CANCEL", app.jobs.request_cancel(args.job_id))
        return 0
    if args.command == "wake":
        _print_transition("JOB_WAKE", app.jobs.wake(args.job_id))
        return 0
    raise RuntimeError(f"Unsupported jobs desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"JOBS_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
