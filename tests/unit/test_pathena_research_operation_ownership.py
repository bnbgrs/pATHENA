from __future__ import annotations

from athena.desktop.research_workspace import _operation_owns_selected_job


def test_research_operation_owns_only_the_same_selected_job() -> None:
    job_id = "11111111-1111-1111-1111-111111111111"

    assert _operation_owns_selected_job(job_id, job_id) is True
    assert (
        _operation_owns_selected_job(
            job_id,
            "22222222-2222-2222-2222-222222222222",
        )
        is False
    )


def test_unscoped_research_operation_never_owns_detail_selection() -> None:
    assert _operation_owns_selected_job(None, None) is False
    assert (
        _operation_owns_selected_job(
            None,
            "11111111-1111-1111-1111-111111111111",
        )
        is False
    )
