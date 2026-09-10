# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@7f4de6d99485972f2abf39e8e8c01fdeed513821`.
- Error worker entered this run at `postmerge/errors@c6ff8849cd49badfb94688610bc9e01dda3b65c1`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Previous Develop canonical Quality `34452334591@8c342e1b6ea07025983726ec24d48786759c28fa = SUCCESS`.
- Current Develop canonical Quality `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821` is still `IN_PROGRESS`; its `Windows path safety` job has already failed specifically at `Run Windows storage path regressions`.
- Same current SHA already has Linux storage and Local-install/pypdf green; specification validator, Ruff and mypy are green; full pytest remains in progress.
- `postmerge/errors` had no canonical Quality runs before mutation.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- OPEN: `ERR-0032`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- STALE: `ERR-0014`, `ERR-0025`.
- BLOCKED: none.

## Hard progress this run — ERR-0032 exact-current regression boundary

### ERR-0032 — Windows schema-reinitialization contract lane regression

Status: `OPEN`, P1 current Develop integration blocker.

The previous authoritative Develop `8c342e1b6ea07025983726ec24d48786759c28fa` is canonical-green via Quality `34452334591`. Current Develop `7f4de6d99485972f2abf39e8e8c01fdeed513821` is exactly one commit ahead. That commit changes no production source: it adds `tests/unit/test_schema_reinitialization_contract.py`, appends that test to the Windows storage regression command, and refreshes the Integrator handoff.

Canonical Quality `34457702662` on exact current SHA `7f4de6d99485972f2abf39e8e8c01fdeed513821` provides new hard evidence: `Windows path safety` is already `FAILURE`; deterministic Windows locality passed, then `Run Windows storage path regressions` failed. Linux storage and Local-install/pypdf pass on the same SHA, as do specification validator, Ruff and mypy. Full pytest is still running.

The newly introduced contract opens a fresh SQLite database, calls `initialize_schema()`, verifies `PRAGMA user_version == SCHEMA_VERSION`, calls `initialize_schema()` a second time on that same current-schema database, and verifies the version again. The contract is specifically meant to expose accidental additive-migration replay / duplicate-column startup behavior without making migrations idempotent or swallowing SQLite errors.

This exact delta and lane result localize the current regression to the newly introduced Windows execution surface of that contract or an interaction it exposes. The Windows job does not persist its stdout as canonical diagnostics, and the overall run is still active, so the exact assertion/exception is not yet available. Do not invent it and do not patch production behavior speculatively.

Required next action: consume `34457702662@7f4de6d99485972f2abf39e8e8c01fdeed513821` first after completion. Isolate the exact failing Windows assertion/exception from the completed run or a focused reproduction before any fix. Preserve duplicate-column detection, Storage/Recovery/startup fail-closed behavior, and all persistent release guards. No competing Develop Quality while the current run is active.

## Lower-priority worker clusters held

### ERR-0026 — Backend Ruff/import-layout drift

`IN_PROGRESS`, P2 worker-local. Last exact red worker evidence remains `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60`; current Backend head `7ef45c5e37d98f56ba9327353ec7f9a8b615a0f2` is later documentation/handoff state without new canonical evidence. Error/Develop already carry the normalized schema import layout. Do not create a duplicate Error-owned formatter patch.

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2 worker-local. Last exact diagnostics still decompose into nine stale terminal-v41 assertions, six duplicate-v41-table fixture collisions, and two downstream storage-bootstrap cascades. Broad v41 worker history remains HOLD and must not be integrated mechanically.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending fresh exact-current Backend evidence. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current Develop: `7f4de6d99485972f2abf39e8e8c01fdeed513821`.
- Current canonical Quality: `34457702662`, still active; Windows path safety already failed at Windows storage regressions.
- `ERR-0032 = OPEN / P1`: regression boundary is the single commit from canonical-green `8c342e1b...` to `7f4de6d9...`; no production source changed, only the new schema-reinitialization contract plus its Windows-lane inclusion.
- No exact exception is claimed yet. Consume the completed run first; then focused-reproduce and fix only the smallest root cause.
- Keep lower-priority Backend v41/Ruff/WAL clusters on HOLD while this current Develop P1 exists.
- Preserve pypdf packaging, Frozen argv, two-EXE topology, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping, duplicate-column/Core-startup/storage-bootstrap guards.
