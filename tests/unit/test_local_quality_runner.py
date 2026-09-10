from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from scripts import quality as quality_script


def test_check_plan_matches_canonical_locked_environment() -> None:
    checks = quality_script.build_checks()
    prefix = ("uv", "run", "--locked", "--extra", "dev", "--extra", "desktop")

    assert [check.name for check in checks] == [
        "Dependency lock",
        "Specification validator",
        "Ruff",
        "mypy",
        "pytest",
    ]
    assert checks[0].command == ("uv", "lock", "--check")
    assert checks[1].command == (*prefix, "python", "scripts/validate_spec.py")
    assert checks[2].command == (
        *prefix,
        "python",
        "-m",
        "ruff",
        "check",
        "src",
        "tests",
        "scripts",
    )
    assert checks[3].command == (*prefix, "python", "-m", "mypy", "src/athena")
    assert checks[4].command == (*prefix, "python", "-m", "pytest")


def test_local_plan_is_present_in_canonical_quality_workflow() -> None:
    workflow = (
        quality_script.REPO_ROOT / ".github" / "workflows" / "quality.yml"
    ).read_text(encoding="utf-8")

    for check in quality_script.build_checks():
        command = " ".join(check.command)
        assert command in workflow

    assert "QT_QPA_PLATFORM: offscreen" in workflow


def test_main_runs_every_check_from_repo_root_with_offscreen_qt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[tuple[str, ...], Path, dict[str, str]]] = []

    def fake_run(
        command: tuple[str, ...],
        *,
        check: bool,
        cwd: Path,
        env: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        assert check is False
        calls.append((command, cwd, env))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.setattr(quality_script.subprocess, "run", fake_run)

    assert quality_script.main([]) == 0
    assert [command for command, _, _ in calls] == [
        check.command for check in quality_script.build_checks()
    ]
    assert all(cwd == quality_script.REPO_ROOT for _, cwd, _ in calls)
    assert all(env["QT_QPA_PLATFORM"] == "offscreen" for _, _, env in calls)


def test_explicit_qt_platform_is_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_run(
        command: tuple[str, ...],
        *,
        check: bool,
        cwd: Path,
        env: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        del check, cwd
        seen.append(env["QT_QPA_PLATFORM"])
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setenv("QT_QPA_PLATFORM", "windows")
    monkeypatch.setattr(quality_script.subprocess, "run", fake_run)

    assert quality_script.main([]) == 0
    assert seen == ["windows"] * len(quality_script.build_checks())


def test_default_mode_stops_at_first_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    returncodes = iter([0, 7])
    calls: list[tuple[str, ...]] = []

    def fake_run(
        command: tuple[str, ...],
        **_: Any,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, next(returncodes))

    monkeypatch.setattr(quality_script.subprocess, "run", fake_run)

    assert quality_script.main([]) == 7
    assert calls == [check.command for check in quality_script.build_checks()[:2]]


def test_keep_going_runs_all_checks_and_returns_first_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    returncodes = iter([0, 5, 0, 9, 0])
    calls: list[tuple[str, ...]] = []

    def fake_run(
        command: tuple[str, ...],
        **_: Any,
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, next(returncodes))

    monkeypatch.setattr(quality_script.subprocess, "run", fake_run)

    assert quality_script.main(["--keep-going"]) == 5
    assert calls == [check.command for check in quality_script.build_checks()]


def test_missing_uv_fails_with_command_not_found_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(command: tuple[str, ...], **_: Any) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError(command[0])

    monkeypatch.setattr(quality_script.subprocess, "run", fake_run)

    assert quality_script.main([]) == 127


def test_dry_run_works_from_outside_repository(tmp_path: Path) -> None:
    script = quality_script.REPO_ROOT / "scripts" / "quality.py"

    result = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert f"Repository root: {quality_script.REPO_ROOT}" in result.stdout
    assert "uv lock --check" in result.stdout
    assert "uv run --locked --extra dev --extra desktop python -m pytest" in result.stdout


def test_dry_run_has_no_subprocess_side_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_run(*_: Any, **__: Any) -> subprocess.CompletedProcess[str]:
        raise AssertionError("dry-run must not execute commands")

    monkeypatch.setattr(quality_script.subprocess, "run", fail_run)

    assert quality_script.main(["--dry-run"]) == 0
