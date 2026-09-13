from __future__ import annotations

from athena.desktop.workspace_detail_presenter import (
    format_job_show,
    format_research_show,
    format_source_show,
)


def test_format_research_show_groups_scope_and_work_items_without_losing_values() -> None:
    raw = "\n".join(
        (
            "JOB 11111111-1111-1111-1111-111111111111",
            "STATE running",
            "STAGE discovery",
            "QUERY local provenance",
            "RETRIES 1",
            "BLOCKED -",
            "SCOPE 22222222-2222-2222-2222-222222222222",
            "SCOPE_STATE frozen",
            "SNAPSHOT_COMMIT 42",
            "MODEL local-model",
            "COVERAGE 0.750",
            "COUNTS eligible=4 processed=3 successful=3 irrelevant=0 failed=0 unavailable=0 excluded=0",
            "WORK_ITEMS 1",
            "WORK 33333333-3333-3333-3333-333333333333 state=running attempts=2 processing=- analysis=44444444-4444-4444-4444-444444444444",
            "FUTURE_FIELD future-value",
        )
    )

    rendered = format_research_show(raw)

    assert rendered.startswith("RESEARCH RUN\nJob: 11111111-1111-1111-1111-111111111111")
    assert "\nSCOPE\nScope: 22222222-2222-2222-2222-222222222222" in rendered
    assert "Coverage: 0.750" in rendered
    assert "\nWORK ITEMS\nWork items: 1" in rendered
    assert "• 33333333-3333-3333-3333-333333333333 state=running attempts=2" in rendered
    assert "FUTURE_FIELD future-value" in rendered


def test_format_job_show_preserves_multiline_json_and_checkpoint_diagnostics() -> None:
    raw = "\n".join(
        (
            "JOB aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "TYPE source.process",
            "STATE running",
            "PRIORITY 10 (NORMAL)",
            "STAGE chunk",
            "RETRIES 0",
            "BLOCKED -",
            "CREATED_AT_US 100",
            "UPDATED_AT_US 200",
            "NEXT_RUN_AT_US -",
            "WORKER worker-1",
            "LEASE_ACQUIRED_AT_US 150",
            "LEASE_EXPIRES_AT_US 250",
            "HEARTBEAT_AT_US 190",
            "FENCING_SEQUENCE 3",
            "PROCESSING_RUN run-7",
            "LAST_CHECKPOINT cp-1",
            "PROTECTION_SCOPE -",
            "PROTECTED_PAYLOAD -",
            "REQUESTED_SCOPE {",
            '  "source_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"',
            "}",
            "PINNED_CONFIGURATION {",
            '  "model": "local"',
            "}",
            "CHECKPOINTS 1",
            "CHECKPOINT cp-1 created_at_us=175 fence=3 commit=99",
            '  PROGRESS {"chunks": 4}',
            '  RESUME {"offset": 4}',
            "FUTURE_JOB_FIELD retained",
        )
    )

    rendered = format_job_show(raw)

    assert rendered.startswith("JOB\nJob: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    assert "\nEXECUTION\nWorker: worker-1" in rendered
    assert "\nREQUESTED SCOPE\n{" in rendered
    assert '  "source_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"' in rendered
    assert "\nPINNED CONFIGURATION\n{" in rendered
    assert "\nCHECKPOINTS\nCheckpoints: 1" in rendered
    assert "• cp-1 created_at_us=175 fence=3 commit=99" in rendered
    assert '  Progress: {"chunks": 4}' in rendered
    assert '  Resume: {"offset": 4}' in rendered
    assert "FUTURE_JOB_FIELD retained" in rendered


def test_format_source_show_groups_retrieval_and_processing_without_losing_values() -> None:
    raw = "\n".join(
        (
            "SOURCE cccccccc-cccc-cccc-cccc-cccccccccccc",
            "NAME notes.md",
            "TYPE file",
            "MIME text/markdown",
            "BYTES 4096",
            "URI file:///notes.md",
            "CAPTURE_STATE captured",
            "RETRIEVAL_READINESS ready",
            "PROCESSABLE yes",
            "REPRESENTATIONS 1",
            "CHUNKS 8",
            "PROCESS_JOB dddddddd-dddd-dddd-dddd-dddddddddddd",
            "PROCESS_STATE completed",
            "PROCESS_STAGE done",
            "PROCESS_RETRIES 0",
            "PROCESS_BLOCKED -",
            "FUTURE_SOURCE_FIELD visible",
        )
    )

    rendered = format_source_show(raw)

    assert rendered.startswith("SOURCE\nSource: cccccccc-cccc-cccc-cccc-cccccccccccc")
    assert "URI: file:///notes.md" in rendered
    assert "\nCAPTURE & RETRIEVAL\nCapture state: captured" in rendered
    assert "Retrieval readiness: ready" in rendered
    assert "\nPROCESSING\nProcess job: dddddddd-dddd-dddd-dddd-dddddddddddd" in rendered
    assert "FUTURE_SOURCE_FIELD visible" in rendered


def test_formatters_keep_empty_output_unchanged() -> None:
    assert format_research_show("") == ""
    assert format_job_show("   \n") == "   \n"
    assert format_source_show("") == ""
