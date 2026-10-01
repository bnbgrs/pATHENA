from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import athena.recovery_cli as recovery_cli
from athena.core.derived_recovery import (
    DerivedRecoveryError,
    DerivedRecoveryRequiredError,
)


class _FakeSettings:
    @classmethod
    def from_environment(cls) -> object:
        return object()


class _FakeRuntimePaths:
    database_path = Path("C:/athena-test/athena.db")
    derived_root = Path("C:/athena-test/derived")

    @classmethod
    def from_settings(cls, settings: object) -> _FakeRuntimePaths:
        del settings
        return cls()


def _install_runtime_stubs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        recovery_cli,
        "AthenaSettings",
        _FakeSettings,
    )
    monkeypatch.setattr(
        recovery_cli,
        "RuntimePaths",
        _FakeRuntimePaths,
    )


@pytest.mark.parametrize(
    ("target", "method_name", "expected_count", "result_name"),
    (
        (
            "canonical-fts",
            "rebuild_canonical_fts",
            11,
            "documents_indexed",
        ),
        (
            "archive-fts",
            "rebuild_archive_fts",
            12,
            "documents_indexed",
        ),
        (
            "canonical-hnsw",
            "rebuild_canonical_hnsw_from_persisted",
            2,
            "model_indexes_rebuilt",
        ),
        (
            "archive-hnsw",
            "rebuild_archive_hnsw_from_persisted",
            3,
            "model_indexes_rebuilt",
        ),
    ),
)
def test_rebuild_derived_dispatches_one_explicit_safe_target(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    target: str,
    method_name: str,
    expected_count: int,
    result_name: str,
) -> None:
    _install_runtime_stubs(monkeypatch)
    calls: list[str] = []

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            assert database_path == _FakeRuntimePaths.database_path
            assert derived_root == _FakeRuntimePaths.derived_root

        def rebuild_canonical_fts(self) -> int:
            calls.append("rebuild_canonical_fts")
            return 11

        def rebuild_archive_fts(self) -> int:
            calls.append("rebuild_archive_fts")
            return 12

        def rebuild_canonical_hnsw_from_persisted(self) -> int:
            calls.append("rebuild_canonical_hnsw_from_persisted")
            return 2

        def rebuild_archive_hnsw_from_persisted(self) -> int:
            calls.append("rebuild_archive_hnsw_from_persisted")
            return 3

    monkeypatch.setattr(
        recovery_cli,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    result = recovery_cli.run_rebuild_derived(target)

    assert result == 0
    assert calls == [method_name]

    captured = capsys.readouterr()
    assert captured.err == ""
    assert f"target={target}" in captured.out
    assert f"{result_name}={expected_count}" in captured.out
    assert "Normal ATHENA Core startup was bypassed." in captured.out
    assert "No model/provider call was used for this rebuild." in captured.out


def test_rebuild_derived_maps_broader_recovery_requirement_to_exit_four(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_runtime_stubs(monkeypatch)

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            del database_path, derived_root

        def rebuild_canonical_fts(self) -> int:
            raise DerivedRecoveryRequiredError(
                "canonical integrity is not sufficient"
            )

    monkeypatch.setattr(
        recovery_cli,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    result = recovery_cli.run_rebuild_derived(
        "canonical-fts"
    )

    assert result == 4
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ATHENA recovery required:" in captured.err
    assert "canonical integrity is not sufficient" in captured.err


def test_rebuild_derived_maps_rebuild_failure_without_claiming_recovery_required(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_runtime_stubs(monkeypatch)

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            del database_path, derived_root

        def rebuild_archive_fts(self) -> int:
            raise DerivedRecoveryError(
                "post-rebuild validation failed"
            )

    monkeypatch.setattr(
        recovery_cli,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    result = recovery_cli.run_rebuild_derived(
        "archive-fts"
    )

    assert result == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "ATHENA recovery rebuild error:" in captured.err
    assert "post-rebuild validation failed" in captured.err
    assert "ATHENA recovery required:" not in captured.err


@pytest.mark.parametrize(
    "error_type",
    (
        RuntimeError,
        ValueError,
    ),
)
def test_rebuild_derived_does_not_mask_unexpected_programming_failure(
    monkeypatch: pytest.MonkeyPatch,
    error_type: type[Exception],
) -> None:
    _install_runtime_stubs(monkeypatch)

    class FakeDerivedRecoveryService:
        def __init__(
            self,
            *,
            database_path: Path,
            derived_root: Path,
        ) -> None:
            del database_path, derived_root

        def rebuild_canonical_hnsw_from_persisted(self) -> int:
            raise error_type("unexpected implementation defect")

    monkeypatch.setattr(
        recovery_cli,
        "DerivedRecoveryService",
        FakeDerivedRecoveryService,
    )

    with pytest.raises(
        error_type,
        match="unexpected implementation defect",
    ):
        recovery_cli.run_rebuild_derived(
            "canonical-hnsw"
        )


def test_rebuild_derived_rejects_unknown_target_before_runtime_loading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invoked = SimpleNamespace(settings=False)

    class UnexpectedSettings:
        @classmethod
        def from_environment(cls) -> object:
            invoked.settings = True
            raise AssertionError("runtime should not load")

    monkeypatch.setattr(
        recovery_cli,
        "AthenaSettings",
        UnexpectedSettings,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported Derived Recovery rebuild target",
    ):
        recovery_cli.run_rebuild_derived(
            "everything"
        )

    assert invoked.settings is False


@pytest.mark.parametrize(
    "target",
    (
        "canonical-fts",
        "archive-fts",
        "canonical-hnsw",
        "archive-hnsw",
    ),
)
def test_recovery_parser_exposes_only_supported_derived_rebuild_targets(
    target: str,
) -> None:
    args = recovery_cli.build_parser().parse_args(
        [
            "rebuild-derived",
            target,
        ]
    )

    assert args.command == "rebuild-derived"
    assert args.target == target



def test_recovery_main_dispatches_derived_rebuild_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[str] = []

    def fake_rebuild(target: str) -> int:
        seen.append(target)
        return 17

    monkeypatch.setattr(
        recovery_cli,
        "run_rebuild_derived",
        fake_rebuild,
    )

    result = recovery_cli.main(
        [
            "rebuild-derived",
            "archive-hnsw",
        ]
    )

    assert result == 17
    assert seen == ["archive-hnsw"]
