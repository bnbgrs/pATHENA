# pATHENA UI Handoff

## Current baseline

- Develop checked first and rechecked: `develop/pathena-next@7fa2108d820cfc5b48a9f92d42ffa61697b74818`.
- Develop canonical `ATHENA Quality Gate` run `34522965434` is `success` on that exact SHA.
- UI worker entered the run at `postmerge/ui@2ede7add4d70ee9f11ef2e05103504e9a1838a2a`.
- `main` and `bnbgrs/ATHENA` remained READ-ONLY.
- Required Core, Backend, Errors, Integrator, 11-screen manifest and Visual Gap Ledger sources were consumed before mutation.

## 11-screen evidence now real on both sides

All eleven user reference PNGs in `/pATHENA/Designreferenz – 11 Screenshots` were directly opened again. The worker visual regression workflow was then enabled for `postmerge/ui`, allowing a real exact-SHA Windows PySide6 capture instead of relying on code/QSS inference.

The first candidate `551b93b1d86baa4925c9536f3b3cecfcf72bdf2a` failed during capture with `ModuleNotFoundError: No module named 'scripts'`. The root cause was the font-safe wrapper importing `scripts.render_pathena_ui_snapshot` while itself being executed from the `scripts` directory. The import was corrected to the sibling module form. No backend, storage or security semantics changed.

The successor candidate `191c9cecd6edebe1744d66f0eae6bf9e96e519fe` produced and uploaded all eleven real runtime screenshots on native Windows. The capture manifest reports zero errors and `PASS`. All eleven current images were downloaded and directly opened in this run.

Focused evidence on `191c9cec…`:

- visual-harness Ruff: PASS;
- comparator mypy: PASS;
- comparator contract tests: `5 passed`;
- exactly eleven canonical surfaces captured: PASS;
- baseline proposal generation/comparison step: PASS as proposal;
- artifact upload: PASS;
- overall visual workflow: FAILURE only at final enforcement because a generated proposal is not an approved committed baseline.

## Visual verdict

No `MATCH` is claimed.

- References opened: `11/11`.
- Current runtime renders opened: `11/11`.
- State-aligned/direct pairs: `3/11` (ComfyUI, PALLAS, Help).
- Remaining slots have real current screenshots but different runtime data/context state or isolated capture scope, so pixel parity remains unverified.
- `PAIRS_VERIFIED_3_OF_11`.

The largest repeated visible gap is shared shell/workspace hierarchy. Current surfaces are substantially sparser than the references, with smaller headings, large unused regions, missing reference-style textual top navigation and, on several workspaces, a generic `Evidence & Activity` inspector showing `CHAT / NONE` instead of page-specific context. This is now based on opened pixels, not memory or QSS inference.

A second recurring gap is that real PALLAS, Help and ComfyUI controllers render in isolated/utility surfaces whereas their references place them inside richer pATHENA product framing. Any future integration must preserve the real controller paths and must not replace them with fake data or decorative mock features.

## Branch mutations this run

1. `551b93b1d86baa4925c9536f3b3cecfcf72bdf2a` — `ci(ui): capture visual surfaces on UI worker`
2. `191c9cecd6edebe1744d66f0eae6bf9e96e519fe` — `fix(ui): make visual capture wrapper executable`
3. Documentation-only evidence updates followed after the exact visual run completed.

No force push, history rewrite, merge to main, test relaxation, skip or xfail was used.

## Next visual slice

Prioritize `VISUAL-GAP-0001`: a bounded shared-shell/hierarchy correction, then one contextual-inspector integration if tightly coupled. Do not create synthetic content merely to resemble the references. Re-render the affected actual pages through the now-working native-Windows harness and compare BEFORE -> AFTER. Separately improve the harness to capture state-aligned loaded Workspace/Jobs/System/Research/Knowledge states before any pixel-parity promotion.
