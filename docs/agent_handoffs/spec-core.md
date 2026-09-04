# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@a0e0a2bcf76b0e7f77bb3cd15b8c2ccf79d5c600`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization was completed through GitHub PR #64, merging current Develop into the worker as `029bb7042c2f38f5d2d68c782d74679f66b72c5a`. No `main` mutation occurred.

## Current verified foundation

Develop already verifies normal-Hybrid Search facade/application composition and temporal contradiction composition. Canonical Exhaustive Research coverage accounting and the durable ResearchScope counter composition are implemented on the Core lineage.

Exact Core head `ae691a463c0188c3b8c824a5d9d784297efcff5d` passed canonical ATHENA Quality Gate `33858321148` with conclusion `success`; this verifies durable ResearchScope counter composition product `341852850c18766f88833530f9e73565c268c3d0` plus the focused persistence acceptance test on that exact lineage.

## Implemented product slice — Research coverage formula identity drift

Product commit: `b1e93c5bd3121bcb8c871964e8a24b65a200694a`.
Focused test commit: `9b4fe08205f50cbc57004044685058c5f01a51b5`.

Current code inspection exposed two distinct persisted formula identifiers for the same Beta §36 coverage contract:

- `ResearchService` already pins `eligible-success-or-irrelevant-v1` into the durable Research job configuration and rejects drift from that value during initialization;
- canonical `ResearchCoverage.result_payload()` used `eligible-successful-irrelevant-v1`.

The product correction makes `ResearchCoverage` use the already persisted job-contract identity `eligible-success-or-irrelevant-v1`. No coverage arithmetic changed. The focused test now locks the literal identity and verifies that `ResearchService.COVERAGE_FORMULA_ID` and `athena.research.coverage.COVERAGE_FORMULA_ID` are identical, preventing the two durable surfaces from drifting independently again.

Retained invariants:

- eligible = candidate_total - excluded_count;
- processed = successful + irrelevant + failed + unavailable;
- only successful + irrelevant are coverage-positive;
- failed/unavailable remain visible and never inflate coverage;
- zero eligible work cannot synthesize 100% coverage;
- no schema, transaction, snapshot, recovery, fencing, idempotency, provider/transport, security, provenance, PALLAS or UI semantics changed.

## Verification state

- Durable ResearchScope composition exact head `ae691a463c0188c3b8c824a5d9d784297efcff5d`: canonical Quality `33858321148` = `success`.
- Current formula-identity product/test head `9b4fe08205f50cbc57004044685058c5f01a51b5`: canonical Quality not yet observed at this handoff update. No PASS is claimed for the new formula-identity correction until an exact product-containing run completes successfully.

## Coordination

- Backend-owned Research runtime/input boundaries and deeper Storage/Recovery/System contracts remain untouched.
- UI-owned presentation/accessibility/visual files remain untouched.
- Error handoff currently has no open confirmed Core defect.
- `main` and `bnbgrs/ATHENA` remain read-only and unchanged.

## Integrator handoff

READY for the previously pending durable ResearchScope counter composition: exact verified worker head `ae691a463c0188c3b8c824a5d9d784297efcff5d`, product `341852850c18766f88833530f9e73565c268c3d0`, canonical Quality `33858321148` = `success`.

NOT READY for formula-identity correction `b1e93c5bd3121bcb8c871964e8a24b65a200694a` + `9b4fe08205f50cbc57004044685058c5f01a51b5` until exact canonical Quality is green.

## Next Core action

First consume exact Quality for `9b4fe08205f50cbc57004044685058c5f01a51b5`. If green, hand off the formula-identity correction as READY. Then compose `ResearchCoverage.result_payload()` into `ResearchResult` finalization so Beta §36 stores the exact canonical formula and counters from one policy object without duplicate arithmetic, preserving existing result idempotency, snapshot, fencing, problem-source visibility and provenance semantics.
