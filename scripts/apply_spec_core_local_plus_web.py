from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 exact match, found {count}")
    return text.replace(old, new, 1)


def patch_service() -> None:
    path = Path("src/athena/research/service.py")
    text = path.read_text(encoding="utf-8")
    marker = "\n    def enqueue_scoped_project(\n"
    method = """
    def enqueue_local_plus_web(
        self,
        *,
        query: str,
        authorization_id: uuid.UUID,
        captured_source_ids: Sequence[uuid.UUID],
        priority: JobPriority = JobPriority.NORMAL,
        coverage_target: float = 1.0,
        requested_model_id: str | None = None,
        context_limit: int | None = None,
        output_reserve: int | None = None,
        safety_margin: int | None = None,
        max_hierarchy_depth: int = DEFAULT_MAX_HIERARCHY_DEPTH,
    ) -> JobRecord:
        if not isinstance(authorization_id, uuid.UUID):
            raise ResearchConfigurationError(
                "Local plus Web Research requires an authorization_id UUID."
            )
        normalized_sources = _stable_uuids(captured_source_ids)
        if not normalized_sources:
            raise ResearchConfigurationError(
                "Local plus Web Research requires captured external Sources."
            )
        internet_scope = {
            "authorization_id": str(authorization_id),
            "captured_source_ids": [str(item) for item in normalized_sources],
        }
        return self._enqueue(
            mode=ResearchMode.LOCAL_PLUS_WEB,
            query=query,
            priority=priority,
            domains=(),
            project_ids=(),
            source_types=(),
            explicit_source_ids=normalized_sources,
            time_start_us=None,
            time_end_us=None,
            coverage_target=coverage_target,
            requested_model_id=requested_model_id,
            context_limit=context_limit,
            output_reserve=output_reserve,
            safety_margin=safety_margin,
            max_hierarchy_depth=max_hierarchy_depth,
            internet_scope=internet_scope,
        )
"""
    text = replace_once(text, marker, method + marker, "service method insertion")
    text = replace_once(
        text,
        """        safety_margin: int | None,
        max_hierarchy_depth: int,
    ) -> JobRecord:
""",
        """        safety_margin: int | None,
        max_hierarchy_depth: int,
        internet_scope: Mapping[str, object] | None = None,
    ) -> JobRecord:
""",
        "service _enqueue signature",
    )
    text = replace_once(
        text,
        '                "internet_scope": None,\n',
        '                "internet_scope": internet_scope,\n',
        "service internet scope persistence",
    )
    path.write_text(text, encoding="utf-8")


def patch_validation() -> None:
    path = Path("src/athena/jobs/payload_validation.py")
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    if mode not in {"local_exhaustive", "scoped_project", "historical_backfill"}:\n',
        """    if mode not in {
        "local_exhaustive",
        "scoped_project",
        "local_plus_web",
        "historical_backfill",
    }:
""",
        "validator mode set",
    )
    text = replace_once(
        text,
        '    _canonical_uuid_list(scope, "explicit_source_ids", label=label)\n',
        """    explicit_source_ids = _canonical_uuid_list(
        scope, "explicit_source_ids", label=label
    )
""",
        "validator explicit source ids",
    )
    text = replace_once(
        text,
        """    if scope.get("internet_scope") is not None:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive local mode requires internet_scope to be null."
        )
""",
        """    internet_scope = scope.get("internet_scope")
    if mode == "local_plus_web":
        if not isinstance(internet_scope, Mapping):
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive local_plus_web mode requires internet_scope."
            )
        _require_exact_keys(
            internet_scope,
            {"authorization_id", "captured_source_ids"},
            label="research.exhaustive internet_scope",
        )
        authorization_id = internet_scope.get("authorization_id")
        if not isinstance(authorization_id, str):
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive internet_scope authorization_id must be UUID text."
            )
        try:
            if str(uuid.UUID(authorization_id)) != authorization_id:
                raise ValueError
        except ValueError as exc:
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive internet_scope authorization_id must be canonical UUID text."
            ) from exc
        captured_source_ids = internet_scope.get("captured_source_ids")
        if not isinstance(captured_source_ids, list) or not captured_source_ids:
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive local_plus_web mode requires captured_source_ids."
            )
        if captured_source_ids != sorted(set(captured_source_ids)):
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive captured_source_ids must be sorted and unique."
            )
        for source_id in captured_source_ids:
            if not isinstance(source_id, str):
                raise BuiltinJobPayloadValidationError(
                    "research.exhaustive captured_source_ids must contain UUID text."
                )
            try:
                if str(uuid.UUID(source_id)) != source_id:
                    raise ValueError
            except ValueError as exc:
                raise BuiltinJobPayloadValidationError(
                    "research.exhaustive captured_source_ids must contain canonical UUID text."
                ) from exc
        if captured_source_ids != explicit_source_ids:
            raise BuiltinJobPayloadValidationError(
                "research.exhaustive Local+Web captured Sources must match explicit_source_ids."
            )
    elif internet_scope is not None:
        raise BuiltinJobPayloadValidationError(
            "research.exhaustive non-Web modes require internet_scope to be null."
        )
""",
        "validator internet scope",
    )
    start = text.index("def _canonical_uuid_list(")
    end = text.index("\n\ndef _equal_text(", start)
    block = text[start:end]
    if ") -> None:" not in block:
        raise SystemExit("canonical UUID helper signature drifted")
    block = block.replace(") -> None:", ") -> list[str]:", 1)
    if "return canonical" in block:
        raise SystemExit("canonical UUID helper already returns a value")
    block = block.rstrip() + "\n    return canonical"
    text = text[:start] + block + text[end:]
    path.write_text(text, encoding="utf-8")


def patch_gateway() -> None:
    path = Path("src/athena/external/gateway.py")
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    """Capture explicit external URLs first, then freeze them through normal local Research."""\n',
        '    """Capture authorized external URLs first, then enqueue truthful Local+Web Research."""\n',
        "external research docstring",
    )
    text = replace_once(
        text,
        """        return self.research.enqueue_local(
            query=query,
            explicit_source_ids=source_ids,
""",
        """        return self.research.enqueue_local_plus_web(
            query=query,
            authorization_id=authorization_id,
            captured_source_ids=source_ids,
""",
        "external research delegation",
    )
    path.write_text(text, encoding="utf-8")


def write_tests() -> None:
    path = Path("tests/unit/test_research_local_plus_web.py")
    if path.exists():
        raise SystemExit("Local+Web acceptance file already exists unexpectedly")
    path.write_text(
        '''from __future__ import annotations

import uuid

import pytest

from athena.core.application import AthenaApplication
from athena.research.service import ResearchConfigurationError


def test_local_plus_web_persists_truthful_authorized_capture_scope(tmp_path) -> None:
    app = AthenaApplication(tmp_path / "athena.db")
    authorization_id = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b001")
    source_a = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b010")
    source_b = uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b011")

    job = app.research.enqueue_local_plus_web(
        query="compare captured external evidence with local knowledge",
        authorization_id=authorization_id,
        captured_source_ids=(source_b, source_a, source_a),
    )

    persisted = app.jobs.get(job.job_id)
    assert persisted.requested_scope["mode"] == "local_plus_web"
    assert persisted.requested_scope["explicit_source_ids"] == [
        str(source_a),
        str(source_b),
    ]
    assert persisted.requested_scope["internet_scope"] == {
        "authorization_id": str(authorization_id),
        "captured_source_ids": [str(source_a), str(source_b)],
    }


def test_local_plus_web_fails_before_persistence_without_captured_sources(tmp_path) -> None:
    app = AthenaApplication(tmp_path / "athena.db")
    before = tuple(app.jobs.list_jobs())

    with pytest.raises(
        ResearchConfigurationError,
        match="requires captured external Sources",
    ):
        app.research.enqueue_local_plus_web(
            query="web research",
            authorization_id=uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b001"),
            captured_source_ids=(),
        )

    assert tuple(app.jobs.list_jobs()) == before


def test_local_plus_web_rejects_non_uuid_authorization_before_persistence(tmp_path) -> None:
    app = AthenaApplication(tmp_path / "athena.db")
    before = tuple(app.jobs.list_jobs())

    with pytest.raises(
        ResearchConfigurationError,
        match="authorization_id UUID",
    ):
        app.research.enqueue_local_plus_web(
            query="web research",
            authorization_id="not-an-authorization",  # type: ignore[arg-type]
            captured_source_ids=(
                uuid.UUID("018f8f31-1f2e-7b37-8a66-a9e28735b010"),
            ),
        )

    assert tuple(app.jobs.list_jobs()) == before
''',
        encoding="utf-8",
    )


def main() -> None:
    patch_service()
    patch_validation()
    patch_gateway()
    write_tests()


if __name__ == "__main__":
    main()
