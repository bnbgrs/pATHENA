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
- **Current state:** The normal `SQLiteDatabase.start()` path still performs legacy live `initialize_schema()` migration. A complete library-neutral safety stack now exists outside startup: read-only migration planning, versioned descriptors and exact free-space preflight, SQLite Online Backup candidate creation, durable external phase journal, exclusive cross-process migration lock, candidate-only schema execution, full WAL checkpoint + DELETE-mode normalization, integrity/FK/version verification, rollback-preserving activation, orphan/journal recovery boundaries and Windows symlink/junction/reparse protection. Quality-reported reparse handling in the new clone path was fixed with targeted regressions.
- **Desired state:** route preflight-detected legacy schemas through this coordinator before opening active SQLite for mutation. Separately decide Alembic-vs-custom revision execution as an explicit architecture/spec decision.
- **Dependencies:** BE-028 IN_PROGRESS; BE-029 reserve bootstrap integration required so migration preflight accounts for the real physical reserve; BE-031/BE-032 DONE.
- **Verification:** 2026-08-23; targeted tests added, not executed because isolated runtime cannot resolve `github.com`.

### FG-014 — Reject network-backed active state roots before SQLite open
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- Windows UNC/mapped remote roots and known Linux network filesystems are refused before RuntimeLayout mutation and SQLite preflight. Remote backup/archive/projection remain separate supported targets.

### FG-015 — Physical Emergency Reserve and disk-pressure policy
- **Source:** Beta 03 emergency reserve/disk-pressure sections and Emergency Reserve Test 270.
- **Ownership / Priority / Status:** BACKEND · P1 · IN_PROGRESS
- **Current state:** `EmergencyReserveStore` and lifecycle service implement non-sparse physical allocation at `state_root/reserve/emergency.reserve`, exact default sizing `max(256 MiB, min(1 GiB, 1% volume))`, durable persistence, path/reparse safety, explicit release and normal-shutdown retention. `DiskPressureController` implements integer-only WARNING/CRITICAL/EMERGENCY thresholds, releases only the reserve at EMERGENCY, immediately reassesses pressure, and never deletes canonical data.
- **Desired state:** integrate Core bootstrap ordering `RuntimeLayout -> EmergencyReserve -> migration/database`; then connect the pressure decision to actual write gating/read-only safe mode. Do not make existing test suites physically allocate >=256 MiB per application start; establish dependency injection first.
- **Dependencies:** BE-029/BE-030/BE-033.
- **Verification:** 2026-08-23; targeted tests added, not executed.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Shared provider/generation files remain ownership-sensitive.
- FG-012 must never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013 clone/journal safety is independent of the Alembic-vs-custom architecture decision.
- FG-014 applies only to active state/database roots.
- FG-015 reserve release is an emergency recovery measure; normal shutdown must retain it.
