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
- Baseline SHA: `4d36d5f13e1449973e74c48df5e2efb53d0e8aae`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with exact current Develop via merge commit `ae52fb6243d85219a0328d602212b280f75b02a2`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0005`.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`.
- BLOCKED: none.

## Current scan

- UI system-tray Quality run `33822842314` on exact UI SHA `19402585415e7b5ed341386bb2d689d6a636e270` completed `failure`: Windows path safety PASS, Linux storage PASS, local-install smoke PASS, specification validator PASS, Ruff PASS, full pytest PASS; Python 3.12 quality failed specifically at `Quality — mypy`, with canonical enforcement failing as the downstream consequence.
- UI immediately supplied bounded correction `72e43bc18c28b5c92f6528919abf788f66924ba9`, narrowing `QApplication.instance()` through a local `application` value and assigning `self.app: QApplication` only after the existing `isinstance(..., QApplication)` guard.
- Exact-head follow-up Quality run `33822861477` on `72e43bc18c28b5c92f6528919abf788f66924ba9` has already passed local-install smoke, Windows path safety, Linux storage, specification validator, Ruff and mypy; full pytest/canonical enforcement remain in progress. Therefore `ERR-0005` is `FIXED_PENDING_VERIFY`, not `FIXED`.
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
  - The first exact Ruff root cause was B010 in `tests/unit/test_pathena_startup_experience_2900.py` from constant-name `setattr(window, "_core_transport_ready", False)`; UI fix `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e` removed that harness-only violation without weakening assertions or Ruff rules.
  - Follow-up run `33792012599` exposed the remaining exact Ruff signature I001 in the same harness import block.
  - Intermediate import formatting `ecbf44ddd0fb8c7428d4cca090834eca284b997e` was insufficient; final symbol-order fix `a5d9530525bd0b6bf0eae3945c23a6805f6b9669` corrected the actual I001 cause.
  - Exact-head canonical Quality run `33804193396` completed `success` across Windows path safety, Linux storage, local-install smoke, Validator, Ruff, mypy, full pytest and canonical enforcement.
- reproducible path before fix: canonical Ruff against the startup/readiness harness first reported B010, then after that correction reported I001 import ordering.
- primary root cause: two bounded test-harness lint defects introduced in the startup/readiness coverage; no product runtime defect was established.
- affected files: `tests/unit/test_pathena_startup_experience_2900.py` only for the root-cause fixes; product startup/readiness semantics unchanged.
- fix_commit: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; final I001 `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification executed: canonical Quality run `33804193396` PASS on exact UI lineage; no skip/XFail/assertion/guard weakening used.
- remaining risks: none for this signature absent recurrence.
- integrator handoff: error blocker cleared; the verified startup/readiness lineage is already represented on Develop.

### ERR-0005 — System-tray QApplication ownership typing fails canonical mypy

- first_seen: 2026-09-04
- last_seen: 2026-09-04
- checked_sha: `19402585415e7b5ed341386bb2d689d6a636e270`
- severity: P2
- area: Qt/Desktop / system tray / static typing
- status: `FIXED_PENDING_VERIFY`
- exact evidence:
  - Canonical UI Quality run `33822842314` completed `failure` on exact SHA `19402585415e7b5ed341386bb2d689d6a636e270`.
  - Windows path safety, Linux storage, local-install smoke, specification validator, Ruff and full pytest all passed; `Quality — mypy` alone failed, and canonical enforcement failed only as its downstream aggregate consequence.
  - UI corrective commit `72e43bc18c28b5c92f6528919abf788f66924ba9` changes only `src/athena/desktop/pathena_system_tray.py`: it assigns `QApplication.instance()`/injected app to local `application`, retains the existing runtime `isinstance(application, QApplication)` fail-closed guard, then assigns `self.app: QApplication = application` after narrowing.
  - Exact-head follow-up run `33822861477` has already passed specification validator, Ruff and mypy plus Windows path safety, Linux storage and local-install smoke; pytest/canonical enforcement are still running.
- reproducible path before fix: canonical mypy on the system-tray candidate could not prove that `self.app` was a `QApplication` when it was assigned directly from `app or QApplication.instance()` before the runtime type guard.
- primary root cause: static type narrowing occurred too late for the instance attribute assignment; the runtime ownership guard itself was correct and remains unchanged.
- affected files: `src/athena/desktop/pathena_system_tray.py`.
- fix_commit: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification executed: exact-head follow-up run `33822861477` mypy PASS; full canonical Quality still pending, therefore no FIXED claim yet.
- remaining risks: none known for runtime semantics; final full-pytest/canonical-enforcement completion remains required.
- integrator handoff: do not integrate the failing `194025...` candidate; consider the corrected `72e43bc...` lineage only after exact-head run `33822861477` completes success.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
