# pATHENA UI Handoff

## Current baseline — 2026-09-11

- Current Develop checked first: `develop/pathena-next@95b636c982a800d75f7d219162a04f6c87976e9f`.
- Exact canonical ATHENA Quality Gate `34560421777 = SUCCESS`.
- UI worker run-start HEAD: `postmerge/ui@103feb7ca6b3513077ce47f83569c13cc626b600`.
- `main` and `bnbgrs/ATHENA` remained READ-ONLY and untouched.
- Current Spec/Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before further work.

## Exact verification this run

The preceding UI lifecycle patch (`fix(ui): make startup event filter teardown-safe`) is now present on current Develop as exact commit `95b636c…`, and canonical Quality is green. This closes the prior exact-current pytest failure without any Backend, Storage or Security semantics change.

Exact worker visual workflow metadata still exists for `103feb7c…`, including uploaded artifact `pathena-visual-103feb7ca6b3513077ce47f83569c13cc626b600`. The artifact bytes could not be materialized through the available GitHub/runtime path this run, so no current PNG is claimed as opened and no old pair is carried forward.

All 11 user reference PNGs were opened directly again. Accounting for this run is `PAIRS_VERIFIED_0_OF_11 · MATCH_0_OF_11` because current pixels are unavailable, not because the reference set is missing.

## Startup-path verification

Source inspection confirms the real desktop `main()` still calls `install_navigation_context_accessibility(window)`. That controller inserts visible `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources` buttons into the real `topBar`, keeps their checked/accessibility state synchronized, and routes clicks through the existing `navigation.setCurrentRow(...)`. The direct `PathenaMainWindow` unit test that expects no `topNavButton` exercises the un-decorated base presentation object, not the complete application startup path. No duplicate router was introduced.

## Current visual priority

Do not patch another visual gap until fresh exact current pixels are accessible. Historical exact screenshots identify contextual inspector composition as the leading repeated product gap, but the hard visual-first rule requires re-opening the current artifact before promoting it to the next mutation.

When fresh pixels are available, compare all 11 slots first. If the inspector gap reproduces, bind at most one or two real contexts (for example Settings system status and Jobs execution state) using existing real controller/workspace data or an explicit unavailable/not-implemented state. Never fabricate healthy system state, evidence, jobs or resource metrics.

## Readiness

- Develop canonical Quality: `SUCCESS` at `95b636c…`.
- Worker exact visual artifact: exists at `103feb7c…`, pixels unavailable to this run.
- Visual readiness: NOT READY.
- `PAIRS_VERIFIED_0_OF_11`.
- Integrator-ready claim: not made; worker and Develop remain materially diverged and no fresh current visual evidence was opened.

## Next run

1. Reacquire/open the exact worker eleven-surface runtime artifact.
2. Re-open all 11 references and perform slot-by-slot same-state comparison.
3. Select only the largest reproduced recurring gap.
4. Implement at most 1–2 tightly coupled UI changes with focused Qt coverage.
5. Produce/open a fresh exact-SHA Windows capture and document BEFORE -> AFTER.
