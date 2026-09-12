"""Validate the Windows packaging/runtime release contract without building an EXE."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

_REQUIRED_WORKFLOW_TOKENS = (
    "runs-on: windows-latest",
    "tests/unit/test_packaged_app_dispatch.py",
    "tests/unit/test_packaged_process_launch.py",
    "tests/unit/test_windows_packaging_contract.py",
    "athena-local-smoke --restart-cycles 1",
    "athena-packaging-smoke --json",
)

_REQUIRED_PACKAGING_TEST_TOKENS = (
    '-Name "pATHENA"',
    "packaged_app.py",
    '-Name "pATHENA-Worker"',
    "packaged_worker.py",
    "pATHENA-Worker.exe",
    "--collect-all pypdf",
)


def validate_windows_release(root: Path) -> dict[str, object]:
    workflow = (root / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    contract_test = (root / "tests/unit/test_windows_packaging_contract.py").read_text(
        encoding="utf-8"
    )

    missing: list[str] = []
    for token in _REQUIRED_WORKFLOW_TOKENS:
        if token not in workflow:
            missing.append(f"workflow:{token}")
    for token in _REQUIRED_PACKAGING_TEST_TOKENS:
        if token not in contract_test:
            missing.append(f"packaging-test:{token}")
    if '"pypdf==' not in pyproject:
        missing.append("dependency:pypdf")
    if '"PySide6-Essentials==' not in pyproject:
        missing.append("desktop-dependency:PySide6-Essentials")

    return {
        "windows_runner": "runs-on: windows-latest" in workflow,
        "two_exe_contract": not any(item.startswith("packaging-test:") for item in missing),
        "pypdf_locked": '"pypdf==' in pyproject,
        "desktop_runtime_locked": '"PySide6-Essentials==' in pyproject,
        "missing": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_windows_release(args.root)
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        for key, value in report.items():
            print(f"{key}={value}")
    return 1 if report["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
