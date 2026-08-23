# pATHENA Feature-Gap Backlog

Central hand-off between the Feature-Gap Scout and BACKEND, UI, and QUALITY owners.
Status vocabulary: `FOUND` · `PARTIAL` · `READY` · `BLOCKED` · `IN_PROGRESS` · `IMPLEMENTED` · `VERIFIED` · `STALE`.
Last refresh: 2026-08-23.

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
- **Current state:** Safe startup routing is now implemented: `StorageBootstrapService` performs read-only preflight and migration planning, provisions the emergency reserve, routes legacy schemas through clone migration before writable database startup, preserves rollback/recovery boundaries, and only then starts `SQLiteDatabase`. The previous integration gap is therefore closed. The remaining divergence is architectural: schema revision execution still uses the custom/library-neutral migration stack rather than the Beta-specified SQLAlchemy 2.x + Alembic toolchain.
- **Desired state:** make the Alembic-vs-custom revision engine an explicit architecture/spec decision. If the custom engine is retained, document the intentional Beta override and the equivalent migration-safety invariants; otherwise migrate revision execution to Alembic without weakening the clone/activation/recovery safety stack.
- **Dependencies:** storage bootstrap integration is present; no longer blocked on routing legacy startup through the coordinator.
- **Verification:** 2026-08-23; inspected current `src/athena/storage/bootstrap.py`, migration stack, and current branch diff. Product tests were not executed by the Scout.

### FG-014 — Reject network-backed active state roots before SQLite open
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- Windows UNC/mapped remote roots and known Linux network filesystems are refused before RuntimeLayout mutation and SQLite preflight. Remote backup/archive/projection remain separate supported targets.

### FG-015 — Physical Emergency Reserve and disk-pressure policy
- **Source:** Beta 03 emergency reserve/disk-pressure sections and Emergency Reserve Test 270.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Current state:** `EmergencyReserveStore` and lifecycle policy implement non-sparse physical allocation at `state_root/reserve/emergency.reserve`, exact default sizing `max(256 MiB, min(1 GiB, 1% volume))`, durable persistence, path/reparse safety, explicit release and normal-shutdown retention. `DiskPressureController` implements integer-only WARNING/CRITICAL/EMERGENCY thresholds, releases only the reserve at EMERGENCY, immediately reassesses pressure, exposes `assert_noncritical_write_allowed()`, and never deletes canonical data. Bootstrap ordering is now real: `RuntimeLayout -> migration-root/preflight -> reserve provisioning -> clone migration if required -> SQLite start`; EMERGENCY refuses writable startup. The remaining integration gap is runtime write gating: `SQLiteDatabase.write_transaction()` does not yet invoke the disk-pressure gate, so an already-running process has no centralized transaction-boundary enforcement when free space later falls into EMERGENCY.
- **Desired state:** inject the pressure gate at canonical write-transaction boundaries (or an equivalent single authoritative write path), enter/readily expose read-only safe mode when EMERGENCY is reached after startup, and preserve critical recovery operations without permitting ordinary writes. Avoid per-start test allocation of >=256 MiB through dependency injection/fakes.
- **Dependencies:** bootstrap/reserve ordering is implemented; remaining work belongs at runtime write arbitration/safe-mode integration.
- **Verification:** 2026-08-23; inspected current `storage/bootstrap.py`, `storage/disk_pressure.py`, and `storage/database.py`. `DiskPressureController.assert_noncritical_write_allowed()` exists but has no call in `SQLiteDatabase.write_transaction()`.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Shared provider/generation files remain ownership-sensitive.
- FG-012 must never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013 clone/journal/startup routing is implemented; only the Alembic-vs-custom architecture/spec decision remains.
- FG-014 applies only to active state/database roots.
- FG-015 reserve release is an emergency recovery measure; normal shutdown must retain it. Runtime noncritical writes still need centralized pressure gating after startup.
