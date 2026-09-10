# Post-Merge Feature Handoff - Integrator

Generated: 2026-09-10T08:50Z
Branch: `develop/pathena-next`
HEAD at run start: `8c342e1b6ea07025983726ec24d48786759c28fa`

## Current evidence

- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Exact Develop canonical Quality `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa = SUCCESS`.
- No queued or in-progress canonical Quality existed on Develop immediately before this mutation.
- Worker heads reviewed: Errors `c6ff8849cd49badfb94688610bc9e01dda3b65c1`, Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`, Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`, UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- No new worker slice is promotion-ready. Backend's latest head is documentation-only over a previously red broad Storage/Migration lineage and has no equivalent exact-head green candidate evidence; Spec/Core and UI expose no new unintegrated bounded product slice; Errors reports worker-local v41 fixture/assertion clusters rather than a current Develop defect.
- Current UI source-of-truth files are `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` and `docs/ui/VISUAL_GAP_LEDGER.md`. No already-integrated UI/Core slice is re-applied.

## Cross-cutting slice — duplicate-column startup regression contract

- Added `tests/unit/test_schema_reinitialization_contract.py`.
- The contract initializes a fresh ATHENA database to the current schema and then invokes `initialize_schema()` again on the same current-schema database. The second initialization must complete while preserving `SCHEMA_VERSION`; any accidental reapplication of an additive column migration would surface as a SQLite duplicate-column failure rather than being masked.
- Canonical Quality runs this test in the existing Windows storage-path job, giving the persistent duplicate-column/Core-startup class explicit Windows evidence.
- This does not make schema migrations idempotent, catch/ignore `sqlite3.OperationalError`, or relax compatibility checks. Malformed partial legacy fixtures still fail closed.
- Production storage, recovery, migration, runtime and security behavior are unchanged.

## Persistent release guards

- pypdf packaging remains fail-closed.
- Frozen argv remains fail-closed.
- Desktop/Worker two-EXE topology remains guarded.
- Exactly one Desktop instance with bounded workers remains a Windows-Beta requirement.
- Adaptive 2048-context Chat reserve remains guarded.
- Windows lane-lock/path-safety cluster remains guarded.
- Storage-bootstrap and Core-startup are explicitly exercised in Windows canonical Quality.
- Duplicate-column startup reinitialization is now explicitly exercised in Windows canonical Quality, pending exact-result consumption for the resulting Develop SHA.

## Next integration

1. Consume canonical Quality on the resulting exact Develop SHA; freeze Develop while queued/in progress.
2. If the new contract fails, treat the exact failure as evidence and fix only its smallest current-Develop root cause; do not weaken schema safeguards.
3. Keep broad Backend v41/WAL/Storage/Migration history on HOLD absent a fresh bounded exact-green candidate.
4. Do not re-integrate already landed UI/Core slices.
