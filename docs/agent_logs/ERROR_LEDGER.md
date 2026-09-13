# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`; bounded `ERR-0049` paired-sidecar guard integrated. Exact canonical Quality `34753048193` is currently `IN_PROGRESS`.
- Error worker before this update: `c64e6be7d2c4b1bde22426c610925564684652c6`; exact-SHA workflow count = 0.
- Spec/Core: `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`; Core Focused `34751831134 = FAILURE`; canonical Quality `34751831135 = FAILURE`.
- Backend: `aab04d0c4564a07f9af5c12e6fa496a5e1038ff7`; last exact Storage Focused and canonical were both `SUCCESS`; its bounded two-file Storage slice is now integrated into Develop.
- UI: `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc`; last exact UI Focused, Core Focused and canonical were all `SUCCESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0055`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0049`, `ERR-0053`.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`, `ERR-0054`.
- BLOCKED: none.

## ERR-0055 — Spec/Core user-correction-policy Ruff import-block failure

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Exact reproduction: `postmerge/spec-core@e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38`.
- Core Focused `34751831134 = FAILURE`; canonical Quality `34751831135 = FAILURE`.
- Focused diagnostics identify exactly one current failure: Ruff `I001` in `tests/unit/test_user_correction_policy.py:1:1`.
- Ruff remediation is deterministic and behavior-neutral: remove the extra blank line immediately before `USER_ID`. `ruff --fix` reports one fix and zero remaining errors.
- Canonical full pytest succeeds on the same SHA; Linux Storage, Windows path/release guards and Local Install also succeed. Therefore this is not a product-behavior, Storage, Security or runtime cascade.
- Ownership: Spec/Core. Do not parallel-edit the worker-owned test from `postmerge/errors` while the Fach-Worker owns this exact slice.
- Closure: require a new Spec/Core exact SHA with Core Focused and canonical both `SUCCESS`, then integrated Develop canonical success before `FIXED` if the slice is promoted.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Owner-side candidate `postmerge/backend@aab04d0c4564a07f9af5c12e6fa496a5e1038ff7` was Storage-Focused and canonical green.
- Integrator extracted only `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py` onto Develop.
- Resulting Develop SHA is `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5` (`fix(storage): integrate paired sidecar replacement guard`).
- Exact canonical Quality `34753048193` is currently `IN_PROGRESS`; no competing canonical run may be started and Develop must not be mutated until it completes.
- Keep `FIXED_PENDING_VERIFY` until this exact Develop canonical run succeeds. Any current exact failure must be classified from its own signature before changing status.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Current UI successor `3dfd310c06f3a6b3e34db0d524bf752269fe8bcc` remains owner-side exact green in the consumed evidence.
- No current deterministic UI regression is reproduced. Keep `FIXED_PENDING_VERIFY` until the bounded UI fix receives integrated Develop canonical verification.

## ERR-0054 — historical visual-baseline absence on superseded UI SHA

- Severity: P2 visual-evidence blocker when reproduced.
- Status: `STALE`.
- Last exact reproduction remains on superseded UI SHA `541c367547c698489ad548cc791f72dd27d141b4`.
- No current exact-SHA visual failure on `3dfd310c...` was consumed. Reopen only on a new exact reproduction; do not weaken comparator tolerance or blindly accept generated baselines.

## Current worker requalification

- Spec/Core `e361ef5f...` has one current Ruff-only blocker, `ERR-0055`; canonical full pytest itself is green.
- Backend `aab04d0c...` is owner-side green and its bounded `ERR-0049` slice is integrated into current Develop.
- UI `3dfd310c...` remains owner-side green; only `ERR-0053` awaits integrated verification.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors@c64e6be7d2c4b1bde22426c610925564684652c6` had zero workflow runs before mutation.
- Current Develop canonical `34753048193` is already active; no Develop/worker candidate is superseded.
- No foreign worker product branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
