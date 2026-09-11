"""Fail-closed diagnostics for the BE-046 and BE-052 identity boundaries.

This script intentionally does not modify Storage product code. It gives the
Backend/Error workers a machine-readable way to confirm whether the two known
pathname identity gaps are still present on a candidate tree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _function_body(source: str, name: str) -> str:
    marker = f"    def {name}("
    start = source.find(marker)
    if start < 0:
        return ""
    next_def = source.find("\n    def ", start + len(marker))
    return source[start:] if next_def < 0 else source[start:next_def]


def audit_storage_identity(root: Path) -> dict[str, object]:
    reserve_source = (root / "src/athena/storage/emergency_reserve.py").read_text(
        encoding="utf-8"
    )
    database_source = (root / "src/athena/storage/database.py").read_text(encoding="utf-8")

    posix = _function_body(reserve_source, "_unlink_reserve_posix")
    non_posix = _function_body(reserve_source, "_unlink_reserve_non_posix")
    start = _function_body(database_source, "start")

    findings: list[str] = []
    if "os.close(fd)" in posix and "record.path.unlink(" in posix:
        findings.append("BE-046_POSIX_FD_CLOSED_BEFORE_PATH_UNLINK")
    if "_capture_file_identity(record.path)" in non_posix and "record.path.unlink(" in non_posix:
        findings.append("BE-046_NONPOSIX_PATHNAME_UNLINK_AFTER_IDENTITY_CHECK")
    if "inspect_database_read_only(self.path)" in start and "sqlite3.connect(" in start:
        findings.append("BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN")

    return {
        "be046_open": any(item.startswith("BE-046") for item in findings),
        "be052_open": any(item.startswith("BE-052") for item in findings),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = audit_storage_identity(args.root)
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        for finding in report["findings"]:
            print(finding)
    return 2 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
