# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and BACKEND, UI, and QUALITY owners.

Status vocabulary: `FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`

## Findings

### FG-001 — Complete the PrimaryModelProvider lifecycle/control contract
- **Source:** Beta 08 sections 6, 8–11.
- **Ownership / Priority / Status:** BACKEND · P1 · BLOCKED
- **Current state:** Core management protocol exists; LM Studio adapter completion remains pending in a shared active file.
- **Verification:** Re-read 2026-08-23.

### FG-002 — Add the Beta ModelRegistry / active-primary-model runtime layer
- **Source:** Beta 08 sections 17–20.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Core ModelRegistry provides provider-scoped identity, capability eligibility, infrastructure exclusion and exactly one active primary.
- **Verification:** Implemented 2026-08-23; tests added, no pass claimed.

### FG-003 — Represent all normative provider health states
- **Source:** Beta 08 section 11.
- **Ownership / Priority / Status:** BACKEND · P2 · IMPLEMENTED
- **Current state:** unavailable, starting, ready, busy, degraded and error are represented.
- **Verification:** 2026-08-23.

### FG-004 — Explicit provider capability representation
- **Source:** Beta 08 sections 10, 15, 18–20.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** supported, unsupported and unknown remain distinct across provider capabilities.
- **Verification:** 2026-08-23.

### FG-005 — Enforce source diversity during Context Builder selection
- **Source:** Beta 09 section 25 and test 67.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** rank 1 preserved, near duplicates deferred, contradiction-bearing Claims exempt.
- **Verification:** 2026-08-23.

### FG-006 — Provider-aware dynamic token accounting
- **Source:** Beta 09 sections 5–9 and tests 60–61.
- **Ownership / Priority / Status:** BACKEND · P1 · STALE
- **Current state:** MemoryAugmentedChatService already performs capacity-aware budgeting and rendered-input convergence.
- **Verification:** 2026-08-23.

### FG-007 — Enforce model load ownership before automatic unload
- **Source:** Beta 08 section 21 and test 73.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** only explicitly ATHENA-owned loads may auto-unload; external/unknown ownership is preserved.
- **Verification:** 2026-08-23.

### FG-008 — Preserve provider-observed model revision in ModelSignature
- **Source:** Beta 08 sections 15 and 31–35.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** optional exact provider revision participates in signature identity and ContextPackage propagation; unknown is never inferred.
- **Verification:** 2026-08-23.

### FG-009 — Introduce a first-class ModelSession / generation execution context
- **Source:** Beta 08 sections 27–30 and 50–52.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Core ModelSession owns request identity, signature/budget binding, cancellation and late-result discard. Provider request binding remains.
- **Dependencies:** provider request-ID plumbing and safe adapter ownership window.
- **Verification:** 2026-08-23.

### FG-010 — Normalize provider backend failure taxonomy
- **Source:** Beta 08 sections 45–49 and 52.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Current state:** Core failure kinds/retry classes exist; LM Studio mapping remains.
- **Dependencies:** safe adapter ownership window.
- **Verification:** 2026-08-23.

### FG-011 — Complete the Beta model-management surface and real switch/load flow
- **Source:** Beta 08 model management requirements.
- **Ownership / Priority / Status:** MIXED · P1 · BLOCKED
- **Current state:** desktop discovery/selection exists but full Core-owned load/unload/switch orchestration is incomplete.
- **Dependencies:** FG-001, FG-008, FG-009 and later UI wiring.
- **Verification:** 2026-08-23.

### FG-012 — Carry and enforce Protection Scope through retrieval-to-context assembly
- **Source:** Beta 09 sections 24, 49–51 and test 65.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Current state:** protected runtime retrieval/context and pre-provider execution guard exist; explicit protected generation/persistence policy remains.
- **Dependencies:** orchestration integration without protected plaintext leakage to unprotected persistence.
- **Verification:** 2026-08-23.

### FG-013 — Reconcile the v1 migration engine with Beta 03's SQLAlchemy/Alembic contract
- **Source:** Beta 03 section 3 and sections 193–209.
- **Ownership / Priority / Status:** BACKEND · P1 · PARTIAL
- **Evidence / code paths:** `SQLiteDatabase.start()` still invokes legacy live `initialize_schema()` migration. `docs/agent_coordination/migration_engine_reconciliation.md` records the architecture divergence.
- **Current state:** A library-neutral clone-first safety stack is now implemented independently of startup: explicit MigrationDescriptor/free-space preflight, SQLite Online Backup clone, durable external phase journal, exclusive cross-process migration lock, full integrity/FK/version verification, rollback-preserving activation and crash/recovery boundaries. Quality-reported Windows junction/reparse handling in the new migration path was fixed using the shared storage trust-boundary predicate. Normal DB startup is not yet routed through the coordinator. Alembic-vs-custom revision execution remains an explicit architecture decision rather than a hidden maintenance change.
- **Desired state:** integrate a candidate-only schema executor and route preflight-detected legacy schemas through the clone coordinator before opening the active DB for mutation; retain rollback candidate and recovery journal semantics. Separately resolve Alembic-vs-custom executor at architecture/spec level.
- **Dependencies:** BE-027 DONE; BE-028 IN_PROGRESS; BE-029 reserve lifecycle production integration required before migration preflight can account for the real physical reserve.
- **Verification:** 2026-08-23; targeted migration safety/clone/journal/lock/activation/coordinator tests added but not executed because the isolated runtime cannot resolve github.com.

### FG-014 — Reject network-backed active state roots before opening SQLite
- **Source:** Beta 03 section 7.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** Windows UNC/mapped remote roots and known Linux network filesystems are refused before RuntimeLayout mutation and SQLite preflight; backup/archive/projection roots remain allowed separately.
- **Verification:** 2026-08-23; targeted tests added, no pass claimed.

### FG-015 — Provision physical Emergency Reserve and disk-pressure policy
- **Source:** Beta 03 emergency reserve/disk-pressure sections and Emergency Reserve Test 270.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Evidence / code paths:** `src/athena/storage/emergency_reserve.py` implements non-sparse physical allocation at `state_root/reserve/emergency.reserve`, exact default sizing `max(256 MiB, min(1 GiB, 1% volume))`, durable persistence, explicit release and a lifecycle service. `src/athena/storage/disk_pressure.py` implements WARNING/CRITICAL/EMERGENCY thresholds with integer-only arithmetic and exposes reserve-release/noncritical-write/read-only-safe-mode decisions.
- **Current state:** storage primitives and targeted tests exist. Application bootstrap does not yet provision the reserve before DatabaseService, and there is no side-effect controller that releases it only at EMERGENCY and gates noncritical writes.
- **Desired state:** RuntimeLayout -> EmergencyReserveService -> migration/database startup ordering; then connect disk-pressure assessment to reserve release and write gating without deleting canonical data.
- **Dependencies:** BE-029/BE-030.
- **Verification:** 2026-08-23; targeted tests added, not executed in connector runtime.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Provider lifecycle adapter work remains separate while the LM Studio adapter is concurrently active.
- FG-011 remains blocked until backend lifecycle/switch semantics stabilize; UI must not invent load semantics.
- FG-012 requires explicit protected generation persistence policy; never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013 clone/journal safety can proceed independently, but Alembic-vs-custom executor requires an explicit architecture decision.
- FG-014 applies only to active state/database roots; remote archive/backup targets remain supported.
- FG-015 reserve release is only an emergency recovery measure; normal shutdown must retain the reserve.
