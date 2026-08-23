# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.
Status: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`.
Last queue refresh: 2026-08-23.

## Active / ready work

### BE-028 — Clone/journal migration before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: clone-first stack is implemented: migration metadata/free-space preflight, SQLite Online Backup clone, durable phase journal, exclusive migration lock, full integrity/FK/version verification, rollback-preserving activation, orphan/journal recovery boundaries and Windows junction/reparse hardening. Read-only startup migration planning and a candidate-only schema executor now also exist. Normal `SQLiteDatabase.start()` still invokes legacy live `initialize_schema()`.
- Components: `migration_safety.py`, `migration_clone.py`, `migration_journal.py`, `migration_lock.py`, `migration_activation.py`, `migration_coordinator.py`, `migration_executor.py`, `migration_plan.py`, database/application startup integration and tests.
- Dependencies: BE-027 DONE; BE-029 reserve must be integrated before startup migration accounts for the real physical reserve. Alembic-vs-custom executor remains an architecture decision.
- Security handoff: SEC-009 P1 requires clone creation/cleanup and activation to bind filesystem decisions to directory/object identity across sensitive operations rather than relying only on pre-operation pathname/reparse checks; add deterministic parent-replacement race coverage including Windows reparse/junction behavior. SEC-010 P2 requires a conservative byte ceiling for `migration_state.json`, checked with `fstat()` before full read/JSON decode while preserving the current no-follow and handle/path identity checks.
- Last verification: 2026-08-23; targeted tests added, not executed because isolated runtime cannot resolve `github.com`. Quality-reported reparse boundary in this new path was fixed; Security static trace found residual TOCTOU/resource-bound gaps tracked as SEC-009/010.

### BE-029 — Physically allocated Emergency Reserve
- Priority: P1
- Status: IN_PROGRESS
- Evidence: `EmergencyReserveStore` and `EmergencyReserveService` implement Beta sizing `max(256 MiB, min(1 GiB, 1% volume))`, non-sparse allocation, durable persistence, path/reparse safety, explicit emergency release and test-only sizing injection. Normal shutdown retains the reserve.
- Components: `storage/emergency_reserve.py`, Core bootstrap ordering/tests.
- Dependencies: RuntimeLayout must create `state_root`; reserve must start before DatabaseService.
- Blocker: naive Core integration would cause every existing application-start test to physically reserve >=256 MiB. A production/test dependency-injection seam must be established before wiring the large shared `core/application.py`.
- Last verification: 2026-08-23; store/service tests added, not executed.

### BE-030 — Disk-pressure state controller
- Priority: P1
- Status: IN_PROGRESS
- Evidence: integer-only Beta thresholds implemented: WARNING `< max(10 GiB,5%)`, CRITICAL `< max(5 GiB,2%)`, EMERGENCY `< max(2 GiB,1%)`. `DiskPressureController` releases only the emergency reserve at EMERGENCY and immediately reassesses; it never deletes canonical data.
- Components: `storage/disk_pressure.py`, write-gating/diagnostics integration/tests.
- Dependencies: BE-029 reserve primitive.
- Last verification: 2026-08-23; policy and side-effect controller tests added, not executed.

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
- Status: READY
- Evidence: required order is read-only preflight/planning -> RuntimeLayout -> EmergencyReserve -> clone migration when needed -> DatabaseService. Current `AthenaApplication` bootstrap tuple is RuntimeLayout -> Database -> protected services.
- Components: `core/application.py`, database startup, storage bootstrap tests.
- Dependencies: testable reserve-service injection seam; BE-029/BE-031/BE-032.
- Last verification: 2026-08-23 against current `core/application.py`.

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
