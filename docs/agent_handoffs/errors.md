# pATHENA Error Handoff

## Baseline

- Develop source of truth: `develop/pathena-next@c217747f73267842ebd26c10eb5affc4fbf7bc0d`.
- Error worker entered this run at `postmerge/errors@901377dbb247161ac2a4be578967a14c9c86741d`.
- Current workers: Spec/Core `b8df82b23583d42a8d5ae8f387aea0fbd0e7859e`; Backend `c5e750a827de4b353da9873cb38d95b46a119d60`; UI `af50dfb76b04e396a2dbf65ec1eeb265f30177fa`.
- Exact current Develop Quality `34443327522@c217747f73267842ebd26c10eb5affc4fbf7bc0d = SUCCESS`; Python quality/full pytest, Windows path safety, Linux storage and Local-install/pypdf all pass.
- Exact current Backend Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60 = FAILURE`; Linux storage, Windows path safety, Local-install/pypdf, specification validator and mypy pass, while Ruff and pytest fail.
- `postmerge/errors` had no canonical Quality runs before either documentation mutation in this run.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current error state

- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`.
- IN_PROGRESS: `ERR-0026`, `ERR-0028`, `ERR-0029`.
- STALE: `ERR-0014`, `ERR-0025`.
- OPEN/BLOCKED: none at top level from exact evidence consumed this run.

## Hard progress this run — ERR-0026 exact-current revalidation

### ERR-0026 — Backend Ruff/import-layout drift

Status: `IN_PROGRESS`.

The current Develop baseline is fully canonical-green via `34443327522@c217747f73267842ebd26c10eb5affc4fbf7bc0d`, so no Develop P1/P2 failure outranks worker-local current evidence.

The current Backend head `c5e750a827de4b353da9873cb38d95b46a119d60` now has exact canonical evidence: Quality `34441278497` completed `FAILURE`. Its Linux storage, Windows path safety and Local-install/pypdf jobs are green. Inside Python Quality, specification validation and mypy pass, while Ruff and pytest fail. This reactivates `ERR-0026` from current exact-SHA evidence rather than historical carry-forward.

The current Backend `src/athena/storage/schema.py` is blob `b5658c38ca061095a951bc85f3a2fbc88b53ee76`. It retains the grouped `schema_contract` import layout together with the `research_delta_migration` import. Current Develop is Ruff-green on the same configured canonical Quality and carries formatter-normalized `schema.py` blob `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`.

Backend commit `c5e750a827de4b353da9873cb38d95b46a119d60` itself changes only `docs/agent_handoffs/backend.md` relative to `31752aefe0d5f79d8c305c531cc7584c0585e175`; it did not change `schema.py`. Therefore the new exact-current Quality run independently revalidates the existing worker source formatting state rather than introducing a different product-code root cause.

Root-cause classification for this bounded cluster: formatter/import-layout drift in Backend worker source. It is separate from the worker's v41 pytest lineage and separate from Storage/Recovery behavior. Backend owns this source lineage, so Errors does not parallel-edit `schema.py` while the Fach-Worker is active.

Required Backend action: apply the pinned Ruff-normalized import layout only, run focused Ruff on `src/athena/storage/schema.py`, then the smallest relevant regression/canonical set. No `FIXED` claim until a real exact-SHA Ruff PASS exists. No Ruff bypass, Skip/XFail, assertion change, or product-guard weakening.

## Closed current Develop cluster

### ERR-0031 — Windows storage-bootstrap path portability

Status: `FIXED`.

Develop `4046459bf2b91f9d30efee1f9b726c40080e2408`, canonical Quality `34439530635`, verified the complete Windows path-safety job green including `Run Windows storage path regressions = SUCCESS`. Current Develop `c217747f73267842ebd26c10eb5affc4fbf7bc0d` is now globally canonical-green via `34443327522`, so no exact-current recurrence exists.

The bounded fix remained test-only: `_ReserveStub.ensure()` now uses a platform-valid absolute reserve path. Production Storage/Recovery/path-safety invariants were not weakened.

## Other worker clusters

### ERR-0028 — Backend v41 harness lineage

`IN_PROGRESS`, P2. Current Backend Quality `34441278497@c5e750a827de4b353da9873cb38d95b46a119d60` confirms pytest remains red, but this run intentionally advances only `ERR-0026`. Historical stale terminal-v41 assertions and legacy-fixture rewind defects are not promoted to current assertion-level truth without new diagnostics. Never weaken production migrations with `IF NOT EXISTS` or swallowed `OperationalError`.

### ERR-0029 — WAL exact-type harness drift

`IN_PROGRESS`, P2 pending exact-current assertion-level diagnostics. Preserve production exact-type fail-closed guards.

## Integrator handoff

- Current authoritative Develop: `c217747f73267842ebd26c10eb5affc4fbf7bc0d`; canonical Quality `34443327522 = SUCCESS`.
- `ERR-0031 = FIXED`; no current Develop error is reproduced.
- Current Backend: `c5e750a827de4b353da9873cb38d95b46a119d60`; canonical Quality `34441278497 = FAILURE` with Ruff and pytest red, other major lanes green.
- `ERR-0026 = IN_PROGRESS` from exact-current evidence. Root cause is bounded formatter/import-layout drift in Backend `src/athena/storage/schema.py`; Errors deliberately made no parallel source mutation because Backend owns the lineage.
- Current Backend `schema.py` blob: `b5658c38ca061095a951bc85f3a2fbc88b53ee76`; Ruff-green Develop comparison blob: `9d6d9fd410662e7f1ec311a93a1e8ee135c51e5f`.
- Do not integrate broad Backend v41/WAL/Storage history merely to repair worker-local Quality. Require bounded reconciliation and exact verification.
- Preserve pypdf packaging, frozen argv, two-EXE split, bounded workers, adaptive 2048-context reserve, Windows lane-lock mapping and duplicate-column/Core-startup/storage-bootstrap release guards.

## Next verification

Consume any newer exact Develop/Backend Quality first. If Develop remains green and Backend has not advanced, do not count re-reading `34441278497` as new progress. The next useful action is either a real focused/exact Backend Ruff verification after its owner fixes `schema.py`, or assertion-level decomposition of exactly one still-current Backend pytest root-cause cluster.
