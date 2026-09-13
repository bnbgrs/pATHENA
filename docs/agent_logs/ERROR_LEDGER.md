# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `7b4779b7be8c19b9ca0acaa57f826d0da8478592` (`fix(ci): cover user-correction focused tests`). Canonical Quality `34758273159 = FAILURE`.
- Exact Develop diagnostics: Ruff-only failure `I001` at `tests/unit/test_core_focused_candidate_workflow.py:1:1`; isolated desktop-controller pytest `6 passed`; remaining canonical suite `5063 passed, 17 skipped`; Linux Storage, Local Install and Windows release guards all `SUCCESS`.
- Error worker before current fixes: `a1f6b796c6d9cb7b5aab3e2b36e663d872569f6d`.
- Spec/Core: `77048de78be4dd7ca2555ed1b09e00d088f9c624`; canonical Quality `34756815221 = SUCCESS`.
- Backend: `e76bfbe266107a781e3602246d143ee8e9e849b3`; canonical Quality `34757222993 = SUCCESS`.
- UI: `d351dba17b69c3f5b55a1447f2ac088b929a1b48`; UI Focused `34757680126 = SUCCESS`, Core Focused `34757680108 = SUCCESS`, canonical Quality `34757680127 = SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0057`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`, `ERR-0055`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`, `ERR-0054`.
- BLOCKED: none.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED`.
- Integrated Develop SHA `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5` passed canonical Quality `34753048193 = SUCCESS`.
- Do not reopen from historical sidecar signatures; require a new current exact-SHA reproduction.

## ERR-0055 — Spec/Core user-correction-policy Ruff import-block failure

- Severity: P2 integration blocker.
- Status: `FIXED`.
- Current Spec/Core successor `77048de78be4dd7ca2555ed1b09e00d088f9c624` is canonical-green (`34756815221 = SUCCESS`).
- The bounded user-correction product slice was integrated into Develop parent `9e607472ba65ce86b795cf8f6926a0809700a2cd`, whose canonical Quality `34755721026 = SUCCESS`.
- The historical Ruff-only signature is closed. Current Develop Ruff failure on `7b4779b7...` is a distinct CI-harness integration regression tracked as `ERR-0057`.

## ERR-0056 — Core-Focused harness omits user-correction tests

- Severity: P2 verification/harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Develop `7b4779b7be8c19b9ca0acaa57f826d0da8478592` contains both missing contracts: `tests/unit/test_user_correction*.py` in the PR path trigger and `test_user_correction.*` in focused selection.
- Canonical pytest is green on this exact Develop SHA, but canonical Quality is red because of the independent Ruff/guard-regression cluster `ERR-0057`.
- Closure requires exact integrated canonical success after the `ERR-0057` repair; no competing run was started.

## ERR-0057 — Core-Focused regression-test replacement removed existing guard coverage

- Severity: P2 verification/harness blocker.
- Status: `OPEN`.
- Exact Develop SHA `7b4779b7be8c19b9ca0acaa57f826d0da8478592` has canonical Quality `34758273159 = FAILURE` with exact Ruff diagnostic `I001 Import block is un-sorted or un-formatted` at `tests/unit/test_core_focused_candidate_workflow.py:1:1`. Ruff proposes `Organize imports`.
- Exact canonical pytest is otherwise green: isolated desktop controller `6 passed`; remaining suite `5063 passed, 17 skipped, 2 warnings`.
- The same integration replaced the pre-existing four workflow-contract tests with one user-correction-only test (`38 deletions`, `7 additions` in this file). Removed guard coverage includes deleted-path filtering, narrow Core-owned pytest selection, knowledge API lint selection, and remediation worktree restoration.
- Error-owned repair on `postmerge/errors`: `ebcb67f065b7cd890c55897c3e9b9d74f0da10f8` restores all four previous contracts, adds user-correction trigger/selection coverage, and removes the Ruff-offending future-import layout by returning to the previously canonical-green import shape.
- The repaired contract assertions were additionally smoke-evaluated against the current workflow shape and all pass. Integrated exact canonical verification is still required before `FIXED`.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Current UI SHA `d351dba17b69c3f5b55a1447f2ac088b929a1b48` is exact-green: UI Focused `34757680126 = SUCCESS`, Core Focused `34757680108 = SUCCESS`, canonical Quality `34757680127 = SUCCESS`.
- Current Develop still lacks `ShellGeometry.composer_action_size`; current UI adds `composer_action_size: int = 48` and carries the related shared-component/test lineage.
- UI is broadly divergent from current Develop, so broad branch promotion is unsafe. Closure still requires a bounded current-baseline token + component + focused-test slice followed by exact Develop canonical success.

## ERR-0054 — historical visual-baseline absence on superseded UI SHA

- Severity: P2 visual-evidence blocker when reproduced.
- Status: `STALE`.
- Reopen only on a current exact visual reproduction; do not weaken comparator tolerance or blindly accept generated baselines.

## Current worker requalification

- Spec/Core exact current candidate is canonical-green; no current Core product failure is reproduced.
- Backend exact current candidate is canonical-green; no current Backend/Storage failure is reproduced.
- UI exact current candidate is focused- and canonical-green; no new UI error is opened.
- Develop current exact candidate has one current Ruff failure in the CI-harness integration delta; canonical pytest and all other release lanes are green.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- No Backend/UI/Spec-Core product branch was mutated by the Error worker.
- Error-owned mutations remain only on `postmerge/errors`.
- `main` and `bnbgrs/ATHENA` remain read-only.
- No force push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
