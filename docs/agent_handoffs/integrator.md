# pATHENA Feature Integrator Handoff

## Current branch state

- `main` (strict read-only): `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop before this run: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `b7942416aef738a4063d335675493b82ca414016`; spec-core `6e31cb229651faeb3cd005badbe5f878e00c40b7`; backend `1cfd18c69014390380bb960b86c8e1b81a5067ac`; ui `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d`.

## Integrated this run — UI-GAP-0002

READY evidence:

- Product commit `177bef4dcdb4956f1df75bfcce9ee10c7a4bd1e2` changes only `src/athena/desktop/pathena_window.py` and makes Chat inspector visibility derive from truthful grounded-context state while preserving non-chat visibility.
- Presentation-contract commit `1685221150c724deceb5d150a4d2dcff2bdd867b` changes only `tests/unit/test_pathena_ui_presentation.py` and strengthens the complete interaction contract rather than weakening assertions.
- Exact corrected worker head `ce959e148ddbe8f13952ca56f7d07e7a7ce1addb` passed ATHENA Quality Gate `33745885426` with conclusion `success`.
- Compare review showed current Develop changed from the worker merge base only in Integrator/progress documentation; neither product nor test target file changed on Develop. Therefore the two verified exact file blobs were safe to transplant without carrying later unverified UI-GAP-0003 work.

Integration method:

- Base Develop tree: `63742ba81ade7dfcb82eb1f60c2efcd4b11fbeb5` / tree `dcf653670d27cb54535ef5863249d9ba016d7b3d`.
- Exact product blob from verified product commit: `src/athena/desktop/pathena_window.py@b683903cc6e6a1a99950bba168e6e314df545ca1`.
- Exact test blob from corrected contract commit: `tests/unit/test_pathena_ui_presentation.py@171f209728831feb1ac7bb06172e30aee12973ae`.
- Integration tree: `42f07a246bff09aa099f6b2ed36f6ad96e0ff11a`.
- Integration commit: `93a9344d3902c920da5ff283eb51bbb1f0d815b8`.
- `develop/pathena-next` advanced NON-FORCE to that commit. No conflict, force update, history rewrite, auto-merge or `main` mutation occurred.

## Integration bookkeeping

- `docs/development/ALPHA_BETA_PROGRESS.md` now marks contextual inspector visibility `VERIFIED` and records Backend/UI pending states accurately.
- `docs/ui/VISUAL_GAP_LEDGER.md` now records UI-GAP-0001 and UI-GAP-0002 as `FIXED`, and UI-GAP-0003 as `FIXED_PENDING_VERIFY` / not integrated.
- `docs/ui/11_SCREEN_REFERENCE_MANIFEST.md` still contains exactly eleven slots. Screens 01 and 10 are technically implemented but remain `IMPLEMENTED_PENDING_VISUAL_REVIEW`; `MATCH=0` because original reference pixels are unavailable. Screen 08 remains `IMPLEMENTED_PENDING_VERIFY` due to UI-GAP-0003.

## Inputs not integrated

### Error worker

`postmerge/errors@b7942416aef738a4063d335675493b82ca414016` contains ledger/handoff coordination only; no independently verified product fix to integrate. Its Ruff hypothesis is superseded by Backend's later exact diagnosis, but Error still owns independent post-integration re-verification once Backend lands.

### Core worker

`postmerge/spec-core@6e31cb229651faeb3cd005badbe5f878e00c40b7` is NOT READY. Normal-Hybrid Search facade/application behavior is pinned by acceptance coverage, but product implementation and successful verification are still missing. Do not integrate red acceptance-only work as a completed capability.

### Backend worker

`postmerge/backend@1cfd18c69014390380bb960b86c8e1b81a5067ac` is NOT READY yet. Product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus Ruff-import correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd` are bounded and reviewed, but the fresh exact worker Quality run `33749788522` is still in progress. Previous run `33744816398` proved validator/mypy/Windows path safety/Linux storage/local install green, exposed only Backend Ruff I001 plus an independent UI/PALLAS pytest failure. Require fresh corrected-lineage evidence before integration.

### UI worker — UI-GAP-0003

Later UI candidate `689da6c1dc2221f89825fffde947f792c7b503e7` + regression `034cb8d923d48bea708b48cac0ef0f6343511051` are NOT READY. Current UI head `76cb122dbe7b58b0fa49bbcb36de2bd732922d4d` has Quality run `33751403354` pending. Do not import this PALLAS lifecycle fix until successful evidence exists.

## Product / quality state

- Contextual inspector visibility / UI-GAP-0002: `VERIFIED` and integrated.
- UI-GAP-0003 PALLAS lifecycle: `FIXED_PENDING_VERIFY`, unintegrated.
- ERR-0001 deletion-ledger runtime boundary: `IMPLEMENTED_PENDING_VERIFY`, unintegrated.
- ERR-0002 Backend Ruff harness defect: corrected on Backend worker, fresh verification pending.
- Normal-Hybrid CoreApiFacade/AthenaApplication Search composition: product implementation missing; Core-owned.
- No visual `MATCH` claim for any of the eleven reference slots; `VISUAL_REFERENCE_PENDING` remains binding.

## Handoffs / next priorities

1. `postmerge/backend`: consume exact result of Quality `33749788522`; if corrected deletion-boundary/Ruff lineage is green with no Backend-owned regression, mark exact commits READY.
2. `postmerge/ui`: consume Quality `33751403354`; if green, mark UI-GAP-0003 exact candidate READY; if red, diagnose only the concrete failure.
3. `postmerge/spec-core`: implement the already-pinned normal-Hybrid `CoreApiFacade` attachment/capability/delegation plus exact `AthenaApplication` wiring; then run focused and canonical verification.
4. `postmerge/errors`: refresh the canonical ledger against current Develop, incorporate the confirmed Backend Ruff I001 diagnosis rather than the earlier E721 hypothesis, and independently scan the new integrated UI lineage for regressions.

## Rules retained

- `main` remains strictly read-only.
- No force-push, history rewrite, auto-merge or automatic promotion to main.
- Worker commits are integrated only with compatible baseline, bounded scope, real verification, no weakened tests/guards, clear ownership and no confirmed regression.
- Pending/cancelled workflow runs are never PASS evidence.
- After every completed integration continue immediately with the next READY worker or highest unclaimed cross-cutting gap.
