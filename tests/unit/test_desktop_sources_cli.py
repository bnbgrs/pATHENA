from __future__ import annotations

import argparse
import re
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.desktop.sources_cli import (
    _artifact_counts,
    _latest_source_job,
    _readiness,
    _run,
)
from athena.jobs.models import JobState

_SOURCE_ID_RE = re.compile(r"^SOURCE_CAPTURED\s+([0-9a-fA-F-]{36})$", re.MULTILINE)


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def _source_id(output: str) -> str:
    match = _SOURCE_ID_RE.search(output)
    assert match is not None
    return match.group(1)


def test_desktop_source_import_queues_processing_and_becomes_ready(
    tmp_path: Path,
    capsys,
) -> None:
    app = _app(tmp_path / "runtime")
    source_path = tmp_path / "notes.md"
    source_path.write_text(
        "pATHENA retrieval-ready desktop source marker.\n\n" + ("context " * 120),
        encoding="utf-8",
    )

    try:
        result = _run(
            app,
            argparse.Namespace(command="import", path=source_path),
        )
        assert result == 0
        imported = capsys.readouterr().out
        source_id_text = _source_id(imported)
        assert "PROCESS_QUEUED" in imported

        source_id = app.sources.list(limit=1)[0][0].source_id
        assert str(source_id) == source_id_text
        job = _latest_source_job(app, source_id)
        assert job is not None
        assert job.state is JobState.QUEUED

        completed = app.source_processing.run_to_completion(
            job.job_id,
            worker_id="desktop-source-test",
            lease_seconds=60,
        )
        assert completed.done is True
        assert completed.job.state is JobState.COMPLETED

        representations, chunks = _artifact_counts(app, source_id)
        assert representations == 1
        assert chunks >= 1
        latest = _latest_source_job(app, source_id)
        assert latest is not None
        assert _readiness(latest_job=latest, chunk_count=chunks) == "ready"

        _run(app, argparse.Namespace(command="list", limit=10))
        listing = capsys.readouterr().out
        assert f"{source_id}\tready\tcompleted\t" in listing
        assert "notes.md" in listing
    finally:
        app.stop()


def test_desktop_source_import_leaves_unsupported_binary_captured(
    tmp_path: Path,
    capsys,
) -> None:
    app = _app(tmp_path / "runtime")
    source_path = tmp_path / "payload.bin"
    source_path.write_bytes(b"\x00\x01\x02\xffbinary")

    try:
        result = _run(
            app,
            argparse.Namespace(command="import", path=source_path),
        )
        assert result == 0
        output = capsys.readouterr().out
        assert "PROCESS_NOT_QUEUED unsupported_format" in output

        source_id = app.sources.list(limit=1)[0][0].source_id
        assert _latest_source_job(app, source_id) is None
        representations, chunks = _artifact_counts(app, source_id)
        assert representations == 0
        assert chunks == 0
        assert _readiness(latest_job=None, chunk_count=0) == "captured"
    finally:
        app.stop()


def test_desktop_source_process_reuses_existing_active_job(
    tmp_path: Path,
    capsys,
) -> None:
    app = _app(tmp_path / "runtime")
    source_path = tmp_path / "duplicate.md"
    source_path.write_text("Do not queue duplicate active processing jobs.", encoding="utf-8")

    try:
        _run(app, argparse.Namespace(command="import", path=source_path))
        capsys.readouterr()
        source_id = app.sources.list(limit=1)[0][0].source_id
        first = _latest_source_job(app, source_id)
        assert first is not None

        _run(app, argparse.Namespace(command="process", source_id=source_id))
        output = capsys.readouterr().out
        assert f"PROCESS_QUEUED {first.job_id} queued" in output

        source_jobs = [
            job
            for job in app.jobs.list(limit=500)
            if job.job_type == "source.process"
        ]
        assert [job.job_id for job in source_jobs] == [first.job_id]
    finally:
        app.stop()
