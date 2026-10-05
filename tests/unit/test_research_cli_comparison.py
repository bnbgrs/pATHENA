from __future__ import annotations

import json
import uuid
from types import SimpleNamespace

from athena.desktop.research_cli import _parser, _print_compare_previous

JOB_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
BASELINE_JOB_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


class _Comparison:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls: list[uuid.UUID] = []

    def compare_previous(self, job_id: uuid.UUID):
        self.calls.append(job_id)
        return self.value


class _Delta:
    def as_dict(self) -> dict[str, object]:
        return {
            "available": True,
            "comparison_mode": "exact_persisted_text_and_provenance",
            "query": "What changed?",
            "baseline": {
                "result_id": "31111111-1111-1111-1111-111111111111",
                "job_id": str(BASELINE_JOB_ID),
                "snapshot_commit_seq": 10,
                "model_signature_id": None,
                "coverage_ratio": 0.5,
                "summary": "Before",
                "uncertainty": "",
            },
            "current": {
                "result_id": "41111111-1111-1111-1111-111111111111",
                "job_id": str(JOB_ID),
                "snapshot_commit_seq": 20,
                "model_signature_id": None,
                "coverage_ratio": 1.0,
                "summary": "After",
                "uncertainty": "",
            },
            "changes": {
                "summary_changed": True,
                "uncertainty_changed": False,
                "model_signature_changed": False,
                "added_findings": ["Added"],
                "removed_findings": [],
                "added_contradictions": [],
                "removed_contradictions": [],
                "added_source_ids": [],
                "removed_source_ids": [],
            },
        }


def _payload(output: str) -> dict[str, object]:
    prefix = "RESEARCH_COMPARE "
    assert output.startswith(prefix)
    return json.loads(output[len(prefix) :])


def test_compare_previous_cli_emits_exact_service_delta(capsys) -> None:
    comparison = _Comparison(_Delta())
    app = SimpleNamespace(research_comparison=comparison)

    _print_compare_previous(app, JOB_ID)  # type: ignore[arg-type]

    assert comparison.calls == [JOB_ID]
    payload = _payload(capsys.readouterr().out.strip())
    assert payload["available"] is True
    assert payload["comparison_mode"] == "exact_persisted_text_and_provenance"
    assert payload["query"] == "What changed?"


def test_compare_previous_cli_emits_explicit_unavailable_state(capsys) -> None:
    comparison = _Comparison(None)
    app = SimpleNamespace(research_comparison=comparison)

    _print_compare_previous(app, JOB_ID)  # type: ignore[arg-type]

    payload = _payload(capsys.readouterr().out.strip())
    assert payload == {
        "available": False,
        "comparison_mode": "exact_persisted_text_and_provenance",
        "current_job_id": str(JOB_ID),
    }


def test_research_cli_parser_accepts_compare_previous_job_identity() -> None:
    args = _parser().parse_args(["compare-previous", str(JOB_ID)])

    assert args.command == "compare-previous"
    assert args.job_id == JOB_ID
