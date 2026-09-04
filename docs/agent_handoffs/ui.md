# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@25089e434412e7c1b8ede229438324338a0d5da0`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `713408e4495cdda3d4ff2a1e3650a852fa68ca59`, with parents `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` + `25089e434412e7c1b8ede229438324338a0d5da0`; Develop changes were disjoint attribution-policy/integration/progress files.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0018 — unavailable provider detail semantic state

Status: `FIXED / INTEGRATOR_READY`, P2.

Verified implementation:

- product `82fb17da950f8234e28c69bd576e38047ba9b2bb` makes unavailable provider detail fail closed to `error` while retaining `unavailable` freshness;
- focused test `6aad966258288a7519af6d261dea4695e7ffde76` verifies provider/detail state coherence and synchronized accessibility for a real snapshot with `provider=None`;
- exact canonical failure on the first candidate showed provider absence still exposed `pathenaRuntimeFreshness=fresh` despite unavailable presentation;
- corrective product `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` makes provider absence force `provider_freshness=unavailable` consistently for provider and detail;
- exact corrective UI head `9df9d7d46e3c4774aeea5439f91166a2092bd7fb` passed ATHENA Quality Gate `33926653411` with conclusion `success`;
- no provider/backend/storage/network/security behavior changed.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Current Develop attribution-policy product/test plus Integrator/progress documentation were incorporated through the non-force synchronization merge and are disjoint from the Settings slice.
- Core owns Search/Research/Knowledge composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb presentation-only state contracts.
- Historical `ERR-0004` remains closed unless its exact signature recurs.

## Integrator handoff

- READY: UI-GAP-0018 bounded lineage `82fb17da950f8234e28c69bd576e38047ba9b2bb` -> `6aad966258288a7519af6d261dea4695e7ffde76` -> corrective product `9df9d7d46e3c4774aeea5439f91166a2092bd7fb`, backed by exact green Quality `33926653411`.
- Screen 07 returns to `IMPLEMENTED_PENDING_VISUAL_REVIEW`; no screenshot-level `MATCH` is claimed.

## Next UI step

Inspect the current synchronized Settings state machine for the next concrete, evidence-backed interaction/accessibility inconsistency. The first candidate to verify is unavailable-provider fallback detail copy: when `provider=None` and no explicit `model_error` exists, the detail falls back to generic readiness explanatory text even though the adjacent provider state is explicitly unavailable/error. Register a stable `UI-GAP-####` only after confirming the exact current-lineage presentation/test path, then apply a minimal presentation-only fix with focused Qt coverage and canonical exact-head Quality. Do not change provider/backend/storage/network/security semantics.
