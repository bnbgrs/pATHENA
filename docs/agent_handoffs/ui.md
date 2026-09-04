# pATHENA UI Handoff

## Current baseline

- Base: `develop/pathena-next@a7c1d8cd1530a3003690292a9bf4c660472d59ce`.
- Worker: `postmerge/ui`.
- History-preserving NON-FORCE synchronization commit: `79afe45ec83194ffd56fd13c8f25a0701e723ba7`, parents `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` + `a7c1d8cd1530a3003690292a9bf4c660472d59ce`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.
- Original eleven reference images remain `VISUAL_REFERENCE_PENDING`; no pixel-level `MATCH` claim is made.

## UI-GAP-0010 — immediate fresh-snapshot accessibility boundary

Status: `FIXED / INTEGRATOR_READY`, P1.

Evidence: before this slice `SettingsRuntimeController.apply_snapshot()` set the immediate accessible description to the generic visible text and relied on the separate `SettingsComprehensionController` sync/timer to add the explicit local-loopback / no-Internet-inference boundary. That created a short-lived accessibility-state mismatch after a fresh snapshot.

Verified implementation:

- product `0722d780b94d8d297bd89e417ae09fab08cb4dcf` makes the runtime snapshot itself set `pathenaNetworkScope=loopback-only`, `pathenaInternetStateInferred=False`, and self-contained accessibility/tooltip copy stating that Local Core status does not indicate Internet access;
- focused test `a2d7030101a01415af99b5a8cba31ad10550e5de` asserts those semantics immediately after `_apply(...)`, before `comprehension.sync()` is called;
- exact documented UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` passed ATHENA Quality Gate `33864721817` with conclusion `success`;
- no backend/network/security semantics, quality rules, assertions, provider commands or fake runtime capabilities changed.

Integrator may independently review/import the bounded UI-GAP-0010 product/test lineage. This is technical state/accessibility evidence only; Screen 07 remains pending original visual review.

## Current next evidence-backed Settings gap

The next bounded Settings target is the pre-first-snapshot state in `SettingsRuntimeController.__init__`: visible labels say `awaiting Core` / `awaiting connection`, but unlike snapshot and connection-failure paths they are not initialized through `_set_state()` and do not yet carry explicit fail-closed runtime freshness/network-scope/Internet-inference metadata. The next product slice should make that initial state explicitly non-ready/unavailable for assistive/state consumers while preserving the existing visible copy and without inventing any Core or Internet capability.

Acceptance for that next slice:

- provider and Local Core initial labels carry explicit non-success UI/freshness state before any snapshot;
- Local Core initial state exposes `pathenaNetworkScope=unavailable` and `pathenaInternetStateInferred=False` with self-contained accessibility text that Internet access is not inferred;
- no ready/connected claim is introduced before a real snapshot;
- focused Qt coverage checks the state immediately after `install_settings_runtime(...)`, before any snapshot signal;
- no backend, Storage, Security, provider or transport semantics change.

## Collision / ownership guidance

- UI owns only Settings presentation/accessibility state in this lineage.
- Core owns Search/research composition and must not infer Internet state from UI metadata.
- Backend owns durable runtime/storage/network mechanics and must not absorb this presentation-only state contract.
- Error worker should treat any new canonical failure by exact signature; historical `ERR-0004` remains closed unless it recurs.

## Integrator handoff

- READY: UI-GAP-0010 product `0722d780b94d8d297bd89e417ae09fab08cb4dcf` + focused test `a2d7030101a01415af99b5a8cba31ad10550e5de`, backed by exact green UI head `dc82cdded9e9d3c87be964a5f582965a9f4d3c9a` / Quality `33864721817`.
- The later synchronization merge `79afe45ec83194ffd56fd13c8f25a0701e723ba7` carried current Develop research/integrator changes while preserving the verified UI product/test blobs; it is not new UI behavior.

## Next UI step

Implement the bounded pre-first-snapshot fail-closed Settings state described above, add focused Qt coverage, then run canonical Quality on the exact final worker candidate. If the canonical run is green, register/close the new stable `UI-GAP-####`, update Screen 07 without claiming `MATCH`, and hand the exact verified lineage to Integrator.
