# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only failures reproduced or evidenced on the stated SHA are opened.
- Historical failures are not carried forward unless their signature recurs on the current baseline.
- Cascades are deduplicated under their primary root cause.
- `FIXED` requires observed verification; unverified fixes remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `e98c88e0d3b41b81de7efa70873729f873038080`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- This ledger update is prepared on a history-preserving NON-FORCE synchronization merge of prior Error head `550d3337151c3201452fc79ca7cb4580e060d560` with current Develop.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`.
- BLOCKED: none.

## Current scan

- Current Develop `e98c88e0d3b41b81de7efa70873729f873038080` includes the verified startup/readiness UI integration in `9f7ac114b69ee0d415ed37d27245ae28cbd3e999` and marks the capability verified in progress tracking.
- Exact UI canonical Quality run `33804193396` on `1ffd2fbc063c1836cdc2dd9504ce297807e5745a` completed successfully: specification validator PASS, Ruff PASS, mypy PASS, full pytest PASS, Windows path safety PASS, Linux storage PASS, local-install smoke PASS, canonical enforcement PASS.
- Therefore `ERR-0004` is now `FIXED`. The B010→I001 sequence was one deduplicated harness lint cluster; no production/runtime defect was implicated.
- No new concrete current-lineage failure is evidenced in this scan. Cancelled/action-required workflows without failing jobs are not allocated new ERR IDs.
- Qt deleted-`QProcess` stderr remains warning-only because no current-lineage failing path has been reproduced.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence: product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` integrated; canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke.
- primary root cause: deletion-ledger APIs lacked explicit bool-safe fail-before-SQL runtime validation.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Backend run `33749788522`.
- remaining risks: none for this signature absent recurrence.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Ruff PASS in run `33749788522`.

### ERR-0003 — Shell tests retain obsolete permanently-visible inspector contract

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `f76911dfef6530041d62fb6c2e0ddec242d64231`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED`
- primary root cause: test-harness/contract drift after UI-GAP-0002 changed the inspector to contextual visibility.
- affected files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_commit: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification executed: canonical Quality run `33745885426` PASS on byte-identical affected product/test blobs.

### ERR-0004 — UI startup/readiness harness fails canonical Ruff

- first_seen: 2026-09-03
- last_seen: 2026-09-04
- checked_sha: `1ffd2fbc063c1836cdc2dd9504ce297807e5745a`
- severity: P2
- area: Quality / Python lint / Qt startup-readiness test harness
- status: `FIXED`
- exact evidence:
  - Run `33785726577`: exact Ruff `B010` at startup harness line 61; all other required stages passed.
  - UI correction `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removed the constant-name `setattr` site.
  - Run `33792012599` then exposed Ruff `I001`; formatting-only correction `ecbf44ddd0fb8c7428d4cca090834eca284b997e` was insufficient.
  - Run `33797732276` proved the remaining failure was exactly `I001` at line 1 while full pytest passed `4492 passed, 3 skipped` and all non-Ruff required stages were green.
  - Final correction `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` changed only the local import symbol order so `UI_REFINEMENT_TASKS_2801_2900` precedes `PathenaStartupExperience`.
  - Exact current-head Quality `33804193396` completed SUCCESS: validator, Ruff, mypy, full pytest, Windows path safety, Linux storage, local-install smoke and canonical enforcement all PASS.
- primary root cause: startup harness lint defects: first constant-name `setattr` violating B010, then incorrect import symbol ordering violating I001.
- affected file: `tests/unit/test_pathena_startup_experience_2900.py`; no production/runtime defect implicated.
- fix_commit: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; final I001 `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification executed: canonical exact-head Quality run `33804193396` completed success across every required job/stage.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: error-cleared; verified equivalent product/test blobs are integrated on Develop in `9f7ac114b69ee0d415ed37d27245ae28cbd3e999`.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
