# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `5048e8f2e88c1ac0553d3052db48c9c3be22bff1`.
- Exact canonical Quality on that parent: `34851187301 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain strictly read-only.
- `BUNDLED_SLICES=NONE` — this is a single Backend-owned bounded slice; Storage/Recovery-adjacent work is not bundled.

## Iteration — periodic Deep backup verification planner

Source head: `d0da4ca3677ebcda1e65e1637fd0d447810fb7fb`.
Exact evidence: Backend Focused `34851416776 = SUCCESS`; canonical Quality `34851416765 = SUCCESS`.

Only two bounded blobs are integrated from the worker lineage: `src/athena/jobs/backup_verify.py` and `tests/unit/test_backup_deep_verify_planner.py`. No worker history is merged.

The new planner deterministically selects the oldest active completed backup snapshot whose Deep verification is due. It excludes failed, pruned, offline and not-due snapshots, uses a deterministic occurrence slot and idempotency key, leaves retryable environment/busy failures due for later orchestration, and fails closed on invalid runtime types or negative timestamps. It performs no backup creation, verification execution, schema change, migration or recovery mutation.

## Current worker truth at integration time

- Errors: `a80e39b8b1669086d8db00deea10a7d37041507f` — documentation/evidence refresh only.
- Spec/Core: `7719c3f18de715fe1343980bdc466a2d12cdb286` — supersession slice already represented in Develop.
- Backend: `d0da4ca3677ebcda1e65e1637fd0d447810fb7fb` — bounded Deep verification planner selected here.
- UI: `575b8de0a4f25f512e423c78623bfa5b398c379d` — not selected; separate PALLAS candidate qualification remains UI-owned.

## Source-of-truth notes

- `docs/agent_logs/ERROR_LEDGER.md` remains historical wherever newer exact-SHA evidence exists; historical signatures are not OPEN without current reproduction.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md` remain fail-closed: no `MATCH` without opened original reference and real exact-SHA render. Verified Send target remains 44×44 outer geometry.
- The Backend worker handoff is stale relative to its current head, so this integration relies only on the bounded current-head code/test delta plus exact-head focused and canonical evidence; no broader Backend claims are imported.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail.

## Promotion state

`PROMOTION_READY=NO`

Require complete canonical Quality `SUCCESS` on the resulting exact Develop SHA before any further Develop mutation.
