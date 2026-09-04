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
- Baseline SHA: `3659470baa5cc0cdeea538bcfe241174f319a502`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with exact current Develop via merge commit `880ecb17aa000ed02782e8338481217f54000e41`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`, `ERR-0005`.
- BLOCKED: none.

## Current scan

- Exact-head UI follow-up Quality run `33822861477` on `72e43bc18c28b5c92f6528919abf788f66924ba9` completed `success`; this closes `ERR-0005` with real canonical verification.
- Integrator has already accepted the verified UI-GAP-0006 system-tray product/test blobs onto Develop and records that integration from the exact green UI lineage.
- Current UI head `6d1862eddf6fff3620a7871ccb9176c62e6b737e` has Quality run `33826919058` still in progress; no new error is allocated without a concrete failing job/signature.
- No recurrence of `ERR-0001`..`ERR-0004` is evidenced.

## Entries

### ERR-0001 — Deletion-ledger mutation/cursor boundaries accept malformed runtime types

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Storage / Persistence / Deletion Ledger / Recovery boundary
- status: `FIXED`
- exact evidence:
  - Product fix `780d25d74ce2e310b6a4bc434f547a23163e8b78` is integrated into Develop.
  - Canonical Backend run `33749788522` passed all 22 deletion-boundary tests plus validator, Ruff, mypy, Windows path safety, Linux storage and local-install smoke on the exact integrated product/test content.
- reproducible path before fix: malformed entity/runtime integer boundaries could cross validation before SQL because Python `bool` is an `int` subclass and annotations did not enforce runtime types.
- primary root cause: deletion-ledger APIs lacked explicit bool-safe fail-before-SQL runtime validation.
- affected files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_commit: `780d25d74ce2e310b6a4bc434f547a23163e8b78`; harness correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: 22 focused boundary tests PASS inside canonical Backend run `33749788522`; validator/Ruff/mypy/Windows/Linux-storage/local-install PASS.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: no action required.

### ERR-0002 — Backend deletion-boundary test import block failed canonical Ruff I001

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `58dbd4d80bc61c4cc8e9cd6d61adaa5b311ea4c3`
- severity: P2
- area: Quality / Python lint / Storage boundary test harness
- status: `FIXED`
- exact evidence: canonical Ruff failure in `33744816398`, import-format-only correction `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`, canonical Ruff PASS in `33749788522`.
- reproducible path: canonical Ruff on the previous Backend lineage reproduced I001.
- primary root cause: import ordering/formatting defect in `tests/unit/test_deletion_ledger_boundaries.py`.
- affected files: `tests/unit/test_deletion_ledger_boundaries.py` only.
- fix_commit: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification executed: canonical Ruff PASS in run `33749788522`.
- remaining risks: none for this signature.
- integrator handoff: no action required.

### ERR-0003 — Shell tests retain obsolete permanently-visible inspector contract

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `7be496d2fcbb94ab81f5e520f2e45ee2820d3fd9`
- severity: P1
- area: Qt/Desktop / UI contract harness / contextual Evidence & Activity inspector
- status: `FIXED`
- exact evidence:
  - Canonical Backend Quality run `33755878184` failed only at full pytest with two stale persistent-inspector assertions.
  - Diagnostics artifact `9894914799` records exactly `2 failed, 4488 passed, 3 skipped, 2 warnings`.
  - Fix `6253577227d427c9bb00707c3e3e578a16c0f9d6` restores the known-green shell-test contract for contextual inspector visibility.
  - Canonical UI run `33745885426` completed `success` on byte-identical affected product/harness blobs.
- reproducible path before fix: Workspace without grounded context correctly hid the contextual inspector while stale tests required permanent visibility.
- primary root cause: test-harness/contract drift, not a product visibility regression.
- affected files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_commit: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification executed: canonical Quality `33745885426` PASS on byte-identical relevant blobs.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: no action required.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions

- first_seen: 2026-09-03
- last_seen: 2026-09-03
- checked_sha: `1ffd2fbc063c1836cdc2dd9504ce297807e5745a`
- severity: P2
- area: Qt/Desktop / startup-readiness test harness / canonical Ruff
- status: `FIXED`
- exact evidence:
  - Quality run `33785726577` on `b76115748aed53e3502a71eef10a41b11f97f8ae` passed Windows path safety, Linux storage, local-install smoke, Validator, mypy and full pytest; Ruff alone failed.
  - First exact Ruff root cause was B010 in `tests/unit/test_pathena_startup_experience_2900.py`; UI fix `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removed it without weakening assertions or Ruff rules.
  - Follow-up run `33792012599` exposed I001 in the same harness import block.
  - Final symbol-order fix `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` corrected the actual I001 cause.
  - Exact-head canonical Quality run `33804193396` completed `success` across Windows path safety, Linux storage, local-install smoke, Validator, Ruff, mypy, full pytest and canonical enforcement.
- reproducible path before fix: canonical Ruff first reported B010, then after that correction I001 import ordering.
- primary root cause: two bounded test-harness lint defects; no product runtime defect established.
- affected files: `tests/unit/test_pathena_startup_experience_2900.py`.
- fix_commit: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; final I001 `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification executed: canonical Quality `33804193396` PASS; no skip/XFail/assertion/guard weakening used.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: error blocker cleared.

### ERR-0005 — System-tray QApplication ownership typing fails canonical mypy

- first_seen: 2026-09-04
- last_seen: 2026-09-04
- checked_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`
- severity: P2
- area: Qt/Desktop / system tray / static typing
- status: `FIXED`
- exact evidence:
  - Canonical UI Quality run `33822842314` failed on exact SHA `19402585415e7b5ed341386bb2d689d6a636e270`; Windows path safety, Linux storage, local-install smoke, validator, Ruff and full pytest passed, while `Quality — mypy` was the only primary failure.
  - UI correction `72e43bc18c28b5c92f6528919abf788f66924ba9` changes only `src/athena/desktop/pathena_system_tray.py`, retaining the runtime ownership guard and moving `self.app: QApplication` assignment after successful narrowing.
  - Exact-head follow-up canonical Quality run `33822861477` completed `success` on `72e43bc18c28b5c92f6528919abf788f66924ba9`, including validator, Ruff, mypy, Windows path safety, Linux storage, local-install smoke, full pytest and canonical enforcement.
  - Integrator handoff confirms the verified system-tray product/test blobs were integrated onto `develop/pathena-next` as UI-GAP-0006.
- reproducible path before fix: canonical mypy could not prove that `self.app` was a `QApplication` because the instance attribute was assigned from `app or QApplication.instance()` before the runtime type guard narrowed it.
- primary root cause: static type narrowing occurred too late for instance-attribute assignment; runtime ownership guard was correct and remains unchanged.
- affected files: `src/athena/desktop/pathena_system_tray.py`.
- fix_commit: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification executed: exact-head canonical Quality `33822861477` PASS across every required stage.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: error blocker cleared; failing `194025...` remains rejected, corrected verified lineage is already represented on Develop.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
