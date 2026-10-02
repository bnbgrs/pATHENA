from __future__ import annotations

import uuid
from pathlib import Path

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.retrieval.universal import UniversalSearchEntityType


def _started_app(root: Path) -> AthenaApplication:
    app = AthenaApplication(
        settings=AthenaSettings(
            local_root=root,
        )
    )
    app.start()
    return app


def test_universal_search_uses_real_application_schema_for_sources_and_jobs(
    tmp_path: Path,
) -> None:
    app = _started_app(tmp_path / "local")
    try:
        document = tmp_path / "Alpha field notes.txt"
        document.write_text("captured source bytes", encoding="utf-8")
        source = app.sources.capture_file(document).source

        job = app.jobs.create(
            job_type="backup.create",
            requested_scope={
                "schedule_slot_us": 0,
                "target_id": str(
                    uuid.UUID("11111111-1111-4111-8111-111111111111")
                ),
            },
            pinned_configuration={
                "pipeline_version": "backup-scheduler-v1",
                "quiet_hour_utc": 2,
            },
        )

        source_results = app.universal_search.search(
            "field alpha",
            entity_types=(UniversalSearchEntityType.SOURCE,),
        )
        assert len(source_results) == 1
        assert source_results[0].entity_id == source.source_id
        assert source_results[0].revision_id is None

        job_results = app.universal_search.search(
            "backup",
            entity_types=(UniversalSearchEntityType.JOB,),
        )
        assert len(job_results) == 1
        assert job_results[0].entity_id == job.job_id
        assert job_results[0].revision_id is None

        api_results = app.api.universal_search(
            "field alpha",
            entity_types=(UniversalSearchEntityType.SOURCE,),
        )
        assert len(api_results) == 1
        assert api_results[0].result_ref == f"source:{source.source_id}"
        assert api_results[0].revision_id is None
    finally:
        app.stop()
