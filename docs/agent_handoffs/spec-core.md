# pATHENA Alpha/Beta Core Handoff

## Baseline

- Shared baseline: `develop/pathena-next@647ea036329280378a7e573aca0df905f48ac3b1`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge: `3cd0a0d4e5ddd936ab7dbdf08c9632057ecece41`, retaining the prior Core lineage and current Develop as parents.

## Verified prior slices

- Normal-Hybrid facade/application composition is `VERIFIED` and integrated on Develop. Worker product `e93cd24ce3deaf19d4fe6cdc2c14169a2ad9c1be` passed bounded run `33795894172`; Integrator applied the reviewed product/test blobs in `a104b7c9c3b3108cd13e1653c8f9794116108dfd`; combined Develop validation `33799110483` succeeded.
- Temporal contradiction disjoint-window policy is `VERIFIED` and integrated on Develop. Worker product `f2db1041d73312b27fe9d74eb82f0f5c76f297aa` plus tests `76a4ab8011ee163e2ce1c58fd01772e006273fc9` passed canonical Quality `33801697326`; Integrator applied equivalent product/test contents in `a915719f6ac7dd8e3b212d1f39cbaef077c89b02` and `df981f2718d7df508dfb608261b93abebaccbc0a`.

## Current gap — canonical contradiction review gate

Spec anchors: Beta Knowledge/Claims §§56, 58, 60, 69–70.

The integrated temporal policy operates on canonical `ClaimDraft` validity windows, but the model-proposal acceptance path queues contradiction review from exact Claim revision IDs. A safe composition prerequisite is therefore an exact-revision adapter that reconstructs the persisted Claim payload and applies the temporal policy before review enqueue.

Implemented this run:

- Product commit `214e0dc3ff8d7227bae023d7f368ebfa62daa779` adds `src/athena/knowledge/contradiction_review_gate.py`.
- Test commit `b3a87154fda34c9d9044d0bb1f2f58d4e37471f5` adds focused coverage.
- `assess_canonical_claim_revisions(connection, left_revision_id, right_revision_id)` is bound to exact persisted Claim revisions, not mutable heads.
- The adapter reconstructs only established canonical Claim fields and delegates the temporal decision to `TemporalContradictionPolicy`.
- Provably disjoint validity windows return `DISJOINT`; touching, overlapping, open, or unknown bounds remain contradiction-review candidates.
- Missing/non-Claim revisions fail closed; no temporal values are inferred.
- No Claim/relation/review/persistence mutation occurs in this slice.

Focused tests cover disjoint revisions, touching windows, unknown bounds, missing revisions and invalid revision-ID types.

## Verification state

`IMPLEMENTED_PENDING_VERIFY`.

PR #56 remains a draft verification vehicle targeting `develop/pathena-next`; it must not auto-merge. At handoff update time no exact-head workflow run was yet observable for `b3a87154fda34c9d9044d0bb1f2f58d4e37471f5`, so no PASS is claimed.

## Ownership / collision avoidance

- Backend owns ExternalAccessGateway/runtime-system boundaries.
- UI owns current UI-GAP/ERR-0004 startup/readiness work.
- Error worker owns canonical error closure and regression scanning.
- Core does not modify UI, transport, storage schema, security policy or main.

## Integrator handoff

Not READY until exact worker verification exists. Review only the two-file product/test delta after Quality starts/completes; do not integrate merely from static inspection.

## Next Alpha/Beta gap

After this adapter is green, compose it into `ProposalAcceptanceService` immediately before contradiction-review enqueue. For a model-proposed `contradicts` relation, exact canonical revision pairs assessed as `DISJOINT` must not enqueue contradiction review; overlapping/touching/unknown windows must preserve existing explicit human-review behavior. Historical Claims must remain intact and no contradiction relation may be auto-created.
