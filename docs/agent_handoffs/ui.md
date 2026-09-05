# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@cf33955bcaa91649f2b5ac1142940e5e72ffa43a`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `f5f8ba8b261a1e586eb682a4af68b1968e841fab`, with parents `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` + `cf33955bcaa91649f2b5ac1142940e5e72ffa43a`; Develop changes were limited to current Integrator/progress plus local HTTP product/test files and were disjoint from the Settings slice.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0019 — unavailable provider detail copy

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `6bfce859c177dfc75119a63c270c028b5b3c5772` changes only the provider-absent presentation fallback to `Model provider is unavailable in the local Core snapshot.`;
- explicit `model_error` still has first precedence, provider-supplied detail retains provider-present precedence, and generic readiness copy remains only the provider-present/no-detail fallback;
- focused test `de688468ff3265d997a2b4c5a39d0aebdf89a9da` verifies exact copy, `error/unavailable` state, and synchronized accessible description for a real snapshot with `provider=None`;
- harness-only commit `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` aligned an unrelated deterministic LM Studio monotonic-deadline fixture with the unchanged bounded transport checks without weakening assertions or product semantics;
- exact final UI head `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` passed ATHENA Quality Gate `33937005854` with conclusion `success`;
- no provider/backend/storage/network/security behavior changed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Current Develop Integrator/progress and local HTTP product/test changes were incorporated through the non-force synchronization merge and are disjoint from the Settings slice.
- Core owns Search/Research/Knowledge composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- READY: UI-GAP-0019 bounded UI lineage `6bfce859c177dfc75119a63c270c028b5b3c5772` -> `de688468ff3265d997a2b4c5a39d0aebdf89a9da`, with final exact-green descendant `f6d2b3afe58fcb0552a0fbd7c72737c2038b18b0` backed by ATHENA Quality Gate `33937005854 = success`.
- The LM Studio fixture commit on the exact-green descendant is harness-only and unrelated to UI product semantics; Integrator should independently review whether it is already present or needed on current Develop rather than treating it as UI product scope.
- Screen 07 is `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` is claimed.

## Next UI step

Select the next highest evidence-backed interaction/accessibility gap from the synchronized current lineage. Until the original reference images are directly available, make no screenshot-level `MATCH` claim and continue only spec-/ledger-backed state, interaction, accessibility or responsive polishing.