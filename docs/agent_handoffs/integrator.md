# pATHENA Feature Integrator Handoff

## Current branch state

- `main` (strict read-only): `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `280066cc5450f172693e2ee913bd269b6755f7bb`.
- Develop cross-cutting diagnostic commit: `5596949685b41139363a4298b741c5967df3cca4`.
- No Worker product slice was integrated in this run.

## Worker heads reviewed

- `postmerge/errors`: `8ba00d4327468badb5be1b0f1a08aabd63c724b1` — synchronized ledger/handoff only; no product fix ready; `ERR-0001` remains Backend-owned.
- `postmerge/spec-core`: `d6fd113b7592d7f8f6e076f383fbefb5ab1d725e` — contains the Search facade/application contract plus red acceptance test `4b6523d30f61a57c29bace801393648b579f0427`; no product implementation or verification yet, so not READY.
- `postmerge/backend`: `5d431c2d6f66b05a29591f93f777f95b11c7fce8` — synchronized with Develop and retains the focused ERR-0001 regression harness, but no deletion-ledger product guard fix and no successful exact-head verification; not READY.
- `postmerge/ui`: `110c3985fb521fdbd3e472d42a0a3c58ee0a325d` — synchronized with Develop; UI-GAP-0002 implementation remains unintegrated. The exact product/test SHA `ff14f8fbe9c99e043521605c1ae790f20e807ae2` failed canonical Quality run `33729667950`.

## READY decision

No Worker input satisfies the READY rule in this run.

- Core: red acceptance coverage without the product slice.
- Backend: reproducing harness without product fix and without successful canonical verification.
- UI: exact-head canonical failure, now diagnosed but not yet corrected/reverified.
- Error: coordination state only and no product fix.

No force update, history rewrite, auto-merge or promotion to `main` was performed.

## Cross-cutting slice this run — canonical UI failure diagnosis

The previously opaque UI-GAP-0002 Quality failure was resolved to an exact test-contract collision by downloading and reading workflow artifact `canonical-quality-diagnostics-ff14f8fbe9c99e043521605c1ae790f20e807ae2` from run `33729667950`.

Canonical pytest result:

- `1 failed, 4458 passed, 3 skipped, 2 warnings`.
- Sole failure: `tests/unit/test_pathena_ui_presentation.py::test_pathena_secondary_context_is_grounded_only_and_user_controlled`.
- Failing assertion: the legacy presentation test requires `inspector.isHidden() is False` immediately after constructing an ungrounded Chat window.
- The UI-GAP-0002 focused contract in `tests/unit/test_pathena_window.py` intentionally requires the opposite: initial/new ungrounded Chat hides the inspector; grounded Chat reveals it; non-chat surfaces keep it visible; returning to ungrounded Chat hides it again.
- Product commit `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2` implements exactly that contextual rule by removing unconditional `inspector.show()` calls and centralizing visibility in `_sync_inspector_visibility()`.

Independent review therefore classifies the canonical failure as a stale/conflicting legacy test contract, not as evidence that the new contextual-visibility implementation itself violates its stated UI-GAP contract. This does NOT make the worker READY yet: the UI worker must reconcile the legacy presentation test without weakening contextual visibility, preserve grounded/non-chat assertions, and obtain focused plus canonical PASS on the corrected exact head.

`docs/development/ALPHA_BETA_PROGRESS.md` was updated on Develop at `5596949685b41139363a4298b741c5967df3cca4` with this exact diagnosis.

## Current product status

- Retrieval-method provenance: `VERIFIED`.
- Search Response final rank: `VERIFIED`.
- Archive Search source-anchor provenance: `VERIFIED`.
- Search Response protection-state provenance: `VERIFIED`.
- Canonical Search API DTO + normal-Hybrid adapter: `VERIFIED` and integrated.
- Resource policy runtime mutation boundary: `VERIFIED`.
- Grounded Chat inspector hierarchy / Evidence & Activity copy: `VERIFIED`.
- Contextual inspector visibility: `PARTIAL`; implementation exists on UI worker, canonical failure is now diagnosed as a legacy test-contract collision, but corrected exact-head verification is still required.
- Canonical error state: `PARTIAL`; `ERR-0001` remains open and Backend-owned.
- 11-screen UI: exactly 11 manifest slots retained; no visual MATCH claim without opened original references.

## Next prioritized handoffs

1. `postmerge/ui`: reconcile `test_pathena_secondary_context_is_grounded_only_and_user_controlled` with the evidence-backed contextual inspector contract. Do not merely delete/weaken the assertion: require initial ungrounded Chat hidden, grounded Chat visible, non-chat visible, and return-to-ungrounded Chat hidden. Rerun focused Qt tests and canonical Quality on one exact corrected head.
2. `postmerge/backend`: implement ERR-0001 exact runtime guards, prove fail-before-SQL with the focused harness, run deletion/recovery regressions and canonical Quality on the exact product/test lineage.
3. `postmerge/spec-core`: implement the already pinned `CoreApiFacade` + `AthenaApplication` normal-Hybrid Search attachment/delegation/capability-registration slice with focused API/application tests; Integrator must not duplicate this claimed scope.
4. `postmerge/errors`: independently verify eventual integrated ERR-0001 fix on exact Develop and continue unrelated regression scans.

## Integration rules retained

- `main` remains strictly read-only.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Only baseline-compatible, independently reviewed and adequately tested worker slices are integrated.
- A green focused/exact-product run is evidence, not an exemption from scope, ownership, provenance, security or recovery review.
- A confirmed failing exact-product canonical run blocks integration until diagnosed and corrected.
