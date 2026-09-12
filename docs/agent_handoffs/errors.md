# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49` (`fix(storage): integrate fail-closed reserve release`).
- Error worker entered this run at `postmerge/errors@5464243058495896783116ccd3610311e4e823db`.
- Current workers: Spec/Core `52aaf68001bf141c779491ac005bb1d3e367700c`; Backend `b778b6af57f24f5edd19c699395c995818b959ed`; UI `0c1b746bf4e2060a9630258db49bca3a98b991cf`.
- Exact-current Develop canonical Quality: `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49 = IN_PROGRESS`; do not infer PASS/FAIL while it is running and do not start a competing run.
- Current Spec/Core, Backend and UI worker HEADs have no workflow runs attached to those exact SHAs.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0035`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0033`.
- STALE includes historical `ERR-0038` and `ERR-0039`.
- BLOCKED: none.

## Hard progress this run — ERR-0035 current-exact reproduction

### ERR-0035 — SQLite preflight-to-writer whole-file-set continuity

Status: `OPEN / P1 / Backend BE-052 owned`.

Fresh exact reproduction is now recorded on `develop/pathena-next@ca87e42c8820c47db7d6626feb17698560cd3b49`.

Current `src/athena/storage/recovery.py` blob `1bb6adaaccc3703b4334daa3ea753aae9d3cb3e7` performs the startup preflight. `inspect_database_read_only()` validates locality/path safety, checks DB plus WAL/SHM path type, opens the DB using SQLite `mode=ro`, validates application/schema metadata and `PRAGMA quick_check`, and then closes that read-only connection in `finally`. Its returned `DatabasePreflightReport` contains metadata plus boolean `wal_present` / `shm_present` observations, not a durable identity token for the SQLite file set.

Current `src/athena/storage/database.py` blob `aa6f8a285e8c730302441979ca4b26bb1646a0f1` then makes the gap explicit: `SQLiteDatabase.start()` invokes `inspect_database_read_only(self.path)` without retaining the report and subsequently establishes a separate writable `sqlite3.connect(self.path, ...)`. There is no carried descriptor/stat identity, DB/WAL/SHM identity token, or equivalent revalidation binding the accepted preflight objects to those used at writer establishment.

Therefore BE-052 remains current on an exact current Develop SHA: after the read-only inspection has completed and before the independent writer opens, the DB/WAL/SHM file set can change without any preflight identity continuity check. This is an attestation-continuity finding only; it is not a claim that arbitrary malformed WAL/SHM input would be accepted by SQLite.

Required bounded Backend fix remains: bind or fail-closed revalidate the primary DB plus WAL/SHM identity across the preflight→writer transition. Add focused adversarial coverage that pauses after accepted inspection, mutates/replaces/creates/removes a member of that file set before writer open, and proves startup rejects the identity change while preserving locality, schema, quick-check, Storage and Recovery guards. Do not merely run a second pathname-only preflight if it leaves another equivalent gap afterward.

Backend still owns BE-052, so Errors did not make a competing database/storage product patch.

### ERR-0033 — Emergency-reserve physical-reclamation/accounting continuity

Status remains `FIXED_PENDING_VERIFY / P1 / Backend BE-046 owned`.

The BE-046 fix is now integrated in current Develop `ca87e42c8820c47db7d6626feb17698560cd3b49`, but its exact integrated canonical Quality `34666307002` is still `IN_PROGRESS`. Do not mark `FIXED` until that existing run is consumed successfully; do not launch a competing run.

### ERR-0039 and ERR-0038

Both remain `STALE`; do not reopen without their own current exact-SHA reproductions.

## CI discipline

- `postmerge/errors@5464243058495896783116ccd3610311e4e823db` had zero workflow runs immediately before the ledger mutation.
- After ledger commit `378428614cfa5a6fa2813e773789c4e405860993`, `postmerge/errors` again had zero workflow runs before this handoff mutation.
- Errors started no canonical Quality run and did not mutate a branch with a queued/in-progress Error-worker run.
- Current Develop canonical `34666307002@ca87e42c8820c47db7d6626feb17698560cd3b49` remains in progress and was left untouched.

## Integrator handoff

- Develop: `ca87e42c8820c47db7d6626feb17698560cd3b49`; canonical `34666307002 = IN_PROGRESS`.
- Spec/Core: `52aaf68001bf141c779491ac005bb1d3e367700c`; no workflow run attached to this exact head.
- Backend: `b778b6af57f24f5edd19c699395c995818b959ed`; no workflow run attached to this exact head.
- UI: `0c1b746bf4e2060a9630258db49bca3a98b991cf`; no workflow run attached to this exact head.
- `ERR-0035 = OPEN / P1`: fresh current-exact reproduction on `ca87e42...`; Backend BE-052 must close the preflight→writer DB/WAL/SHM identity-continuity gap with focused adversarial evidence.
- `ERR-0033 = FIXED_PENDING_VERIFY / P1`: integrated on `ca87e42...`; consume canonical `34666307002` before final closure.
- `ERR-0039 = STALE`; `ERR-0038 = STALE`.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards and all Storage/Recovery/Security fail-closed invariants.
