# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.
Status: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`.
Last queue refresh: 2026-08-23.

## Active / ready work

### BE-028 — Clone/journal migration before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: clone-first stack is implemented: migration metadata/free-space preflight, SQLite Online Backup clone, durable phase journal, exclusive migration lock, full integrity/FK/version verification, rollback-preserving activation, orphan/journal recovery boundaries and Windows junction/reparse hardening. Read-only startup planning, candidate-only schema execution, emergency reserve provisioning and ordered `StorageBootstrapService` routing are implemented. Remaining work is the security hardening tracked as BE-034/035/036 plus the Alembic-vs-custom architecture decision.
- Components: `migration_safety.py`, `migration_clone.py`, `migration_journal.py`, `migration_lock.py`, `migration_activation.py`, `migration_coordinator.py`, `migration_executor.py`, `migration_plan.py`, `bootstrap.py` and tests.
- Dependencies: BE-027/029/031/032/033 DONE.
- Last verification: 2026-08-23; product routing is present on current remote. Targeted tests exist but were not executed in this automation runtime because `github.com` DNS resolution failed from the isolated container.

### BE-034 — Bound migration journal reads before JSON decode
- Priority: P2
- Status: READY
- Evidence: Security SEC-010 requires a conservative byte ceiling for `migration_state.json`, enforced with `fstat()` before full read/JSON decode while preserving no-follow and handle/path identity checks.
- Components: `storage/migration_journal.py`, targeted corruption/oversize tests.
- Dependencies: BE-028 migration journal.
- Last verification: 2026-08-23 security handoff in BE-028.

### BE-035 — Bind migration lock to migration-root identity
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Security SEC-013 requires migration-lock ownership to remain bound to the same migration-root identity for the full critical section; root rename/replacement must not permit a second logical migration at the same pathname.
- Components: `storage/migration_lock.py`, deterministic replacement-race tests including Windows reparse behavior where available.
- Dependencies: BE-028 migration lock.
- Last verification: 2026-08-23 current remote confirms the lock file still lives inside the replaceable migration root.

### BE-036 — Close migration parent-replacement TOCTOU
- Priority: P1
- Status: READY
- Evidence: Security SEC-009 requires clone/journal creation, cleanup and activation to bind filesystem decisions to directory/object identity across sensitive operations rather than relying only on pre-operation pathname/reparse checks.
- Components: migration clone/journal/activation filesystem boundaries and deterministic parent-replacement race tests.
- Dependencies: BE-028; coordinate carefully with BE-035 because both touch migration-root identity.
- Last verification: 2026-08-23 security handoff in BE-028.

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
- Components: retrieval/context_package.py/tests.
- Dependencies: safe mutation window for shared ContextPackage file.

## Recently completed storage slices

### BE-029 — Physically allocated Emergency Reserve
- Priority: P1
- Status: DONE
- Evidence: `EmergencyReserveStore` plus bootstrap integration implement Beta sizing `max(256 MiB, min(1 GiB, 1% volume))`, non-sparse allocation, durable persistence, path/reparse safety, explicit emergency release and test injection. Normal shutdown retains the reserve.
- Components: `storage/emergency_reserve.py`, `storage/bootstrap.py`, tests.
- Last verification: 2026-08-23 current remote; tests present, not executed in isolated runtime.

### BE-030 — Disk-pressure state controller and runtime write gate
- Priority: P1
- Status: DONE
- Evidence: integer-only Beta thresholds are implemented; runtime canonical `SQLiteDatabase.write_transaction()` now invokes the controller gate before `BEGIN IMMEDIATE`. First runtime EMERGENCY releases only the reserve, latches read-only safe mode for the controller lifetime, blocks the current and subsequent noncritical writes, and leaves restart/bootstrap to re-evaluate recovery.
- Components: `storage/disk_pressure.py`, `storage/database.py`, `storage/bootstrap.py`, targeted tests.
- Last verification: 2026-08-23 current remote. Static integration complete; targeted tests were added but not executed because isolated runtime could not resolve `github.com`.

### BE-031 — Candidate-only schema executor
- Priority: P1
- Status: DONE
- Evidence: `migrate_schema_candidate()` runs the existing schema engine only against the clone candidate, requires current `SCHEMA_VERSION`, requires a complete WAL checkpoint, restores DELETE journal mode and fails if WAL/SHM sidecars remain.
- Components: `storage/migration_executor.py`, targeted tests.
- Dependencies: BE-028 standalone coordinator.
- Last verification: 2026-08-23; executor and incomplete-checkpoint regressions added, not executed.

### BE-032 — Read-only startup migration planner
- Priority: P1
- Status: DONE
- Evidence: `plan_database_migration()` converts the preflight report into no-op for missing/current DB or an exact clone-required legacy-to-current descriptor; unsupported versions fail closed.
- Components: `storage/migration_plan.py`, targeted tests.
- Dependencies: BE-027.
- Last verification: 2026-08-23; tests added, not executed.

### BE-033 — Integrate safe storage bootstrap ordering
- Priority: P1
- Status: DONE
- Evidence: `StorageBootstrapService` now owns RuntimeLayout -> migration-root/preflight/recovery -> EmergencyReserve -> clone migration if required -> database startup, and binds runtime disk-pressure write arbitration to the database before startup.
- Components: `storage/bootstrap.py`, `storage/database.py`, bootstrap tests.
- Dependencies: BE-029/031/032 DONE.
- Last verification: 2026-08-23 current remote; integration regression added, not executed in isolated runtime.

## Blocked / in-progress older slices

- BE-002 · P1 · BLOCKED — provider lifecycle/control adapter completion; shared LM Studio adapter ownership window required. Security SEC-003 also requires this adapter's loopback transport to ignore ambient HTTP(S) proxies.
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
- BE-011 DONE — BlobStore/durable FS symlink+junction confinement; Security SEC-006/007 track residual concurrent parent-replacement races not closed by static boundary checks.
- BE-012 DONE — provider-observed model revision in signatures.
- BE-017 DONE — ModelSession cancellation invariants.
- BE-018 DONE — UUIDv7 clock-range guard.
- BE-022 DONE — persistent wall-clock int64 guard.
- BE-023 DONE — Unicode line-control rejection in schema IDs.
- BE-024 DONE — runtime mutation lock identity/permissions.
- BE-025 DONE — backup target lock identity.
- BE-026 DONE — reject network-backed active SQLite state.
- BE-027 DONE — clone-migration metadata/free-space contract.
