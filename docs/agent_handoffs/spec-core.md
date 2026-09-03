# pATHENA Alpha/Beta Core Handoff

## Current baseline

- Shared baseline: `develop/pathena-next@a728668f046bf0d8b66724bb8004a1767bd5589f`.
- Stable read-only branch: `main@0d4d621f8a38ddf8eccfa09622bf193687619943` (unchanged).
- Worker branch: `postmerge/spec-core`.
- History-preserving NON-FORCE synchronization merge for this run: `06b4e1a56308478d342ad8dfcd3175a9258266fd`, with parents prior Core head `8d5fa074a30451d5d8c8d2f8897689883c65a1ed` and current Develop `a728668f046bf0d8b66724bb8004a1767bd5589f`.

Normal-Hybrid `CoreApiFacade <-> AthenaApplication` composition is already integrated on Develop and is no longer an active Core gap.

## Current spec anchor

Primary source: `docs/beta/05_Wissenseinheiten_Claims_und_Wissensgraph.md`.

- §56: contradiction detection may identify potential contradictions, initially as candidates.
- §58: claims from non-overlapping validity periods must not be misclassified as the same temporal contradiction.
- §60: contradiction resolution preserves historical claims rather than deleting them.
- §69–70 require contradiction and temporal tests.

The existing Claim model already carries validated `valid_from_us` / `valid_to_us` fields, but the current Core had no small deterministic reusable policy that can prove two Claim validity windows disjoint before semantic contradiction marking/review.

## Slice this run — temporal contradiction gate

Product commit: `f2db1041d73312b27fe9d74eb82f0f5c76f297aa`.
Focused-test commit: `76a4ab8011ee163e2ce1c58fd01772e006273fc9`.

Added `src/athena/knowledge/contradiction_policy.py` with:

- `TemporalContradictionState` (`overlapping_or_unknown` / `disjoint`);
- immutable `TemporalContradictionAssessment` preserving both input validity windows;
- `TemporalContradictionPolicy.assess(left, right)` over canonical `ClaimDraft` values;
- fail-closed type validation for non-Claim inputs;
- open/unknown bounds treated as uncertainty rather than evidence of separation;
- only provably disjoint windows suppress a contradiction candidate;
- touching windows remain potentially overlapping.

This policy makes no semantic truth judgment, changes no Claim, writes no database rows, creates no relation/review, and does not infer missing time bounds. It is intentionally a deterministic gate to be composed into the existing contradiction-review path in a later bounded slice.

## Focused acceptance coverage

`tests/unit/test_knowledge_temporal_contradiction_policy.py` covers:

1. Beta-style non-overlapping periods (2024 vs 2026) => `DISJOINT`, candidate suppressed;
2. touching windows => not proven disjoint;
3. unknown/open bounds => candidate remains possible;
4. open-ended disjoint windows detected symmetrically;
5. non-Claim inputs rejected.

Draft verification PR `#56` targets `develop/pathena-next` from `postmerge/spec-core`; it is a verification vehicle only and must not auto-merge. ATHENA Quality Gate run `33801697326` is in progress on exact worker head `76a4ab8011ee163e2ce1c58fd01772e006273fc9`. No PASS is claimed until that run completes successfully.

## Product contract / invariants

- Temporal separation can only suppress contradiction candidacy when disjointness is provable from canonical validity bounds.
- Missing temporal bounds remain unknown/open, never synthesized.
- Existing Claim temporal-range validation remains authoritative.
- No automatic canonical relation is created by this policy.
- No historical Claim is deleted or rewritten.
- No persistence, security, recovery, storage, UI or provider semantics changed.

## Coordination

- Backend retains ExternalAccessGateway and deep system/runtime ownership.
- UI/Error retain `ERR-0004` / `UI-GAP-0004` ownership.
- Core did not touch active Backend/UI/Error files.
- `main` remains read-only.

## Integrator handoff

Current slice is `IMPLEMENTED_PENDING_VERIFY`, not READY yet. Integrator should consume exact Quality run `33801697326`; only if green should the bounded two-file product/test slice be considered for integration.

Do not treat the policy as full contradiction handling. It does not yet modify the existing `ProposalAcceptanceService` contradiction-review enqueue path.

## Next Alpha/Beta gap

After exact-head verification, compose this temporal gate into the existing contradiction-candidate/review path so a model-proposed `contradicts` relation with provably disjoint validity windows cannot enqueue a contradiction review, while overlapping/unknown windows retain current review behavior. Preserve atomic acceptance, provenance, historical Claims and explicit human review.
