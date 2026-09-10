# pATHENA UI Handoff

## Current baseline — 2026-09-11

- Develop checked first: `develop/pathena-next@29540b7a1f2cb09e3a1be9aee2a29e357c8a8724`.
- Develop canonical ATHENA Quality Gate `34534330414` on that exact SHA: `SUCCESS`.
- UI worker product head at run start: `postmerge/ui@6b1777ef181dc2f1b15f5a7f70c3cab84ff0b9dc`.
- `main` and `bnbgrs/ATHENA` remained READ-ONLY.
- Current Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger were consumed before any worker-side documentation mutation.
- No worker workflow was queued or in progress at run start.

## 11-screen evidence

All 11 user reference images were directly opened again. The exact native-Windows artifact from visual run `34533820471` for `6b1777ef…` was downloaded; all 11 real current PySide6 renderings were directly opened. Artifact manifest: candidate SHA `6b1777ef…`, platform `win32`, 11 captures, zero capture errors, `status=PASS`.

No screenshot `MATCH` is claimed. Same-state/directly comparable pairs remain 3/11 (ComfyUI, PALLAS, Help). The other eight slots have real current screenshots but materially different data/context state or capture scope.

`PAIRS_VERIFIED_3_OF_11` · `MATCH_0_OF_11`.

## Exact visual finding after typography candidate

The typography hierarchy change on `6b1777ef…` is visible in the current renders. Direct reference/current review now isolates the next repeated P0 shell gap more precisely: normal workspace captures have the wordmark, slim icon rail, current large page-title tokens and bounded inspector, but **no textual top-level navigation**. The reference family repeatedly shows textual primary navigation across the top.

Current `PathenaMainWindow` already owns one real navigation model. Current `pathena_theme.py` already styles `QPushButton#topNavButton` including checked/focus/hover states, but `_install_reference_shell()` creates no such controls. The next safe product slice is therefore presentation-only: expose the existing real primary routes as top-bar buttons and synchronize their checked state with `self.navigation.currentRow()`. Proposed labels follow the user references and product semantics: `Chat`, `Knowledge`, `Research`, `Jobs`, `Sources`. System and Settings remain utility destinations.

This must reuse the existing routing model and must not create a parallel navigation state, fake page, backend stub or fabricated status.

## Focused evidence

The current worker design-token contract was reproduced in this run against the worker values and completed `5 passed`. Exact native-Windows rendering for the candidate remains backed by run `34533820471`. The visual run itself predates Develop's new selection of `tests/unit/test_pathena_design_tokens.py`, so this local focused result is not misrepresented as canonical exact-SHA CI evidence.

Develop commit `29540b7…` adds the focused hierarchy-token test to future visual workflow candidates and is exact-SHA canonical green. That Develop workflow mutation remains READ-ONLY and was not merged/cherry-picked by UI.

## Readiness / collision state

Current worker vs Develop is diverged (`ahead 655`, `behind 20` in this run). Therefore no `INTEGRATOR_READY` claim is made for the current broad lineage. No Backend/Storage/Security semantics were changed. Historical closed UI/error slices remain closed absent a current exact-SHA regression.

## Next visual slice

Implement the bounded functional textual top navigation in the shared shell, add focused Qt interaction/accessibility coverage, then produce a new exact-SHA 11-surface native-Windows capture. Open all 11 new renders and record `BEFORE 6b1777ef… -> AFTER <candidate>` against the same 11 references. Keep contextual inspector work separate unless it can reuse a real existing page-specific data path without semantic changes.
