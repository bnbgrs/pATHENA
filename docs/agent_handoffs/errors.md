# pATHENA Error Handoff

## Baseline

- Develop: `1213c49a391f4ffed6f64d63bcf1527a21adf071` (`fix(storage): accept validated WAL sidecar withdrawal`).
- Develop canonical Quality `34721255765@1213c49a391f4ffed6f64d63bcf1527a21adf071 = IN_PROGRESS`; no competing run started by Errors.
- Superseded Develop `915668a376390d86fb333291f555eb804dfa4358` canonical `34718446158 = FAILURE`; all static checks, Linux Storage, Local Install and Windows release guards passed, while Full Pytest exposed the legitimate complete WAL+SHM withdrawal false positive now handled by current Develop.
- Errors worker entered this run at `5907ea74435c0529fe93da00febc63b9a40ae23d`; exact branch had zero workflow runs before mutation.
- Current workers: Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`; Backend `c185967474ebd603a21fb697caa9f9aa1cd43034`; UI `0e5e03b6c3885d700f4d9f34b45e20b834e5796e`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current error state

- OPEN: `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`, `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0044`, `ERR-0041`, `ERR-0040`, `ERR-0035`, `ERR-0033` and prior closed clusters.
- STALE: `ERR-0038`, `ERR-0039` and prior stale clusters.

## ITERATION-1 — ERR-0043 root-cause boundary refined on integrated exact SHA

`ERR-0043 = FIXED_PENDING_VERIFY / P1`.

The superseded integrated Develop exact `915668a376390d86fb333291f555eb804dfa4358` did not fail on the historical foreign-sidecar replacement reproducer. Its canonical `34718446158` failed only in Full Pytest, specifically `test_two_scheduler_processes_consume_one_retry_budget_slot`: concurrent startup rejected a legitimate lifecycle where a previously validated complete WAL+SHM pair disappeared together while the primary DB identity stayed unchanged. The exception propagated as `DatabaseStartupIdentityChangedError` through storage bootstrap and caused both scheduler processes to exit.

Backend isolated and fixed that adjacent false positive on exact `0ca66fceb78bf7744f12029430780c7cb20be72f`:

- Storage Focused `34720329575 = SUCCESS`.
- canonical Quality `34720329568 = SUCCESS`.

Integrator copied the bounded two-file delta into current Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071`. The accepted case is only complete WAL+SHM withdrawal with unchanged primary identity; partial changes, foreign replacement, primary replacement and unstable revalidation remain fail-closed.

Current Develop canonical `34721255765` is still running. Linux Storage, Local Install and Windows release-guard jobs are already green. Do not mark `FIXED` until the exact whole run is SUCCESS.

## ITERATION-2 — ERR-0045 advances on current integration

`ERR-0045 = FIXED_PENDING_VERIFY / P2`.

The absent-sidecar fixture repair remains carried by the same storage lineage, and current Develop `1213c49a...` has its Linux Storage job green. No Storage/Recovery guard was loosened. The only remaining closure condition is whole canonical SUCCESS on `34721255765@1213c49a...`.

## ITERATION-3 — ERR-0042 owner current-exact green, integration still absent

`ERR-0042 = FIXED_PENDING_VERIFY / P1`.

Current Spec/Core exact is now `2d92eec5c63234ab2af85ac8a06617043723a707` and is fully owner-green:

- Core Focused `34719455494 = SUCCESS`.
- canonical Quality `34719455510 = SUCCESS`.

The historical revision-change Ruff `I001` is not reproduced on this current owner SHA. However, current Develop `1213c49a...` does not contain `tests/unit/test_revision_change_explanation.py`; compare shows that revision-change slice is still added only on Spec/Core. Therefore owner repair is verified but not integrated. Keep `FIXED_PENDING_VERIFY`, not `FIXED` and not `OPEN`.

## ITERATION-4 — ERR-0046 re-reproduced more strongly on newest UI exact

`ERR-0046 = OPEN / P2`.

Newest exact reproducer is `postmerge/ui@0e5e03b6c3885d700f4d9f34b45e20b834e5796e`:

- UI Focused `34721263621 = SUCCESS`.
- Core Focused `34721263642 = FAILURE`.
- UI canonical `34721263617 = IN_PROGRESS`.

Downloaded exact Core-Focused diagnostics strengthen the same harness root cause:

- `test_pathena_layout_refinement_2200.py` is selected by Core Focused and fails during collection with `ModuleNotFoundError: No module named 'PySide6'`.
- `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` are selected and skipped because the same UI runtime is absent.
- A separate Ruff `I001` is present in `test_pathena_layout_refinement_2200.py`; do not open another cluster unless the current UI canonical reproduces it as a canonical blocker after completion.

This is not a reason to weaken the final Core lane outcome gate. The safe repair remains ownership-correct selection: Core Focused must select only Core-owned test patterns, while preserving deleted-file filtering, tracked-worktree fail-closed Ruff remediation and genuine Core-failure propagation.

## ITERATION-5 — current worker/canonical discipline

Backend has advanced to exact `c185967474ebd603a21fb697caa9f9aa1cd43034`: Backend Focused `34721362133 = SUCCESS`, canonical `34721361998 = IN_PROGRESS`. No parallel Backend mutation or competing canonical was started.

UI canonical `34721263617` and Develop canonical `34721255765` are also still running. Their wait time was used read-only to refine `ERR-0043`, verify current Spec/Core, and strengthen `ERR-0046` evidence.

## Integrator handoff

- `ERR-0043 = FIXED_PENDING_VERIFY / P1`: current Develop `1213c49a...` contains exact-green bounded Backend repair for complete validated WAL+SHM withdrawal; close only after `34721255765 = SUCCESS`.
- `ERR-0045 = FIXED_PENDING_VERIFY / P2`: storage fixture lineage remains green and integrated; close on the same Develop canonical SUCCESS.
- `ERR-0042 = FIXED_PENDING_VERIFY / P1`: current Spec/Core `2d92eec...` Core Focused + canonical SUCCESS, but revision-change slice is not yet in current Develop; integrate then require resulting Develop canonical SUCCESS.
- `ERR-0046 = OPEN / P2`: current UI exact `0e5e03b...` again proves Core-Focused over-selection, now with a direct missing-PySide6 collection error. Repair test ownership selection, never skip-to-green.

## CI discipline

- `postmerge/errors@5907ea74435c0529fe93da00febc63b9a40ae23d` had zero workflow runs before ledger mutation.
- Ledger commit `1b74648c71d87d7c34b4bf2d2d6ef0aafe6ca815` also had zero workflow runs before this handoff mutation.
- No canonical run was started or duplicated by Errors.
- No product code or foreign worker branch was mutated.

## NEXT_ROOT_CAUSE

1. Consume `34721255765@develop/1213c49a...`; on SUCCESS close `ERR-0043` and `ERR-0045`, on FAILURE classify only the exact new signature.
2. Consume UI canonical `34721263617`; if it fails on `test_pathena_layout_refinement_2200.py` Ruff `I001`, open a separate current UI-owned cluster; otherwise keep that finding subordinate to current exact outcome.
3. Follow a Core-Focused harness successor for `ERR-0046`; require UI-only non-selection plus a genuine Core-failure negative control.
4. Follow integration of current-green Spec/Core `2d92eec...`; close `ERR-0042` only after integrated Develop canonical success.
5. Consume Backend canonical `34721361998` before classifying any current Backend successor.
