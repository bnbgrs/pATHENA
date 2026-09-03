# pATHENA Alpha/Beta Core Handoff

## Baseline

- Shared baseline: `develop/pathena-next@e98c88e0d3b41b81de7efa70873729f873038080`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE resync merge: `a35dabd7dd3aea8e85a1cca5c401d9e6955dd361`, parents current Develop and previous Core head `23828fc9a9085bc6441231b94bcb3182c4e3c930`.

## Verified prior slices

- Normal-Hybrid facade/application composition is `VERIFIED` and integrated on Develop. Worker product `e93cd24ce3deaf19d4fe6cdc2c14169a2ad9c1be` passed bounded run `33795894172`; Integrator applied it to Develop and combined validation `33799110483` succeeded.
- Temporal contradiction disjoint-window policy is `VERIFIED` and integrated on Develop. Worker product `f2db1041d73312b27fe9d74eb82f0f5c76f297aa` plus tests `76a4ab8011ee163e2ce1c58fd01772e006273fc9` passed canonical Quality `33801697326` and were integrated.

## Current gap — canonical contradiction review exact-revision adapter

Spec anchors: Beta Knowledge/Claims §§56, 58, 60, 69–70.

Product source: `src/athena/knowledge/contradiction_review_gate.py`.
Focused tests: `tests/unit/test_knowledge_contradiction_review_gate.py`.

Contract:

- assess the exact persisted Claim revision IDs that would participate in contradiction review;
- reconstruct only canonical Claim fields and delegate to `TemporalContradictionPolicy`;
- return `DISJOINT` only for provably non-overlapping validity windows;
- touching, overlapping, open, or unknown bounds remain contradiction-review candidates;
- missing/non-Claim revisions fail closed;
- no inferred temporal data, Claim/relation/review mutation, history deletion, storage schema change, UI change, or security-policy change.

The previous exact test head `b3a87154fda34c9d9044d0bb1f2f58d4e37471f5` received Quality run `33807193108`, but that run was cancelled after the PR head moved; therefore it is not PASS evidence.

To avoid repeating an unverifiable stale worker state, this run rebuilt the exact same two reviewed product/test blobs onto the current Develop tree in merge commit `a35dabd7dd3aea8e85a1cca5c401d9e6955dd361`. The merge preserves both histories and contains no foreign-worker product overwrite.

## Verification state

`IMPLEMENTED_PENDING_VERIFY`.

Require an exact-head canonical Quality run for the current worker head after this handoff commit. Do not claim READY until that run succeeds.

## Ownership / collision avoidance

- Backend owns ExternalAccessGateway/runtime-system boundaries.
- UI owns visual/reference-backed UI work.
- Error worker owns canonical error closure and regression scanning.
- Core does not modify UI, transport, storage schema, security policy, or main.

## Integrator handoff

Not READY until exact current-head verification exists. If green, Integrator may review the bounded two-file adapter/test delta independently and integrate only those product/test contents or a compatible descendant.

## Next Alpha/Beta gap

After the exact-revision adapter is green and integrated, compose `assess_canonical_claim_revisions()` into `ProposalAcceptanceService` immediately before contradiction-review enqueue. For model-proposed `contradicts` relations, exact canonical revision pairs assessed as `DISJOINT` must not enqueue contradiction review; touching/overlapping/unknown pairs must preserve existing explicit human-review behavior. Historical Claims remain intact and no contradiction relation is auto-created.
