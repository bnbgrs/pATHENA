from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.jobs.service import InvalidJobPayloadError


def _app(root: Path) -> AthenaApplication:
    app = AthenaApplication(settings=AthenaSettings(local_root=root))
    app.start(run_startup_maintenance=False)
    return app


def _scope() -> dict[str, object]:
    return {
        "source_id": str(uuid.uuid4()),
        "representation_id": str(uuid.uuid4()),
        "question": "Which claims are supported by this source?",
    }


def _config() -> dict[str, object]:
    return {
        "pipeline_version": "source-analysis-v1",
        "model_id": "test-model",
        "model_signature_id": str(uuid.uuid4()),
        "model_signature_sha256": "ab" * 32,
        "effective_context_limit": 8192,
        "output_reserve": 2048,
        "safety_margin": 256,
        "token_estimator": "utf8-bytes-div3-v1",
        "max_hierarchy_depth": 12,
        "prompt_template_id": "athena.source_analysis",
        "prompt_template_version": "1",
    }


def _source_analysis_job_count(app: AthenaApplication) -> int:
    return sum(job.job_type == "source.analyze" for job in app.jobs.list(limit=500))


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("effective_context_limit", True),
        ("output_reserve", True),
        ("safety_margin", False),
        ("max_hierarchy_depth", True),
        ("output_reserve", "2048"),
        ("safety_margin", 1.5),
    ),
)
def test_source_analysis_numeric_contract_rejects_invalid_types_before_persistence(
    tmp_path: Path,
    field: str,
    invalid: object,
) -> None:
    app = _app(tmp_path / f"runtime-{field}-{type(invalid).__name__}")
    try:
        before = _source_analysis_job_count(app)
        config = _config()
        config[field] = invalid

        with pytest.raises(InvalidJobPayloadError):
            app.jobs.create(
                job_type="source.analyze",
                requested_scope=_scope(),
                pinned_configuration=config,
            )

        assert _source_analysis_job_count(app) == before
    finally:
        app.stop()


def test_source_analysis_context_budget_is_rejected_before_persistence(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-budget")
    try:
        before = _source_analysis_job_count(app)
        config = _config()
        config["effective_context_limit"] = 1024
        config["output_reserve"] = 768
        config["safety_margin"] = 256

        with pytest.raises(InvalidJobPayloadError, match="input budget"):
            app.jobs.create(
                job_type="source.analyze",
                requested_scope=_scope(),
                pinned_configuration=config,
            )

        assert _source_analysis_job_count(app) == before
    finally:
        app.stop()


@pytest.mark.parametrize(
    ("field", "invalid"),
    (
        ("source_id", "not-a-uuid"),
        ("representation_id", ""),
        ("question", 7),
    ),
)
def test_source_analysis_scope_contract_is_rejected_before_persistence(
    tmp_path: Path,
    field: str,
    invalid: object,
) -> None:
    app = _app(tmp_path / f"runtime-scope-{field}")
    try:
        before = _source_analysis_job_count(app)
        scope = _scope()
        scope[field] = invalid

        with pytest.raises(InvalidJobPayloadError):
            app.jobs.create(
                job_type="source.analyze",
                requested_scope=scope,
                pinned_configuration=_config(),
            )

        assert _source_analysis_job_count(app) == before
    finally:
        app.stop()


def test_source_analysis_rejects_invalid_signature_and_unexpected_fields(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-signature")
    try:
        before = _source_analysis_job_count(app)
        config = _config()
        config["model_signature_sha256"] = "aa"

        with pytest.raises(InvalidJobPayloadError, match="SHA-256"):
            app.jobs.create(
                job_type="source.analyze",
                requested_scope=_scope(),
                pinned_configuration=config,
            )

        scope = _scope()
        scope["unexpected"] = "must-not-persist"
        with pytest.raises(InvalidJobPayloadError, match="unexpected or missing"):
            app.jobs.create(
                job_type="source.analyze",
                requested_scope=scope,
                pinned_configuration=_config(),
            )

        assert _source_analysis_job_count(app) == before
    finally:
        app.stop()


def test_valid_source_analysis_job_roundtrips_through_existing_decoder(
    tmp_path: Path,
) -> None:
    app = _app(tmp_path / "runtime-valid")
    try:
        config = _config()
        job = app.jobs.create(
            job_type="source.analyze",
            requested_scope=_scope(),
            pinned_configuration=config,
        )

        pinned = app.source_analysis_service.pinned_configuration(job)
        assert pinned.model_id == "test-model"
        assert pinned.effective_context_limit == 8192
        assert pinned.output_reserve == 2048
        assert pinned.safety_margin == 256
        assert pinned.max_hierarchy_depth == 12
        assert pinned.model_signature_hash == bytes.fromhex("ab" * 32)
    finally:
        app.stop()
