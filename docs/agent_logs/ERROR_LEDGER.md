# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`; bounded `ERR-0049` paired-sidecar guard integrated. Exact canonical Quality `34753048193` is currently `IN_PROGRESS`.
- Error worker before the latest harness mutation: `9fff88bb1771cb5e42cb9624bb0db4248ff02bf5`; exact-SHA workflow count = 0.
- Current Error worker after the harness fix/test commits: `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e`; exact-SHA workflow count = 0.
- Spec/Core: `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`; Core Focused `34751831134 = FAILURE`; canonical Quality `34751831135 = FAILURE`.
- Backend: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`; last exact Storage Focused and canonical were both `SUCCESS`; its bounded two-file Storage slice is now integrated into Develop.
- UI: `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; last exact UI Focused, Core Focused and canonical were all `SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0055`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`, `ERR-0054`.
- BLOCKED: none.

## ERR-0056 — Core-Focused harness omits user-correction tests

- Severity: P2 verification/harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Root-cause evidence came from exact `postmerge/spec-core@e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`: the Core-Focused diagnostics reported `No changed Core-owned unit-test files selected; lint evidence only` even though the candidate introduced `tests/unit/test_user_correction_policy.py`.
- Current Develop workflow selection covered claim, knowledge, concept-note, identity-transition and temporal tests, but omitted `test_user_correction*.py` from both the PR path trigger and the focused-test regex.
- Error-owned/harness-owned bounded fix committed on `postmerge/errors`: `4b723fe7202c841e0c768aaf3a62600eaadf02ff` adds `tests/unit/test_user_correction*.py` to the trigger and `test_user_correction.*` to focused selection.
- Regression commit `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e` adds `tests/unit/test_core_focused_candidate_workflow.py`, asserting both selection contracts remain present.
- The current Error-worker SHA has zero workflow runs, so no CI PASS is claimed. Keep `FIXED_PENDING_VERIFY` until the harness slice is independently exercised/integrated and exact evidence proves the intended user-correction test is selected and passes.
- This fix does not weaken any test: it expands mandatory focused coverage.

## ERR-0055 — Spec/Core user-correction-policy Ruff import-block failure

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Exact reproduction: `postmerge/spec-core@e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`.
- Core Focused `34751831134 = FAILURE`; canonical Quality `34751831135 = FAILURE`.
- Focused diagnostics identify exactly one current lint failure: Ruff `I001` in `tests/unit/test_user_correction_policy.py:1:1`.
- Ruff remediation is deterministic and behavior-neutral: remove the extra blank line immediately before `USER_ID`; diagnostic `ruff --fix` reports one fixed and zero remaining errors.
- Canonical full pytest succeeds on the same SHA; Linux Storage, Windows path/release guards and Local Install also succeed. Therefore this is not a product-behavior, Storage, Security or runtime cascade.
- Ownership: Spec/Core. Do not parallel-edit the worker-owned test from `postmerge/errors` while the Fach-Worker owns this exact slice.
- Closure: require a new Spec/Core exact SHA with Core Focused and canonical both `SUCCESS`, then integrated Develop canonical success before `FIXED` if the slice is promoted.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner-side candidate `postmerge/backend@aab04d0c4564a07f9af5c12e6fa496a5e1038ff7` was Storage-Focused and canonical green.
- Integrator extracted only `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py` onto Develop.
- Resulting Develop SHA is `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5` (`fix(storage): integrate paired sidecar replacement guard`).
- Exact canonical Quality `34753048193` is currently `IN_PROGRESS`. Already green on that exact SHA: Specification Validator, Ruff, mypy, Linux Storage regressions, Windows path/release guards, Local Install and pypdf packaging. Full pytest remains the outstanding job.
- No competing canonical run may be started and Develop must not be mutated until the active run completes.
- Keep `FIXED_PENDING_VERIFY` until this exact Develop canonical run succeeds. Any current exact failure must be classified from its own signature before changing status.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Current UI successor `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc` remains owner-side exact green in the consumed evidence.
- Historical bounded product fix is commit `541c367547c698489ad548cc791f72dd27d141b4`, which changes only `src/athena/desktop/pathena_shared_components.py` to derive the send-button geometry from `SHELL.composer_action_size`.
- Current UI and Develop have since diverged and the current UI tree contains many unrelated changes. Therefore the whole current UI branch is not the `ERR-0053` integration slice. Integrator must extract only the bounded verified geometry change and its relevant tests, then require exact Develop canonical success.

## ERR-0054 — historical visual-baseline absence on superseded UI SHA

- Severity: P2 visual-evidence blocker when reproduced.
- Status: `STALE`.
- Last exact reproduction remains on superseded UI SHA `541c367547c698489ad548cc791f72dd27d141b4`.
- No current exact-SHA visual failure on `3dfd310c...` was consumed. Reopen only on a new exact reproduction; do not weaken comparator tolerance or blindly accept generated baselines.

## Current worker requalification

- Spec/Core `e361ef5f...` has current Ruff-only `ERR-0055`; canonical full pytest itself is green. Its focused harness omission is separately tracked as Error-owned `ERR-0056`.
- Backend `aab04d0c...` is owner-side green and its bounded `ERR-0049` slice is integrated into current Develop.
- UI `3dfd310c...` remains owner-side green; only bounded `ERR-0053` awaits integrated verification.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors@9fff88bb1771cb5e42cb9624bb0db4248ff02bf5` had zero workflow runs before the harness mutation; `postmerge/errors@ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e` also has zero workflow runs.
- Current Develop canonical `34753048193` is already active; no Develop/worker candidate is superseded.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
