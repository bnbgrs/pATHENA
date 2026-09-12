from subprocess import CompletedProcess
from unittest.mock import patch

from scripts import quality


def test_quality_gate_is_fail_fast_by_default() -> None:
    failed = CompletedProcess(args=("check",), returncode=7)

    with patch.object(quality.subprocess, "run", return_value=failed) as run:
        assert quality.main([]) == 7

    assert run.call_count == 1


def test_quality_gate_keep_going_runs_every_check() -> None:
    results = [
        CompletedProcess(args=("lock",), returncode=0),
        CompletedProcess(args=("spec",), returncode=0),
        CompletedProcess(args=("ruff",), returncode=0),
        CompletedProcess(args=("mypy",), returncode=7),
        CompletedProcess(args=("pytest",), returncode=0),
    ]

    with patch.object(quality.subprocess, "run", side_effect=results) as run:
        assert quality.main(["--keep-going"]) == 7

    assert run.call_count == len(quality.build_checks())
    assert [call.args[0] for call in run.call_args_list] == [
        check.command for check in quality.build_checks()
    ]
