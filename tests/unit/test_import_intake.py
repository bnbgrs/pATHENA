from __future__ import annotations

import os
from pathlib import Path

import pytest

from athena.config.settings import AthenaSettings
from athena.core.application import AthenaApplication
from athena.source.import_intake import (
    ImportIntakeService,
    ImportOrigin,
    ImportPreflightBlockedError,
    ImportRequest,
    ImportRequestError,
    ImportState,
    SymlinkPolicy,
)


def _service(tmp_path: Path) -> tuple[AthenaApplication, ImportIntakeService]:
    app = AthenaApplication(AthenaSettings(local_root=tmp_path / "runtime"))
    app.start()
    return app, ImportIntakeService(sources=app.sources, paths=app.paths)


def test_import_request_payload_roundtrip_is_exact_and_bool_safe(tmp_path: Path) -> None:
    request = ImportRequest.from_paths(
        (tmp_path / "a.txt", tmp_path / "folder"),
        origin=ImportOrigin.DRAG_DROP,
        recursive=False,
        symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
        max_file_bytes=123,
        expected_count=2,
        temporary=False,
        do_not_store=False,
        include_system_metadata=True,
    )

    assert ImportRequest.from_payload(request.to_payload()) == request

    bad = request.to_payload()
    bad["recursive"] = 1
    with pytest.raises(ImportRequestError, match="recursive must be a bool"):
        ImportRequest.from_payload(bad)


def test_preflight_enumerates_deterministically_and_reports_system_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "input"
    nested = root / "nested"
    nested.mkdir(parents=True)
    (root / "b.txt").write_text("b", encoding="utf-8")
    (root / "A.txt").write_text("a", encoding="utf-8")
    (nested / "c.txt").write_text("c", encoding="utf-8")
    (root / ".DS_Store").write_bytes(b"metadata")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "cache.pyc").write_bytes(b"cache")

    app, service = _service(tmp_path)
    try:
        preflight = service.preflight(
            ImportRequest.from_paths((root,), origin=ImportOrigin.FOLDER)
        )

        assert not preflight.blocked
        assert [item.path.name for item in preflight.candidates] == [
            "A.txt",
            "b.txt",
            "c.txt",
        ]
        assert preflight.total_bytes == 3
        assert sum(issue.code == "filtered_system_metadata" for issue in preflight.issues) == 2
    finally:
        app.stop()


def test_default_symlink_policy_never_follows_links_and_reports_them(
    tmp_path: Path,
) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("target", encoding="utf-8")
    link = root / "link.txt"
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable in this environment")

    app, service = _service(tmp_path)
    try:
        preflight = service.preflight(ImportRequest.from_paths((root,)))
        assert not preflight.blocked
        assert [item.path for item in preflight.candidates] == [target.resolve()]
        assert any(
            issue.code == "filtered_link" and issue.path == link
            for issue in preflight.issues
        )
    finally:
        app.stop()


def test_follow_inside_root_deduplicates_target_and_never_crosses_boundary(
    tmp_path: Path,
) -> None:
    root = tmp_path / "input"
    root.mkdir()
    target = root / "target.txt"
    target.write_text("inside", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    inside_link = root / "inside-link.txt"
    outside_link = root / "outside-link.txt"
    try:
        os.symlink(target, inside_link)
        os.symlink(outside, outside_link)
    except (OSError, NotImplementedError):
        pytest.skip("symbolic links unavailable in this environment")

    app, service = _service(tmp_path)
    try:
        preflight = service.preflight(
            ImportRequest.from_paths(
                (root,),
                symlink_policy=SymlinkPolicy.FOLLOW_INSIDE_ROOT,
            )
        )
        assert not preflight.blocked
        assert [item.path for item in preflight.candidates] == [target.resolve()]
        assert any(issue.code == "duplicate_resolved_path" for issue in preflight.issues)
        assert any(issue.code == "filtered_link_outside_root" for issue in preflight.issues)
    finally:
        app.stop()


def test_size_and_storage_rules_block_before_any_source_commit(tmp_path: Path) -> None:
    root = tmp_path / "input"
    root.mkdir()
    large = root / "large.bin"
    large.write_bytes(b"1234")

    app, service = _service(tmp_path)
    try:
        request = ImportRequest.from_paths((root,), max_file_bytes=3)
        preflight = service.preflight(request)
        assert preflight.blocked
        assert any(issue.code == "file_exceeds_max_size" for issue in preflight.issues)
        with pytest.raises(ImportPreflightBlockedError):
            service.capture(request)
        assert app.sources.list() == ()

        do_not_store = ImportRequest.from_paths((large,), do_not_store=True)
        with pytest.raises(ImportPreflightBlockedError):
            service.capture(do_not_store)
        assert app.sources.list() == ()
    finally:
        app.stop()


def test_capture_imports_multiple_files_as_distinct_sources_in_plan_order(
    tmp_path: Path,
) -> None:
    root = tmp_path / "input"
    root.mkdir()
    first = root / "a.txt"
    second = root / "b.txt"
    first.write_text("same bytes", encoding="utf-8")
    second.write_text("same bytes", encoding="utf-8")

    app, service = _service(tmp_path)
    try:
        result = service.capture(
            ImportRequest.from_paths(
                (root,),
                origin=ImportOrigin.FOLDER,
                expected_count=2,
            )
        )

        assert result.state is ImportState.READY
        assert result.failures == ()
        assert [item.path for item in result.preflight.candidates] == [
            first.resolve(),
            second.resolve(),
        ]
        assert len(result.captures) == 2
        assert result.captures[0].source.source_id != result.captures[1].source.source_id
        assert result.captures[0].blob.blob_id == result.captures[1].blob.blob_id
        assert len(app.sources.list()) == 2
    finally:
        app.stop()
