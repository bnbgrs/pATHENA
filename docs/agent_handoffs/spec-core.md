# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE sync merge: `ce465846a084db57e51db9f8009c765863ab64b5`, parents `8ed5913ffc0b1fd222bff854c138ff23e94572bb` and `c91e76804e74595f92c8eb624ce7c5d83b66bad2`.
- Sync tree is exact current Develop plus this versioned Core handoff; previously verified formula-identity product/test content is already integrated on Develop and was not overwritten.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Verified predecessor state

- Normal-Hybrid Search application/facade composition: `VERIFIED / INTEGRATED`.
- Transaction-bound Research source-coverage composition: `VERIFIED / INTEGRATED`.
- Canonical Research coverage formula identity: exact Core head `921c6868c8813c92da200cdd68a0ba12df583e9c`, Quality `33900087353 = success`, and now integrated on Develop.

## ResearchResult repository finalization blocker

`ResearchRepository.finalize_result_fenced()` still does not persist the already-verified Core-owned `source_coverage` payload. Complete exact blob `142c98f8ada90d5ea7266a5a8aeeb83bffe618dc` was retrieved and the minimal target delta remains known, but authenticated mutation currently exposes only complete-file replacement for the 110 KB repository file. Local checkout again failed DNS resolution. No unsafe large-file reconstruction or overwrite was performed.

Per the hard progress rule this blocker was not repeated as the run result; the worker moved immediately to a disjoint evidence-backed Core gap.

## Current slice — attribution-aware contradiction candidate policy

Spec anchor: Beta Knowledge/Claims §59 (different opinions from different sources are not automatically logical contradictions over an objective fact).

Product commit: `2e88324d91b72656e6af707110989edffd25ec6a`.
Focused-test commit: `29722370080121da3d577abe9b88aa84f7403c72`.
Status: `IMPLEMENTED_PENDING_VERIFY`.
Canonical Quality run started on exact product/test head: `33910588440`; it was `pending` when this handoff was written. No PASS is claimed.

The bounded policy suppresses automatic objective contradiction candidacy only when both inputs are explicit `attributed_opinion` ClaimDrafts with two distinct real `attributed_to_entity_id` values. Same-attribution opinions, factual/mixed claim kinds, and missing attribution remain eligible for semantic review; missing identity never causes invented attribution. The slice performs no persistence writes and introduces no Source/Evidence/Provenance/PALLAS data.

Files:

- `src/athena/knowledge/attribution_contradiction_policy.py`
- `tests/unit/test_attribution_contradiction_policy.py`

Acceptance coverage locks:

- distinct identified speakers suppress objective contradiction candidacy;
- same speaker remains review-eligible;
- missing attribution fails open to semantic review rather than inventing identity;
- mixed/factual claims are not suppressed;
- non-ClaimDraft runtime inputs fail fast.

## Ownership / collision avoidance

- Backend deep storage/runtime/recovery/system paths untouched.
- UI-owned presentation/Qt paths untouched.
- Error-owned ERR-0009 work untouched.
- Existing temporal contradiction policy remains unchanged; this is a separate attribution semantic gate for later composition.
- No fake Source, Claim, Evidence, Provenance or PALLAS data introduced.

## Integrator handoff

The previously verified formula-identity slice is already integrated on Develop and requires no further Core import.

Attribution policy is NOT READY until exact canonical Quality for the product/test lineage completes green. Integrator should not import `2e88324d91b72656e6af707110989edffd25ec6a` + `29722370080121da3d577abe9b88aa84f7403c72` before that evidence exists.

## Next Alpha/Beta gap

First consume exact Quality for the attribution policy. If green, hand the product/test commits READY, then compose attribution with the existing temporal contradiction review gate so a candidate is only auto-promoted when neither proven temporal disjointness nor distinct attributed-opinion identity rules it out. Preserve exact revision binding and fail-closed lookup behavior. Repository source-coverage finalization remains pending until a safe bounded mutation primitive is available; do not repeat the same transport blocker without a new mutation path.
