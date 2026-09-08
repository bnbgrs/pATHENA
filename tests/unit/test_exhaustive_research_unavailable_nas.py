from __future__ import annotations

from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.research.models import ResearchCandidateSetState, ResearchWorkState


def _capture_source(app: AthenaApplication, path: Path, text: str):
    path.write_text(text, encoding="utf-8", newline="")
    return app.sources.capture_file(path).source


def test_exhaustive_research_unavailable_scope_remains_unavailable_not_irrelevant(
    tmp_path: Path,
) -> None:
    app = AthenaApplication(settings=AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    try:
        sources = (
            _capture_source(app, tmp_path / "nas-online-a.txt", "reachable evidence a"),
            _capture_source(app, tmp_path / "nas-online-b.txt", "reachable evidence b"),
            _capture_source(app, tmp_path / "nas-offline.txt", "snapshot from NAS scope"),
        )

        job = app.research.enqueue_local(
            query="Evaluate all scoped evidence including the unavailable NAS source.",
            explicit_source_ids=tuple(source.source_id for source in sources),
        )
        candidate_set = app.research.freeze_candidates(job.job_id)

        assert candidate_set.state is ResearchCandidateSetState.FROZEN
        assert candidate_set.candidate_total == 3
        assert candidate_set.eligible_count == 3
        assert candidate_set.excluded_count == 0

        work = app.research.work_items(job.job_id)
        assert len(work) == 3
        work_by_source = {
            app.research_repository.get_candidate(item.candidate_id).source_id: item
            for item in work
        }
        assert set(work_by_source) == {source.source_id for source in sources}

        online_a = work_by_source[sources[0].source_id]
        online_b = work_by_source[sources[1].source_id]
        nas_offline = work_by_source[sources[2].source_id]

        app.research.mark_work_state(
            online_a.work_item_id,
            state=ResearchWorkState.SUCCESSFUL,
        )
        app.research.mark_work_state(
            online_b.work_item_id,
            state=ResearchWorkState.IRRELEVANT,
        )
        unavailable = app.research.mark_work_state(
            nas_offline.work_item_id,
            state=ResearchWorkState.UNAVAILABLE,
        )
        assert unavailable.work_item_id == nas_offline.work_item_id
        assert unavailable.state is ResearchWorkState.UNAVAILABLE

        coverage = app.research.coverage(job.job_id)
        assert coverage.candidate_total == 3
        assert coverage.eligible_count == 3
        assert coverage.processed_count == 3
        assert coverage.successful_count == 1
        assert coverage.irrelevant_count == 1
        assert coverage.failed_count == 0
        assert coverage.unavailable_count == 1
        assert coverage.coverage_ratio == 2 / 3
        assert coverage.coverage_ratio < 1.0

        scope = app.research.initialize(job.job_id)
        assert scope.unavailable_count == 1
        assert scope.irrelevant_count == 1
        assert scope.coverage_ratio == coverage.coverage_ratio

        persisted = {
            item.work_item_id: item.state for item in app.research.work_items(job.job_id)
        }
        assert persisted[nas_offline.work_item_id] is ResearchWorkState.UNAVAILABLE
        assert persisted[nas_offline.work_item_id] is not ResearchWorkState.IRRELEVANT
    finally:
        app.stop()
