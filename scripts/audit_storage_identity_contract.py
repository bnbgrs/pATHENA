"""Fail-closed diagnostics for the open BE-046 and BE-052 identity boundaries.

This helper never mutates Storage product code. It inspects the current source
shape and emits stable findings plus acceptance cases for Backend/Error workers.
The signatures intentionally track the *current* implementation rather than
historical helper names, so refactors do not silently turn the detector green.
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


def _line_of(source: str, token: str, *, start: int = 0) -> int | None:
    offset = source.find(token, start)
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

    ensure = _function_body(reserve_source, "ensure")
    release = _function_body(reserve_source, "release")
    start = _function_body(database_source, "start")

    findings: list[str] = []
    evidence: dict[str, dict[str, object]] = {}

    # Current POSIX release validates the target through an open descriptor, then
    # closes that descriptor before unlinking the pathname relative to root_fd.
    # The parent directory remains bound, but the target name can still be
    # substituted between close() and unlink().
    release_posix_close = release.find("os.close(descriptor)")
    release_posix_unlink = release.find("os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)")
    if release_posix_close >= 0 and release_posix_unlink > release_posix_close:
        finding = "BE-046_POSIX_RELEASE_HANDLE_CLOSED_BEFORE_DIRFD_UNLINK"
        findings.append(finding)
        release_start = reserve_source.find("    def release(")
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "close_line": _line_of(
                reserve_source,
                "os.close(descriptor)",
                start=max(0, release_start),
            ),
            "unlink_line": _line_of(
                reserve_source,
                "os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)",
                start=max(0, release_start),
            ),
            "risk": "target handle is released before destructive dir-fd-relative pathname unlink",
        }

    # Current non-POSIX release reads size via pathname and then independently
    # unlinks that pathname. No handle-bound target identity survives the gap.
    if "size = self.path.stat(follow_symlinks=False).st_size" in release and "self.path.unlink()" in release:
        finding = "BE-046_WINDOWS_RELEASE_PATHNAME_NOT_BOUND_TO_TARGET_HANDLE"
        findings.append(finding)
        release_start = reserve_source.find("    def release(")
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "stat_line": _line_of(
                reserve_source,
                "size = self.path.stat(follow_symlinks=False).st_size",
                start=max(0, release_start),
            ),
            "unlink_line": _line_of(
                reserve_source,
                "self.path.unlink()",
                start=max(0, release_start),
            ),
            "risk": "non-POSIX release performs destructive pathname unlink without a bound target handle",
        }

    # Failure cleanup on non-POSIX compares the current pathname to the created
    # handle identity, but the handle is already closed and a second race remains
    # between samestat() and pathname unlink().
    if (
        "created_identity = os.fstat(descriptor)" in ensure
        and "os.path.samestat(" in ensure
        and "self.path.unlink()" in ensure
    ):
        finding = "BE-046_WINDOWS_CLEANUP_RECHECK_THEN_PATHNAME_UNLINK"
        findings.append(finding)
        ensure_start = reserve_source.find("    def ensure(")
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "identity_line": _line_of(
                reserve_source,
                "created_identity = os.fstat(descriptor)",
                start=max(0, ensure_start),
            ),
            "unlink_line": _line_of(
                reserve_source,
                "self.path.unlink()",
                start=max(0, ensure_start),
            ),
            "risk": "identity recheck and destructive pathname unlink are separate events after handle close",
        }

    # POSIX creation cleanup also closes the created target descriptor before the
    # name is unlinked relative to the still-bound parent directory.
    posix_ensure = _function_body(reserve_source, "_ensure_posix")
    if "os.close(descriptor)" in posix_ensure and "os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)" in posix_ensure:
        finding = "BE-046_POSIX_CLEANUP_HANDLE_CLOSED_BEFORE_DIRFD_UNLINK"
        findings.append(finding)
        posix_start = reserve_source.find("    def _ensure_posix(")
        evidence[finding] = {
            "file": str(reserve_path.relative_to(root)),
            "close_line": _line_of(
                reserve_source,
                "os.close(descriptor)",
                start=max(0, posix_start),
            ),
            "unlink_line": _line_of(
                reserve_source,
                "os.unlink(_RESERVE_FILENAME, dir_fd=root_fd)",
                start=max(0, posix_start),
            ),
            "risk": "failure cleanup can unlink a replacement name after the created target handle is closed",
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
            "id": "BE046_POSIX_RELEASE_SAME_PARENT_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "posix",
            "expected": "fail closed without deleting replacement file",
        },
        {
            "id": "BE046_POSIX_FAILURE_CLEANUP_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "posix",
            "expected": "cleanup never deletes a replacement object after created handle closes",
        },
        {
            "id": "BE046_WINDOWS_RELEASE_SAME_PARENT_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "windows",
            "expected": "fail closed without deleting replacement file",
        },
        {
            "id": "BE046_WINDOWS_FAILURE_CLEANUP_TARGET_REPLACEMENT",
            "owner": "Backend",
            "platform": "windows",
            "expected": "samestat recheck cannot be followed by deletion of a substituted object",
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
            "be046": "parent and target filesystem object identity remain bound through every destructive release/cleanup step",
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
