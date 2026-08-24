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
- **Current state:** Safe startup routing is implemented end-to-end. POSIX filesystem-identity hardening covers durable replacement, durable byte publication and durable directory creation through opened parent-directory FDs, and recovery artifact presence classification now opens no-follow regular-file handles and compares pathname/handle identity before accepting a snapshot. Deterministic replacement regressions cover `os.replace`, `os.open`, `os.mkdir`, and recovery file replacement. POSIX SQLite clone creation is now parent-FD bound via a reserved candidate and `/proc/self/fd` or `/dev/fd` child path. Remaining safety work is primarily the Windows HANDLE equivalent. The remaining architecture divergence is the custom/library-neutral revision engine versus Beta-specified SQLAlchemy 2.x + Alembic.
- **Desired state:** finish BE-036/038 without weakening crash durability, then make the Alembic-vs-custom revision engine an explicit architecture/spec decision.
- **Dependencies:** storage bootstrap runtime integration is present; POSIX durable publication and clone-destination identity are substantially closed; Windows HANDLE publication remains.
- **Verification:** 2026-08-24 current remote static re-trace; prior focused storage gate ran 172 passed / 4 failed / 2 skipped and the four stale pathname-instrumentation tests were subsequently corrected. A green rerun is not yet claimed. Status remains PARTIAL.

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
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Evidence:** Beta requires bounded/paginated long readers so checkpointing is not indefinitely blocked, `wal_autocheckpoint=1000` as a baseline, active observation of `athena.db-wal`, diagnosis/escalation of abnormal growth, background `PASSIVE` checkpoints, optional idle `TRUNCATE` checkpoints, and a clean checkpoint before controlled offline copies/migrations.
- **Current state:** `storage/wal_maintenance.py` now provides an explicit non-destructive WAL maintenance API. It observes the live `page_size` and `wal_autocheckpoint` policy, reads WAL presence/size through a no-follow regular-file handle with pathname/handle identity fencing, runs SQLite `PASSIVE` checkpoints outside active ATHENA transactions, reports busy/log/checkpointed state and post-checkpoint WAL size, and exposes `TRUNCATE` only behind an explicit caller-confirmed idle boundary. It never deletes `-wal` manually. `tests/unit/test_wal_maintenance.py` covers live-policy observation, PASSIVE operation, active-transaction refusal, idle-gated TRUNCATE and fail-closed disabled-autocheckpoint behavior.
- **Remaining state:** no background scheduler/orchestrator or abnormal-growth escalation is composed yet, and no checkpoint has been inserted into backup/migration paths pending explicit proof of a safe boundary. Long-reader pagination remains a separate integration concern.
- **Desired state:** compose bounded monitoring/maintenance around this API, diagnose repeated blocked checkpoints/abnormal growth, and integrate clean checkpoints only at existing safe idle/offline snapshot boundaries without weakening SQLite backup semantics.
- **Dependencies:** coordinate with existing storage bootstrap/migration/backup ownership and Full-Gate Recovery; active BACKEND P0 recovery entries remain evidence-blocked rather than being displaced.
- **Verification:** 2026-08-24 remote static re-read through `d61435cdcc84f3184c9c9bc8dd0f2524ed55b41e`. Tests were added but are NOT EXECUTABLE in this automation environment; no PASS is claimed.

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

### FG-020 — Complete normative backup preflight before snapshot mutation
- **Source:** Beta 21 backup preflight requirements.
- **Ownership / Priority / Status:** BACKEND · P1 · STALE
- **Current state:** current `BackupService` already performs the relevant target-online/manifest/free-space/database-health/migration/disk-pressure checks before snapshot mutation; the earlier candidate was based on an incomplete cross-layer trace.
- **Desired state:** preserve the existing fail-closed preflight and do not create a duplicate backup preflight layer.
- **Verification:** 2026-08-24 static re-evaluation on current `agent/pathena`; no new test PASS claimed.

### FG-021 — Persist explicit job dependencies / parent-child policy and bounded priority inheritance
- **Source:** Beta 12 Job-System / Queue / Scheduler — parent-child jobs, dependency policies and priority inheritance.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** the durable `JobRecord` models job identity, type, priority, state, retry/schedule timestamp, protection scope, lease/fencing and checkpoint linkage, but has no parent ID, dependency relation, dependency completion policy or child cancellation policy. `DurableJobService.create()` likewise accepts no parent/dependency contract. The scheduler's `_rank_key()` derives effective priority only from the job's base priority and fairness aging; it has no dependency-driven temporary inheritance. `WaitingReason.DEPENDENCY` exists, but the generic durable model does not represent the dependency that caused it.
- **Current state:** leases, fencing, retries, waiting states, fairness aging, resource admission and safe-boundary yielding are real and must not be reimplemented. Some domain-specific workflows reconcile their own dependencies, but there is no generic persistent B12 dependency graph / parent-child contract.
- **Desired state:** add explicit durable parent/dependency records with deterministic completion/cancellation semantics; make scheduler eligibility dependency-aware; add bounded priority inheritance when a higher-priority runnable job is blocked on a lower-priority dependency, without allowing inheritance to bypass P0 data-safety, resource, security or protection-scope gates.
- **Security pre-implementation invariant:** dependency insertion/update must reject cycles and fail closed on corrupt/dangling edges; traversal and transitive inheritance work must be bounded; inherited priority must never bypass protection scope, security/resource admission, cancellation fencing, P0 data-safety gates, or turn a dependency-blocked job dispatch-ready. Add adversarial regressions for cyclic/deep graphs and inherited-priority gate bypass before promotion.
- **Dependencies:** BACKEND job schema/repository/service/scheduler; migration required for new durable fields/tables; preserve existing fencing/idempotency and domain-specific workflow behavior during convergence.
- **Verification:** 2026-08-24 static B12 cross-layer trace on exact remote HEAD `e6c86094c2d52119ea8629e112fe69020de4d96d`; Security review on `a86c3b6fa05ec2d291a78d9fb78e1af6695cc197`; no targeted Security tests executed.

### FG-022 — Generic persistent ScheduleDefinition with missed-run and timezone/DST semantics
- **Source:** Beta 12 Job-System / Queue / Scheduler — persistent ScheduleDefinition, per-occurrence jobs, missed-run policies and IANA timezone handling.
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** `DurableJobService` persists individual jobs with optional `next_run_at_us`; the generic `JobRecord` has no schedule-definition identity or occurrence identity. Repository/code search found no `ScheduleDefinition`, `backfill_bounded` or equivalent generic missed-run policy contract. Backup and News implement useful domain-specific scheduling/catch-up behavior, but that is not a reusable persistent B12 schedule-definition layer.
- **Current state:** per-job delayed execution, retry timestamps and domain-specific schedulers exist. They should be preserved rather than replaced wholesale.
- **Desired state:** persist schedule definitions separately from generated job occurrences; create stable occurrence identity/deduplication; implement `skip`, `run_once`, `backfill_all` and bounded backfill semantics; store IANA timezone identity and define deterministic DST gap/fold behavior. Existing Backup/News scheduling should converge incrementally only where the shared contract is proven equivalent.
- **Security pre-implementation invariant:** cap backfill count and lookback horizon before materializing jobs; recurrence/timezone parsing must be bounded and data-only (no eval/dynamic execution); stable occurrence identity must feed idempotency/claim semantics so restart/catch-up cannot create duplicate storms; every generated occurrence must still pass normal protection, security and resource gates; corrupt schedule state fails closed rather than expanding into unbounded work. Add restart/DST/corrupt-state/backfill-cap regressions before promotion.
- **Dependencies:** BACKEND job schema/repository/service/scheduler plus careful migration; coordinate with FG-018 backup quiet-time semantics so DST/timezone behavior is defined once rather than inconsistently per subsystem.
- **Verification:** 2026-08-24 static B12 cross-layer trace on exact remote HEAD `e6c86094c2d52119ea8629e112fe69020de4d96d`; Security review on `a86c3b6fa05ec2d291a78d9fb78e1af6695cc197`; no targeted Security tests executed.

### FG-029 — Durable ImportRequest identity and pre-capture Source lifecycle
- **Source:** Beta 04 sections 5, 7, 8 and 17 (atomic capture, persistable ImportRequest/job scope, preflight, early stable `source_id`).
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** `SourceCaptureService.capture_file()` directly stages and captures one path. `BlobStore.capture_file()` correctly streams into local staging, computes SHA-256, fsyncs and rejects a source that changes during intake. However `SourceRepository.capture_file()` allocates `source_id = new_uuid7()` only after physical blob preparation, inside the final Source transaction. `SourceLifecycleState` begins at `captured` and has no `discovered` or `staging` state. Repository/code search found no durable `ImportRequest` contract in the current source layer.
- **Current state:** single-file capture is durable and atomic once the blob is prepared, but there is no persistent intake identity that survives copy retry/offline-spool/preflight work, and the Source identity is not allocated early enough to remain stable across an interrupted/retried logical import attempt.
- **Desired state:** introduce a bounded persistable import/intake scope with stable import/request identity and early reserved Source identity (or an equivalently strong explicit identity contract), recording protection scope, options, recursion/symlink policy, temporary/do-not-store flags and preflight state. Retries must resume/reconcile the same logical attempt without silently creating duplicate Source identities. Preserve existing original-first blob durability and final Source+Blob atomic commit.
- **Dependencies:** BACKEND source/job/schema migration work; coordinate with disk-pressure/preflight controls and existing blob orphan reconciliation. Do not weaken current symlink, hash, fsync, source-change or protected-content guarantees.
- **Verification:** 2026-08-24 static B04 trace on current observable `agent/pathena` tree; tests NOT EXECUTABLE in this Scout run, no PASS claimed.

### FG-030 — Complete the v1 unified import entry surfaces around one backend intake contract
- **Source:** Beta 04 sections 3 and 7–13 (single/multiple files, folders, Core API submissions, text paste, chat attachments, deterministic directory intake; Desktop drag-and-drop).
- **Ownership / Priority / Status:** MIXED · P1 · READY
- **Primary implementation owner:** BACKEND
- **Secondary reviewers:** UI
- **Verification owner:** QUALITY
- **Sub-slices:**
  - **Owner: BACKEND** — define the single durable import/intake API used by file, multi-file, folder and text-paste inputs; expose Core API import operations; preserve per-file Source identity, deterministic folder enumeration, recursion/symlink policy and bounded preflight/reporting.
  - **Owner: UI** — only after the backend contract is stable, route Desktop file/folder selection, multi-file and drag-and-drop into that contract without duplicating import semantics.
  - **Owner: QUALITY** — verify all v1 entry surfaces converge on the same original-first capture semantics, including retry/idempotency and failure reporting.
- **Evidence:** the current `SourceCaptureService` exposes `capture_file()`, `capture_protected_file()` and `capture_external_snapshot()` but no generic multi-file/folder/text-paste import orchestration. `CoreApiSurface` exposes health/capabilities/chat/knowledge/model operations and no Source/import operation; the ASGI route table likewise contains no `/api/v1/sources` or equivalent import resource. The source tree has rich capture/representation/chunking primitives, so this is an integration/surface gap rather than a missing Raw Archive engine.
- **Current state:** low-level Source capture, protected capture, external snapshot capture, representations and chunking exist, but the normative v1 input classes do not yet converge through one durable public intake contract.
- **Desired state:** establish one backend-owned import contract and reuse it from Core API and Desktop surfaces; do not invent separate UI-only ingestion logic. Unknown formats must remain capturable even when processing is unavailable.
- **Dependencies:** FG-029 for durable import identity/lifecycle; BACKEND API/source ownership first, UI wiring second; preserve SECURITY ownership of filesystem/protection trust boundaries.
- **Verification:** 2026-08-24 static B04 cross-layer trace; no runtime/test execution claimed.

### FG-031 — Add OCR and Speech-to-Text provider-backed representation paths
- **Source:** Beta 04 sections 22 and 29–35 (representation profiles, OCRProvider, OCR fallback/confidence, SpeechToTextProvider, timestamped segments, audio/video fallback semantics).
- **Ownership / Priority / Status:** BACKEND · P1 · READY
- **Evidence:** the current source package has concrete retained representation paths for native text, PDF, DOCX and HTML plus shared immutable representation/provenance stores. `SourceRepresentationType` currently contains only `normalized_text` and `extracted_text`. Repository code search on the exact current branch found no `OCRProvider` or `SpeechToTextProvider` contract and no audio/video transcript representation path. Beta 04 requires OCR and STT to be provider interfaces rather than hard-coded model implementations and requires Source capture to remain valid when those infrastructure models are unavailable.
- **Current state:** retained text/document representations are real and provenance-aware, and PDF parsing is isolated/bounded, but image OCR and audio/video transcription are not integrated through the normative provider contracts. The Raw Archive itself must not be replaced or coupled to any particular OCR/STT model.
- **Desired state:** add narrow infrastructure-provider contracts for OCR and speech-to-text; create immutable retained representation records with provider/parser identity, version/options, ProcessingRun and content hash; support timestamped transcript anchors; use native-text-first/OCR-fallback for image-based PDFs; when providers are unavailable leave the Source captured and the representation job retryable/waiting/failed without losing original bytes. Do not let OCR/STT output directly create canonical Knowledge or Personal Memory.
- **Dependencies:** BACKEND source/model-infrastructure/job composition; preserve existing `SourceRepresentationRepository`, ProcessingRun provenance, protected-source boundaries and resource admission. UI is not required until backend representation capabilities are stable.
- **Verification:** 2026-08-24 static exact-HEAD trace on `285cc8271cd611eefe6dcb20a610dd7253d61ff5`; repository searches for `OCRProvider` and `SpeechToTextProvider` returned no implementation. Tests NOT EXECUTABLE; no PASS claimed.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Shared provider/generation files remain ownership-sensitive.
- FG-012 must never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013: POSIX publication/recovery and SQLite clone-destination identity are substantially closed; BE-038 Windows HANDLE publication remains READY. Alembic-vs-custom remains an explicit architecture decision.
- FG-014 applies only to active state/database roots.
- FG-015 includes a last-moment pre-writer pressure fence; promote only after green relevant validation.
- FG-016 is implemented in the live database service; promote only after green relevant validation.
- FG-017 is now IN_PROGRESS with an isolated WAL API; do not mark implemented until runtime orchestration/diagnosis and safe-boundary integration are complete and validated.
- FG-018 is a B21 configurability handoff only; the daily/catch-up/overlap scheduler itself already exists and must not be reimplemented.
- FG-019 must reuse the existing deep-verify/restore-smoke primitives; BACKEND should add durable scheduling/audit orchestration rather than a parallel validation engine.
- FG-020 is STALE after the complete B21 preflight was found on the current branch; do not duplicate it.
- FG-021 is a generic dependency/parent-child/inheritance handoff; preserve existing lease/fencing/resource controls and domain-specific dependency behavior; Security review requires bounded graph work and forbids inherited-priority gate bypass.
- FG-022 is a generic schedule-definition handoff; do not replace working Backup/News catch-up logic until equivalence is proven; Security review requires bounded backfill/lookback and restart-safe deduplication before job materialization.
- FG-029 and FG-030 are B04 intake handoffs. Keep the existing durable Raw Archive primitives; build orchestration/surfaces around them rather than replacing blob/source persistence.
- FG-031 is a B04 representation-provider handoff. Reuse the existing immutable SourceRepresentation/ProcessingRun machinery; do not couple the import core to a particular OCR/STT model and do not let infrastructure representations make canonical semantic decisions. IDs FG-023 through FG-028 remain reserved for previously reported Scout candidates pending SSOT revalidation, so they are not reused here.
