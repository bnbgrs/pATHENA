# pATHENA Feature Integrator Handoff

## Current integration

- Integration target: `develop/pathena-next`.
- Develop parent before this integration: `8c2dda7794ef4949844feb30d265d34248aa4660`.
- Exact parent canonical Quality `34744264489 = SUCCESS`.
- Selected Core source candidate: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`.
- Exact candidate Core Focused `34745747874 = SUCCESS`; canonical Quality `34745747939 = SUCCESS`.

## Iteration 1 — truthful stale-Knowledge policy integrated

The integration adds only `src/athena/knowledge/staleness_policy.py` and `tests/unit/test_stale_knowledge_policy.py` from the exact-green Core candidate. The policy treats recorded `valid_to_us` as a maintenance signal only: expired validity may signal stale, the exact boundary is not yet stale, and missing end-validity remains insufficient temporal evidence rather than an invented permanently-current claim. It does not mutate epistemic status, infer source age, claim falsity or fabricate replacement revisions.

The worker branch history is not merged. The bounded product/test slice is extracted onto the exact Develop parent.

## Current worker state observed before mutation

- Errors: `0e90f96d3819a37a5143e2d9c58495eace67c586`.
- Spec/Core: `12a2c2a4ac14c14a28f3bcfda9429d4db7a61830`.
- Backend: `2182382b8aa4a2c37cbf698c51b9de8f7c148287`; new paired-sidecar fix requires its own exact focused plus canonical qualification before any Storage integration.
- UI: `402d80180d29a4a9ddf1d678bc9f75c808bbbb16`; no UI slice is promoted without current exact evidence.

## Persistent release guards

Retain without relaxation: pypdf packaging; fail-closed Frozen argv; Desktop/Worker two-EXE split; exactly one Desktop instance with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock cluster; duplicate-column/Core-startup/storage-bootstrap signatures; Security/Storage/Recovery guards; no Skip/XFail. `main` and `bnbgrs/ATHENA` remain read-only.

## Visual truth

Eleven-screen parity remains fail-closed: no `MATCH` without opened original reference plus real exact-SHA render. Historical `ERROR_LEDGER.md` state does not override current exact-SHA evidence.

## Promotion state

`PROMOTION_READY=NO`

Require canonical Quality on the resulting exact Develop SHA before any further Develop mutation.
