# pATHENA Feature Integrator Handoff

## Current branch state

- `main` remains strict read-only at `0d4d621f8a38ddf8eccfa09622bf193687619943`.
- Develop baseline for this run: `8b7d83ba170a121414a26055f0c5df9acf97914e`.
- Integration target: `develop/pathena-next` only.
- Worker heads reviewed: errors `76032cc170df2758d2ee7737bf919d619f67407a`; spec-core `48ed95dd1a667e58777599998e07751cb9a0e27c`; backend `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947`; UI `f02642bda40feebb5c6c91803386ceb0f05e0e1a`.
- `main` and `bnbgrs/ATHENA` remain untouched/read-only; no force update, history rewrite, auto-merge or main promotion was used.

## Exact evidence consumed

- Exact Develop head `8b7d83ba170a121414a26055f0c5df9acf97914e` had no associated canonical Quality run and no queued/in-progress exact-head gate when mutation eligibility was checked.
- Backend exact head `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` has canonical Quality `34299682340` still in progress. Windows path safety, Linux storage regressions and Local install smoke are green; specification validator and mypy are green; Ruff is already red and pytest is still running. Backend is therefore not Integrator-ready.
- Spec/Core exact-green evidence only verifies the adaptive DirectChat product/test tree already on Develop; no new Core product slice requires pickup.
- UI current head is a synchronization descendant after the already integrated black/orange foundation; no new bounded UI product slice is ready.

## Progress this run — adaptive DirectChat zero-margin boundary

No compatible Worker product slice was READY. A bounded Core-owned release regression was added to the existing adaptive DirectChat context-budget test family. With a 2048-token loaded context, 2047 estimated input tokens, requested output reserve 2048 and an explicit safety margin of zero, exactly one output token must remain available. This complements the existing 256-token safety-margin one-token boundary and the fail-closed exhaustion case.

Production code is unchanged. The slice adds no Skip/XFail, weakens no assertion, and changes no Provider, Backend, Storage, Security, Recovery, scheduler/worker, packaging, Windows process or migration semantics.

## Current quality/error state

- Develop after this commit requires exact-current canonical/focused verification before any Beta or promotion-ready claim.
- Backend remains conservative hold while exact head `82d3d7d219a6fb4f122a10ffaa2a0c0e3e44f947` has an in-progress canonical run with Ruff failure already observed.
- Historical Windows/runtime signatures remain release guards and are not reopened without exact-current reproduction.

## Tracker / visual state

- The 11-screen manifest and Visual-Gap ledger remain authoritative; no UI mutation or new pixel-match claim was made this run.
- `docs/development/ALPHA_BETA_PROGRESS.md` remains evidence source; no percentage was invented and no unverified capability was promoted.

## Next integration order

1. Re-check exact-current Develop CI before any further Develop mutation.
2. Consume final exact Backend Quality `34299682340`; do not integrate its Storage/WAL/schema lineage while Ruff or independent pytest failures remain red.
3. Prefer the first exact-green dependency-unblocking Backend prerequisite once all bounded storage/migration/runtime evidence is clean.
4. Otherwise consume exactly one new bounded Core/UI successor with non-superseded exact evidence.
5. Preserve the Windows/Packaging/Runtime regression matrix before any Beta/release claim.

## Persistent release guards

Retain explicit Beta/release acceptance for pypdf packaging metadata; fail-closed frozen argv routing and Desktop/Worker two-EXE split; exactly one Desktop with bounded/non-growing workers; adaptive 2048-context DirectChat budgeting including configured-upper-bound, one-token-with-margin and one-token-with-zero-margin behavior; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; and storage-bootstrap/migration startup signatures including duplicate-column failures.

## Rules retained

No direct work on `main`; no main promotion; no force-push/history rewrite/auto-merge; no new Skip/XFail or weaker assertions; no Security/Storage/Windows/Recovery/validator relaxation; no fake success or fabricated provenance.
