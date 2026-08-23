# pATHENA Backend Queue

Persistent prioritized backend work queue for `agent/pathena`.

Status vocabulary: `READY` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `STALE`

## Queue

### BE-001 — Complete normative provider health states
- Priority: P1
- Status: DONE
- Evidence: FG-003 six-state provider health domain implemented.
- Components: model domain/tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added, not executed in connector runtime.

### BE-002 — Complete provider lifecycle/control contract
- Priority: P1
- Status: BLOCKED
- Evidence: Core management port exists; LM Studio adapter remains a shared active file. SEC-003 also requires loopback transport to ignore ambient proxies.
- Components: model ports, LM Studio adapter/tests.
- Dependencies: safe adapter ownership window.
- Last verification: 2026-08-23.

### BE-003 — Add normalized provider capability representation
- Priority: P1
- Status: DONE
- Evidence: FG-004 supported/unsupported/unknown capability contract implemented.
- Components: model domain/tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added, not executed.

### BE-004 — Add context-builder source diversity constraint
- Priority: P1
- Status: DONE
- Evidence: FG-005 rank-1 preservation, near-duplicate deferral, deterministic ordering and contradiction protection implemented.
- Components: retrieval context/tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added, not executed.

### BE-005 — Provider-aware dynamic token accounting
- Priority: P1
- Status: STALE
- Evidence: Current MemoryAugmentedChatService already budgets from provider capacity and converges rendered input.
- Components: chat memory/context package.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-006 — Add active primary model registry/runtime layer
- Priority: P1
- Status: DONE
- Evidence: FG-002 ModelRegistry implements provider-scoped identity, eligibility, infrastructure exclusion and one active primary.
- Components: model registry/tests.
- Dependencies: BE-003.
- Last verification: 2026-08-23; tests not executed due environment DNS.

### BE-007 — Enforce model load ownership before automatic unload
- Priority: P1
- Status: DONE
- Evidence: FG-007 distinguishes loaded_by_athena / loaded_externally / unknown; only ATHENA-owned loads auto-unload.
- Components: model registry/tests.
- Dependencies: BE-006.
- Last verification: 2026-08-23; tests added, not executed.

### BE-008 — Persist/audit active primary model switch semantics
- Priority: P2
- Status: BLOCKED
- Evidence: Beta 08 requires auditable switching; no dedicated durable audit contract exists.
- Components: model runtime/application audit.
- Dependencies: durable audit storage contract decision.
- Last verification: 2026-08-23.

### BE-009 — Provider request cancellation/discard contract
- Priority: P2
- Status: BLOCKED
- Evidence: ModelSession has request identity/cancellation/late-result discard, but provider stream port cannot bind the exact backend request yet.
- Components: model session/provider orchestration.
- Dependencies: safe request-ID plumbing and adapter ownership window.
- Last verification: 2026-08-23.

### BE-010 — Generation numeric/control boundary hardening
- Priority: P2
- Status: IN_PROGRESS
- Evidence: direct persistent chat controls hardened before persistence; remaining grounded/provider-private boundaries need re-trace.
- Components: chat/direct, ContextPackage/provider controls/tests.
- Dependencies: avoid collision on chat/generation.py.
- Last verification: 2026-08-23; BE-021 remains open.

### BE-011 — Confine BlobStore writes against symlink/junction ancestors
- Priority: P1
- Status: DONE
- Evidence: durable filesystem trust boundary rejects symlinks and Windows junction/reparse points.
- Components: durable_fs/BlobStore tests.
- Dependencies: none.
- Last verification: 2026-08-23; test execution blocked by DNS.

### BE-012 — Preserve provider-observed model revision in ModelSignature
- Priority: P1
- Status: DONE
- Evidence: FG-008 optional exact provider revision participates in signature identity and ContextPackage propagation without inference.
- Components: model domain/provenance/tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-013 — Complete first-class ModelSession binding
- Priority: P1
- Status: BLOCKED
- Evidence: FG-009 Core ModelSession exists; exact provider request binding remains absent.
- Components: model session/ports/chat orchestration/provider adapter.
- Dependencies: safe adapter ownership window.
- Last verification: 2026-08-23.

### BE-014 — Carry ModelSignature revision through ContextPackage and drift checks
- Priority: P1
- Status: IN_PROGRESS
- Evidence: ContextPackage preserves revision and reusable runtime drift guard exists; ChatGenerationService integration remains.
- Components: ContextPackage/signature_guard/chat generation/tests.
- Dependencies: safe mutation window for shared chat/generation.py.
- Last verification: 2026-08-23.

### BE-015 — Normalize Core provider failure taxonomy
- Priority: P1
- Status: BLOCKED
- Evidence: FG-010 Core taxonomy/retry classes exist; adapter mapping remains.
- Components: model/failures, LM Studio adapter, consumers/tests.
- Dependencies: safe adapter ownership window.
- Last verification: 2026-08-23.

### BE-016 — Protection-aware retrieval/context bridge
- Priority: P1
- Status: IN_PROGRESS
- Evidence: FG-012 ephemeral protected retrieval and execution guard exist; end-to-end generation/persistence policy remains.
- Components: protected_source/protected_execution/orchestration/tests.
- Dependencies: explicit protected output persistence policy.
- Last verification: 2026-08-23.

### BE-017 — Enforce ModelSession constructor cancellation invariants
- Priority: P2
- Status: DONE
- Evidence: impossible direct lifecycle combinations rejected.
- Components: model/session tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-018 — Fail closed on out-of-range UUIDv7 system clock
- Priority: P2
- Status: DONE
- Evidence: UUIDv7 timestamp no longer silently wraps outside RFC range.
- Components: common/ids tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-019 — Canonicalize provider-observed model identity metadata
- Priority: P2
- Status: BLOCKED
- Evidence: domain-only normalization breaks provider error taxonomy; change must be atomic with adapter parsing.
- Components: LM Studio parsing/ModelInfo/tests.
- Dependencies: safe adapter ownership window.
- Last verification: 2026-08-23.

### BE-020 — Integrate runtime ModelSignature drift guard into generation
- Priority: P1
- Status: READY
- Evidence: reusable guard exists; ChatGenerationService still uses older inline comparison.
- Components: chat/generation.py, signature_guard/tests.
- Dependencies: safe mutation window for shared generation file.
- Last verification: 2026-08-23.

### BE-021 — Harden ContextPackage generation-temperature conversion
- Priority: P2
- Status: READY
- Evidence: extreme JSON integer can OverflowError during float conversion outside ContextPackage error contract.
- Components: retrieval/context_package.py/tests.
- Dependencies: safe mutation window for shared ContextPackage file.
- Last verification: 2026-08-23.

### BE-022 — Fail closed on invalid persistent wall-clock range
- Priority: P1
- Status: DONE
- Evidence: utc_now_us rejects negative/out-of-SQLite-int64 timestamps.
- Components: common/time tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-023 — Reject Unicode line controls in structured schema IDs
- Priority: P2
- Status: DONE
- Evidence: Unicode line/paragraph controls are rejected from single-line schema IDs.
- Components: model/ports tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-024 — Harden runtime mutation lock identity and permissions
- Priority: P1
- Status: DONE
- Evidence: owner-only POSIX mode plus path/handle identity checks before/after lock.
- Components: lifecycle/runtime_lock tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-025 — Harden backup target lock identity against pathname replacement
- Priority: P1
- Status: DONE
- Evidence: backup lock validates path/handle identity after open/acquisition.
- Components: backup/target_lock tests.
- Dependencies: none.
- Last verification: 2026-08-23.

### BE-026 — Reject network-backed active SQLite state roots
- Priority: P1
- Status: DONE
- Evidence: FG-014 refuses Windows UNC/mapped network and known Linux network filesystems before RuntimeLayout mutation and SQLite preflight.
- Components: storage/locality, runtime, recovery/tests.
- Dependencies: none.
- Last verification: 2026-08-23; tests added, no pass claimed.

### BE-027 — Establish clone-migration safety metadata and free-space contract
- Priority: P1
- Status: DONE
- Evidence: FG-013 exact migration metadata and DB + 25% + 512 MiB + emergency reserve preflight implemented with integer-only arithmetic.
- Components: migration_safety/tests/reconciliation note.
- Dependencies: none.
- Last verification: 2026-08-23; tests added, not executed.

### BE-028 — Implement clone/journal migration coordinator before live schema mutation
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Standalone clone-first migration stack now exists: versioned descriptor/preflight, SQLite Online Backup candidate, durable external phase journal, exclusive cross-process lock, full integrity/FK/version verification, rollback-preserving activation, orphan/journal fail-closed recovery boundaries and crash-phase tests. Quality-reported Windows junction/reparse issue in the new clone path was fixed via the shared durable-fs trust-boundary predicate and regressions were added. Normal SQLiteDatabase.start() is not yet wired to this coordinator and still performs legacy live initialize_schema migration.
- Components: migration_safety, migration_clone, migration_journal, migration_lock, migration_activation, migration_coordinator, database startup integration/tests.
- Dependencies: BE-027 DONE; BE-029 reserve lifecycle must be production-integrated before startup migration uses a real reserve size. Alembic-vs-custom executor remains a separate architecture decision.
- Last verification: 2026-08-23; targeted tests added but not executed because isolated runtime cannot resolve github.com.

### BE-029 — Provision physically allocated Emergency Reserve
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Beta 03 requires state_root/reserve/emergency.reserve, physically allocated and non-sparse, default max(256 MiB, min(1 GiB, 1% volume)). EmergencyReserveStore and EmergencyReserveService implement exact sizing, physical allocation, path/reparse safety, durable persistence, explicit release and a test override that avoids large allocations. Application bootstrap integration remains outstanding.
- Components: storage/emergency_reserve.py, RuntimeLayout/Application startup, targeted tests.
- Dependencies: RuntimeLayout must create state_root before reserve provisioning; DatabaseService must start only after reserve provisioning.
- Last verification: 2026-08-23; store/service and targeted tests added, not executed.

### BE-030 — Implement deterministic disk-pressure state controller
- Priority: P1
- Status: IN_PROGRESS
- Evidence: Beta 03 thresholds are encoded as pure integer policy: WARNING free < max(10 GiB, 5%), CRITICAL free < max(5 GiB, 2%), EMERGENCY free < max(2 GiB, 1%). Assessment exposes reserve-release/noncritical-write/read-only-safe-mode decisions; side-effect controller integration remains outstanding.
- Components: storage/disk_pressure.py, reserve release controller, diagnostics/jobs/tests.
- Dependencies: BE-029 reserve primitive available.
- Last verification: 2026-08-23; pure policy and boundary tests added, not executed.

### BE-031 — Wire candidate-only schema executor into clone migration
- Priority: P1
- Status: READY
- Evidence: BE-028 coordinator intentionally accepts an executor but current initialize_schema configures WAL on its connection. Candidate execution needs a dedicated wrapper that migrates only candidate.db, checkpoints/normalizes journal mode and leaves no WAL/SHM before verification/activation.
- Components: schema executor, schema.py/database integration/tests.
- Dependencies: BE-028 standalone coordinator.
- Last verification: 2026-08-23 against current schema/database path.
