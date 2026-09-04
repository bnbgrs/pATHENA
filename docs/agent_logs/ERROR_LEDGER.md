# pATHENA Error Ledger

Canonical post-merge error register for `bnbgrs/pATHENA`.

## Rules

- Stable IDs use `ERR-####`.
- Only reproduced or exact-SHA evidenced failures are opened.
- Cascades are deduplicated under the primary root cause.
- `FIXED` requires observed verification; unverified corrections remain `FIXED_PENDING_VERIFY`.
- Allowed states: `OPEN`, `IN_PROGRESS`, `FIXED_PENDING_VERIFY`, `FIXED`, `STALE`, `BLOCKED`.
- `main` and `bnbgrs/ATHENA` remain read-only.

## Current baseline

- Baseline branch: `develop/pathena-next`
- Baseline SHA: `5d7061678afd2e2f6195d5a3ce6e15cde2797007`
- Stable read-only parent: `main@0d4d621f8a38ddf8eccfa09622bf193687619943`
- Worker branch: `postmerge/errors`
- History-preserving NON-FORCE synchronization merge: `2fc8b3cfb7a764a223d56fffe80eb720c00ba13f`.

## Current error state

- OPEN: none.
- IN_PROGRESS: none.
- FIXED_PENDING_VERIFY: none.
- FIXED: `ERR-0001` through `ERR-0007`.
- BLOCKED: none.

## Current scan

- Repaired-lineage canonical Quality `33838658964` completed `success` on `7ee8638187acf77221631db944fa0628adb36c5c`, closing both `ERR-0006` and `ERR-0007` with exact combined verification.
- Backend source-types Sequence boundary Quality `33840621670` on `75ae07fdb0bf72c100cc8401f7881ffa03b96b03` also completed `success`; no new Error ID is allocated from that slice.
- Current Develop additionally records canonical-green Research coverage integration; no concrete new current-lineage failure signature was found in this run.

## Entries

### ERR-0001 — Deletion-ledger malformed runtime boundaries
- first_seen: 2026-09-03
- severity: P2
- area: Storage / Persistence / Recovery boundary
- status: `FIXED`
- evidence: canonical Backend `33749788522`.
- root_cause: bool-safe/runtime validation missing before SQL mutation/cursor boundaries.
- files: `src/athena/lifecycle/deletion.py`; `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `780d25d74ce2e310b6a4bc434f547a23163e8b78` plus harness `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: focused boundary tests, validator, Ruff, mypy, Windows/Linux-storage/local-install PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0002 — Deletion-boundary harness Ruff I001
- first_seen: 2026-09-03
- severity: P2
- area: Quality / Python lint
- status: `FIXED`
- evidence: Ruff failure `33744816398`; Ruff PASS `33749788522`.
- root_cause: import ordering/formatting in `tests/unit/test_deletion_ledger_boundaries.py`.
- files: `tests/unit/test_deletion_ledger_boundaries.py`.
- fix_sha: `2f705d5e0fc1c77dd60612b5aeaa16d9380e46cd`.
- verification: canonical Ruff PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0003 — Stale permanent-inspector harness contract
- first_seen: 2026-09-03
- severity: P1
- area: Qt/Desktop / UI contract harness
- status: `FIXED`
- evidence: Backend `33755878184` failed two stale inspector assertions; canonical UI `33745885426` passed byte-identical relevant product/harness blobs.
- root_cause: test contract lagged contextual `Evidence & Activity` inspector behavior.
- files: `tests/unit/test_pathena_window.py`; product reference `src/athena/desktop/pathena_window.py` unchanged.
- fix_sha: `6253577227d427c9bb00707c3e3e578a16c0f9d6`.
- verification: canonical exact-content PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0004 — Startup/readiness harness canonical Ruff regressions
- first_seen: 2026-09-03
- severity: P2
- area: Qt/Desktop / startup-readiness harness / Ruff
- status: `FIXED`
- evidence: `33785726577` exposed B010; `33792012599` exposed residual I001; exact-head `33804193396` completed SUCCESS.
- root_cause: bounded test-harness lint defects, not runtime behavior.
- files: `tests/unit/test_pathena_startup_experience_2900.py`.
- fix_sha: B010 `77e7b4c7d95202e6814226e2b4a2c4a54e3f5c8e`; I001 `a5d9530525bd0b6bf0eae3945c23a6805f6b9669`.
- verification: Windows path safety, Linux storage, local-install, validator, Ruff, mypy, full pytest, canonical enforcement PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0005 — System-tray QApplication ownership typing
- first_seen: 2026-09-04
- severity: P2
- area: Qt/Desktop / system tray / mypy
- status: `FIXED`
- evidence: canonical UI `33822842314` failed mypy only; corrected exact-head `33822861477` completed SUCCESS.
- root_cause: typed `self.app` assignment occurred before runtime `QApplication` narrowing.
- files: `src/athena/desktop/pathena_system_tray.py`.
- fix_sha: `72e43bc18c28b5c92f6528919abf788f66924ba9`.
- verification: all canonical stages PASS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0006 — Research UUID filter container boundary is not runtime-safe
- first_seen: 2026-09-04
- severity: P2
- area: Research / Jobs / runtime validation / API boundary
- status: `FIXED`
- evidence: Backend canonical `33833499697` on `24775cd9b6dd621a1cde188a376a3926c3c062b2` failed API runtime boundary/local-install/mypy/pytest; focused verifier `33833496929` passed.
- repro: scalar text-like or non-Sequence values could cross `_stable_uuids()` normalization instead of failing closed.
- root_cause: static `Sequence[uuid.UUID]` annotation was trusted at runtime without explicit container validation.
- files: `src/athena/research/service.py`; `tests/unit/test_research_stable_strings_boundaries.py`.
- fix_sha: owner fix `462fba22637e0083c87df32f987134ce0fb3de00`; equivalent integrated blobs `4b390b4fcc39affc1884f304f460901d07ea622a`.
- verification: focused pytest/Ruff/mypy/diff-check PASS; repaired-lineage combined canonical Quality `33838658964` completed SUCCESS.
- risk: none absent recurrence.
- integrator_handoff: cleared.

### ERR-0007 — Missing contradiction-review dependency breaks integrated Core import graph
- first_seen: 2026-09-04
- severity: P1
- area: Core / Knowledge / application composition / integration dependency
- status: `FIXED`
- checked_sha: defective integrated lineage validated by run `33838377083`; repair `05bca268e2d2fc8e5b0f5ae59c564f2403605540`; combined verification head `7ee8638187acf77221631db944fa0628adb36c5c`.
- evidence: post-integration Quality `33838377083` produced `ModuleNotFoundError: No module named 'athena.knowledge.contradiction_review_gate'`; pytest collection cascaded to 131 errors, with mypy, local-install and API-runtime checks failing from the same absent module.
- repro: import `athena.knowledge.acceptance_service` on the defective integrated lineage; its direct import of `athena.knowledge.contradiction_review_gate` cannot resolve.
- root_cause: earlier Core integration carried `acceptance_service.py` without its required contradiction-review module dependency. This is an integration omission, not a Research UUID regression.
- files: restored `src/athena/knowledge/contradiction_review_gate.py`; importer `src/athena/knowledge/acceptance_service.py` unchanged by repair.
- fix_sha: `05bca268e2d2fc8e5b0f5ae59c564f2403605540`, restoring exact blob `95866345cfa5fd2727bdb01c60ec4b2a60660707` from canonical-green Core head `a20dbe70824d5fc07bdd1d981e3acf431554877a` / Quality `33826094843`.
- verification: repaired-lineage combined canonical Quality `33838658964` completed SUCCESS, including full pytest and canonical enforcement.
- risk: none absent recurrence.
- integrator_handoff: cleared.

## Historical/stale evidence

Historical pre-consolidation/recovery/platform-parity failures remain stale unless their exact signature recurs on current `develop/pathena-next`.
