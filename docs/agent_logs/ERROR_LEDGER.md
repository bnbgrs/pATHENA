# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

Stable IDs use `ERR-####`. Only current exact-SHA reproduced or verified failures are active; cascades are deduplicated. `FIXED` requires real integrated verification. Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`. No Skip/XFail, dummy success path, guard/assertion weakening, main mutation, force-push or history rewrite.

## Current baseline

- Develop: `f301540eb707013e7b88c08ef248ea98edc1564d`; exact canonical Quality `34741552444 = IN_PROGRESS`. The immediately preceding integrated parent `a26e2c03be10342476e406a18fbfb917a5a47ffe` has canonical `34739022121 = SUCCESS`.
- Error worker entered this run at `f73625ea0b3e42ef298bd1d09fc49e95b4c6f528`; zero workflow runs existed on that exact branch before mutation.
- Workers: Spec/Core `3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`; Backend `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1`; UI `718d9002d5300afce74b04b0e4e8d40a9d00642e`.
- Spec/Core exact: Core Focused `34740030025 = FAILURE`; canonical `34740029996 = FAILURE`. Focused behavior is `4 passed`; full canonical pytest is `5041 passed, 17 skipped`. Both failing lanes reduce to one Ruff `I001` in `tests/unit/test_knowledge_read_api.py`.
- Backend exact: Storage Focused `34740393786 = FAILURE`; canonical `34740393790 = FAILURE`. Canonical full pytest is `1 failed, 5037 passed, 17 skipped`; the sole failure is `test_bound_preflight_rejects_invalid_complete_sidecar_rotation`. Specification Validator, Ruff, mypy, Linux Storage, Local Install/pypdf and the complete Windows release-guard lane are green on the same exact SHA.
- UI exact: UI Focused `34741192757 = SUCCESS`; Core Focused `34741192744 = SUCCESS`; canonical `34741192787 = IN_PROGRESS`. No current UI product error is evidenced by the completed focused lanes.
- `main` and `bnbgrs/ATHENA` remain read-only and untouched.

## Current state

- OPEN: `ERR-0049`, `ERR-0052`.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: prior closures plus `ERR-0047`, `ERR-0050`, `ERR-0051`.
- STALE: `ERR-0014`, `ERR-0025`, `ERR-0026`, `ERR-0028`, `ERR-0029`, `ERR-0038`, `ERR-0039`.
- BLOCKED: none.

## ERR-0052 — Spec/Core Knowledge Read API Ruff/import blocker

- Severity: P2 integration blocker.
- Status: `OPEN`.
- Current exact reproducer: `postmerge/spec-core@3e3dc4d3f4777b083d9ef2b09819cbad51ab9034`.
- Core Focused `34740030025 = FAILURE`; canonical `34740029996 = FAILURE`.
- Focused pytest is `4 passed`; canonical full pytest is `5041 passed, 17 skipped`. Product behavior therefore passes on both focused and full-suite paths.
- The only current blocking signature is Ruff `I001` at `tests/unit/test_knowledge_read_api.py:1:1`.
- Exact Ruff remediation changes only the import-block formatting: one excess blank line before `KNOWLEDGE_ID` is removed. No product logic, assertion, security/storage/recovery behavior or test coverage needs to change.
- The current Spec/Core delta from the last green integrated parent is bounded to the new `src/athena/api/knowledge_read.py` plus `tests/unit/test_knowledge_read_api.py`, so this is Spec/Core-owned rather than a Develop cascade.
- Error worker must not duplicate the feature worker mutation. Required closure path: Spec/Core applies only the Ruff-safe formatting correction, reruns Core Focused and canonical on the resulting exact SHA, then Integrator imports the bounded slice and obtains integrated canonical success before `FIXED`.

## ERR-0049 — concurrent SQLite writer startup vs fail-closed sidecar identity continuity

- Severity: P1 Storage/Recovery integration blocker.
- Status: `OPEN`.
- Current Backend successor `517ca6ebd98ee2ff719827b043e2eee7ddd1e2e1` reproduces the same fail-closed defect: Storage Focused `34740393786 = FAILURE`; canonical `34740393790 = FAILURE`.
- Canonical full pytest is `1 failed, 5037 passed, 17 skipped`. The sole failure remains `tests/unit/test_storage_database_startup_identity.py::test_bound_preflight_rejects_invalid_complete_sidecar_rotation`: simultaneous replacement of already-present WAL and SHM while primary DB identity is unchanged is not rejected with `DatabaseStartupIdentityChangedError`.
- Relative to the last integrated parent `a26e2c03...`, the Backend product/test delta is still bounded to `src/athena/storage/database.py` and `tests/unit/test_storage_database_startup_identity.py`; no second Backend product cluster is evidenced.
- Current `_revalidate_existing_identity()` admits complete->complete transitions when both sidecar filesystem identities rotate, then validates the new pair read-only. Readability proves compatibility but not continuity/provenance with the preflight generation.
- `DatabaseFileSetIdentity` carries presence/device/inode only. Once both sidecars are replaced, that token alone cannot distinguish a legitimate same-database lifecycle rotation from an arbitrary coherent replacement.
- The positive process-separated regression explains the original race: two legitimate starters can interleave between preflight and live-writer establishment because no cross-process startup ownership fence spans a fresh preflight through writer establishment.
- Do not solve this by another broad permissive `complete_rotation` exception. Safe design space remains: positive same-generation continuity, or a bounded cross-process startup ownership mechanism that waits safely, re-preflights after ownership, and holds ownership through writer establishment. A nonblocking lock that simply fails the second legitimate starter is insufficient.
- Required same-SHA evidence before promotion: (1) paired foreign WAL+SHM replacement is rejected; (2) legitimate two-process startup succeeds for both starters; (3) single-sidecar replacement remains rejected; (4) partial publication/withdrawal remains rejected; (5) complete publication/withdrawal retain their specified legitimate behavior; (6) Storage Focused and canonical are both green.

## Recent integrated closures

- `ERR-0047 = FIXED`: schedule-startup priority contract repaired and integrated; current green Develop predecessor confirms closure.
- `ERR-0050 = FIXED`: mandatory desktop-controller tests remain active in fail-closed process isolation; integrated canonical is green.
- `ERR-0051 = FIXED`: Knowledge model-disclosure Ruff blocker is owner- and integrated-green.
- Closed IDs stay closed unless a new current exact-SHA reproduction exists.

## Persistent release guards

Closed/stale historical signatures reopen only on current exact-SHA reproduction. Binding guards remain: Windows pypdf packaging; fail-closed Frozen argv; separate Desktop/Worker EXEs; exactly one Desktop with bounded workers; adaptive 2048-context Chat reserve; Windows lane-lock `PermissionError` -> `SchedulerLaneOwnershipError` -> packaged-worker `OSError`; duplicate-column/Core-startup/storage-bootstrap signatures. On current Backend `517ca6e...`, all Windows release-guard steps, Linux Storage and Local Install/pypdf are green despite the isolated canonical pytest failure. Current Develop `f301540e...` remains under its already-running exact canonical verification; no competing run is permitted.

## CI discipline

- No competing canonical run was started by the Error worker.
- `postmerge/errors` had zero workflow runs before this run's first mutation.
- Current Develop and UI exact canonical runs were already active and were left untouched.
- No product code or foreign worker branch was mutated.
- No force push, history rewrite, main mutation, Skip/XFail, guard relaxation, or Security/Storage/Recovery weakening occurred.
