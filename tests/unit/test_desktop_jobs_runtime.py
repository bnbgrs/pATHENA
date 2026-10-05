from __future__ import annotations

from athena.desktop import jobs_cli
from athena.desktop.jobs_lifecycle import parse_current_progress


def test_compact_progress_summary_uses_persisted_values_without_fake_percentage() -> None:
    summary = jobs_cli._compact_progress_summary(
        '{"processed":347,"phase":"indexing","total":null}'
    )
    assert summary == '{"phase":"indexing","processed":347,"total":null}'
    assert "%" not in summary


def test_parse_current_progress_is_fail_closed_for_missing_checkpoint_progress() -> None:
    assert parse_current_progress("JOB abc\nCURRENT_PROGRESS -\nCHECKPOINTS 0\n") is None
    assert parse_current_progress("JOB abc\nCHECKPOINTS 0\n") is None


def test_parse_current_progress_reads_exact_cli_projection() -> None:
    output = 'JOB abc\nCURRENT_PROGRESS {"phase":"indexing","processed":347}\n'
    assert parse_current_progress(output) == '{"phase":"indexing","processed":347}'
