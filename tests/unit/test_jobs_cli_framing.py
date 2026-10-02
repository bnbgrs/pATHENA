from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from athena.desktop.jobs_cli import _print_list, _scope_summary, _single_line


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("alpha\rbravo", "alpha bravo"),
        ("alpha\nbravo", "alpha bravo"),
        ("alpha\r\nbravo", "alpha bravo"),
        ("alpha\tbravo", "alpha bravo"),
        ("alpha\vbravo", "alpha bravo"),
        ("alpha\fbravo", "alpha bravo"),
        ("alpha\x1cbravo", "alpha bravo"),
        ("alpha\x85bravo", "alpha bravo"),
        ("alpha\u2028bravo", "alpha bravo"),
        ("alpha\u2029bravo", "alpha bravo"),
    ],
)
def test_single_line_removes_python_splitlines_boundaries(
    value: str,
    expected: str,
) -> None:
    assert _single_line(value) == expected


def test_scope_summary_sanitizes_preferred_value_line_framing() -> None:
    raw = json.dumps(
        {
            "query": "first\rsecond\tthird\u2028fourth",
            "source_id": "source-1",
        }
    )

    summary = _scope_summary(raw)

    assert summary == "query=first second third fourth source_id=source-1"
    assert "\t" not in summary
    assert summary.splitlines() == [summary]


def test_scope_summary_sanitizes_fallback_keys_and_values() -> None:
    raw = json.dumps(
        {
            "custom\rkey": "value\npart",
            "other\tkey": "other\u2029part",
        }
    )

    summary = _scope_summary(raw)

    assert summary == "custom key=value part other key=other part"
    assert "\t" not in summary
    assert summary.splitlines() == [summary]


def test_scope_summary_sanitizes_invalid_json_diagnostics() -> None:
    summary = _scope_summary("{not-json\r\nwith-tab\tvalue")

    assert summary == "{not-json with-tab value"
    assert "\t" not in summary
    assert summary.splitlines() == [summary]


def test_print_list_keeps_untrusted_scope_inside_one_tsv_record(
    capsys: pytest.CaptureFixture[str],
) -> None:
    job = SimpleNamespace(
        job_id="11111111-1111-1111-1111-111111111111",
        state=SimpleNamespace(value="queued"),
        priority=1,
        job_type="research.exhaustive",
        current_stage=None,
        retry_count=0,
        updated_at_us=123,
        requested_scope_json=json.dumps(
            {
                "query": "line one\rline two\u2028line three",
            }
        ),
    )
    app = SimpleNamespace(
        jobs=SimpleNamespace(
            list=lambda *, limit: (job,),
        )
    )

    _print_list(app, limit=150)  # type: ignore[arg-type]

    output = capsys.readouterr().out
    records = output.splitlines()
    assert len(records) == 1
    fields = records[0].split("\t")
    assert len(fields) == 8
    assert fields[-1] == "query=line one line two line three"
