# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and BACKEND, UI, and QUALITY owners.
Status vocabulary: `FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`.
Last refresh: 2026-08-24.

## Findings

### FG-001 — Complete PrimaryModelProvider lifecycle/control contract
- **Ownership / Priority / Status:** BACKEND · P1 · BLOCKED
- Core management protocol exists; LM Studio adapter completion remains in a shared active file.

### FG-002 — Beta ModelRegistry / active-primary-model runtime
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- Core ModelRegistry provides provider-scoped identity, capability eligibility, infrastructure exclusion and exactly one active primary.

### FG-003 — Normative provider health states
- **Ownership / Priority / Status:** BACKEND · P2 · IMPLEMENTED
- unavailable, starting, ready, busy, degraded and error are represented.

### FG-004 — Explicit provider capability representation
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- supported / unsupported / unknown remain distinct.

### FG-005 — Context Builder source diversity
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- rank 1 preserved, near duplicates deferred, contradiction-bearing Claims exempt.

### FG-006 — Provider-aware dynamic token accounting
- **Ownership / Priority / Status:** BACKEND · P1 · STALE
- MemoryAugmentedChatService already performs provider-capacity-aware budgeting and rendered-input convergence.

### FG-007 — Model load ownership before automatic unload
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- only explicitly ATHENA-owned loads may auto-unload; external/unknown ownership is preserved.

### FG-008 — Provider-observed model revision in ModelSignature
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- exact optional provider revision participates in signature identity and ContextPackage propagation without inference.

### FG-009 — First-class ModelSession / generation execution context
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- Core ModelSession owns request identity, signature/budget binding, cancellation and late-result discard. Exact provider request binding remains.

### FG-010 — Normalized provider failure taxonomy
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- Core failure kinds/retry classes exist; LM Studio mapping remains blocked by shared adapter ownership.

### FG-011 — Complete model-management surface and real switch/load flow
- **Ownership / Priority / Status:** MIXED · P1 · BLOCKED
- Backend load/unload/switch orchestration remains incomplete; UI must not invent lifecycle semantics.

### FG-012 — Protection Scope through retrieval-to-context assembly
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- protected runtime retrieval/context and pre-provider execution guard exist; explicit protected generation/persistence policy remains.

### FG-013 — Reconcile migration engine with Beta 03 architecture
- **Source:** Beta 03 section 3 and sections 193–209.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Safe startup routing is implemented end-to-end. POSIX filesystem-identity hardening covers durable replacement, durable byte publication and durable directory creation through opened parent-directory FDs, and recovery artifact presence classification now opens no-follow regular-file handles and compares pathname/handle identity before accepting a snapshot. Deterministic replacement regressions cover `os.replace`, `os.open`, `os.mkdir`, and recovery file replacement. Remaining safety work is the Windows HANDLE equivalent and identity-binding of the SQLite clone destination. The remaining architecture divergence is the custom/library-neutral revision engine versus Beta-specified SQLAlchemy 2.x + Alembic.
- **Desired state:** finish BE-036/038/039 without weakening crash durability, then make the Alembic-vs-custom revision engine an explicit architecture/spec decision.
- **Dependencies:** storage bootstrap runtime integration is present; POSIX durable publication identity is substantially closed; Windows HANDLE and SQLite clone destination binding remain.
- **Verification:** 2026-08-23 focused storage gate ran 172 passed / 4 failed / 2 skipped; the four failures were stale tests instrumenting pathname-based durability and were corrected in `11811fd` without reverting product hardening. A green rerun is not yet claimed. Status remains PARTIAL.

### FG-014 — Reject network-backed active state roots before SQLite open
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- Windows UNC/mapped remote roots and known Linux network filesystems are refused before RuntimeLayout mutation and SQLite preflight. Remote backup/archive/projection remain separate supported targets.

### FG-015 — Physical Emergency Reserve and disk-pressure policy
- **Source:** Beta 03 emergency reserve/disk-pressure sections and Emergency Reserve Test 270.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `EmergencyReserveStore` implements non-sparse physical allocation at `state_root/reserve/emergency.reserve`, exact default sizing `max(256 MiB, min(1 GiB, 1% volume))`, durable persistence, path/reparse safety, explicit release and normal-shutdown retention. `StorageBootstrapService` owns reserve-before-database ordering and refuses writable startup when the volume is already EMERGENCY. It now also performs a second pressure assessment after any clone migration and immediately before opening the live SQLite writer. If intervening storage consumption pushes the volume into EMERGENCY, only the reserve is released, read-only safe mode remains latched, and writer startup is refused even when that release temporarily lifts free space above the emergency threshold. Runtime `SQLiteDatabase.write_transaction()` checks the same controller before `BEGIN IMMEDIATE`; no canonical data is deleted.
- **Recovery contract:** read-only safe mode clears only by controlled restart, which repeats bootstrap pressure assessment before writable operation can resume. Migration/recovery retain reserve headroom rather than allowing a newly opened live writer to consume it.
- **Verification:** 2026-08-23 current remote after `62658b9` / `7a0d9fc`; dedicated pre-writer pressure regression added. No green relevant gate is yet claimed, so status remains IMPLEMENTED.

### FG-016 — Verify safety-critical SQLite PRAGMAs after applying them
- **Source:** Beta 03 sections 30–40, especially section 30 (`foreign_keys` readback), section 33 (configurable `busy_timeout`) and section 37 (`trusted_schema` readback).
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `storage/connection_policy.py` owns the live per-connection safety contract. It accepts only integer busy timeouts in the bounded 5,000–120,000 ms range, applies `foreign_keys=ON`, configured `busy_timeout`, and `trusted_schema=OFF`, then reads all three back and raises `DatabaseCompatibilityError` unless SQLite confirms the requested state exactly. `SQLiteDatabase` uses the same timeout for `sqlite3.connect(timeout=...)` and reapplies/verifies the policy after schema initialization.
- **Tests:** focused regressions cover invalid/valid timeout boundaries, direct policy application/readback and real `SQLiteDatabase.start()` with a non-default timeout.
- **Verification:** 2026-08-23 current remote after `525936a`, `80bbb3e`, `4fe780f`; associated gate was cancelled, so no test pass is claimed.

### FG-017 — Runtime WAL-size monitoring and controlled checkpoint orchestration
- **Source:** Beta 03 sections 27 and 39–41.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** Beta requires bounded/paginated long readers so checkpointing is not indefinitely blocked, `wal_autocheckpoint=1000` as a baseline, active observation of `athena.db-wal`, diagnosis/escalation of abnormal growth, background `PASSIVE` checkpoints, optional idle `TRUNCATE` checkpoints, and a clean checkpoint before controlled offline copies/migrations. Current `SQLiteDatabase` starts one live connection, applies the connection policy and explicit transactions, but exposes no WAL-size observer, checkpoint scheduler/orchestrator, blocked-checkpoint diagnosis, or checkpoint API. Repository search on the active branch found no `wal_checkpoint` implementation.
- **Current state:** WAL mode and autocheckpoint baseline exist; runtime WAL health/maintenance semantics do not.
- **Desired state:** add a bounded, non-destructive WAL maintenance service/API in BACKEND scope. It must never delete `-wal` manually; use SQLite checkpoint primitives, avoid indefinite reader interference, expose observable state, and keep aggressive/TRUNCATE behavior restricted to safe idle/offline boundaries. Integrate controlled pre-copy/pre-migration checkpointing only where the existing backup/migration snapshot contracts make it safe.
- **Dependencies:** coordinate with existing storage bootstrap/migration/backup ownership and Full-Gate Recovery; do not broaden mutation while current P0 gate recovery is active.
- **Verification:** read-only scout trace on 2026-08-24. No implementation or test PASS is claimed.

### FG-018 — Make the normative daily backup quiet time runtime-configurable
- **Source:** Beta 21 sections 9–13, especially section 10 (daily backup in a configurable quiet time / at next opportunity).
- **Ownership / Priority / Status:** BACKEND · P2 · FOUND
- **Evidence:** `DurableBackupWorker` implements deterministic daily slots, missed-slot catch-up, per-target overlap prevention, idempotent slot deduplication and storage/backoff waiting. It accepts `quiet_hour_utc`, but `AthenaApplication` constructs it without passing configuration, so production uses the internal 03:00 UTC default. `AthenaSettings` exposes roots and model timeouts but no backup quiet-time setting. The scheduler therefore satisfies automatic daily/catch-up semantics but not the normative configurability requirement.
- **Current state:** daily scheduling works, but its quiet hour is effectively fixed in production composition.
- **Desired state:** expose a bounded persisted or bootstrap-visible backup quiet-time setting and wire it into `DurableBackupWorker` without changing the existing catch-up/overlap/idempotency semantics. If local-time semantics are intended rather than UTC, define DST behavior explicitly before implementation.
- **Dependencies:** BACKEND/settings + job-scheduler composition; no mutation while Full-Gate Recovery is P0 unless explicitly promoted.
- **Verification:** read-only B21 trace on current `agent/pathena` in the 2026-08-24 scout run. No implementation or test PASS is claimed.

### FG-019 — Schedule periodic deep backup verification and isolated restore tests
- **Source:** Beta 21 sections 33–40, especially periodic Deep Verify and Scheduled Restore Test.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** `BackupService.verify_deep()` already owns the deep-verification primitive and isolated restore-smoke boundary, while `DurableBackupWorker` defines and executes only `backup.create`. The daily worker schedules creation slots, catch-up, overlap prevention and retries but exposes no durable periodic deep-verification/restore-test job type. `AthenaApplication` composes that create-only worker directly. The missing feature is therefore orchestration, not another backup or restore engine.
- **Current state:** each completed snapshot receives light verification and deep verification can be invoked explicitly, but Beta's periodic deep verification and regular staged restore-test requirement is not durably scheduled.
- **Desired state:** add a durable BACKEND-owned maintenance job that periodically selects eligible complete snapshots, invokes the existing deep verification / isolated staging restore primitives, records auditable outcome/checkpoint state, prevents target overlap, retries safely, and never touches production roots. Preserve `verified_light`/`verified_deep` semantics and do not duplicate `BackupService` validation logic.
- **Dependencies:** coordinate with backup target locking, scheduler control-lane ownership, existing `BackupService.verify_deep()` and B21 audit semantics. This is a READY handoff during active Full-Gate Recovery, not a Scout product-code mutation.
- **Verification:** read-only trace on `agent/pathena` @ `8553fe2655b8789130f6be58a985f716ff252c95` on 2026-08-24. No implementation or test PASS is claimed.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Shared provider/generation files remain ownership-sensitive.
- FG-012 must never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013: BE-036 POSIX publication/recovery identity is substantially closed; BE-038 Windows HANDLE publication and BE-039 SQLite clone destination binding remain READY. Alembic-vs-custom remains an explicit architecture decision.
- FG-014 applies only to active state/database roots.
- FG-015 includes a last-moment pre-writer pressure fence; promote only after green relevant validation.
- FG-016 is implemented in the live database service; promote only after green relevant validation.
- FG-017 is a BACKEND handoff only while Full-Gate Recovery is P0; do not let WAL-maintenance work displace active recovery blockers or introduce broad storage churn.
- FG-018 is a B21 configurability handoff only; the daily/catch-up/overlap scheduler itself already exists and must not be reimplemented.
- FG-019 must reuse the existing deep-verify/restore-smoke primitives; BACKEND should add durable scheduling/audit orchestration rather than a parallel validation engine.
