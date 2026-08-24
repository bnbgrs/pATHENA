"""Process boundary for the native pATHENA SOURCES / FILES workspace.

The desktop must not invent a second ingestion pipeline.  This helper calls the
canonical SourceCaptureService, DurableSourceProcessingWorker and repositories in a
short-lived process so capture and SQLite work never block Qt's GUI thread.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from collections.abc import Sequence
from pathlib import Path

from athena.core.application import AthenaApplication
from athena.jobs.models import JobRecord, JobState
from athena.source.models import SourceRecord

_ACTIVE_JOB_STATES = frozenset(
    {
        JobState.QUEUED,
        JobState.WAITING,
        JobState.RUNNING,
        JobState.PAUSED,
        JobState.CANCEL_REQUESTED,
    }
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pathena-sources-desktop")
    commands = parser.add_subparsers(dest="command", required=True)

    import_parser = commands.add_parser("import")
    import_parser.add_argument("path", type=Path)

    listing = commands.add_parser("list")
    listing.add_argument("--limit", type=int, default=100)

    show = commands.add_parser("show")
    show.add_argument("source_id", type=uuid.UUID)

    process = commands.add_parser("process")
    process.add_argument("source_id", type=uuid.UUID)
    return parser


def _scope_source_id(job: JobRecord) -> uuid.UUID | None:
    if not job.requested_scope_json:
        return None
    try:
        scope = json.loads(job.requested_scope_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(scope, dict):
        return None
    raw_source_id = scope.get("source_id")
    if not isinstance(raw_source_id, str):
        return None
    try:
        return uuid.UUID(raw_source_id)
    except ValueError:
        return None


def _latest_source_job(
    app: AthenaApplication,
    source_id: uuid.UUID,
) -> JobRecord | None:
    matches = tuple(
        job
        for job in app.jobs.list(limit=500)
        if job.job_type == "source.process" and _scope_source_id(job) == source_id
    )
    if not matches:
        return None
    return max(
        matches,
        key=lambda job: (job.updated_at_us, job.created_at_us, str(job.job_id)),
    )


def _supports_processing(app: AthenaApplication, source: SourceRecord) -> bool:
    if source.protection_scope_id is not None:
        return False
    return any(
        service.supports(source)
        for service in (
            app.source_text,
            app.source_pdf,
            app.source_docx,
            app.source_html,
        )
    )


def _artifact_counts(
    app: AthenaApplication,
    source_id: uuid.UUID,
) -> tuple[int, int]:
    representations = app.source_text.list_for_source(source_id, limit=100)
    chunk_count = sum(
        app.source_chunks.count_for_representation(representation.representation_id)
        for representation, _blob in representations
    )
    return len(representations), chunk_count


def _readiness(
    *,
    latest_job: JobRecord | None,
    chunk_count: int,
) -> str:
    if chunk_count > 0:
        return "ready"
    if latest_job is None:
        return "captured"
    if latest_job.state is JobState.COMPLETED:
        return "repair_required"
    return str(latest_job.state.value)


def _safe_field(value: str | None, *, fallback: str = "-") -> str:
    if not value:
        return fallback
    return value.replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _print_list(app: AthenaApplication, *, limit: int) -> None:
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")

    for source, blob in app.sources.list(limit=limit):
        latest_job = _latest_source_job(app, source.source_id)
        representations, chunks = _artifact_counts(app, source.source_id)
        readiness = _readiness(latest_job=latest_job, chunk_count=chunks)
        job_state = "-" if latest_job is None else latest_job.state.value
        processable = "yes" if _supports_processing(app, source) else "no"
        print(
            "\t".join(
                (
                    str(source.source_id),
                    readiness,
                    job_state,
                    source.lifecycle_state.value,
                    _safe_field(source.original_name, fallback="<unnamed>"),
                    _safe_field(source.mime_type),
                    str(blob.byte_length),
                    processable,
                    str(representations),
                    str(chunks),
                )
            )
        )


def _print_show(app: AthenaApplication, source_id: uuid.UUID) -> None:
    source, blob = app.sources.get(source_id)
    latest_job = _latest_source_job(app, source_id)
    representations, chunks = _artifact_counts(app, source_id)
    readiness = _readiness(latest_job=latest_job, chunk_count=chunks)

    print(f"SOURCE {source.source_id}")
    print(f"NAME {_safe_field(source.original_name, fallback='<unnamed>')}")
    print(f"TYPE {source.source_type.value}")
    print(f"MIME {_safe_field(source.mime_type)}")
    print(f"BYTES {blob.byte_length}")
    print(f"URI {_safe_field(source.source_uri)}")
    print(f"CAPTURE_STATE {source.lifecycle_state.value}")
    print(f"RETRIEVAL_READINESS {readiness}")
    print(f"PROCESSABLE {'yes' if _supports_processing(app, source) else 'no'}")
    print(f"REPRESENTATIONS {representations}")
    print(f"CHUNKS {chunks}")
    if latest_job is None:
        print("PROCESS_JOB -")
        return
    print(f"PROCESS_JOB {latest_job.job_id}")
    print(f"PROCESS_STATE {latest_job.state.value}")
    print(f"PROCESS_STAGE {latest_job.current_stage or '-'}")
    print(f"PROCESS_RETRIES {latest_job.retry_count}")
    print(f"PROCESS_BLOCKED {latest_job.blocked_reason or '-'}")


def _queue_processing(
    app: AthenaApplication,
    source_id: uuid.UUID,
) -> JobRecord | None:
    source, _blob = app.sources.get(source_id)
    if not _supports_processing(app, source):
        raise ValueError(
            "Source has no deterministic desktop processing path; supported local "
            "formats are TXT/Markdown, PDF, DOCX and HTML."
        )

    _representations, chunks = _artifact_counts(app, source_id)
    if chunks > 0:
        return None

    latest_job = _latest_source_job(app, source_id)
    if latest_job is not None and latest_job.state in _ACTIVE_JOB_STATES:
        return latest_job
    return app.source_processing.enqueue(source_id)


def _run(app: AthenaApplication, args: argparse.Namespace) -> int:
    if args.command == "import":
        result = app.sources.capture_file(args.path)
        source = result.source
        print(f"SOURCE_CAPTURED {source.source_id}")
        print(f"NAME {_safe_field(source.original_name, fallback='<unnamed>')}")
        print(f"MIME {_safe_field(source.mime_type)}")
        print(f"BYTES {result.blob.byte_length}")
        if not _supports_processing(app, source):
            print("PROCESS_NOT_QUEUED unsupported_format")
            return 0
        job = _queue_processing(app, source.source_id)
        if job is None:
            print("PROCESS_NOT_QUEUED already_ready")
        else:
            print(f"PROCESS_QUEUED {job.job_id} {job.state.value}")
        return 0

    if args.command == "list":
        _print_list(app, limit=args.limit)
        return 0

    if args.command == "show":
        _print_show(app, args.source_id)
        return 0

    if args.command == "process":
        job = _queue_processing(app, args.source_id)
        if job is None:
            print(f"PROCESS_NOT_QUEUED already_ready {args.source_id}")
        else:
            print(f"PROCESS_QUEUED {job.job_id} {job.state.value}")
        return 0

    raise RuntimeError(f"Unsupported sources desktop command: {args.command!r}")


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    app = AthenaApplication()
    try:
        app.start(run_startup_maintenance=False)
        return _run(app, args)
    except Exception as exc:
        print(f"SOURCES_ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    finally:
        try:
            app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
