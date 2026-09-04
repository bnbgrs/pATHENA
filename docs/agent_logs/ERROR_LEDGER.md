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
- Baseline SHA: `606e9dc72278ec331856e998a1b3fb4fa4754787`
- Stable read-only parent: `main` at `0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- Worker synchronized history-preservingly and NON-FORCE with exact current Develop via merge commit `256f2381d20a98323e2d4f52829a8a710f19152a`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: `ERR-0006`.
- FIXED: `ERR-0001`, `ERR-0002`, `ERR-0003`, `ERR-0004`, `ERR-0005`.
- BLOCKED: none.

## Current scan

- Canonical Backend Quality run `33833499697` on `24775cd9b6dd621a1cde188a376a3926c3c062b2` failed reproducibly across API runtime path-boundary/local-install/full-pytest execution; validator and Ruff passed, while mypy and pytest failed.
- The dedicated bounded verifier `33833496929` completed `success` and produced Backend commit `462fba22637e0083c87df32f987134ce0fb3de00`, hardening `_stable_uuids()` against scalar text-like and non-Sequence containers and adding focused regression coverage.
- Canonical Quality on exact fix SHA `462fba22637e0083c87df32f987134ce0fb3de00` is not yet available: run `33833527206` concluded `action_required` without executing jobs. Therefore `ERR-0006` remains `FIXED_PENDING_VERIFY`, not `FIXED`.
- Current UI Quality `33834029967` on `3407fd0169ff3b5ccfc711d2562153f25cc3ce26` has Windows path safety, Linux storage, local-install smoke, validator, Ruff and mypy passing; full pytest remains in progress and supplies no new failure signature yet.
- No recurrence of `ERR-0001`..`ERR-0005` is evidenced.

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

### ERR-0006 — Research UUID filter container boundary is not runtime-safe

- first_seen: 2026-09-04
- last_seen: 2026-09-04
- checked_sha: `24775cd9b6dd621a1cde188a376a3926c3c062b2`
- severity: P2
- area: Research / Jobs / runtime validation / API boundary
- status: `FIXED_PENDING_VERIFY`
- exact evidence:
  - Canonical Backend Quality `33833499697` on exact SHA `24775cd9b6dd621a1cde188a376a3926c3c062b2` failed. Linux storage's focused storage tests passed, then `Run API runtime path-boundary regressions` failed; local-install smoke failed at the disposable Core/API restart smoke; Windows path safety passed locality/storage checks then failed at the same API runtime path-boundary regressions; Quality passed validator and Ruff but failed mypy and pytest, with canonical enforcement failing as a cascade.
  - Dedicated bounded verifier workflow `33833496929` completed `success`. Its exact focused contract applies the UUID-container patch, runs `tests/unit/test_research_stable_strings_boundaries.py`, Ruff on `src/athena/research/service.py` plus that test, mypy on `src/athena/research/service.py`, and `git diff --check`, then commits the verified product/test delta.
  - Resulting owner fix commit `462fba22637e0083c87df32f987134ce0fb3de00` changes `_stable_uuids(values: Sequence[uuid.UUID])` to a runtime-checked `object` boundary, rejects scalar `str`/`bytes`/`bytearray` and non-`Sequence` containers with `ResearchConfigurationError`, preserves UUID-only element validation and deterministic UUID normalization, and adds focused regression tests.
  - Exact-fix canonical Quality `33833527206` concluded `action_required` before jobs ran; this is not failure evidence but also not canonical verification.
- reproducible path before fix: `_stable_uuids()` trusted a `Sequence[uuid.UUID]` annotation at runtime, so text-like scalars and other unexpected containers could cross the normalization boundary instead of failing closed with the configured Research validation error.
- primary root cause: Research UUID filter normalization lacked explicit runtime container validation; static typing did not enforce the boundary at runtime.
- affected files: `src/athena/research/service.py`; `tests/unit/test_research_stable_strings_boundaries.py`.
- fix_commit: `462fba22637e0083c87df32f987134ce0fb3de00`.
- verification executed: focused verifier `33833496929` PASS for the exact product/test patch, focused pytest, Ruff, mypy and diff-check. Canonical exact-fix verification remains pending because `33833527206` was `action_required` without jobs.
- remaining risks: exact candidate still needs canonical Quality (or equivalent exact-SHA full verification) before promotion from `FIXED_PENDING_VERIFY` to `FIXED`.
- integrator handoff: do not treat failing `24775cd9...` as READY. Review `462fba22637e0083c87df32f987134ce0fb3de00` only after exact-fix canonical/full evidence is available under normal READY policy.

## Historical/stale evidence

Historical pre-consolidation and recovery/platform-parity failures remain stale unless their signature recurs on current `develop/pathena-next`.
