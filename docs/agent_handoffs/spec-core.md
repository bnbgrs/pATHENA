# pATHENA Alpha/Beta Core Handoff

## Current source of truth

- Current shared baseline: `develop/pathena-next@2a90e71bc2c604cd745766a608481fc14106ec07`.
- Worker branch before this handoff update: `postmerge/spec-core@571ecf65e3892a424afe8cbc5393e3ef0679ef76`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- `bnbgrs/ATHENA` remains strictly read-only and untouched.
- Current Develop advanced after the worker candidate; the worker is therefore not claimed baseline-current or Integrator-ready solely by virtue of its prior green run.

## Exact candidate verification consumed this run

Canonical ATHENA Quality Gate run `34333900454` completed `success` on exact worker SHA `571ecf65e3892a424afe8cbc5393e3ef0679ef76`.

This closes verification of that exact candidate. The candidate was a history-preserving NON-FORCE synchronization commit with parents `850b631007ba3f359b9b16c619c692d853d75663` and then-current Develop `0abc53a35e6c99bf7070875633d3f81f6bc09395`.

No new product mutation is added in this run because the run's one bounded Core slice is the exact-SHA verification above.

## Current handoff evidence reviewed

- `errors.md`: no current OPEN / IN_PROGRESS / BLOCKED errors are recorded in the checked Develop handoff; historical signatures remain guards only until current-lineage reproduction.
- `backend.md`: Backend owns deletion-ledger / storage-system boundaries; Core does not duplicate that work.
- `ui.md`: inspector presentation/visibility remains UI-owned; Core does not mutate Qt/UI presentation state.
- `integrator.md`: current integration policy preserves canonical Quality guards and reports no new promotion-qualified Core product delta; current Develop has since advanced to `2a90e71bc2c604cd745766a608481fc14106ec07`.

## Closed / retained Core contracts

- Adaptive DirectChat output reserve and 2048-context behavior remain closed absent new exact-current regression evidence.
- Normal Hybrid Search DTO/adapter work already verified on prior Core lineage is not reopened without a current demonstrated gap.
- Contradiction review enqueue bypass remains unmodified unless a concrete current production caller bypassing the canonical gate is demonstrated.
- No fake provenance, synthetic Sources/Claims/Knowledge, or synthetic PALLAS state is permitted.

## Persistent release guards

The following remain binding acceptance guards but are not automatic Core priority absent current reproduction: pypdf/Frozen argv/two-EXE packaging, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock cluster, duplicate-column/Core-startup/storage-bootstrap signatures.

## Readiness

- Exact worker candidate `571ecf65e3892a424afe8cbc5393e3ef0679ef76`: `VERIFIED_EXACT_SHA` by Quality `34333900454 = success`.
- Current worker lineage versus Develop: `BASELINE_STALE` because Develop is now `2a90e71bc2c604cd745766a608481fc14106ec07`.
- Therefore no new Integrator-ready claim is made in this handoff update.

## Next Alpha/Beta Core run

1. Consume any exact-SHA Quality result for the then-current worker head before mutation.
2. Re-read current Develop head, all worker handoffs, Alpha/Beta specs, Capability Coverage, ADRs and relevant focused tests.
3. Select the highest evidenced independent Core gap in Chat, Knowledge, Research, PALLAS, Controller/ViewModel/API composition, Provenance, Claims/Evidence, Durable Knowledge or Human Control.
4. If that gap depends on red/unverified Backend/Storage work, skip it and take the next independent Core gap.
5. Advance exactly one bounded vertical product + acceptance-test slice, or exactly verify an existing candidate; do not reopen already verified slices without new regression evidence.
