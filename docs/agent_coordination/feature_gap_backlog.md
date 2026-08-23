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
- **Current state:** Safe startup routing is implemented end-to-end in the productive Core lifecycle. POSIX filesystem-identity hardening now covers shared durable replacement, journal byte publication, and durable directory creation: all three mutate relative to opened parent-directory FDs and fail closed if the logical parent pathname no longer names that handle. Deterministic parent-replacement regressions cover `os.replace`, `os.open`, and `os.mkdir`. Remaining safety work is the Windows HANDLE equivalent and identity-binding of the SQLite clone destination. The remaining architecture divergence is the custom/library-neutral revision engine versus the Beta-specified SQLAlchemy 2.x + Alembic toolchain.
- **Desired state:** finish BE-036/038/039 without weakening crash durability, then make the Alembic-vs-custom revision engine an explicit architecture/spec decision. If the custom engine is retained, document the intentional Beta override and equivalent migration-safety invariants; otherwise migrate revision execution to Alembic without weakening clone/activation/recovery safety.
- **Dependencies:** storage bootstrap runtime integration is present; POSIX durable publication identity is substantially closed; Windows HANDLE and SQLite clone destination binding remain.
- **Verification:** 2026-08-23 current remote after the POSIX durable-mkdir regression commit. Its quality-gate run is pending, so no green validation is claimed. Status remains PARTIAL rather than VERIFIED.

### FG-014 — Reject network-backed active state roots before SQLite open
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- Windows UNC/mapped remote roots and known Linux network filesystems are refused before RuntimeLayout mutation and SQLite preflight. Remote backup/archive/projection remain separate supported targets.

### FG-015 — Physical Emergency Reserve and disk-pressure policy
- **Source:** Beta 03 emergency reserve/disk-pressure sections and Emergency Reserve Test 270.
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `EmergencyReserveStore` implements non-sparse physical allocation at `state_root/reserve/emergency.reserve`, exact default sizing `max(256 MiB, min(1 GiB, 1% volume))`, durable persistence, path/reparse safety, explicit release and normal-shutdown retention. `StorageBootstrapService` owns reserve-before-database ordering, is wired into the real `AthenaApplication` lifecycle, and refuses writable startup when the volume is already EMERGENCY. Runtime `SQLiteDatabase.write_transaction()` checks the configured `DiskPressureController` before `BEGIN IMMEDIATE`. On first runtime EMERGENCY, the controller releases only the emergency reserve, immediately reassesses, latches read-only safe mode for its lifetime, blocks that transaction and blocks later noncritical writes even if reserve release temporarily improves free space. No canonical data is deleted.
- **Recovery contract:** read-only safe mode is deliberately cleared only by a controlled process restart, which re-runs bootstrap pressure assessment before writable service can resume. Clone migration/recovery paths remain outside ordinary runtime `write_transaction()` arbitration and therefore retain the released reserve headroom for recovery.
- **Verification:** 2026-08-23 production wiring revalidated; no green gate is newly claimed.

### FG-016 — Verify safety-critical SQLite PRAGMAs after applying them
- **Source:** Beta 03 sections 30–40, especially section 30 (`foreign_keys` readback), section 33 (configurable `busy_timeout`) and section 37 (`trusted_schema` readback).
- **Ownership / Priority / Status:** BACKEND · P1 · IMPLEMENTED
- **Current state:** `storage/connection_policy.py` now owns the live per-connection safety contract. It accepts only integer busy timeouts in the bounded 5,000–120,000 ms range, applies `foreign_keys=ON`, configured `busy_timeout`, and `trusted_schema=OFF`, then reads all three back and raises `DatabaseCompatibilityError` unless SQLite confirms the requested state exactly. `SQLiteDatabase` accepts the bounded timeout, uses the same value for `sqlite3.connect(timeout=...)`, and reapplies/verifies the policy after schema initialization so the productive live connection cannot silently continue with a refused safety pragma. The application default remains the historical 5,000 ms floor; callers can explicitly supply a larger bounded runtime value through the database service contract.
- **Tests:** focused regressions cover invalid/valid timeout boundaries, direct policy application/readback, and the real `SQLiteDatabase.start()` path with a non-default timeout.
- **Dependencies:** none beyond existing SQLite bootstrap.
- **Verification:** 2026-08-23 current remote after commits `525936a`, `80bbb3e`, `4fe780f`. The quality-gate run associated with the test commit was cancelled, so status is IMPLEMENTED rather than VERIFIED and no test pass is claimed.

## Handoff notes
- Re-read current HEAD and affected files before every mutation.
- Preserve `unknown` versus `unsupported`; never invent provider facts.
- Shared provider/generation files remain ownership-sensitive.
- FG-012 must never route protected cleartext into ordinary indexes/logs/run snapshots/unprotected assistant persistence.
- FG-013 clone/journal/startup routing is implemented; BE-036 POSIX durable publication is substantially closed, with BE-038 Windows HANDLE publication and BE-039 SQLite clone destination binding still READY. Alembic-vs-custom remains an explicit architecture decision.
- FG-014 applies only to active state/database roots.
- FG-015 runtime write arbitration is implemented and wired into application startup; promote to VERIFIED only after a green relevant gate.
- FG-016 is implemented in the live database service and should move to VERIFIED only after a green relevant targeted/full gate.
