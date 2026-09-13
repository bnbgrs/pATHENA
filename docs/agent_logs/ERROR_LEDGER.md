# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `9e607472ba65ce86b795cf8f6926a0809700a2cd` (`feat(core): integrate source-age and user correction guards`). Canonical Quality `34755721026` is `IN_PROGRESS`; no competing run started.
- Error worker before this documentation update: `0786a8dca2f5d27c443d91a9d281a11b7e3b767c`.
- Spec/Core: `367bf6ee879450373cde5f116ca78fbe28a2dbac`; Core Focused `34754120108 = SUCCESS`; canonical Quality `34754120154 = SUCCESS`; Storage Focused `34754120185 = SUCCESS`.
- Backend: `21f6276bbd62bc5a918da040ddbd2d9865a67092`; canonical Quality `34754571928 = SUCCESS`.
- UI: `da52341488a365f999bbbb949acbe7f186c894ae`; Core Focused `34755623489 = SUCCESS`; canonical Quality `34755623363 = IN_PROGRESS`.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0053`, `ERR-0055`, `ERR-0056`.
- FIXED: prior closures plus `ERR-0049`, `ERR-0047`, `ERR-0050`, `ERR-0051`, `ERR-0052`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`, `ERR-0054`.
- BLOCKED: none.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `FIXED`.
- Owner-side bounded Storage candidate was exact-green before integration.
- Integrator extracted only `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py` onto Develop SHA `09d43c348420dc5ad0eb2be80ebf8681ae8f25c5`.
- Integrated exact canonical Quality `34753048193 = SUCCESS`.
- This is sufficient integrated evidence for closure. Do not reopen from historical sidecar signatures; require a new current exact-SHA reproduction.

## ERR-0055 — Spec/Core user-correction-policy Ruff import-block failure

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical failing worker SHA `e361ef5f365d7afd1d1b5d4b9fa242aeebfdee38` is superseded.
- Current Spec/Core SHA `367bf6ee879450373cde5f116ca78fbe28a2dbac` is exact-green: Core Focused `34754120108 = SUCCESS`, canonical Quality `34754120154 = SUCCESS`, Storage Focused `34754120185 = SUCCESS`.
- Integrator extracted only `src/athena/knowledge/user_correction_policy.py` and `tests/unit/test_knowledge_user_correction_policy.py` into current Develop.
- Current Develop canonical `34755721026` is still `IN_PROGRESS`, so integrated closure is not yet claimed.
- If that exact Develop run succeeds, promote to `FIXED`; if it fails, classify only the new exact failure signature.

## ERR-0056 — Core-Focused harness omits user-correction tests

- Severity: P2 verification/harness blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Error-owned fix remains on `postmerge/errors`: `4b723fe7202c841e0c768aaf3a62600eaadf02ff` adds `tests/unit/test_user_correction*.py` to the workflow path trigger and `test_user_correction.*` to focused selection; `ef1e9d4cb40f1c17d8c28439312fdcdeb15baa4e` adds the regression contract test.
- Current Develop `.github/workflows/core-focused-candidate.yml` still omits both user-correction selectors. Therefore the harness fix is not integrated and cannot be marked `FIXED`.
- The current Core worker avoided the gap by renaming acceptance coverage into the existing `test_knowledge*.py` selector. That proves the product slice, but does not close the harness coverage defect.
- This fix expands mandatory test coverage and does not weaken any guard.

## ERR-0053 — UI send-button shell geometry mismatch

- Severity: P2 integration blocker.
- Status: `FIXED_PENDING_VERIFY`.
- Historical UI geometry lineage was owner-side green, but Integrator correctly rejected a one-file extraction because current Develop `ShellGeometry` lacks the required `composer_action_size` token while the stylesheet references it.
- Current UI has advanced to `da52341488a365f999bbbb949acbe7f186c894ae`; its canonical Quality `34755623363` is still `IN_PROGRESS` and must not be superseded.
- Closure requires a bounded current-baseline geometry-token + component/test slice with exact worker evidence, followed by exact Develop canonical success. Do not promote the broad UI branch.

## ERR-0054 — historical visual-baseline absence on superseded UI SHA

- Severity: P2 visual-evidence blocker when reproduced.
- Status: `STALE`.
- Last exact reproduction remains on a superseded UI SHA. Reopen only on a current exact visual reproduction; do not weaken comparator tolerance or blindly accept generated baselines.

## Current worker requalification

- Spec/Core current exact candidate is fully owner-side green; `ERR-0055` now waits only on current Develop canonical.
- Backend current exact candidate is canonical green. No current Backend/Storage error cluster is reproduced.
- UI current canonical is still running; no new UI error may be opened until an exact failure exists.
- Develop current canonical is still running; no competing canonical run or Develop mutation is permitted while active.

## Persistent release guards

Closed historical signatures reopen only on a current exact-SHA reproduction. Current evidence does not reopen pypdf Packaging, fail-closed Frozen argv, Desktop/Worker two-EXE split, bounded worker tree, adaptive 2048-context Chat reserve, Windows lane-lock, duplicate-column/Core-startup/storage-bootstrap, Security, Storage or Recovery guards.

## CI discipline

- No competing canonical run was started by the Error worker.
- No Backend/UI/Spec-Core product branch was mutated by the Error worker.
- `main` and `bnbgrs/ATHENA` remain read-only.
- No force push, history rewrite, Skip/XFail, guard weakening, visual-tolerance relaxation, or Security/Storage/Recovery relaxation occurred.
