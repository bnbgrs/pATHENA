from __future__ import annotations

import argparse
import uuid
from types import SimpleNamespace

from athena.desktop.research_results_cli import _run


class _Promotion:
    def __init__(self) -> None:
        self.result_id = uuid.uuid4()
        self.job_id = uuid.uuid4()
        self.proposal_id = uuid.uuid4()
        self.accept_calls: list[bool] = []
        self.reject_calls = 0

    def result_view(self, identifier: uuid.UUID):
        assert identifier in {self.job_id, self.result_id}
        return {
            "result_id": str(self.result_id),
            "job_id": str(self.job_id),
            "query": "What changed?",
            "scope_state": "completed",
            "content": {"summary": "Evidence-backed summary"},
            "evidence": {"findings": [], "contradictions": []},
        }

    def create_proposals(self, result_id: uuid.UUID):
        assert result_id == self.result_id
        return SimpleNamespace(proposal_set_id=uuid.uuid4())

    def proposals_for_result(self, result_id: uuid.UUID):
        assert result_id == self.result_id
        return (
            SimpleNamespace(
                proposal_id=self.proposal_id,
                ordinal=0,
                proposal_type=SimpleNamespace(value="knowledge"),
                state=SimpleNamespace(value="pending"),
                evidence_kind="summary",
                evidence_ordinal=None,
                accepted_entity_id=None,
                payload_json='{"body":"Evidence-backed summary"}',
            ),
        )

    def accept(self, proposal_id: uuid.UUID, *, keep_separate_near_duplicates: bool = False):
        assert proposal_id == self.proposal_id
        self.accept_calls.append(keep_separate_near_duplicates)
        return SimpleNamespace(
            proposal_id=proposal_id,
            entity_id=uuid.uuid4(),
            revision_id=uuid.uuid4(),
            commit_id=uuid.uuid4(),
        )

    def reject(self, proposal_id: uuid.UUID):
        assert proposal_id == self.proposal_id
        self.reject_calls += 1
        return SimpleNamespace(
            proposal_id=proposal_id,
            state=SimpleNamespace(value="rejected"),
        )


def test_result_and_proposal_workflow_is_explicit(capsys) -> None:
    promotion = _Promotion()
    app = SimpleNamespace(research_promotion=promotion)

    assert _run(
        app,
        argparse.Namespace(command="result", identifier=promotion.job_id),
    ) == 0
    result = capsys.readouterr().out
    assert str(promotion.result_id) in result
    assert "Evidence-backed summary" in result

    assert _run(
        app,
        argparse.Namespace(command="propose", identifier=promotion.job_id),
    ) == 0
    proposed = capsys.readouterr().out
    assert "PROPOSAL_SET" in proposed
    assert f"PROPOSAL\t{promotion.proposal_id}" in proposed

    assert _run(
        app,
        argparse.Namespace(command="proposals", identifier=promotion.job_id),
    ) == 0
    listed = capsys.readouterr().out
    assert "PROPOSAL_COUNT 1" in listed
    assert "knowledge\tpending\tsummary" in listed

    assert _run(
        app,
        argparse.Namespace(
            command="accept",
            proposal_id=promotion.proposal_id,
            keep_separate_near_duplicates=False,
        ),
    ) == 0
    assert "ACCEPTED" in capsys.readouterr().out

    assert _run(
        app,
        argparse.Namespace(
            command="accept",
            proposal_id=promotion.proposal_id,
            keep_separate_near_duplicates=True,
        ),
    ) == 0
    capsys.readouterr()
    assert promotion.accept_calls == [False, True]

    assert _run(
        app,
        argparse.Namespace(command="reject", proposal_id=promotion.proposal_id),
    ) == 0
    rejected = capsys.readouterr().out
    assert "REJECTED" in rejected
    assert promotion.reject_calls == 1

class _Comparison:
    def __init__(self, payload: dict[str, object] | None) -> None:
        self.payload = payload
        self.previous_calls: list[uuid.UUID] = []
        self.explicit_calls: list[tuple[uuid.UUID, uuid.UUID]] = []

    def compare_previous(self, identifier: uuid.UUID):
        self.previous_calls.append(identifier)
        if self.payload is None:
            return None
        return SimpleNamespace(as_dict=lambda: self.payload)

    def compare(self, identifier: uuid.UUID, *, baseline_identifier: uuid.UUID):
        self.explicit_calls.append((identifier, baseline_identifier))
        if self.payload is None:
            raise AssertionError("explicit comparison requires a payload")
        return SimpleNamespace(as_dict=lambda: self.payload)


def test_compare_command_surfaces_real_delta_or_honest_unavailable_state(capsys) -> None:
    promotion = _Promotion()
    payload = {
        "available": True,
        "comparison_mode": "exact_persisted_text_and_provenance",
        "query": "What changed?",
        "baseline": {},
        "current": {},
        "changes": {},
    }
    comparison = _Comparison(payload)
    app = SimpleNamespace(
        research_promotion=promotion,
        research_comparison=comparison,
    )

    assert _run(
        app,
        argparse.Namespace(
            command="compare",
            identifier=promotion.job_id,
            baseline=None,
        ),
    ) == 0
    output = capsys.readouterr().out
    assert "exact_persisted_text_and_provenance" in output
    assert comparison.previous_calls == [promotion.job_id]

    baseline = uuid.uuid4()
    assert _run(
        app,
        argparse.Namespace(
            command="compare",
            identifier=promotion.job_id,
            baseline=baseline,
        ),
    ) == 0
    capsys.readouterr()
    assert comparison.explicit_calls == [(promotion.job_id, baseline)]

    unavailable = _Comparison(None)
    app.research_comparison = unavailable
    assert _run(
        app,
        argparse.Namespace(
            command="compare",
            identifier=promotion.job_id,
            baseline=None,
        ),
    ) == 0
    output = capsys.readouterr().out
    assert '"available": false' in output
    assert "No earlier comparable completed ResearchResult exists." in output

