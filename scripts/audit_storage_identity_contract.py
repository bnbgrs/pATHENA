"""Fail-closed diagnostics for the BE-046 and BE-052 identity boundaries.

This is intentionally independent of Storage product code.  It turns the two
open identity-continuity defects into stable, machine-readable findings and
acceptance cases that Backend/Error workers can consume without duplicating
ownership of the actual product fix.
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


def _line_of(source: str, token: str) -> int | None:
    offset = source.find(token)
    if offset < 0:
        return None
    return source.count("\n", 0, offset) + 1


def audit_storage_identity(root: Path) -> dict[str, object]:
    reserve_path = root / "src/athena/storage/emergency_reserve.py"
    database_path = root / "src/athena/storage/database.py"
    recovery_path = root / "src/athena/storage/recovery.py"
    reserve_source = reserve_path.read_text(encoding="utf-8")
    database_source = database_path.read_text(encoding="utf-8")
    recovery_source = recovery_path.read_text(encoding="utf-8")

    posix = _function_body(reserve_source, "_unlink_reserve_posix")
    non_posix = _function_body(reserve_source, "_unlink_reserve_non_posix")
    start = _function_body(database_source, "start")

    findings: list[str] = []
    evidence: dict[str, dict[str, object]] = {}

    if "os.close(fd)" in posix and "record.path.unlink(" in posix:
        finding = "BE-046_POSIX_FD_CLOSED_BEFORE_PATH_UNLINK"
        findings.append(finding)
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "close_line": _line_of(reserve_source, "os.close(fd)"),
            "unlink_line": _line_of(reserve_source, "record.path.unlink("),
            "risk": "validated object handle is released before destructive pathname unlink",
        }

    if "_capture_file_identity(record.path)" in non_posix and "record.path.unlink(" in non_posix:
        finding = "BE-046_NONPOSIX_PATHNAME_UNLINK_AFTER_IDENTITY_CHECK"
        findings.append(finding)
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "identity_line": _line_of(reserve_source, "_capture_file_identity(record.path)"),
            "risk": "pathname identity check and destructive pathname unlink remain separate events",
        }

    if "inspect_database_read_only(self.path)" in start and "sqlite3.connect(" in start:
        finding = "BE-052_PREFLIGHT_IDENTITY_NOT_BOUND_TO_WRITER_OPEN"
        findings.append(finding)
        evidence[finding] = {
            "file": str(database_path.relative_to(root)),
            "preflight_line": _line_of(database_source, "inspect_database_read_only(self.path)"),
            "writer_open_line": _line_of(database_source, "connection = sqlite3.connect("),
            "risk": "read-only attestation is not carried into the independent writer open",
        }

    sidecars_attested = (
        "wal_present=os.path.lexists(wal_path)" in recovery_source
        and "shm_present=os.path.lexists(shm_path)" in recovery_source
    )
    preflight_result_dropped = (
        "inspect_database_read_only(self.path)" in start
        and "= inspect_database_read_only(self.path)" not in start
    )
    if sidecars_attested and preflight_result_dropped:
        finding = "BE-052_FILESET_SIDECAR_ATTESTATION_DROPPED_BEFORE_WRITER"
        findings.append(finding)
        evidence[finding] = {
            "file": str(recovery_path.relative_to(root)),
            "wal_attestation_line": _line_of(
                recovery_source, "wal_present=os.path.lexists(wal_path)"
            ),
            "shm_attestation_line": _line_of(
                recovery_source, "shm_present=os.path.lexists(shm_path)"
            ),
            "risk": "WAL/SHM state is attested but no file-set token survives to writer startup",
        }

    acceptance_cases = [
        {
            "id": "BE046_POSIX_SAME_PARENT_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "posix",
            "expected": "fail closed without deleting replacement file",
        },
        {
            "id": "BE046_WINDOWS_SAME_PARENT_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "windows",
            "expected": "fail closed without deleting replacement file",
        },
        {
            "id": "BE046_WINDOWS_PARENT_DIRECTORY_SUBSTITUTION",
            "owner": "Backend",
            "platform": "windows",
            "expected": "bound parent and target identity survive destructive step",
        },
        {
            "id": "BE052_WAL_APPEARS_AFTER_PREFLIGHT",
            "owner": "Backend",
            "platform": "all",
            "expected": "writer startup detects file-set change and fails closed",
        },
        {
            "id": "BE052_SHM_REPLACED_AFTER_PREFLIGHT",
            "owner": "Backend",
            "platform": "all",
            "expected": "writer startup detects file-set change and fails closed",
        },
        {
            "id": "BE052_PRIMARY_REPLACED_AFTER_PREFLIGHT",
            "owner": "Backend",
            "platform": "all",
            "expected": "writer cannot consume an object different from the attested primary database",
        },
    ]

    return {
        "be046_open": any(item.startswith("BE-046") for item in findings),
        "be052_open": any(item.startswith("BE-052") for item in findings),
        "findings": findings,
        "evidence": evidence,
        "acceptance_cases": acceptance_cases,
        "closure_contract": {
            "be046": "filesystem object identity remains bound through destructive release",
            "be052": "primary database plus WAL/SHM attestation remains bound through writer establishment",
        },
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
        for case in report["acceptance_cases"]:
            print(f"ACCEPTANCE {case['id']}: {case['expected']}")
    return 2 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
