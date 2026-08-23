# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.
Status: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`.
Last queue refresh: 2026-08-23.

## Active / ready work

### BE-028 — Clone/journal migration before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: clone-first startup, reserve, candidate migration, journal, lock, activation and recovery stack are implemented. POSIX durable replace/byte publication/directory creation are parent-FD bound; recovery artifact presence classification now uses no-follow file handles plus pathname/handle identity fencing. Remaining work is Windows HANDLE publication, SQLite clone destination binding and the Alembic-vs-custom decision.
- Components: migration storage stack, `storage/durable_fs.py`, `storage/migration_recovery.py`, `core/application.py`, tests.
- Dependencies: BE-027/029/031/032/033/034/035/040/042/043 DONE; BE-036/038/039 active.
- Last verification: 2026-08-23 current remote; latest focused storage gate exposed four stale durable-fs test contracts, corrected in `11811fd`; rerun evidence not yet available.

### BE-036 — Close migration parent-replacement TOCTOU
- Priority: P1
- Status: IN_PROGRESS
- Evidence: POSIX replace/write/mkdir mutations are bound to opened parent directory FDs and fail closed on parent identity drift. Recovery regular-file classification is also handle-bound. Deterministic race tests cover replace/open/mkdir plus recovery file replacement. Cross-platform closure still requires BE-038 and BE-039.
- Components: `storage/durable_fs.py`, `storage/migration_journal.py`, `storage/migration_recovery.py`, activation/recovery tests.
- Dependencies: BE-028; BE-035 DONE.
- Last verification: 2026-08-23. Focused gate on `c894c4f` ran 172 passing / 4 failing / 2 skipped storage tests; all four failures were outdated tests expecting pathname-based hooks and were updated in `11811fd` without weakening product semantics.

### BE-038 — Windows HANDLE-bound durable filesystem publication
- Priority: P1
- Status: READY
- Evidence: Windows still uses pathname-based `MoveFileExW` after static reparse checks. Race closure needs source/destination HANDLE identity bound through mutation.
- Components: `storage/durable_fs.py`, Windows-only race tests, migration consumers.
- Dependencies: BE-036 POSIX primitives implemented.
- Last verification: 2026-08-23 current remote; Windows path-safety job on the prior focused gate was green, but it does not prove HANDLE-bound race closure.

### BE-039 — Bind migration SQLite clone destination to parent identity
- Priority: P1
- Status: READY
- Evidence: `create_migration_clone()` still calls `sqlite3.connect(candidate_path)` after pathname/reparse checks. Repeated checks do not close parent replacement between validation and SQLite open.
- Components: `storage/migration_clone.py`, coordinator, deterministic race tests.
- Dependencies: BE-036; platform-specific SQLite-compatible strategy required.
- Last verification: 2026-08-23 current remote.

### BE-020 — Runtime ModelSignature drift guard in generation
- Priority: P1
- Status: READY
- Evidence: reusable revision-aware guard exists; shared `chat/generation.py` still uses older inline comparison.
- Components: chat generation/signature guard/tests.
- Dependencies: safe mutation window for shared generation file.

### BE-021 — ContextPackage temperature conversion overflow
- Priority: P2
- Status: READY
- Evidence: extreme JSON integer can escape the ContextPackage error contract via `float()` OverflowError.
- Components: `retrieval/context_package.py`, tests.
- Dependencies: safe mutation window for shared file.

## Recently completed backend/storage slices

### BE-043 — Handle-bound migration recovery artifact classification
- Priority: P1
- Status: DONE
- Evidence: recovery presence checks now open source/candidate/rollback with `O_NOFOLLOW` when available, require regular `fstat`, re-check boundaries, and compare opened-handle identity with `lstat` via `samestat`; replacement/disappearance during classification fails closed instead of mixing snapshots. Deterministic after-open replacement regression added and corrected to trigger at the intended second safety fence.
- Components: `storage/migration_recovery.py`, `tests/unit/test_migration_recovery.py`.
- Last verification: 2026-08-23 current remote after `12a9390` / `a02fb1d`; no green run yet.

### BE-042 — Recheck disk pressure immediately before live writer startup
- Priority: P1
- Status: DONE
- Evidence: after optional clone migration, bootstrap now performs a final `DiskPressureController.check()` before `SQLiteDatabase.start()`. If migration/other consumption pushed the volume into EMERGENCY, only the reserve is released, safe mode remains latched, and writable startup is refused even if release improves free space. Regression covers NORMAL at reserve provision -> EMERGENCY before writer -> post-release recovery headroom with writer still blocked.
- Components: `storage/bootstrap.py`, `tests/unit/test_storage_bootstrap.py`.
- Last verification: 2026-08-23 current remote after `62658b9` / `7a0d9fc`; no green run yet.

### BE-041 — Verify SQLite runtime connection policy
- Priority: P1
- Status: DONE
- Evidence: bounded 5,000–120,000 ms busy timeout; live connection applies and reads back `foreign_keys=ON`, exact `busy_timeout`, `trusted_schema=OFF`; mismatch fails closed. `SQLiteDatabase` uses the same timeout for connect and post-schema policy verification.
- Components: `storage/connection_policy.py`, `storage/database.py`, tests.
- Last verification: 2026-08-23; associated gate was cancelled, no pass claimed.

### BE-040 — Bind POSIX durable mkdir to parent identity
- Priority: P1
- Status: DONE
- Evidence: child creation uses `os.mkdir(..., dir_fd=opened_parent_fd)`, fsyncs that parent FD, and checks parent identity before return. Race and nested creation regressions exist.
- Components: `storage/durable_fs.py`, durable-fs tests.
- Last verification: focused gate on `c894c4f` showed product path working broadly but four old tests asserted pre-FD instrumentation. Tests were aligned in `11811fd`; rerun not yet observed.

### BE-034 — Bound migration journal reads before JSON decode
- Priority: P2
- Status: DONE
- Evidence: journal reads/writes capped at 64 KiB with handle identity and bounded reads.

### BE-035 — Bind migration lock to migration-root identity
- Priority: P1
- Status: DONE
- Evidence: parent-level lock plus root identity fencing before/after critical section.

### BE-029 — Physically allocated Emergency Reserve
- Priority: P1
- Status: DONE

### BE-030 — Disk-pressure state controller and runtime write gate
- Priority: P1
- Status: DONE

### BE-031 — Candidate-only schema executor
- Priority: P1
- Status: DONE

### BE-032 — Read-only startup migration planner
- Priority: P1
- Status: DONE

### BE-033 — Integrate safe storage bootstrap ordering
- Priority: P1
- Status: DONE

### BE-037 — Bound backup deletion-ledger resource usage
- Priority: P2
- Status: DONE

## Blocked / in-progress older slices

- BE-002 · P1 · BLOCKED — provider lifecycle/control adapter completion; shared LM Studio adapter ownership window required.
- BE-008 · P2 · BLOCKED — auditable primary-model switch needs durable audit contract.
- BE-009 · P2 · BLOCKED — provider request cancellation needs exact backend request-ID plumbing.
- BE-010 · P2 · IN_PROGRESS — generation numeric/control boundaries; shared generation path remains.
- BE-013 · P1 · BLOCKED — ModelSession exact provider binding remains.
- BE-014 · P1 · IN_PROGRESS — revision-aware ContextPackage/drift guard; generation integration remains.
- BE-015 · P1 · BLOCKED — provider failure taxonomy mapping needs adapter ownership.
- BE-016 · P1 · IN_PROGRESS — protected retrieval execution exists; explicit protected generation/persistence policy remains.
- BE-019 · P2 · BLOCKED — provider identity canonicalization must be atomic with adapter parsing.

## Completed / stale reference

- BE-001 DONE — normative provider health states.
- BE-003 DONE — normalized provider capabilities.
- BE-004 DONE — Context Builder source diversity.
- BE-005 STALE — provider-aware dynamic token accounting already present.
- BE-006 DONE — active primary ModelRegistry.
- BE-007 DONE — model load ownership.
- BE-011 DONE — BlobStore/durable FS symlink+junction confinement.
- BE-012 DONE — provider-observed model revision in signatures.
- BE-017 DONE — ModelSession cancellation invariants.
- BE-018 DONE — UUIDv7 clock-range guard.
- BE-022 DONE — persistent wall-clock int64 guard.
- BE-023 DONE — Unicode line-control rejection in schema IDs.
- BE-024 DONE — runtime mutation lock identity/permissions.
- BE-025 DONE — backup target lock identity.
- BE-026 DONE — reject network-backed active SQLite state.
- BE-027 DONE — clone-migration metadata/free-space contract.
