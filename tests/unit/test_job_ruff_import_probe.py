from __future__ import annotations

import subprocess


def test_emit_exact_ruff_import_fix_diff() -> None:
    completed = subprocess.run(
        [
            "ruff",
            "check",
            "--select",
            "I001",
            "--fix",
            "--diff",
            "tests/unit/test_job_backup_deep_verify_worker.py",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    output = completed.stdout + completed.stderr
    raise AssertionError(output or "Ruff produced no import diff.")
