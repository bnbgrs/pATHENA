# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only reproduced or exact-SHA-evidenced failures are active; cascades are deduplicated. `FIXED` requires real verification on the relevant integrated exact SHA. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, assertion/static-check weakening, Security/Storage/Recovery/Windows guard weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop source of truth: `develop/pathena-next@1213c49a391f4ffed6f64d63bcf1527a21adf071` (`fix(storage): accept validated WAL sidecar withdrawal`).
- Current Develop canonical Quality: `34721255765@1213c49a391f4ffed6f64d63bcf1527a21adf071 = IN_PROGRESS`; Errors started no competing run.
- The superseded Develop exact `915668a376390d86fb333291f555eb804dfa4358` canonical `34718446158 = FAILURE`: Specification Validator, Ruff, mypy, Linux Storage, Local Install and Windows release guards passed; Full Pytest failed in `test_two_scheduler_processes_consume_one_retry_budget_slot` because startup identity revalidation rejected a legitimate complete WAL+SHM withdrawal. This is deduplicated into `ERR-0043`, not a new cluster.
- Error worker entered this run at `postmerge/errors@5907ea74435c0529fe93da00febc63b9a40ae23d`; exact branch has zero workflow runs before mutation.
- Current workers: Spec/Core `2d92eec5c63234ab2af85ac8a06617043723a707`; Backend `c185967474ebd603a21fb697caa9f9aa1cd43034`; UI `0e5e03b6c3885d700f4d9f34b45e20b834e5796e`.
- Spec/Core exact `2d92eec5c63234ab2af85ac8a06617043723a707`: Core Focused `34719455494 = SUCCESS`; canonical Quality `34719455510 = SUCCESS`.
- Backend exact `c185967474ebd603a21fb697caa9f9aa1cd43034`: Backend Focused `34721362133 = SUCCESS`; canonical Quality `34721361998 = IN_PROGRESS`.
- UI exact `0e5e03b6c3885d700f4d9f34b45e20b834e5796e`: UI Focused `34721263621 = SUCCESS`; Core Focused `34721263642 = FAILURE`; canonical Quality `34721263617 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0046`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0042`, `ERR-0043`, `ERR-0045`.
- FIXED: `ERR-0001` through `ERR-0013`, `ERR-0015` through `ERR-0024`, `ERR-0027`, `ERR-0030`, `ERR-0031`, `ERR-0032`, `ERR-0033`, `ERR-0034`, `ERR-0035`, `ERR-0036`, `ERR-0037`, `ERR-0040`, `ERR-0041`, `ERR-0044`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none at top level.

## ERR-0046 — Core Focused harness selects UI unit tests without UI runtime

- Severity: P2 CI/harness integration blocker.
- Status: `OPEN`.
- Newest exact reproducer: Core Focused Candidate `34721263642` on `postmerge/ui@0e5e03b6c3885d700f4d9f34b45e20b834e5796e`.
- Exact diagnostics now show stronger reproduction than the prior skipped-only case: Core Focused selects UI/PySide tests while its environment lacks `PySide6`; `test_pathena_layout_refinement_2200.py` fails during collection with `ModuleNotFoundError: No module named 'PySide6'`, while `test_pathena_comfyui_shell.py` and `test_pathena_pallas_full_view.py` are skipped for the same missing UI runtime.
- The same diagnostics also contain a separate Ruff `I001` in `tests/unit/test_pathena_layout_refinement_2200.py`; do not open a second cluster unless current UI canonical reproduces that canonical blocker after completion.
- UI owner lane is green on this exact SHA: UI Focused `34721263621 = SUCCESS`. UI canonical `34721263617` is still running, so no canonical UI PASS/FAIL claim yet.
- Root cause remains Core-Focused ownership selection: UI-only unit tests are passed into a Core lane that installs only Core/dev runtime. Never treat skipped-only execution as success.
- Safe repair: make focused pytest selection mirror explicit Core ownership patterns or another explicit Core allowlist. Preserve `--diff-filter=ACMR`, tracked-worktree fail-closed remediation, and final outcome enforcement.
- Closure requirement: exact candidate proving UI-only changed tests are not spuriously selected, plus a negative control showing a genuine Core failing test still fails, then integrated canonical success.

## ERR-0045 — Backend absent-sidecar test fixture recreates WAL/SHM during read-only preflight

- Severity: P2 Storage test/harness integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner repair remains exact-green in the Backend lineage. Linux Storage is green on current integrated Develop `1213c49a...` canonical while the overall run remains in progress.
- No Storage/Recovery guard was relaxed.
- Final closure requirement: current integrated Develop canonical `34721255765@1213c49a... = SUCCESS` before `FIXED`.

## ERR-0043 — Backend SQLite startup identity continuity

- Severity: P1 Storage/release integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- The historical foreign-sidecar replacement bug remains repaired fail-closed. New exact integrated evidence exposed an adjacent valid-lifecycle false positive on Develop `915668a...`: two concurrent schedulers can legitimately withdraw a previously validated complete WAL+SHM pair while the primary DB identity remains unchanged; old revalidation rejected that transition and crashed storage bootstrap.
- Backend repair `0ca66fceb78bf7744f12029430780c7cb20be72f` was exact-green in Storage Focused `34720329575 = SUCCESS` and canonical `34720329568 = SUCCESS`; Integrator bounded the same two-file delta into current Develop `1213c49a391f4ffed6f64d63bcf1527a21adf071`.
- Accepted transition is narrowly bounded: previously validated complete WAL+SHM may be withdrawn together only with unchanged primary identity; partial sidecar change, foreign replacement, primary replacement, or unstable revalidation remain fail-closed.
- Current Develop canonical `34721255765` is still `IN_PROGRESS`; Linux Storage, Local Install and Windows release-guard jobs are already green, while final integrated closure waits for the whole run.
- Final closure requirement: `34721255765@1213c49a... = SUCCESS` before `FIXED`.

## ERR-0042 — Spec/Core Ruff blocker in revision-change slice

- Severity: P1 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical exact reproducer: one Ruff `I001` in `tests/unit/test_revision_change_explanation.py` while focused behavior tests passed.
- Current Spec/Core exact `2d92eec5c63234ab2af85ac8a06617043723a707` is owner-green: Core Focused `34719455494 = SUCCESS`; canonical Quality `34719455510 = SUCCESS`.
- The current Develop exact `1213c49a...` does not contain `tests/unit/test_revision_change_explanation.py`; compare against Spec/Core shows that file and its slice remain added only on the worker side. Therefore owner repair is verified but not yet integrated.
- Final closure requirement: integrate the verified Spec/Core slice and require canonical success on the resulting Develop exact SHA.

## ERR-0044 — Core Focused harness selects deleted files from PR diff

- Severity: P2 CI/harness integration blocker.
- Status: `FIXED`.
- Repair uses `git diff --diff-filter=ACMR --name-only` and tracked-worktree fail-closed remediation.
- Integrated verification: canonical `34710920451@b8afe9661387c4a1a3d65f539c39ca772f37329c = SUCCESS`.

## ERR-0041 / ERR-0040 / ERR-0035 / ERR-0033

All remain `FIXED` with previously recorded integrated exact-SHA canonical success. Historical closed signatures are not reopened without current exact-SHA reproduction.

## ERR-0039 / ERR-0038

Both remain `STALE`; reopen only with a new current exact-SHA reproduction.

## Persistent release guards

Historical closed/stale clusters remain unchanged. Reopen only with current exact-SHA reproduction. Persistent guards remain binding: Windows `pypdf` packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. Current Develop `1213c49a...` already has Linux Storage, Local Install and Windows release-guard jobs green while canonical remains in progress. No promotion-ready claim until the exact canonical run completes successfully.
