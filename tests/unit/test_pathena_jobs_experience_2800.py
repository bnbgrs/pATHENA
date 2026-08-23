from __future__ import annotations

from athena.desktop.pathena_jobs_experience_2800 import (
    UI_REFINEMENT_TASKS_2701_2800,
    _DETAIL_LABELS,
    _REFINEMENTS,
    _STYLESHEET,
    _TARGETS,
    _humanize_detail_text,
)


def test_jobs_experience_defines_exactly_one_hundred_unique_tasks() -> None:
    assert len(_TARGETS) == 20
    assert len(_REFINEMENTS) == 5
    assert len(UI_REFINEMENT_TASKS_2701_2800) == 100
    assert len(set(UI_REFINEMENT_TASKS_2701_2800)) == 100


def test_jobs_experience_covers_real_transition_and_inspection_surfaces() -> None:
    keys = {target.key for target in _TARGETS}
    assert {
        "jobsWorkspace",
        "jobsFilter",
        "schedulerStatus",
        "jobsStatus",
        "durableJobList",
        "jobsPrimarySplitter",
        "jobDetails",
        "jobsRefreshButton",
        "jobPauseButton",
        "jobResumeButton",
        "jobWakeButton",
        "jobCancelButton",
    } <= keys


def test_job_detail_humanizer_preserves_values_and_improves_labels() -> None:
    raw = "\n".join(
        (
            "JOB 1234",
            "STATE waiting",
            "STAGE fetch",
            "RETRIES 2",
            "LAST_CHECKPOINT abcd",
            "REQUESTED_SCOPE {\"query\":\"example\"}",
            "CHECKPOINT deadbeef created_at_us=42 fence=3 commit=-",
            "  PROGRESS {\"done\":1}",
        )
    )
    rendered = _humanize_detail_text(raw)
    assert "Job: 1234" in rendered
    assert "State: waiting" in rendered
    assert "Stage: fetch" in rendered
    assert "Retries: 2" in rendered
    assert "Last checkpoint: abcd" in rendered
    assert '{"query":"example"}' in rendered
    assert "Checkpoint · deadbeef" in rendered
    assert '{"done":1}' in rendered
    assert _DETAIL_LABELS["REQUESTED_SCOPE"] == "Requested scope"


def test_jobs_experience_keeps_quiet_workspace_contract() -> None:
    assert "#F26A21" in _STYLESHEET
    assert "#080808" in _STYLESHEET
    lowered = _STYLESHEET.lower()
    assert "glow" not in lowered
    assert "shadow" not in lowered
    assert "gradient" not in lowered
