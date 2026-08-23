# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.
Status: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`.
Last queue refresh: 2026-08-23.

## Active / ready work

### BE-028 — Clone/journal migration before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: clone-first stack is implemented: migration metadata/free-space preflight, SQLite Online Backup clone, durable phase journal, exclusive migration lock, full integrity/FK/version verification, rollback-preserving activation, orphan/journal recovery boundaries and Windows junction/reparse hardening. Read-only startup planning, candidate-only schema execution, emergency reserve provisioning and `StorageBootstrapService` are wired before protected/database-dependent services. POSIX durable replace, durable byte publication and durable mkdir are now parent-directory-FD bound. Remaining work is Windows HANDLE-equivalent publication, candidate SQLite pathname binding and the Alembic-vs-custom architecture decision.
- Components: migration storage stack, `storage/durable_fs.py`, `core/application.py`, targeted tests.
- Dependencies: BE-027/029/031/032/033/034/035/040 DONE; BE-036/038/039 active.
- Last verification: 2026-08-23 current remote; new workflow evidence remains pending/cancelled, so no green gate is claimed.

### BE-036 — Close migration parent-replacement TOCTOU
- Priority: P1
- Status: IN_PROGRESS
- Evidence: POSIX `durable_replace()` is directory-FD bound; `durable_write_bytes()` binds temp creation/publication to one parent FD; `MigrationJournalStore.publish()` uses it; and POSIX `durable_mkdir()` now creates children relative to an opened parent FD and detects parent replacement before successful return. Deterministic tests replace parents during `os.replace`, `os.open`, and `os.mkdir` and verify attacker replacement paths are not mutated. Cross-platform closure still requires BE-038 and BE-039.
- Components: `storage/durable_fs.py`, `storage/migration_journal.py`, migration activation, `tests/unit/test_durable_fs_parent_identity.py`.
- Dependencies: BE-028; BE-035 DONE.
- Last verification: 2026-08-23 current remote after commit `c894c4f`; its quality-gate run is pending, no pass claimed.

### BE-038 — Windows HANDLE-bound durable filesystem publication
- Priority: P1
- Status: READY
- Evidence: Windows still uses pathname-based `MoveFileExW` after static reparse checks. A race-closing solution needs source/destination directory/file HANDLE identity bound through the mutation, not only post-checks.
- Components: `storage/durable_fs.py`, Windows-only deterministic race tests, migration journal/activation consumers.
- Dependencies: BE-036 POSIX primitives implemented.
- Last verification: 2026-08-23 current remote.

### BE-039 — Bind migration SQLite clone destination to parent identity
- Priority: P1
- Status: READY
- Evidence: `create_migration_clone()` still calls `sqlite3.connect(candidate_path)` after pathname/reparse checks. Parent replacement between check and SQLite open can redirect candidate creation. No false fix via repeated checks: requires an SQLite-compatible identity-bound strategy or explicit platform primitive.
- Components: `storage/migration_clone.py`, migration coordinator, deterministic parent-replacement tests.
- Dependencies: BE-036 shared identity primitives; platform-specific solution may be required.
- Last verification: 2026-08-23 current remote trace of `migration_clone.py`.

### BE-020 — Runtime ModelSignature drift guard in generation
- Priority: P1
- Status: READY
- Evidence: reusable revision-aware guard exists; shared `chat/generation.py` still uses older inline comparison.
- Components: chat generation/signature guard/tests.
- Dependencies: safe mutation window for shared generation file; do not blind-replace.

### BE-021 — ContextPackage temperature conversion overflow
- Priority: P2
- Status: READY
- Evidence: extreme JSON integer can escape the ContextPackage error contract via `float()` OverflowError.
- Components: `retrieval/context_package.py`, tests.
- Dependencies: safe mutation window for shared ContextPackage file; do not blind-replace.

## Recently completed backend/storage slices

### BE-041 — Verify SQLite runtime connection policy
- Priority: P1
- Status: DONE
- Evidence: new `storage/connection_policy.py` validates a bounded 5,000–120,000 ms busy timeout, applies `foreign_keys=ON`, configured `busy_timeout`, and `trusted_schema=OFF`, then fails closed unless readback exactly confirms all three. `SQLiteDatabase` accepts the bounded timeout, uses it for `sqlite3.connect()` and reapplies/verifies the policy after schema initialization. Focused unit tests cover limits and the real database-start path.
- Components: `storage/connection_policy.py`, `storage/database.py`, `tests/unit/test_sqlite_connection_policy.py`.
- Dependencies: none.
- Last verification: 2026-08-23 current remote after `4fe780f`; associated quality-gate run was cancelled, so tests are added but not claimed executed.

### BE-040 — Bind POSIX durable mkdir to parent identity
- Priority: P1
- Status: DONE
- Evidence: POSIX directory creation now uses `os.mkdir(..., dir_fd=opened_parent_fd)`, fsyncs the same parent handle and fails closed if the logical parent pathname no longer names that handle. `exist_ok` inspects the child relative to the bound parent without following links. Race and nested-creation regressions added.
- Components: `storage/durable_fs.py`, `tests/unit/test_durable_fs_parent_identity.py`.
- Dependencies: BE-036.
- Last verification: 2026-08-23 current remote after `c894c4f`; quality-gate run pending, no pass claimed.

### BE-034 — Bound migration journal reads before JSON decode
- Priority: P2
- Status: DONE
- Evidence: journal reads/writes are capped at 64 KiB and use opened-handle identity/regular-file verification with bounded reads.
- Components: `storage/migration_journal.py`, resource-bound tests.
- Last verification: 2026-08-23 current remote; no new green gate claimed.

### BE-035 — Bind migration lock to migration-root identity
- Priority: P1
- Status: DONE
- Evidence: lock lives in the migration root parent and fences original root filesystem identity before/after the critical section; deterministic replacement regression exists.
- Components: `storage/migration_lock.py`, tests.
- Last verification: 2026-08-23 current remote.

### BE-029 — Physically allocated Emergency Reserve
- Priority: P1
- Status: DONE
- Evidence: physical non-sparse reserve sizing, durable persistence, explicit release and normal-shutdown retention implemented.

### BE-030 — Disk-pressure state controller and runtime write gate
- Priority: P1
- Status: DONE
- Evidence: runtime canonical writes are gated before `BEGIN IMMEDIATE`; EMERGENCY releases only reserve then latches read-only safe mode.

### BE-031 — Candidate-only schema executor
- Priority: P1
- Status: DONE
- Evidence: schema engine runs only against clone candidate with current-version, checkpoint, DELETE-journal and no-sidecar requirements.

### BE-032 — Read-only startup migration planner
- Priority: P1
- Status: DONE
- Evidence: preflight maps missing/current DB to no-op and legacy schema to exact clone-required descriptor; unsupported versions fail closed.

### BE-033 — Integrate safe storage bootstrap ordering
- Priority: P1
- Status: DONE
- Evidence: RuntimeLayout -> preflight/recovery -> EmergencyReserve -> clone migration -> live DB startup is wired as the first application lifecycle service.

### BE-037 — Bound backup deletion-ledger resource usage
- Priority: P2
- Status: DONE
- Evidence: no-follow bounded record/head reads plus record-count, per-record, head and aggregate byte ceilings; publication enforces matching limits.

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
